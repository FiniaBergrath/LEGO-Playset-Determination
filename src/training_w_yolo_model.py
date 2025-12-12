from ultralytics import YOLO
from ultralytics.data.converter import convert_coco
import os

def main():
    
     #Lädt ein vortrainiertes Model von ultralytics - Zu Beginn "yolov8m.pt" um mit einen vortrainierten Model zu starten
     #"path/to/last.pt" -> Startet das Training vom letzten Checkpoint aus
    model = YOLO("yolov8m.pt")

    #Versuch das Datenset ins Yolo-Format zu konvertieren -> Funktioniert mit meinem Datenset leider nicht, das Datenset muss dafür eine bestimmte Struktur erfüllen
    #convert_coco(labels_dir="LEGO-ObjectDetection/data/b100-lego-detection-dataset/annotations") 

    #Yaml mit Pfadangabe und Klassenids zum Datenset
    datasetpath = r"data/b100-lego-detection-dataset/yolov8_formated_data/yolov8_formated_data.yaml"

    #Holt sich aus dem letzten Training 
    trainings = os.listdir("runs")
    if len(trainings) != 0:
        weights = True
    else:
        last_training = sorted(trainings)[trainings.count()-1]
        weights = os.path.join("runs",last_training,"weights/best.pt")

      #workers: Defininiert die Anzahl an Dataloadern; Hier gleich 0 um eine Überlastung des Bus zu vermeiden?
    #resume:  Lässt das Model an einem zuvor gespeicherten Checkpoint weitertrainieren
    #batch:   Kann als ganze Zahl, Auslastungsprozentsatz für die GPU oder Automatisch gestellt sein
    #save_period: Ermöglicht das Speichern von Checkpoints
    #pretrained: Lädt vortrainierte Gewichte zum training - oben hole ich die des letzten trainings bzw. setzte weights = true, dabei werden Gewichte geladen die von Ultralytics stammen
    #fraction: Da das Datenset sehr groß ist, beschränke ich hier die Menge der Bilder die zum Training genommen werden auf 70%
    model.train(data=datasetpath, epochs = 50, device='CUDA', workers = 1, batch = 6, save_period = True, pretrained = weights, fraction=0.6)
    results = model.val(data=datasetpath, workers = 0)
    print(results.box.map)  # Print mAP50-95

    #Führt je nach eingabe ein
    #results = model.predict(source="0", show=True)

if __name__ == "__main__":
    main()
