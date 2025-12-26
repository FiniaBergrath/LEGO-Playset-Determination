import rebrick
import json
import matplotlib.pyplot as plt
import numpy as np
import asyncio

rb = None
def connect_to_rebrick():
        API_KEY = "efdc569787c300ddb18940ffa2081b2d"
        rebrick.init(API_KEY)

        rb = rebrick.Rebrick(API_KEY, silent=True)
        rb.login("ChilliMilli", "3V$gImjlsjjUDrRj")

def get_colors():
        print("Get colors:")
        response = rebrick.lego.get_colors()
        print(json.loads(response.read()))

def search_sets(search_name):
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



def get_element_by_id(id):
        data = rb.get_element(id)
        print(data)
        print()

def get_element_image(element_id):
        print("Get element image:")
        data = rb.get_element_image(element_id)
        print(data)
        data_arr = np.asarray(data)
        print(data_arr)
        #plt.imshow(data_arr)
        #plt.show()

#7891-1
def get_set(set_id):
        print("Get set:")
        response = rebrick.lego.get_set(set_id)
        print(json.loads(response.read()))
        print()

def get_set_elements(set_id):
        print("Get set elements:")
        data = rebrick.lego.get_set_elements(set_id, part_details= True)
        data = json.loads(data.read())

        count = data['count']
        
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
        
        

def get_element(part_id, color_id, api_key=None):

        parameters = {'key': api_key}

        path = rebrick.config.API_LEGO_URL + "parts/%s/" % part_id + "colors/%s/" % color_id

        result = rebrick.request.request(path, parameters)
        print(json.loads(result.read()))


        

connect_to_rebrick()
#sets = search_sets("Star Wars")
#get_element("3004","15")
#print(get_set_elements("7891-1"))