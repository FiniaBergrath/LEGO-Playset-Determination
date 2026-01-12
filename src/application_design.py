import customtkinter as ctk
import tkinter as tk
import tk_async_execute as tae 
import asyncio
import random
import traceback

import cross_entropy_determining_set as ce

from PIL import Image

from working_and_displaying_camera_input import Capture
from database_connection_playground import db_connection
from color_detection_algorithm import color_detector


class Application(ctk.CTk):

    def __init__(self):
        super().__init__(fg_color = '#112233') #Die Anwendung erbt von CTk und entspricht dem Mainwindow
        
        ctk.set_default_color_theme("./assets/themes/custom-theme.json")
        ctk.set_appearance_mode("light")

        self.title("Lego-Set-Detection")
        self.geometry("1920x1080")
        self.minsize(1200,800)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure((0,1),weight=1, pad = 20)
        #self.attributes("-fullscreen",True)

        self.height = 1200
        self.width = 1080

        #Assets:
        loading_image = Image.open("./assets/images/lego_set_detection_1.png")
        self.loading_image = ctk.CTkImage(loading_image, size = (600,430))
        
        
        #Instances:

        #Homescreen
        self.camera_img = ctk.CTkLabel(self, image = self.loading_image, text = None)
        self.camera_img.grid(row = 0, column = 0, padx = (self.width*0.2,self.width *0.05), rowspan = 2) #Einmalige Plazierung um Kameraladezeit zu überbrücken
        self.overview_frame = OverviewFrame(self)
        self.start_button = ctk.CTkButton(self, text = " ▶ Ausführung starten ", bg_color="#ffffff"  , command=self.display_resultscreen, height= 45)

        #Resultscreen
        self.brick_result_frame = Brick_result_frame(self)
        self.set_result_frame = Set_result_frame(self)
        self.return_button = ctk.CTkButton(self, text = " ◀- Zurück zum Hauptmenü ", command = self.display_homescreen)
        
        #External 
        self.capture = None
        self.after(150, lambda: tae.async_execute(self.initialize_camera(), callback = self.start_camera))#Instanzen asynchron initalisieren -> Erhöht Startzeit der Anwendung und verringert Ladezeit während der Ausführung
       
        self.db = None
        tae.async_execute(self.initialize_db_connection(), wait=False, callback=self.on_db_loaded)

        self.detector = None
        
        #Logical
        self.detect_parts = {}

        self.bind("<<SetSelected>>", self.on_set_selected)

        self.display_homescreen(init_display=True)
        
    def on_resize(event):
        pad = max(12, int(event.width * 0.03))
            
    def display_homescreen(self, init_display = False):
        self.brick_result_frame.clear()
        self.set_result_frame.clear()
        self.return_button.grid_forget()

        if not init_display:
            self.capture.start_camera()

        self.overview_frame.grid(row = 0, column = 1, padx = (self.width * 0.05, self.width*0.2), pady = (self.height*0.1,self.height*0.1), sticky = ("ew","ns"), rowspan = 2)
        self.start_button.grid(row=1, column = 1, padx = (self.width*0.05 + 100, self.width*0.2 + 100), pady = (0, self.height * 0.15), sticky = ("ew","s"))

    #Initalisiert die Kamera - Kann Ladezeit beanspruchen, daher asynchron
    async def initialize_camera(self):
        self.capture = Capture(self,self.camera_img)

    #Startet die Kameraaufnahme - wird als Callback direkt nach Initalisierung ausgeführt
    def start_camera(self, cap = None):
        if self.capture is not None:
            self.capture.start_camera()  

    #Initalisiert die Datenbank Verbindung 
    async def initialize_db_connection(self):
        self.db = db_connection()

    def on_db_loaded(self):
        self.overview_frame.set_db_connection(self.db)
        tae.async_execute(self.initialize_detector(), wait=False)

    #Initalisiert die Datenbank Verbindung 
    async def initialize_detector(self):
        self.detector = color_detector(self.db)
  

    def display_resultscreen(self):
        setlist = self.overview_frame.get_selected_sets()
        self.overview_frame.clear()
        self.start_button.grid_forget()

        self.brick_result_frame.grid(row= 0, column = 1, padx = (self.width*0.05, self.width*0.1),pady = (self.height*0.1,self.height*0.05), sticky = ("ew","ns"))
        self.set_result_frame.grid(row= 1, column = 1, padx = (self.width*0.05, self.width*0.1),pady = (self.height*0.05,self.height*0.1), sticky = ("ew","ns"))
        self.return_button.grid(row = 0, column = 0, padx = 50, pady= 50, sticky = "nw")

        tae.async_execute(self.start_set_detection(setlist))

    async def start_set_detection(self, setlist):
        try: 
            #Kamera pausieren
            self.capture.pause_camera()

            #Detections und aktuelles Frame holen
            detections = await self.capture.get_results()
            img = self.capture.get_result_frame()
            print("Detections:", detections)

            if detections is None:
                print("No Parts detected")
                return #TODO: Meldung Anzeigen!!
            
            #Part_id auslesen und Farben bestimmen
            print("Determining Color")
            for object in detections:
                box = object["box"]
                part_id = object["name"]
                confidence = object["confidence"]
                x_start = int(box['x1'])
                y_start = int(box['y1'])
                x_end = int(box['x2'])
                y_end = int(box['y2'])
                
                color_id = random.choice([320, 1050, 69, 89, 1, 2, 35, 326, 226, 334, 14 ]) #TODO: Ersätzen 
                part_id = random.choice(["3004","3001","3023","3003","3005","6141"])
                

                #Farbbestimmung
                color = self.detector.detect_color(x_start=x_start,y_start=y_start,x_end=x_end,y_end=y_end,img=img,part_id=part_id)
                part = (part_id, color)
                
                self.brick_result_frame.display(part,self.db, confidence)
            
            print("Determining the best matching set...")

            detect_parts = self.brick_result_frame.get_parts()
            results = ce.determine_matching_of_sets(list(detect_parts.keys()), list(detect_parts.values()), list(setlist), self.db)
            self.after(0,lambda: self.set_result_frame.display(results, list(setlist)))

        except Exception as e:
            print("Fehler",e)
            traceback.print_exc()

    

    #Fängt geworfene Events und reicht die Ausführung weiter an entsprechende Instanz (Overview_frame)
    def on_set_selected(self, event):
        print("Gefangen!", event)
        self.overview_frame.on_set_selected()


class OverviewFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.root = master
        self.db = None

        #Configurations       
        self.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure((4),weight=1)

        #GUI Layout
        self.title = ctk.CTkLabel(self, text = "Willkommen!")
        self.title.configure(font=("Roboto", 35))
        self.title.grid(row = 0, column = 0, padx= 40, pady= (20,20), sticky = "w")
        
        text = ctk.CTkLabel(self, text = "Wählen Sie die gewünschten Sets aus:", text_color="#7c7977")
        text.grid(row = 1, column = 0, padx = 40, sticky = "w")
        
        sets = ["a","b"]
        self.set_frame = Set_frame(self)
        self.set_frame.grid(row = 2, column = 0, padx = (40,40), pady= 10, sticky = "ew")

        self.search_request_id = 0
        self.set_entry = ctk.CTkEntry(self)
        self.set_entry.grid(row = 3, column = 0, padx = 40, pady = 10, sticky = "nw")
        self.set_entry.insert(0,"Set hinzufügen...")
        self.set_entry.bind("<FocusIn>", lambda args: self.set_entry.delete('0', 'end'))
        self.set_entry.bind("<KeyRelease>", command=  self.on_entry_input)

        self.listbox = myListbox(self)
        
    def set_db_connection(self, db):
        self.db = db
   
    #Eingabe im Input Feld behandeln:
    def on_entry_input(self, event):
        search_name = self.set_entry.get()

        if search_name != "":
            self.search_request_id += 1
            tae.async_execute(self.search(search_name, self.search_request_id))

    #Asynchrone Datenbankabfrage nach passenden Sets zur Suchanfrage
    async def search(self, search_name, request_id):
        if self.db is None:     
            print("DB_Connection not established yet, waiting...")
            await asyncio.sleep(2)
            
            if self.db is None:
                print("Still no connection found, initalizing Connection...")
                self.db = db_connection()

        await asyncio.sleep(0.5)
        if self.search_request_id == request_id:  
            sets = self.db.search_sets(search_name)
            self.root.after(0, lambda: self.on_sets_loaded(sets))
        else: return

    #Darstellung des Ergebnisses in einer Listbox
    def on_sets_loaded(self, sets = None):
        print("Sets loaded:", sets)
        self.listbox.clear()
        if sets is None:
            return
        
        self.listbox.grid(row = 4, column = 0, padx = 40, pady = 5, sticky = "ewn")
        
        self.listbox.display(sets)

    #Fügt ein aus der Listbox ausgewähltes Set hinzu
    def on_set_selected(self):        

        set = self.listbox.get_selection()
        print("Set",set)
        self.set_frame.display_selected_set(set)    
    
    def get_selected_sets(self):
        return self.set_frame.get_selected_sets()
    
    def clear(self):
        self.grid_forget()
        self.listbox.clear()


#Selbstgeschriebenes Widget: Dem tk.Listbox-Widget nachempfunden
class myListbox(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height= 60, fg_color='#ffffff', border_width=3, border_color='#e2a9f1')
        self.set_dict = {}
        self.selected_set = None
        self.parent = master

        #Assets
        bin_image = Image.open("./assets/images/bin.png")
        self.bin_image = ctk.CTkImage(bin_image, size = (10,10))

    def on_set_selected(self, event):
        print("Wurf in Self erkannt!", self.selected_set)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.grid_forget
        self.set_dict = {}

    def display(self, sets):

        print("Displaying Options:")
        for i in range(0,len(sets)):
            self.rowconfigure(i,weight = 1)
            self.columnconfigure((0,1), weight = 1)
            
            name, id = sets[i]
            
            discribtion = f"{name} (ID: {id})"

            button = ctk.CTkButton(self, height = 40, text = discribtion, fg_color='#ffffff', hover_color="#dddddd")
            button.configure( command= lambda b=button: self.on_button_clicked(b))
            button.grid(row = i, column = 0, padx = 3, pady = 3, sticky = "ew", columnspan = 2)
            button.columnconfigure(0, weight = 1)

            self.set_dict[button] = sets[i]
    
    def on_button_clicked(self, button):
        print("Ich werfe....!")
        self.selected_set = self.set_dict[button]
        self.master.master.event_generate("<<SetSelected>>", when="now")

        button.grid_forget()
        self.set_dict.pop(button)

        if len(self.set_dict) == 0:
            self.clear()
        

    def get_selection(self):
        return self.selected_set
  

class Set_frame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(0,weight=1)
        
        #Asset laden  
        bin_image = Image.open("./assets/images/bin.png")
        self.bin_image = ctk.CTkImage(bin_image, size = (40,40))
        
        #Dictonary zum Speichern (Frame -> Set)
        self.set_dict = {}
        

    def display_selected_set(self,set):
        print("Displaying...")
        if set in self.set_dict.values():
            return

        element_row = len(self.set_dict)
        print(element_row)
        
        name,id = set
        discribtion = f"{name}, ID: {id}"

        frame = ctk.CTkFrame(self)
        frame.grid(row = element_row, column = 0, padx = 5, pady = 5, sticky = "ew")
        frame.columnconfigure(1,weight=1)
        set_label = ctk.CTkLabel(frame, text= discribtion)
        set_label.grid(row = 0, column = 1, padx = 10, sticky = "w")
        del_button = ctk.CTkButton(frame, image= self.bin_image, text = None, width = 40, fg_color = '#ffffff', hover_color="#e2a9f1", command = lambda: self.remove_selected_set(frame))
        del_button.grid(row=0, column = 2, padx = (0, 3),  sticky = "e")

        self.set_dict[frame] = set

    #Ausgewähltes Set löschen
    def remove_selected_set(self, set_display):
        self.set_dict.pop(set_display)
        set_display.grid_forget()

    def get_selected_sets(self):
        return self.set_dict.values()
    
    
class Brick_result_frame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.title = ctk.CTkLabel(self, text = "Erkannte Steine")
        self.title.configure(font=("Roboto", 25))
        self.title.grid(row = 0, column = 0, padx= 30, pady= (20,20), sticky = "w")
        
        self.bricks = {} #part -> count
        self.count_display = {} #part -> count_display-Label
        self.columnconfigure(0, weight=1)

    def is_new_brick(self, part):
        if part in self.bricks.values():
            return False
        
        return True

    def add_brick(self,part):
        self.bricks[part] = 1

    def update_part_count(self,part):
        count = self.bricks[part]
        self.bricks[part] = count + 1

        id_label = self.count_display[part]
        id_label.configure(text = f"ID: {count + 1}")

    #Wichtig: Wird in einem Asynchronen Thread aufgerufen -> daher gui-Update mit root.after
    def display(self, part, db, confidence, position = None):

        if not self.is_new_brick(part):
            self.update_part_count(self,part)
        else:
            self.add_brick(part)
        
        print("Displaying part...")
        part_id, color = part
        color_id = color.color_id

        element_ids = db.get_element(part_id,color_id)
        self.master.after(0, lambda : self.update_gui(element_ids, part, db, confidence))

 
    def update_gui(self, element_ids, part, db, confidence):
        
        part_id, color = part

        element_row = len(self.bricks) + 1 #Titel belegt row = 0 !!!

        frame = ctk.CTkFrame(self, border_width=2)
        frame.grid(row = element_row, column = 0, padx = 30, pady = 5, sticky = "ew")
        frame.columnconfigure(0, minsize=50)
        frame.columnconfigure(2, weight=1)

        element_label = ctk.CTkLabel(frame, text = None)
        element_label.grid(row = 0, column = 0, padx=(3,3), pady=(3,3), rowspan = 3)
        img_url = element_ids['part_img_url']
        tae.async_execute(self.load_element_image(db, element_label, img_url), wait = False)
        
        discribtion = ""
        for element in element_ids["elements"]:
            result = db.get_element_details(element)
            if(result != None):
                discribtion = result.part.name
            else: 
                discribtion = part_id
        
        discribtion = discribtion + f", {color.name}"

        discribtion_label = ctk.CTkLabel(frame, text = discribtion)
        discribtion_label.grid(row = 0, column = 1, padx = 5, pady = (3,2), sticky = "w")
        
        id_label = ctk.CTkLabel(frame, text = f"ID: {part_id}")
        id_label.grid(row = 1, column = 1, padx = 5, pady = 0, sticky = "w")
        id_label.configure(font=("Roboto", 13))

        count = self.bricks[part]
        count_label = ctk.CTkLabel(frame, text = f"Anzahl: {count}")
        count_label.grid(row = 2, column = 1, padx = 5, pady = (1,3), sticky = "w")
        count_label.configure(font=("Roboto", 13))

        confidence_label = ctk.CTkLabel(frame, text = f"Confidence: {confidence}")
        confidence_label.grid(row = 0, column = 2, padx = (0,5),  rowspan = 3, sticky = "e")
        
    async def load_element_image(self, db, element, image_url):
        try:
            img = db.get_element_image(image_url)
            if img is None:
                print("Image could not be found")
                #TODO: Platzhalter Img darstellen
            else:
                self.master.after(0,lambda: self.display_part_img(img, element))
        except Exception as e:
            print("Exception: ", e)

    def display_part_img(self,img, element):
        print("Image gesetzt")
        image = ctk.CTkImage(img, size = (40,40))
        element.configure(image = image)
        element.image = image
        element.grid(row = 0, column = 0, padx = 5, pady = 3, sticky ="w")

    def get_parts(self):
        return self.bricks
    
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.grid_forget()
        self.bricks = {}

class Set_result_frame(ctk.CTkScrollableFrame):
    def __init__(self,master):
        super().__init__(master)

        #Asset laden  
        win_image = Image.open("./assets/images/win.png")
        self.win_image = ctk.CTkImage(win_image, size = (50,50))

        self.title = ctk.CTkLabel(self, text = "Setbewertung")
        self.title.configure(font=("Roboto", 25))
        self.title.grid(row = 0, column = 0, padx= 30, pady= (20,20), sticky = "w")
        self.columnconfigure(0, weight=1)
    
    def display(self, results, sets):

        set_dict = {sets[i][1]: sets[i][0] for i in range(0,len(sets))} # Macht aus Setliste (name, set_id) ein dictonary (set_id -> name)
        min_ce = min(list(results.values()))   

        element_row = 1     

        for set_id, ce in results.items():

            frame = ctk.CTkFrame(self, border_width=2)
            frame.grid(row = element_row, column = 0, padx = 30, pady = 5, sticky = "ew")
            frame.columnconfigure(0, minsize=50)
            frame.columnconfigure(3, weight=1)

            element_label = ctk.CTkLabel(frame, text = None)
            element_label.grid(row = 0, column = 0, padx=(3,3), pady=(3,3), rowspan = 3)
            
            print("Suche Set_id", set_id)
            print("Alle Elemente des dict", set_dict)

            name = set_dict[str(set_id)]
            set_name_label = ctk.CTkLabel(frame, text = name)
            set_name_label.grid(row = 0, column = 1, padx = 5, pady = (3,2), sticky = "w")
            
            id_label = ctk.CTkLabel(frame, text = f"ID: {set_id}")
            id_label.grid(row = 1, column = 1, padx = 5, pady = (1,3), sticky = "w")
            id_label.configure(font=("Roboto", 13))

            if min_ce == ce:
                win_label = ctk.CTkLabel(frame, image = self.win_image, text = None)
                win_label.grid(row = 0, column = 2, padx = 5, pady = (3,3), sticky = "w", rowspan = 2)
                frame.configure(border_color = '#00bf63')

            ce_result = ""
            if ce == 1000:
                ce_result = "Es wurden keine Partinformationen zu diesem Set gefunden"
            else:
                ce_result = f"ce: {ce}"
            ce_label = ctk.CTkLabel(frame, text = ce_result)
            ce_label.grid(row = 0, column = 3, padx = (0,5),  rowspan = 2, sticky = "e")
            element_row += 1

    async def load_element_image(self, db, element, image_url):
        img = db.get_element_image(image_url)
        if img is None:
            print("Image could not be found")
            #TODO: Platzhalter Img darstellen
        else:
            self.master.after(0,lambda: self.display_part_img(img, element))

    def display_part_img(self,img, element):
        print("Image gesetzt")
        image = ctk.CTkImage(img, size = (40,40))
        element.configure(image = image)
        element.image = image
        element.grid(row = 0, column = 0, padx = 5, pady = 3, sticky ="w")

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.grid_forget()


if __name__ == "__main__":
    tae.start()  
    app = Application()
    app.mainloop()
    if app.capture != None:
        app.capture.close_camera()
    tae.stop()
   

