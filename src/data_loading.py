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
    labels = []
    for label in os.listdir(location):
        label_path = os.path.join(location,label)
        labels.append(label_path)

    images = []
    for img in os.listdir(os.path.join(input_dir,"images")):
        img_path = os.path.join(input_dir,"images",img)
        images.append(img_path)

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
                case("images","train"): data_list = train_images
                case("images","val"): data_list = val_images
                case("labels","train"): data_list = train_labels
                case("labels","val"): data_list = val_labels

            for each in data_list:
                shutil.copy(each,destination)


def create_yaml_and_txt_files(input_dir,target_dir):

    os.makedirs(target_dir,exist_ok=True)

    print("Creating yaml...")
    yaml_path = os.path.join(target_dir, "yolov8_formated_data.yaml")

    with open(yaml_path, "w", encoding="utf-8") as file:
        file.write(
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
                print("Fortschritt:",int(label[:-4])/2000 * 100)
                
            ##converting xml to txt
            with open(os.path.join(location,'labels', label.replace(".xml", ".txt")), "w", encoding="utf-8") as txt_file:
               
                # Beispiel: nach allen <name>-Einträgen suchen
                for object in root.findall('object'):
                    name = object.find('name').text
                    color = object.find('color').text
                    class_name = name #f"{name}_{color}"
                    if(not class_name in class_dictionary):
                        class_dictionary.append(name)
                        file.write(f"  {class_counter}: {name}\n")
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

                    #Umrechnung in YOLO-Format
                    img_width, img_height = 2048, 2048
                    x_center = ((xmin + xmax) / 2) / img_width
                    y_center = ((ymin + ymax) / 2) / img_height
                    width = (xmax - xmin) / img_width
                    height = (ymax - ymin) / img_height

                    txt_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                   

        print("All Done, bye bye...")

#os.makedirs(os.path.join(location,'labels'),exist_ok=True)

#create_yaml_and_txt_files(input_dir=input_dir,target_dir=target_dir)
format_data(input_dir,target_dir,location)
