import os
import yaml
import tempfile
import random
import shutil
import xml.etree.ElementTree as ET

input_dir = "LEGO-ObjectDetection/data/b100-lego-detection-dataset"
target_dir = os.path.join(input_dir,"yolov8_formated_data")

location = os.path.join(input_dir,"labels_as_txt","labels")
#location = os.path.join(input_dir,"annotations")

def format_data(input_dir, target_dir, location):
    print("Collecting data...")

    #Die zueinander gehörigen Labels und Images müssen in val und train landen
    labels = sorted(os.listdir(location))   
    images = sorted(os.listdir(os.path.join(input_dir,"images")))
 
    data = list(zip(images,labels))

    #random.shuffle(data)
    split_idx = int(len(data)*0.7)

    train_data = data[:split_idx]
    val_data = data[split_idx:]

    train_images, train_labels = zip(*train_data)
    val_images, val_labels = zip(*val_data)

    print("Creating Yolov8 formated Directorys and inserting Data...")
    for type in ["images","labels"]:
        for split in ["train","val"]:
            destination = os.path.join(target_dir,type,split)
            os.makedirs(destination, exist_ok=True)
            
            
            data_list = []
            
            match(type,split):
                case("images","train"): 
                    data_list = train_images
                    current_location = os.path.join(input_dir,"images")
                case("images","val"): 
                    data_list = val_images
                    current_location = os.path.join(input_dir,"images")
                case("labels","train"): 
                    data_list = train_labels
                    current_location = location
                case("labels","val"): 
                    data_list = val_labels
                    current_location = location

            for each in data_list:
                shutil.copy(os.path.join(current_location,each),destination)


def create_yaml_and_txt_files(input_dir,target_dir):

    os.makedirs(target_dir, exist_ok=True)  #Erstellt den Zielordner
    os.makedirs(location, exist_ok = True)  #Erstellt einen Zwischenordner in den die Umgewandelten labels abgelegt werden

    print("Creating yaml...")
    yaml_path = os.path.join(target_dir, "yolov8_formated_data.yaml")

    with open(yaml_path, "w", encoding="utf-8") as yaml_file:
        yaml_file.write(
            f"path: {target_dir}\n"
            f"train: {os.path.join('images', 'train')}\n"
            f"val: {os.path.join('images', 'val')}\n"
            f"names:\n"
        )
        print("Collecting classes")
        class_dictionary = []
        class_counter = 0
        for label in os.listdir(os.path.join(input_dir,'annotations')):

            tree = ET.parse(os.path.join(input_dir,'annotations',label))
            root = tree.getroot()

            if int(label[:-4]) % 100 == 5:
                print("Fortschritt:",int(label[:-4])/1999 * 100) #Funktioniert nicht richtig, da OS die Dateien nicht sortiert durchläuft
                
            #Erstellt eine .txt File mit Namen des aktuellen Labels im Zwischenodner 
            with open(os.path.join(location, label.replace(".xml", ".txt")), "w", encoding="utf-8") as txt_file:
               
                # Der Inhalt der xml Strucktur wird ausgelesen und im Label Format für yolov8 in die txt-Datei geschrieben
                for object in root.findall('object'):
                    name = object.find('name').text
                    color = object.find('color').text
                    class_name = name #f"{name}_{color}"
                    if(not class_name in class_dictionary):
                        class_dictionary.append(name)
                        yaml_file.write(f"  {class_counter}: {name}\n")     #Gibt jeder Klasse einen Identifier und notiert diesen in der yaml
                        class_id = class_counter
                        class_counter +=1
                    else:
                        class_id = class_dictionary.index(class_name)

                    #Umschreiben der Objektinformationen
                    bndbox = object.find('bndbox')
                    xmin = float(bndbox.find("xmin").text)
                    ymin = float(bndbox.find("ymin").text)
                    xmax = float(bndbox.find("xmax").text)
                    ymax = float(bndbox.find("ymax").text)

                    #Umrechnung in YOLO-Format (Aus Pixelpositionen werden relative Werte zwischen 0 und 1)
                    img_width, img_height = 2048, 2048
                    x_center = ((xmin + xmax) / 2) / img_width
                    y_center = ((ymin + ymax) / 2) / img_height
                    width = (xmax - xmin) / img_width
                    height = (ymax - ymin) / img_height

                    txt_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                   

        print("Yaml and Labels were successfully created!")

#os.makedirs(os.path.join(location,'labels'),exist_ok=True)


create_yaml_and_txt_files(input_dir=input_dir,target_dir=target_dir)
format_data(input_dir,target_dir,location)
