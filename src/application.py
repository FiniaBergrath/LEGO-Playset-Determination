import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from PIL import Image
from database_connection_playground import db_connection
#import brick_and_color_detection as detector
import cross_entropy_determining_set as ce
import asyncio
import tk_async_execute as tae 
from working_and_displaying_camera_input import Capture
import json
import random
import io


class Application:

    def __init__(self):
        self.color_theme = {
            "white" : "#ffffff",
            "yellow": "#f3cc6f",
            "orange": "#1234",
            "grey"  : "#f0eae0"
        }
        
        #Fenstereinstellungen
        self.root = tk.Tk()
        self.root.title("Lego-Object-Detection")
        self.root.geometry("1920x1080")
        self.root.configure(bg=self.color_theme["yellow"])

        #Kamera und Database
        self.capture = None
        self.db = db_connection()

        #Listen
        self.setlist = []
        self.buttons = []
        self.detect_parts = []
        self.part_count = []

        #Widget Definitionen:

        #Main-Frame
        self.frame = tk.Frame(self.root, width=200, height=200, bg=self.color_theme["white"])
        self.frame.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor="center")
        #Set-Display
        self.set_frame = tk.Frame(self.frame, bg=self.color_theme["grey"])
        self.set_frame.place(relx = 0.05, rely=0.75, relwidth=0.5, relheight = 0.35, anchor = 'w')
        #Part-Display
        self.part_frame = tk.Frame(self.frame, bg = self.color_theme["grey"])
        #Eingabe-Feld
        self.set_entry = tk.Entry(self.frame, bg = self.color_theme["grey"], fg = "black", width = 30)
        self.set_entry.insert(0,"Set hinzufügen...")
        self.set_entry.bind("<FocusIn>", lambda args: self.set_entry.delete('0', 'end'))
        self.set_entry.bind("<KeyRelease>", func = self.on_entry_input)
        self.set_entry.place(relx=0.05, rely=0.9, anchor='sw')
        #Listbox zum Anzeigen von Suchvorschlägen
        self.listbox = tk.Listbox(self.frame)
        self.listbox.bind("<FocusIn>", func = self.on_child_selected)
        self.listbox.bind("<<ListboxSelect>>", lambda event: self.on_set_selected(self.listbox.curselection()))
        #Button zum Start der Setidentifizierung
        self.start_button = tk.Button(self.frame, text="▶ Ausführung starten", command = lambda: tae.async_execute(self.start_set_detection()))
        self.start_button.place(relx = 0.9, rely = 0.9, anchor = 'sw')
        #Button zum zurückkehren in den Hauptscreen
        self.return_button = tk.Button(self.frame, text = "<- Return to Homescreen", command = self.return_to_homescreen)
        #Assets:
        self.bin_image = tk.PhotoImage(file="./assets/bin.png").subsample(5,5)

        #Kamera starten:
        self.root.after(150, lambda: tae.async_execute(self.initialize_camera(), callback = self.start_camera))

    

    #Soll die Listbox nicht mehr anzeigen sobald sie über keine Inhalte mehr verfügt:
    def on_child_selected(self, event):
        children_count = len(self.listbox.winfo_children())
        if children_count == 0:
            self.listbox.place_forget()

    #Eingabe im Input Feld behandeln:
    def on_entry_input(self, event):
        search_name = self.set_entry.get()
        if search_name != "":
            tae.async_execute(self.search(search_name))
    
    #Asynchrone Datenbankabfrage nach passenden Sets zur suchanfrage
    async def search(self, search_name):
        sets = self.db.search_sets(search_name)
        self.root.after(0, lambda: self.on_sets_loaded(sets))
    
    #Darstellung des Ergebnisses in einer Listbox
    def on_sets_loaded(self, sets = None):
        print("Sets loaded:", sets)
        self.listbox.delete(0, tk.END)
        if not sets:
            return

        self.listbox.place(relx=0.05, rely=0.9,relwidth=0.3, anchor='nw')
        
        for set in sets:
            set_discribtion = 'Name: ' + set[0] + '       SetID: ' + set[1]
            self.listbox.insert(tk.END, set_discribtion)

        

    #Fügt ein aus der Listbox ausgewähltes Set hinzu
    def on_set_selected(self, item_idx):
        print("Set hinzugefügt. Aktuelle Liste:", self.setlist)
        #Setname und ID aus discribtion extrahieren
        set_discribtion = self.listbox.get(item_idx)
        split = set_discribtion.rsplit('       ')
        set_name = split[0].lstrip("Name:")
        set_id = split[1].lstrip("SetID: ")
        item = (set_name,set_id)
        self.listbox.delete(item_idx)

        i = len(self.setlist)
        self.display_set_as_selected(set_name,set_id,i)

        self.setlist.append(item)
        print(self.setlist)
        print("Aktuelle Buttonliste:", self.buttons)

    #Stellt das Set als ausgewählt dar und ergänzt einen Button zum löschen
    def display_set_as_selected(self,set_name, set_id, y_offset):

        y = 0.2 + y_offset * 0.1

        tk.Label(self.set_frame, text = "Name:").place(relx = 0.05, rely = y)
        tk.Label(self.set_frame, text = set_name).place(relx = 0.1, rely = y)
        tk.Label(self.set_frame, text = "ID:").place(relx = 0.6, rely = y)
        tk.Label(self.set_frame, text = set_id).place(relx = 0.65, rely = y)
        
        button = tk.Button(self.set_frame, image = self.bin_image, command = lambda: self.remove_set(button))
        button.place(relx = 0.95, rely = y, anchor= "ne")
        self.buttons.append(button)
        print("Aktuelle Buttonliste:", self.buttons)
        

    #Darstellung bzw. Update der ausgewählten Legosets
    def display_selected_sets(self):
        for widget in self.set_frame.winfo_children():
            widget.destroy()
        print("Alle Inhalte gelöscht, wird neu aufgebaut...")
        for i in range (0,len(self.setlist)):
            set_name,set_id = self.setlist[i]
            self.display_set_as_selected(set_name,set_id,i)


    #Löscht ein ausgewähltes set
    def remove_set(self,button):
        print("betätigter Button:", button)
        print("Entferne Eintrag... Aktuelle Liste:",self.setlist)
        idx = self.buttons.index(button)
        print("Buttons:",self.buttons)
        print("Buttonindex:",idx)

        if idx != None:
            self.setlist.pop(idx)
            self.buttons.pop(idx)
            print("Ergebnis:", self.setlist)
            print(self.buttons)
            self.buttons.clear()
            print("Liste gecleart:", self.buttons)
            self.display_selected_sets()
        else:
            print("Button not found")

    #Initalisiert die Kamera - Kann Ladezeit beanspruchen, daher asynchron
    async def initialize_camera(self):
        self.capture = Capture(self.frame)

    #Startet die Kameraaufnahme
    def start_camera(self, cap = None):
        if self.capture is not None:
            self.capture.start_camera()

    #Startet die Ermittlung des Legosets
    async def start_set_detection(self):
        
        #Kamera pausieren
        self.capture.pause_camera()

        #Detections holen
        self.detect_parts.clear()
        detections = await self.capture.get_results()
        json_format_data = detections[0].to_json()
        data = json.loads(json_format_data)
        print(data)

        #Part_id auslesen und Farben bestimmen
        print("Determining Color")
        for object in data:
            box = object["box"]
            part_id = object["name"]
            x_start = int(box['x1'])
            y_start = int(box['y1'])
            x_end = int(box['x2'])
            y_end = int(box['y2'])
            #detect color 
            color_id = random.choice([320, 1050, 69, 89, 1, 2, 35, 326, 226, 334, 14 ]) #TODO: Ersätzen 
            part_id = random.choice(["3004","3001","3023","3003","3005","6141"])
            part = (part_id, color_id)
            
            #Fügt den Stein der Liste erkannter Steine hinzu bzw. erhöht die Anzahl falls schon vorhanden
            if(part in self.detect_parts):
                idx = self.detect_parts.index(part)
                self.part_count[idx] = self.part_count[idx] + 1
            else:
                self.detect_parts.append((part_id,color_id))    #TODO: Überlegen ob Verwendung von dict statt Liste sinnvoller? 
                self.part_count.append(1)

        #Kreuzentropie bestimmen
        print("Determining the best matching set...")
        results = ce.determine_matching_of_sets(self.detect_parts, self.part_count, self.setlist, self.db)

        #Screen updaten
        self.display_detected_parts()
        self.display_results(results)
        self.return_button.place(relx=0.05, rely=0.05, anchor= 'nw')
        pass
        
    def display_detected_parts(self):
        self.part_frame.place(relx = 0.95, rely=0.03, relwidth=0.5, relheight = 0.35, anchor = 'ne')
        tk.Label(self.part_frame, text = "Erkannte Steine").place(relx = 0.05, rely = 0.05, anchor='nw')

        print('Anzahl erkannter Objekte: ',len(self.detect_parts) )
        if(len(self.detect_parts) != 0):
            index = 0
            for part in self.detect_parts:
                part_id,color_id = part
                #element_ids = self.db.get_element(part_id,color_id)
                element_ids = self.db.get_element("3004","15")
                print(element_ids)
                image_url = element_ids['part_img_url']
                for element in element_ids["elements"]:
                    result = self.db.get_element_details(element)
                    if(result != None):
                        discribtion = result.part.name
                        color = result.color
                
                img = self.db.get_element_image(image_url)
                img = Image.open(io.BytesIO(img))
                img.show()
                img = img.resize((40,40))

                frame = tk.Frame(self.part_frame, bg= self.color_theme["white"])
                frame.place(relx=0.05, rely= 0.1 + index * 0.2, relwidth=0.8, relheight=0.2, anchor='nw')
                print("Frame gesetzt")
                image= ImageTk.PhotoImage(image=img)
                img_label = tk.Label(frame,image = image)
                img_label.image = image
                img_label.place(relx=0.01, rely= 0.5, anchor = 'w')
                tk.Label(frame, text= f"{discribtion}, {color}")    #TODO
                tk.Label(frame, text= f"ID: {part_id}")
                tk.Label(frame, text= "Anzahl:")
                tk.Label(frame, text= "Confidence:")

                index += 1
                #.... TODO

    def display_results(self, results):
        #self.set_frame.place() #An geeigneten Ort umplatzieren
        for widget in self.set_frame.winfo_children():
            widget.destroy()
        print("Alle Inhalte gelöscht, stelle Ergebnisse dar...")
        for i in range (0,len(results)):
            frame = tk.Frame(self.set_frame)
            frame.place(relx=0.05, rely= 0.1 + i * 0.2, relwidth=0.8, relheight=0.2, anchor='nw')

            set_id, ce = results[i]
            y = 0.2 + i * 0.1

            tk.Label(self.set_frame, text = "set_id").place(relx = 0.05, rely = y)
            tk.Label(self.set_frame, text = set_id).place(relx = 0.1, rely = y)
            tk.Label(self.set_frame, text = "ce").place(relx = 0.5, rely =y )
            
            ergebnis = "Es konnten keine Inventarinformationen zu diesem Set gefunden werden"
            if(ce != None):
                ergebnis = ce

            tk.Label(self.set_frame, text = ergebnis).place(relx = 0.55, rely = y)

    def return_to_homescreen(self):
        #GUI zurücksetzen 
        self.part_frame.forget()
        self.return_button.forget()
            ##Falls nötig: self.set_frame.place()
        self.display_selected_sets()
        self.set_entry.place(relx=0.05, rely=0.9, anchor='sw')
        self.start_button.place(relx = 0.9, rely = 0.9, anchor = 'sw')

        #Kamera weiterlaufen lassen
        self.capture.start_camera()

    

if __name__ == "__main__":
    tae.start()  
    app = Application()
    app.root.mainloop()
    if app.capture != None:
        app.capture.close_camera()
    tae.stop()