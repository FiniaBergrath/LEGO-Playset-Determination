from ultralytics import YOLO
from ultralytics.data.converter import convert_coco

def main():
    
     #Lädt ein vortrainiertes Model von ultralytics - Zu Beginn "yolov8m.pt" um mit einen vortrainierten Model zu starten
     #"path/to/last.pt" -> Startet das Training vom letzten Checkpoint aus
    model = YOLO("yolov8m.pt")

    #Versuch das Datenset ins Yolo-Format zu konvertieren -> Funktioniert mit meinem Datenset leider nicht, das Datenset muss dafür eine bestimmte Struktur erfüllen
    #convert_coco(labels_dir="LEGO-ObjectDetection/data/b100-lego-detection-dataset/annotations") 

    #Yaml mit Pfadangabe und Klassenids zum Datenset
    datasetpath = r"LEGO-ObjectDetection/data/b100-lego-detection-dataset/yolov8_formated_data/yolov8_formated_data.yaml"

    #workers: Defininiert die Anzahl an Dataloadern; Hier gleich 0 um eine Überlastung des Bus zu vermeiden?
    #resume:  Lässt das Model an einem zuvor gespeicherten Checkpoint weitertrainieren
    #batch:   Kann als ganze Zahl, Auslastungsprozentsatz für die GPU oder Automatisch gestellt sein
    #save_period: Ermöglicht das Speichern von Checkpoints
    model.train(data=datasetpath, epochs = 5, device='CUDA', workers = 1, batch = 0.7, save_period = True)

    #Führt je nach eingabe ein
    #results = model.predict(source="0", show=True)

if __name__ == "__main__":
    main()
