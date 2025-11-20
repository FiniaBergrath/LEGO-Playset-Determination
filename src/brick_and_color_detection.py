from ultralytics import YOLO
from ultralytics.data.converter import convert_coco
from PIL import Image

def main():
    
    #Lädt  das trainierte Model
    model = YOLO("./runs/detect/train11/weights/best.pt")

    #Lässt eine Prädiktion für ein Bild oder zur Live-Erkennung treffen
    #source = "0" - Nutzt die Kamera des Laptops; source = "/img.png" - wertet das übergebene Bild aus
    #show: Zeigt das Ergebnis visuell in einem externen Fenster

    test_image = "LEGO-ObjectDetection/data/b100-lego-detection-dataset/yolov8_formated_data/images/val/5.png"
    img = Image.open(test_image)
    results = model.predict(source=img, save=True, save_txt=True)

if __name__ == "__main__":
    main()
