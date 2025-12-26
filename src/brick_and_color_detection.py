from ultralytics import YOLO
from ultralytics.data.converter import convert_coco
from PIL import Image
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage import color

def detect_edges(x_start,y_start,x_end,y_end,pixels):
        
    pixels = pixels.convert('RGB')
    bbox_px = np.asarray(pixels) 
    bbox_px = bbox_px[y_start:y_end,x_start:x_end]
    bbox_lab = color.rgb2lab(bbox_px / 255)   

    height = y_end - y_start
    width = x_end - x_start

    color_differences = np.zeros((height,width))

    #Kanten und homogene Flächen finden:
    current_color = bbox_px[0]
    for y in range(0,height):
        current_color = bbox_lab[y,0]
        for x in range(0,width):
            color_differences[y,x] = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            current_color = bbox_lab[y,x]

    plt.imshow(color_differences)
    plt.show()

    plt.imshow(bbox_px)
    plt.show()



def detect_brick_color(x_start,y_start,x_end,y_end,pixels):
        
    pixels = pixels.convert('RGB')
    bbox_px = np.asarray(pixels) 
    bbox_px = bbox_px[y_start:y_end,x_start:x_end]
    bbox_lab = color.rgb2lab(bbox_px / 255)

    plt.imshow(bbox_px)
    plt.show()
    plt.imshow(bbox_lab)
    plt.show()

    threshold = 15
    color_switches = [[] for rows in range(y_end)] #Eine Liste von Listen um die Pixelkoordinaten der Kanten zu speichern
    edge_detected = False
    #Kanten und homogene Flächen finden:
    current_color = bbox_lab[0,0]

    height = y_end - y_start
    width = x_end - x_start
    for y in range(0,height):
        current_color = bbox_lab[y,0]
        edge_detected = False
        for x in range(0,width):
            difference = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            is_edge = bool(difference > threshold)
            match (is_edge,edge_detected):
                    case (True,False):
                        edge_detected = True
                        color_switches[y].append(x)
                    case (False,True):
                        edge_detected = False

            current_color = bbox_lab[y,x]

    detected_object = bbox_px.copy()
    for y in range(0,height):
        switches = color_switches[y]
        switch_count = np.size(color_switches[y])
        if(switch_count > 1):

            begin_left = x_start
            end_left = color_switches[y][0]

            begin_right = color_switches[y][switch_count-1]
            end_right = x_end

            if(switch_count == 3):
                bbox_center = x_end - x_start
                a = abs(bbox_center - color_switches[y][0])
                b = abs(bbox_center - color_switches[y][1])
                c = abs(bbox_center - color_switches[y][2])
                unkown_edge = max(a,b,c)
                if(unkown_edge < bbox_center):
                    begin_left = x_start
                    end_left = color_switches[y][1]
                else:
                    begin_right = color_switches[y][1]
                    end_right = x_end

            detected_object[y, begin_left:end_left] = 0
            

            if(switch_count == 4):
                detected_object[y, color_switches[y][1]:color_switches[y][2]] = 0
                

            detected_object[y, begin_right:end_right] = 0

        else:
            detected_object[y] = 0   


    
    for x in range(0,width):
        current_color = bbox_lab[y,0]
        edge_detected = False
        for y in range(0,height):
            difference = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            is_edge = bool(difference > threshold)
            match (is_edge,edge_detected):
                    case (True,False):
                        edge_detected = True
                        color_switches[x].append(y)
                    case (False,True):
                        edge_detected = False

            current_color = bbox_lab[y,x]

    detected_object = bbox_px.copy()
    for x in range(0,width):
        switches = color_switches[x]
        switch_count = np.size(color_switches[y])
        if(switch_count > 1):

            begin_left = y_start
            end_left = color_switches[y][0]

            begin_right = color_switches[y][switch_count-1]
            end_right = y_end

            if(switch_count == 3):
                bbox_center = y_end - y_start
                a = abs(bbox_center - color_switches[y][0])
                b = abs(bbox_center - color_switches[y][1])
                c = abs(bbox_center - color_switches[y][2])
                unkown_edge = max(a,b,c)
                if(unkown_edge < bbox_center):
                    begin_left = y_end
                    end_left = color_switches[y][1]
                else:
                    begin_right = color_switches[y][1]
                    end_right = y_end

            detected_object[begin_left:end_left,x] = 0
            

            if(switch_count == 4):
                detected_object[color_switches[y][1]:color_switches[y][2],x] = 0
                

            detected_object[begin_right:end_right,x] = 0

        else:
            detected_object[y] = 0   








    #Falls detected_object nach dem Scanning nur noch aus wenigen Pixeln besteht oder ganz leer ist wird davon ausgegangen, dass der gesamte Block die Boundingbox füllt 

    plt.imshow(detected_object)
    plt.show()

    detected_object = color.rgb2lab(detected_object / 255)

    not_empty_pixels = np.all(detected_object != 0, axis=-1) 
    filtered_pixels = detected_object[not_empty_pixels]        
    print(filtered_pixels)
    median_color = np.median(filtered_pixels, axis = 0)
    median_color = median_color.reshape(1,3)

    print(median_color)


    colors_rgb = np.array([
        [255,   0,   0],   # Rot
        [  0, 255,   0],   # Grün
        [  0,   0, 255],   # Blau
        [255, 255,   0],   # Gelb
        [255, 165,   0],   # Orange
        [128,   0, 128],   # Lila
        [255, 192, 203],   # Pink
    ])
    colors_rgb = colors_rgb / 255
    colors_lab = color.rgb2lab(colors_rgb)
    print(f"colors_lab: {colors_lab}")

    color_names = np.array(["rot","grün","blau","gelb","orange","lila","pink"])


    differences = color.deltaE_ciede2000(colors_lab, median_color)
    print(differences)

    smallest_difference = np.argmin(differences) 

    print(colors_rgb[smallest_difference])
    print(color_names[smallest_difference])


    pass


def main():
    
    #Lädt  das trainierte Model
    model = YOLO("./runs/detect/train9/weights/best.pt")

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
    
    print(json_format_data) 
    
    #Über das Dictonary lassen sich nun einfach die boxen zu jedem Stein auslesen um die Farbe des Bausteins zu bestimmen

    for object in data:
        box = object["box"]
        x_start = int(box['x1'])
        y_start = int(box['y1'])
        x_end = int(box['x2'])
        y_end = int(box['y2'])
        detect_edges(x_start,y_start,x_end,y_end,img)
        detect_brick_color(x_start,y_start,x_end,y_end,img)

def determine_bricks():
    #Prediction des Yolomodels

    #Farbbestimmung der erkannten Steine

    #return Liste der erkannten Steine mit Farbe und Anzahl
    return ["3004","red",5],["3001","blue",3]
    pass


if __name__ == "__main__":
    main()
