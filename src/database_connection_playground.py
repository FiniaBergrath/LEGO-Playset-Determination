import rebrick
import json
import matplotlib.pyplot as plt
import numpy as np
import asyncio


class db_connection():

        def __init__(self):
                super().__init__()
                self.rb = self.connect_to_rebrick()


        def connect_to_rebrick(self):
                API_KEY = "efdc569787c300ddb18940ffa2081b2d"
                rebrick.init(API_KEY)

                rb = rebrick.Rebrick(API_KEY, silent=True)
                rb.login("ChilliMilli", "3V$gImjlsjjUDrRj")
                return rb

        def get_colors(self):
                print("Get colors:")
                response = rebrick.lego.get_colors()
                print(json.loads(response.read()))

        def search_sets(self,search_name):
                print("Searching for", search_name)

                sets = []
                data = rebrick.lego.get_sets(search = str(search_name), page= 1, page_size=5)
                print(data)
                data = (json.loads(data.read()))
                print("----", data)
                for result in data['results']:
                        name = result["name"]
                        set_num = result["set_num"]
                        sets.append((name, set_num))
                print(sets)
                return sets

        def get_element_by_id(self,id):
                data = self.rb.get_element(id)
                print(data)
                print()

        def get_element_image(self, element_id):
                print("Get element image:")
                data = self.rb.get_element_image(str(element_id))
                print(data)
                data_arr = np.asarray(data)
                print(data_arr)
                #plt.imshow(data_arr)
                #plt.show()

        def get_element_image(self, element_url):
                return self.rb.get_file(element_url) #Rückgabe: Bildinhalt in byte?
        

        #7891-1
        def get_set(self, set_id):
                print("Get set:")
                response = rebrick.lego.get_set(set_id)
                print(json.loads(response.read()))
                print()

        def get_set_elements(self, set_id):
                print("Get set elements:")
                data = rebrick.lego.get_set_elements(set_id, part_details= True)
                data = json.loads(data.read())
                print(data)

                count = data['count']

                if(count == 0):
                        print("The Inventory of this Set is empty!")
                        return None, None, None
                
                bricks = []
                brick_count = []

                for result in data['results']:
                        part_id = result['part']['part_num']
                
                        color_id = result['color']['id']
                        brick = (part_id, color_id)
                        if len(bricks) > 0 and brick in bricks :
                                index = bricks.index(brick)
                                brick_count[index] += 1
                        else:

                                bricks.append(brick)
                                brick_count.append(1)
        
                return count, bricks, brick_count
        
        def get_element_details(self,element_id):
                result = self.rb.get_element(element_id)
                return result

        def get_element(self,part_id, color_id, api_key=None):

                parameters = {'key': api_key}

                path = rebrick.config.API_LEGO_URL + "parts/%s/" % part_id + "colors/%s/" % color_id

                result = rebrick.request.request(path, parameters)
                result = json.loads(result.read())
                print(result)

                return result
        

db = db_connection()

#sets = db.search_sets("Star Wars")
element_ids = db.get_element("3004","15")
print(element_ids)
image_url = element_ids['part_img_url']
for element in element_ids["elements"]:
        result = db.get_element_details(element)
        discribtion = result.part.name
        color = result.color
        print(discribtion)
        print(color.name)

db.get_element_image(image_url)

#print(db.get_set_elements("7891-1"))
#print(db.get_set_elements("0011-3"))