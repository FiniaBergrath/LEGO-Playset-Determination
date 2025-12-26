import tkinter as tk
from tkinter import ttk
import database_connection_playground as db
#import brick_and_color_detection as detector
import asyncio
import tk_async_execute as tae 
from working_and_displaying_camera_input import Capture
import json

class Application:

    def __init__(self):
        self.color_theme = {
            "white" : "#ffffff",
            "yellow": "#f3cc6f",
            "orange": "#1234",
            "grey"  : "#f0eae0"
        }
        
        self.root = tk.Tk()
        self.root.title("Lego-Object-Detection")
        self.root.geometry("1920x1080")
        self.root.configure(bg=self.color_theme["yellow"])
        self.capture = None

        self.setlist = []
        self.buttons = []

        #Widget Definitionen:

        #Main-Frame
        self.frame = tk.Frame(self.root, width=200, height=200, bg=self.color_theme["white"])
        self.frame.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor="center")
        #Set-Display
        self.set_frame = tk.Frame(self.frame, width=200, height=200, bg=self.color_theme["grey"])
        self.set_frame.place(relx = 0.05, rely=0.75, relwidth=0.5, relheight = 0.35, anchor = 'w')
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
        self.start_button = tk.Button(self.frame, text="Bestimme Set!", command = lambda: tae.async_execute(self.start_set_detection()))
        self.start_button.place(relx = 0.9, rely = 0.9, anchor = 'sw')
        #Assets:
        self.bin_image = tk.PhotoImage(file="./assets/bin.png").subsample(5,5)

        #Kamerastarten:
        self.root.after(150, lambda: tae.async_execute(self.initialize_camera(), callback = self.start_camera))

    

    #Soll die Setliste nicht mehr anzeigen sobald sie über keine Inhalte mehr verfügt:
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
        sets = db.search_sets(search_name)
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
        set_discribtion = self.listbox.get(item_idx)
        split = set_discribtion.rsplit('       ')
        set_name = split[0].lstrip("Name:")
        set_id = split[1].lstrip("SetID:")
        item = (set_name,set_id,set_discribtion)
        self.listbox.delete(item_idx)
        i = len(self.setlist)
        self.setlist.append(item)
        print(self.setlist)
        tk.Label(self.set_frame, text = item[2]).place(relx = 0.05, rely = 0.2 + i * 0.1)
        button = tk.Button(self.set_frame, image = self.bin_image, command = lambda: self.remove_set(button))
        button.place(relx = 0.6, rely = 0.2 + i * 0.1)
        self.buttons.append(button)
        print("Aktuelle Buttonliste:", self.buttons)

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

    #Darstellung bzw. Update der ausgewählten Legosets
    def display_selected_sets(self):
        for widget in self.set_frame.winfo_children():
            widget.destroy()
        print("Alle Inhalte gelöscht, wird neu aufgebaut...")
        for i in range (0,len(self.setlist)):
            tk.Label(self.set_frame, text = self.setlist[i][2]).place(relx = 0.05, rely = 0.2 + i * 0.1)
            button = tk.Button(self.set_frame, image = self.bin_image, command = lambda: self.remove_set(button))
            button.place(relx = 0.6, rely = 0.2 + i * 0.1)
            self.buttons.append(button)
            print(self.buttons)

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
        detections = await self.capture.get_results()
        json_format_data = detections[0].to_json()
        data = json.loads(json_format_data)
        print(data)

        print(detections)
        #Farben bestimmen

        #Sets holen
        #Kreuzentropie bestimmen

        #Screen updaten

        pass
        


if __name__ == "__main__":
    tae.start()    
    db.connect_to_rebrick()
    app = Application()
    app.root.mainloop()
    if app.capture != None:
        app.capture.close_camera()
    tae.stop()