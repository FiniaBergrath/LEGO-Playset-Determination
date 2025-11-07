from ultralytics import YOLO
from ultralytics.data.converter import convert_coco

def main():
    datasetpath = r"LEGO-ObjectDetection\data\b100-lego-detection-dataset\yolov8_formatted_data\yolov8_formatted_data.yaml"

    model = YOLO("yolov8m.pt") #Lädt ein vortrainiertes Model von ultralytics(Hier yolov8)

    #Versuch das Datenset ins Yolo-Format zu konvertieren -> Funktioniert mit meinem Datenset leider nicht
    #convert_coco(labels_dir="LEGO-ObjectDetection/data/b100-lego-detection-dataset/annotations") 

    model.train(data=datasetpath, epochs = 5, device='CUDA')

    #model.train(data="b100-lego-detection-dataset.zip", epochs = 5, device='cuda')
    #results = model.predict(source="0", show=True)

if __name__ == "__main__":
    main()
