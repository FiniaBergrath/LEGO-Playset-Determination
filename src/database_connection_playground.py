import rebrick 
import json
import matplotlib.pyplot as plt
import numpy as np

API_KEY = "efdc569787c300ddb18940ffa2081b2d"
rebrick.init(API_KEY)

rb = rebrick.Rebrick(API_KEY, silent=True)
rb.login("ChilliMilli", "3V$gImjlsjjUDrRj")

print("Get colors:")
response = rebrick.lego.get_colors()
print(json.loads(response.read()))



data = rb.get_element(300401)
print(data)
print()

print("Get element image:")
data = rb.get_element_image(300401)
print(data)
data_arr = np.asarray(data)
print(data_arr)
#plt.imshow(data_arr)
#plt.show()

#7891-1
print("Get set:")
response = rebrick.lego.get_set(7891-1)
print(json.loads(response.read()))
print()

print("Get set elements:")
data = rebrick.lego.get_set_elements(7891-1, part_details= True)
print(json.loads(data.read()))
print()

for object in data:
        box = object["box"]
        x_start = int(box['color'])
        y_start = int(box['element_id'])
        x_end = int(box['quantity'])
        y_end = int(box['y2'])