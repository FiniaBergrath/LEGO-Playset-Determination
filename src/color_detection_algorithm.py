import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import color
import tkinter as tk
from PIL import Image, ImageTk
from database_connection_playground import db_connection

class color_detector():
    def __init__(self, db=None):
        super().__init__()

        if db is None:
            self.db = db_connection()
        else:
            self.db = db
        self.colors_rgb, self.lab_colors, self.colors = self.get_colors(self.db)
        #Einstellungen des Algorithmus
        self.number_of_colors = 20
        self.c_diff_sensitivity = 8

    
    def get_colors(self,db):

        rgb_colors = []
        all_colors = db.get_colors() #Gibt Farben als rebrick Color-Objekte zurück
        colors = [] 
        for result in all_colors:
            #hex Farbwerte zu rgb umwandeln für spätere Verwendung
            hex_color = result.rgb
            hex_color = hex_color.lstrip('#')
            rgb_color = []
            for i in [0,2,4]:
                rgb = int(hex_color[i:i+2], 16)
                rgb_color.append(rgb)
            rgb_colors.append(rgb_color)
            colors.append(result)
        
        #Ab hier werden kein Elemente mehr gesammelt, sondern Rechenoperationen angewendet -> daher nparray
        rgb_colors = np.asarray(rgb_colors)
        colors = np.asarray(colors)

        #Direkte einmalige Umwandlung in lab Farbraum - wird zur Farbbestimmung genutzt
        lab_colors = rgb_colors / 255
        lab_colors = color.rgb2lab(lab_colors)

        return rgb_colors, lab_colors, colors

    #Visualisierung
    def show_images(self, original, quantized, super_quantized, box_middle, result, color_name, img_4_viz):
        root = tk.Tk()
        root.title("Bildvergleich")

        images = [
            ("Original", original),
            ("Quantisiert", quantized),
            ("Farbtöne zusammengefasst", super_quantized),
            ("Bbox Mitte", box_middle),
            ("Ergebnis", result),
            (color_name,img_4_viz)
        ]

        tk_images = [] 

        for idx, (label_text, pil_img) in enumerate(images):
            row = (idx // 3) * 2
            col = idx % 3

            pil_img = pil_img.resize((300, 300))

            tk_img = ImageTk.PhotoImage(pil_img)
            tk_images.append(tk_img)

            label = tk.Label(root, text=label_text, font=("Arial", 12, "bold"))
            label.grid(row=row, column=col, pady=(10, 0))

            img_label = tk.Label(root, image=tk_img)
            img_label.grid(row=row + 1, column=col, padx=10, pady=10)

        
        root.mainloop()
    
    #Beschränkt die möglichen Farben auf Farben die für diesen Baustein tatsächlich exsistieren
    def determine_pot_colors(self,part_id):
        colors = self.db.get_part_colors(part_id)
        if len(colors) != 0:
            print(colors)
            color_idx = []
            original_color_idx = []
            for i in range(0,len(self.colors)):
                for pot_color in colors:
                    if self.colors[i].color_id == pot_color.color_id:
                        color_idx.append(i)
                        original_color_idx.append((i,pot_color))

            #Beschränkung der Farben auf Indizes 
            potential_colors = self.lab_colors[color_idx]
            print(potential_colors)
            pot_colors = sorted(original_color_idx)
            _,pot_colors = zip(*pot_colors)
            pot_colors = list(pot_colors)
        
        else:
            print("Color Information for this part could not be found")
            potential_colors = self.lab_colors
            pot_colors = self.colors

        return potential_colors, pot_colors

    #Ermittelt welche Bausteinfarbe in der Wahrnehmung des Menschen am ähnlichsten zur erkannten Farbe ist
    def determine_color_id(self, average_color, part_id):

        potential_colors, pot_colors = self.determine_pot_colors(part_id)
        
        average_color = average_color / 255
        average_color = color.rgb2lab(average_color)
        detected_color = np.asanyarray(average_color)

        
        differences = color.deltaE_ciede2000(potential_colors, detected_color)
        #print("differences:", differences)

        smallest_difference = np.argmin(differences) 

        result_color = pot_colors[smallest_difference]

        return result_color

    def convert_palette_2_rgb(self, color_palette, number_of_colors):
        colors = []
        for i in range(0,number_of_colors):
        
            r = i*3-1
            g = r+1
            b = r+2

            red = color_palette[r]
            green = color_palette[g]     
            blue = color_palette[b]   

            colors.append((red,green,blue))

        return colors


    #Prüfen wie signifikant die Farbunterschiede der quantisierten Farben sind und ähnliche zusammenfassen
    def combine_similar_colors(self, color_palette, brick_pixels):
        # 1) Umschreibung der color palette in Tupel aus rgb
        colors = self.convert_palette_2_rgb(color_palette,self.number_of_colors)
        
        # 2) Umwandlung in LAB-Farbraum
        rgb_colors = np.asarray(colors)
        rgb_colors = rgb_colors / 255
        lab_colors = color.rgb2lab(rgb_colors)
        #print(lab_colors)
        
        # 3) Farben die sich ähneln zu einer Zusammenfassen
        for color_idx in range(0,len(lab_colors)):
        
            for idx in range(color_idx,len(lab_colors)):
                if color_idx != idx:
                    color_difference = color.deltaE_ciede2000(lab_colors[color_idx], lab_colors[idx])
                    #print(color_difference)
                    if color_difference < self.c_diff_sensitivity:
                        brick_pixels = np.where(brick_pixels == idx, color_idx, brick_pixels)
        return brick_pixels

    def determine_box_middle(self, width, height, brick_pixels):
        x_mid = int(width/2)
        y_mid = int(height/2)
        x_range = int(0.15 * width)
        y_range = int(0.15 * height)

        image_middle = brick_pixels[(y_mid-y_range):(y_mid+y_range), (x_mid-x_range):(x_mid+x_range)]

        return image_middle

    def count_corner_colors(self, brick_pixels, number_of_colors, width, height):
        corners = [(0,0), (width-1,0), (0,height-1), (width-1,height-1)]
        x_rad = 1
        y_rad = 1
        
        corner_count = np.ones(number_of_colors)
        for x,y in corners:
                y_rad = -1 if y > 0 else 1
                for radius in range(0,5):
                    #print("x,y:", x,y)
                    #print("x_rad, y_rad:", x_rad,y_rad)
                    corner_color = (brick_pixels[y+radius*y_rad,x+radius*x_rad])
                    #print(corner_color)
                    corner_count[corner_color] += 1
                x_rad = x_rad * -1
        
        return corner_count

    def count_edge_colors(self, brick_pixels, number_of_colors, width, height):

        edge_count = np.ones(number_of_colors)    
        
        for y in [0,height-1]:
            for x in range(0,width-1):
                edge_color = brick_pixels[y,x]
                edge_count[edge_color] += 1
        
        for x in [0,width-1]:
            for y in range(0,height-1):  
                edge_color = brick_pixels[y,x]
                edge_count[edge_color] += 1
            
        return edge_count
    
        
    #number_of_colors: Anzahl der Farben auf die Quantisiert wird
    #c_diff_sensitivity: Schwellenwert um Farbtöne zu unterscheiden, sollte zwischen 5-10 liegen
    def detect_color(self,x_start,y_start,x_end,y_end,img,part_id,show = False):
    
        #Beschränkung des Bildes auf Bbox Größe
        bbox_px = np.asarray(img)
        bbox_px = bbox_px[y_start:y_end, x_start:x_end]
        width = x_end - x_start
        height = y_end - y_start

        #Farbquantisierung der Bbox
        bbox_image = Image.fromarray(bbox_px)
        original = bbox_image

        pixels = bbox_image.quantize(self.number_of_colors, method = 1)
        # => Wichtig zum nachvollziehen: Ab diesem Punkt sind die Farben mit 0 bis number_of_colors nummeriert - ihr rgb-Wert ist in color_palette gespeichert!
        
        color_list = pixels.getcolors(self.number_of_colors)
        color_palette = pixels.getpalette()
        quantized = pixels

        #Array der quantisierten bbox Pixel was zur Farbsuche manipuliert wird
        brick_pixels = np.asarray(pixels)

        #1) Farben die nach der Quantisierung ähnlich sind weiter zusammenfassen
        brick_pixels = self.combine_similar_colors(color_palette, brick_pixels)
        
        #Darstellung des Ergebnisses nach Zusammenschluss der Farben
        quantized_img = Image.fromarray(brick_pixels)
        quantized_img.putpalette(color_palette)
        super_quantized = quantized_img

        
        # --- Eintscheidungsfindung - Welche Farbe gehört zum Stein? ---


        #1. Annahme - Der Stein befindet sich zentral in der Bbox also ist die Steinfarbe in der Mitte der Box zu finden
        bbox_middle = self.determine_box_middle(width, height, brick_pixels)

            #Umwandlung zur Darstellung des Zwischenergebnisses
        middle_img = Image.fromarray(bbox_middle)
        middle_img.putpalette(color_palette)

        #2. Annahme: Ist der Prozentsatz einer Farbe sehr hoch nimmt der Stein die Bbox fast vollständig ein
        
        color_count = quantized_img.getcolors(self.number_of_colors)
        bbox_size = width * height
        max_color = max(color_count)
        count, _ = max_color
        percentage = count / bbox_size * 100

        if percentage > 55 and percentage < 90:
            for box_color in color_list:
                if box_color[1] not in bbox_middle:
                    brick_pixels = np.where(brick_pixels == box_color[1], -1, brick_pixels) # '-1' bzw. '255'(->int8) signalisiert die Farbe bzw. den Pixel als ausgeschlossen
        
        else:

            #3. Annahme - Farben an Ecken und Kanten sind unwahrscheinlich die Steinfarbe
            
            # A) Bestimmung der Farbwerte in den Eckpunkten (5x5 px) und ihrer Häufigkeit
            #count = self.count_corner_colors(brick_pixels, number_of_colors, width, height)

            # B) Bestimmung der Farbwerte entlang der BBox Kanten
            count = self.count_edge_colors(brick_pixels, self.number_of_colors, width, height)
            
            #Kombination aus Annahme 1 und 3
            for color_idx in range(0,len(count)):
                #1) Farben die nicht in der Mitte vorkommen werden ausgeschlossen
                #3) Hintergrund kommt häufig in Ecken / Kanten vor 
                #ABER: Hintergrund kann auch in der Mitte vorkommen
                #=> Farben die viel am Rand vorkommen werden auch ausgeschlossen wenn sie in der Mitte vorkommen

                percentage_amount = count[color_idx] / sum(count) * 100
                threshold = 100 / self.number_of_colors * 1.2
                
                if (color_idx not in bbox_middle) or (percentage_amount > threshold):
                    brick_pixels = np.where(brick_pixels == color_idx, -1, brick_pixels) # '-1' bzw. '255'(->int8) signalisiert die Farbe bzw. den Pixel als ausgeschlossen 
            
            
        #Umwandlung
        result = Image.fromarray(brick_pixels)
        result.putpalette(color_palette)

        '''
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
        '''
        
        #NP-Array mit Pixeln die Wahrscheinlich die Steinfarbe enthalten
        resulting_brick_array = np.where(brick_pixels == 255, 0, 1)
        #print("Ergebnis", resulting_brick_array)

        #Tatsächliches Array (Numpy)
        image_array = np.asarray(bbox_image)

        ''' #Auch methode:
        if significant_color_differances != 0:
            for y in range(0,height-1):
                for x in range(0,width-1):
                    if resulting_brick_array[y,x] == 1:
        '''             



        
        image_array = image_array * resulting_brick_array[:,:,None]
        
        #Entfernung der leeren Arrayeinträge 
        is_empty_arr = np.any(image_array != 0, axis = 2)
        #print("empty:", is_empty_arr)
        image_array = image_array[is_empty_arr == True]
        #plt.imshow(image_array)
        #plt.show()

        #Mittelwert über die Farbwerte bilden
        resulting_color = np.sum(image_array[None,:], axis = 1) / len(image_array) 
        #print("image_array",image_array)
        #print(resulting_color)
        result_4_visualization = ( resulting_brick_array[:, :, None] * resulting_color).astype(np.uint8)
        img_4_viz = Image.fromarray(result_4_visualization)


        resulting_color = self.determine_color_id(resulting_color, part_id)
        
        if show:
            self.show_images(original, quantized, super_quantized, middle_img ,result, resulting_color.name, img_4_viz)
        
        return resulting_color
