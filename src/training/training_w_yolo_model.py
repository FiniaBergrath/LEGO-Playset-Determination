from ultralytics import YOLO
from ultralytics.data.converter import convert_coco
import os

#Extrahiert die Endungen der trainings und validations damit natürlich sortiert wird 
#['train', 'train1', 'train10', 'train11', 'train2', 'train3', 'train4', 'train5', 'train6', 'train7', 'train8', 'train9', 'val', 'val2', 'val3', 'val4']
def determine_number(txt):
    number = txt.lstrip('train val')
    if(number != ''):
        return int(number)
    else:
        return 0
    

def main():
    
     #Lädt ein vortrainiertes Model von ultralytics - Zu Beginn "yolov8m.pt" um mit einen vortrainierten Model zu starten
     #"path/to/last.pt" -> Startet das Training vom letzten Checkpoint aus
    model = YOLO("yolov8m.pt")

    #Versuch das Datenset ins Yolo-Format zu konvertieren -> Funktioniert mit meinem Datenset leider nicht, das Datenset muss dafür eine bestimmte Struktur erfüllen
    #convert_coco(labels_dir="LEGO-ObjectDetection/data/b100-lego-detection-dataset/annotations") 

    #Yaml mit Pfadangabe und Klassenids zum Datenset
    datasetpath = r"data/b100-lego-detection-dataset/yolov8_formated_data/yolov8_formated_data.yaml"

    #Holt sich aus dem letzten Training 
    if os.path.exists("runs/detect"):
        path = "runs/detect"
        trainings = sorted(os.listdir(path), key = determine_number)
        if len(trainings) == 0: 
            weights = True
        else:
            if len(trainings) == 1 and os.path.exists("runs/detect/loading_weights"): #Falls noch keine regulären trainings vorhanden sind, nutze die loading_weights
                path = "runs/detect/loading_weights"
                trainings = sorted(os.listdir(path), key = determine_number)
        print(trainings)
        i = 1
        last_training = trainings[len(trainings)-i]
        while "train" not in last_training:
            last_training = trainings[len(trainings)-i]
            i += 1
            print("path:", last_training)
        weights = os.path.join("runs/detect",last_training,"weights/best.pt")
        print("Using pretrained weights:", weights)
        input("Press Enter to Continue with these weights or interrupt now")
    else:
        weights = True
    

    #workers: Defininiert die Anzahl an Dataloadern; Hier gleich 0 um eine Überlastung des Bus zu vermeiden?
    #resume:  Lässt das Model an einem zuvor gespeicherten Checkpoint weitertrainieren
    #batch:   Kann als ganze Zahl, Auslastungsprozentsatz für die GPU oder Automatisch gestellt sein
    #save: Ermöglicht das Speichern von Checkpoints
    #save_period: Ermöglicht das Speichern von Checkpoints alle n Epochen 
    #pretrained: Lädt vortrainierte Gewichte zum training - oben hole ich die des letzten trainings bzw. setzte weights = true, dabei werden Gewichte geladen die von Ultralytics stammen
    #fraction: Da das Datenset sehr groß ist, beschränke ich hier die Menge der Bilder die zum Training genommen werden auf 70%
    model.train(data=datasetpath, epochs = 100, device='CUDA', workers = 0, batch = -1 ,save = True, save_period = -1, pretrained = weights, scale=1 , mosaic=0.0)
    #results = model.val(data=datasetpath, workers = 0)
    #print(results.box.map)  # Print mAP50-95


if __name__ == "__main__":
    main()

