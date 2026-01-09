import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import color


'''img_path = r"runs\detect\predict\1.png"
img_path = r"runs\detect\predict\algorithm_test_1.png"
pixels = Image.open(img_path).convert('RGB')


bbox_px = np.asarray(pixels) / 255

# LAB → RGB für Plot
bbox_lab = color.rgb2lab(bbox_px)

#Wir tun so als wäre das img hier unsere Boundingbox, daher sind die Koordinaten aktuell die Bildmaße
x_start = 0
y_start = 0
x_end = 100#95
y_end = 100#49'''


import tkinter as tk
from PIL import Image, ImageTk

#Visualisierung
def show_images(original, quantized, super_quantized, result):
    root = tk.Tk()
    root.title("Bildvergleich")

    images = [
        ("Original", original),
        ("Quantisiert", quantized),
        ("Super-quantisiert", super_quantized),
        ("Ergebnis", result)
    ]

    tk_images = []  # Referenzen halten (wichtig!)

    for idx, (label_text, pil_img) in enumerate(images):
        row = (idx // 2) * 2
        col = idx % 2

        pil_img = pil_img.resize((300, 300))

        tk_img = ImageTk.PhotoImage(pil_img)
        tk_images.append(tk_img)

        label = tk.Label(root, text=label_text, font=("Arial", 12, "bold"))
        label.grid(row=row, column=col, pady=(10, 0))

        img_label = tk.Label(root, image=tk_img)
        img_label.grid(row=row + 1, column=col, padx=10, pady=10)

    root.mainloop()


#Ermittelt welche Bausteinfarbe in der Wahrnehmung des Menschen am ähnlichsten zur erkannten Farbe ist
def detect_color(average_color):
    
    average_color = average_color / 255
    average_color = color.rgb2lab(average_color)
    detected_color = np.asanyarray(average_color)

    #Aktuell noch allgeimeine Farben - Hier sollen in der Anwendung die Legosteinfarben mit FarbID verwendet werden
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
    potential_colors = np.asarray(colors_lab)

    color_names = np.array(["rot","grün","blau","gelb","orange","lila","pink"])

    differences = color.deltaE_ciede2000(potential_colors, detected_color)
    print("differences:" ,differences)

    smallest_difference = np.argmin(differences) 

    print(f"Erkannte Farbe: {color_names[smallest_difference]} : {colors_rgb[smallest_difference]}")
    #return color_id

def versuch_no7(x_start,y_start,x_end,y_end,img):
    #Beschränkung des Bildes auf Bbox Größe
    bbox_px = np.asarray(img)
    bbox_px = bbox_px[y_start:y_end, x_start:x_end]
    width = x_end - x_start
    height = y_end - y_start

    #Umwandlung
    bbox_image = Image.fromarray(bbox_px)
    #bbox_image.show()
    original = bbox_image
    
    #Farbquantisierung
    number_of_colors = 15
    pixels = bbox_image.quantize(number_of_colors)
    # => Wichtig zum nachvollziehen: Ab diesem Punkt sind die Farben mit 0 bis number_of_colors nummeriert - ihr rgb-Wert ist in color_palette gespeichert!
    color_list = pixels.getcolors(number_of_colors)
    color_palette = pixels.getpalette()
    #pixels.show()
    quantized = pixels

    brick_pixels = np.asarray(pixels)

    #Prüfen wie signifikant die Farbunterschiede der quantisierten Farben sind:

    # 1) Umschreibung der color palette in Tupel aus rgb
    colors = []
    for i in range(0,number_of_colors):
       
        r = i*3-1
        g = r+1
        b = r+2

        red = color_palette[r]
        green = color_palette[g]     
        blue = color_palette[b]   

        colors.append((red,green,blue))
    
    # 2) Umwandlung in LAB-Farbraum
    rgb_colors = np.asarray(colors)
    rgb_colors = rgb_colors / 255
    lab_colors = color.rgb2lab(rgb_colors)
    print(lab_colors)

    # 3) Farben die sich ähneln zu einer Zusammenfassen
    for color_idx in range(0,len(lab_colors)):
       
        for idx in range(color_idx,len(lab_colors)):
            if color_idx != idx:
                color_difference = color.deltaE_ciede2000(lab_colors[color_idx], lab_colors[idx])
                print(color_difference)
                if color_difference < 10:
                    brick_pixels = np.where(brick_pixels == idx, color_idx, brick_pixels)

    #Prüfen wie viele Farben nach zusammenschluss noch vorhanden sind:
    quantized_img = Image.fromarray(brick_pixels)
    quantized_img.putpalette(color_palette)
    color_count = quantized_img.getcolors(number_of_colors)
    #quantized_img.show()
    super_quantized = quantized_img
    print("color_counts: ", color_count)

    bbox_size = width * height
    max_color = max(color_count)
    count, _ = max_color
    percentage = count / bbox_size * 100
    if percentage >= 60:
        resulting_brick_array = brick_pixels
    #Wenn maximum 80% des Bildes - dann ist der Stein sehr groß

    else:
        #Eintscheidungsfindung - Welche Farbe gehört zum Stein?

        #1. Annahme - Der Stein befindet sich in der Mitte der Box
        x_mid = int(width/2)
        y_mid = int(height/2)
        x_range = int(0.2 * width)
        y_range = int(0.2 * height)

        image_middle = brick_pixels[(y_mid-y_range):(y_mid+y_range), (x_mid-x_range):(x_mid+x_range)]

        #Umwandlung
        pil_image = Image.fromarray(image_middle)
        pil_image.putpalette(color_palette)
        colors_in_middle = pil_image.getcolors()
        print(max(colors_in_middle))
        pil_image.show()


        #2. Annahme - Farben an Ecken und Kanten sind unwahrscheinlich die Steinfarbe
        pixel_access = pixels.load()
        corners = [(0,0), (width-1,0), (0,height-1), (width-1,height-1)]
        x_rad = 1
        y_rad = 1

        #A) Bestimmung der Farbwerte in den Eckpunkten (5x5 px) und ihrer Häufigkeit
        corner_count = np.ones(number_of_colors)
        '''for x,y in corners:
            y_rad = -1 if y > 0 else 1
            for radius in range(0,5):
                print("x,y:", x,y)
                print("x_rad, y_rad:", x_rad,y_rad)
                corner_color = (pixel_access[x+radius*x_rad,y+radius*y_rad])
                print(corner_color)
                corner_count[corner_color] += 1
            x_rad = x_rad * -1
    '''
        # B) Bestimmung der Farbwerte entlang der BBox Kanten
        
        for y in [0,height-1]:
            for x in range(0,width-1):
                edge_color = brick_pixels[y,x]
                corner_count[edge_color] += 1
        
        for x in [0,width-1]:
            for y in range(0,height-1):  
                edge_color = brick_pixels[y,x]
                corner_count[edge_color] += 1
        
        
        print("Image mitte:", image_middle)
        for color_idx in range(0,len(corner_count)):
            #1) Farben die nicht in der Mitte vorkommen werden ausgeschlossen - siehe Annahme 1
            #2) Hintergrund kommt häufig in Ecken vor - kann aber auch in der Mitte vorkommen
            
            percentage_amount = corner_count[color_idx] / sum(corner_count) * 100
            print("color_idx", color_idx)
            print("prozentzahl:",percentage_amount)
            schwellenwert = 100 / number_of_colors
            print("Schwellenwert:", schwellenwert)
            if (color_idx not in image_middle) or (percentage_amount > schwellenwert):
                print("Farbe ausgeschlossen")
                brick_pixels = np.where(brick_pixels == color_idx, -1, brick_pixels) # '-1' bzw. '255' signalisiert die Farbe bzw. Pixel als ausgeschlossen (hier int8)
        


        #Umwandlung um Ergebnis darzustellen:
        pil_image = Image.fromarray(brick_pixels)
        pil_image.putpalette(color_palette)
        #pil_image.show()
        result = pil_image
            
        #3. Annahme - Die Lage der Legosteine innerhalb eines Bildes lässt sich mit Zielregionen abbilden

        #Umwandlung
    pil_image = Image.fromarray(brick_pixels)
    pil_image.putpalette(color_palette)
    left_over_colors = color.getcolors(pil_image)
    
    #Schatten und übrige Farben entfernen - Methode 
    for color_idx in range(0,len(lab_colors)):
        significant_color_differances = 0
        count, color_idx = left_over_colors[color_idx]
        if(count != 0):
            for idx in range(color_idx,len(lab_colors)):
                if color_idx != idx:
                    color_difference = color.deltaE_ciede2000(lab_colors[color_idx], lab_colors[idx])
                    print(color_difference)
                    if color_difference > 6:
                        significant_color_differances += 1
    
    

    
    

    #NP-Array mit Pixeln die Wahrscheinlich die Steinfarbe enthalten
    resulting_brick_array = np.where(brick_pixels == 255, 0, 1)
    print("Ergebnis", resulting_brick_array)

    #Tatsächliches Array (Numpy)
    image_array = np.asarray(bbox_image)
    
    image_array = image_array * resulting_brick_array[:,:,None]
    
    #Entfernung der leeren Arrayeinträge 
    is_empty_arr = np.any(image_array != 0, axis = 2)
    print("empty:", is_empty_arr)
    image_array = image_array[is_empty_arr == True]
    #plt.imshow(image_array)
    #plt.show()

    #Mittelwert über die Farbwerte bilden
    resulting_color = np.sum(image_array[None,:], axis = 1) / len(image_array) 
    print("image_array",image_array)
    print(np.sum(image_array[None,:], axis = 1))

    detect_color(resulting_color)
    #return detect_color(resulting_color)
    show_images(original, quantized, super_quantized, result)



def detect_objects(x_start,y_start,x_end,y_end,bbox_lab):
    threshold = 0.01
    color_switches = [[] for rows in range(y_end)] #Eine Liste von Listen um die Pixelkoordinaten der Kanten zu speichern
    edge_detected = False

    lab_min = bbox_lab.min(axis=(0,1), keepdims=True)
    lab_max = bbox_lab.max(axis=(0,1), keepdims=True)
    lab_scaled = (bbox_lab - lab_min) / (lab_max - lab_min)
    lab_scaled = np.clip(lab_scaled, 0, 1)

    lab_rounded = np.round(lab_scaled, decimals=2)
    bbox_lab = lab_rounded

    #Kanten und homogene Flächen finden:
    current_color = bbox_lab[0,0]
    for y in range(y_start,y_end):
        current_color = bbox_lab[y,0]
        edge_detected = False
        for x in range(x_start,x_end):
            difference = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            print(difference)
            is_edge = bool(difference > threshold)
        
            match (is_edge,edge_detected):
                    case (True,False):
                        edge_detected = True
                        color_switches[y].append(x)
                    case (False,True):
                        edge_detected = False

            current_color = bbox_lab[y,x]

    print(color_switches)

    detected_object = bbox_lab.copy()
    for y in range(y_start,y_end):
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

    #Falls detected_object nach dem Scanning nur noch aus wenigen Pixeln besteht oder ganz leer ist wird davon ausgegangen, dass der gesamte Block die Boundingbox füllt 

    plt.imshow(detected_object)
    plt.show()

    detected_object = color.rgb2lab(detected_object / 255)


    not_empty_pixels = np.all(detected_object != 0, axis=-1)  # True für Pixel != 0
    filtered_pixels = detected_object[not_empty_pixels]        # shape: (N, 3)
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



def detect_edges(x_start,y_start,x_end,y_end,bbox_lab):
        
    color_differences = np.zeros((y_end,x_end))

    #Kanten und homogene Flächen finden:
    current_color = bbox_lab[0]
    for y in range(y_start,y_end):
        current_color = bbox_lab[y,0]
        for x in range(x_start,x_end):
            color_differences[y,x] = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            current_color = bbox_lab[y,x]

    img_plot = plt.imshow(color_differences)
    plt.colorbar(img_plot, label='Farbabstand (Delta E CIEDE2000)')
    plt.show()

    versuch_no5(x_start,y_start,x_end,y_end,color_differences)


def detect_faces(x_start,y_start,x_end,y_end,bbox_lab):
        
    bbox_px = np.asarray(pixels) 
    bbox_px = bbox_px[y_start:y_end,x_start:x_end]
    bbox_lab = color.rgb2lab(bbox_px / 255)   
    
    lab_rounded = np.round(bbox_lab, decimals=2)
    bbox_lab = lab_rounded
    rgb_plot = color.lab2rgb(lab_rounded)
    print(bbox_lab)
    plt.imshow(rgb_plot)
    plt.show()

    color_switches = [[] for rows in range(y_end)] 
    current_color = bbox_lab[0,0]
    print(current_color)
    for y in range(y_start,y_end):
        current_color = bbox_lab[y,0]
        color_change_detected = False
        for x in range(x_start,x_end):
           
            is_same_color = np.allclose(current_color, bbox_lab[y,x])
            
            #print(difference)
                    
            if(not is_same_color):
                current_color = bbox_lab[y,x] 
                color_switches[y].append(x)

            current_color = bbox_lab[y,x]

    
    detected_object = bbox_px.copy()
    for y in range(y_start,y_end):
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

    plt.imshow(detected_object)
    plt.show()

def versuch_no4(x_start,y_start,x_end,y_end,bbox_lab):

    threshold = 20
    color_switches = [[] for rows in range(y_end)] #Eine Liste von Listen um die Pixelkoordinaten der Kanten zu speichern
    edge_detected = False
    
    plt.imshow(bbox_px)
    plt.show()

    #Kanten und homogene Flächen finden:
    quantizied_image = bbox_px.copy()
    current_color = bbox_lab[0,0]
    for y in range(y_start,y_end):
        current_color = bbox_lab[y,0]
        edge_detected = False
        for x in range(x_start,x_end):
            difference = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            print(difference)
            if(difference < threshold):
                quantizied_image[y,x] = current_color
            else:
                quantizied_image[y,x] = bbox_lab[y,x]
                current_color = bbox_lab[y,x]

    for x in range(x_start,x_end):
        current_color = bbox_lab[y,0]
        edge_detected = False
        for y in range(y_start,y_end):
            difference = color.deltaE_ciede2000(current_color, bbox_lab[y,x])
            print(difference)
            if(difference < threshold):
                quantizied_image[y,x] = current_color
            else:
                quantizied_image[y,x] = bbox_lab[y,x]
                current_color = bbox_lab[y,x]            

    rgb_plot = color.lab2rgb(quantizied_image)
    plt.imshow(rgb_plot)
    plt.show()
    detect_faces(x_start,y_start,x_end,y_end,quantizied_image)

#versuch_no4(x_start,y_start,x_end,y_end,bbox_lab)
from scipy.ndimage import convolve
def versuch_no5(x_start,y_start,x_end,y_end,color_differences):
 

    kernel = (1/9) * np.array([ 
        [ 1,  1,  1],
        [ 1,  1,  1],
        [ 1,  1,  1]
        ], dtype=float)
    
    kernel2 = np.array([ 
        [ 0, -1,  0],
        [-1,  4, -1],
        [ 0, -1,  0]
        ], dtype=float)

    

    # 2. Den 2D-Filter auf den 2D-L*-Kanal anwenden
    output_L = convolve(color_differences, kernel2, mode='constant', cval=0.0)
    print("before" , color_differences)
    print("after" , output_L)

    plt.imshow(output_L)
    plt.show()

#versuch_no5(x_start,y_start,x_end,y_end,bbox_lab)

#detect_faces(x_start,y_start,x_end,y_end,bbox_px)
#detect_edges(x_start,y_start,x_end,y_end,bbox_lab)
#detect_objects(x_start,y_start,x_end,y_end,bbox_lab)

#versuch_no7(x_start,y_start,x_end,y_end,pixels)