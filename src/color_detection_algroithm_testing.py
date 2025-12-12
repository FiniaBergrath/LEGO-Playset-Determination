import matplotlib.pyplot as plt
import numpy as np
x_coords = np.array([10, 50, 20, 80, 45, 75]) 

# Y-Koordinaten der Pixel
y_coords = np.array([20, 10, 60, 30, 90, 55])

# Farbwerte (RGB-Tupel von 0 bis 1). Matplotlib erwartet Farben normalisiert auf [0, 1].
# Beispiel: (255, 0, 0) wird zu (1.0, 0.0, 0.0)
colors_255 = np.array([
    [255, 0, 0],     # Rot
    [0, 255, 0],     # Grün
    [0, 0, 255],     # Blau
    [255, 255, 0],   # Gelb
    [100, 100, 100], # Grau
    [255, 165, 0]    # Orange
])

# Farben auf den Matplotlib-Bereich [0, 1] normalisieren
colors_normalized = colors_255 / 255.0

# 2. Plot erstellen
# -------------------------------------------------------------------

# Neue Figur und Achsen erstellen
fig, ax = plt.subplots(figsize=(6, 6))

# Die Pixel plotten
# s=200 setzt die Größe der Punkte, c=colors_normalized setzt die Farbe
ax.scatter(
    x_coords, 
    y_coords, 
    c=colors_normalized, 
    s=200,  # Größe der Punkte
    marker='s' # Quadratischer Marker, um Pixel besser zu simulieren
)

# Achsenbeschriftung und Titel
ax.set_title('Pixel-Plot (Koordinaten und Farben)')
ax.set_xlabel('X-Koordinate')
ax.set_ylabel('Y-Koordinate')

# Achsenlimits auf 0 bis 100 setzen (typische Bildkoordinaten)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Y-Achse invertieren, um der typischen Bildkoordinate zu folgen (Ursprung oben links)
ax.invert_yaxis() 

# Raster hinzufügen
ax.grid(True, linestyle='--', alpha=0.6)

# Plot anzeigen
plt.show()

###################################################

from skimage import color
import numpy as np
import cv2

test_image = r"data\b100-lego-detection-dataset\yolov8_formatted_data\images\val\5.png"
img = cv2.imread(test_image, flags=cv2.IMREAD_COLOR_RGB) #Flag: Sorgt dafür, dass die Farben in RGB gelesen werden, Standard wäre BGR
img = img / 255 
img_cielab = color.rgb2lab(img)
pixels = img.load()
same_color_classifier = 0.5

def get_all_colors(img_px):
    all_colors = []
    color_count = []
    current_color = 0
    #var current_color
    for pixel in img_px:
        if(current_color != 0):
            new_color = False
            color = 0
            farbunterschied = color.deltaE_ciede2000(current_color, pixel)
            if(farbunterschied > same_color_classifier):
                all_colors.append(pixel)
                new_color = True

            for color in all_colors:
                farbunterschied = color.deltaE_ciede2000(current_color, color)
                if(farbunterschied > same_color_classifier):
                    all_colors.append(pixel)
                    new_color = True
                    color = color 
            
            if(new_color == False):
                if(color != 0):
                    


        else: current_color = pixel


        

       


img= cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

img = img / 255.0

img_lab = color.rgb2lab(img)
