from ultralytics import YOLO
from PIL import Image
import json
import sys
sys.path.append(r".\src\application")
from color_detection_algorithm import color_detector

#Dieses Skript dient zur Visualisierung des Ablaufs des Farberkennungsalgorithmus.
#Dazu wird ein Testbild aus dem Datenset geladen und das trainierte Modell trifft eine Vorhersage
#Anschließend wird für jeden erkannten Stein der Farberkennungsalgorithmus des Scripts color_detection_algorithm.py aufgerufen und die zwischenergebnisse visualisiert

def main():
    
    #Lädt  das trainierte Model
        #model = YOLO("./runs/detect/train9/weights/best.pt")
    model = YOLO("./runs/detect/loading_weights/train_16/best.pt")

    #Lässt eine Prädiktion für ein Bild oder zur Live-Erkennung treffen
    #source = "0" - Nutzt die Kamera des Laptops; source = "/img.png" - wertet das übergebene Bild aus
    #show: Zeigt das Ergebnis visuell in einem externen Fenster

    test_image = r"data\b100-lego-detection-dataset\yolov8_formatted_data\images\val\5.png"
    img = Image.open(test_image)
    results = model.predict(source=img, save=False, save_txt=False)


   # print("Ergebniss",results[0].summary())

    #wandelt das Resultobjekt von Ultralytics ins Json Format um, damit dieses in ein Python Dictonary geladen wird
    json_format_data = results[0].to_json()
    data = json.loads(json_format_data)

    #print("-------\n")
    
    #print(json_format_data) 
    
    #Über das Dictonary lassen sich nun einfach die BBoxen zu jedem Stein auslesen um die Farbe des Bausteins zu bestimmen
    
    detector = color_detector()
    for object in data:
        box = object["box"]
        part_id = object["name"]
        x_start = int(box['x1'])
        y_start = int(box['y1'])
        x_end = int(box['x2'])
        y_end = int(box['y2'])
        color_id = detector.detect_color(x_start=x_start,y_start=y_start,x_end=x_end,y_end=y_end,img=img,part_id=part_id)
        #input("Press Enter to continue...")

if __name__ == "__main__":
    main()
