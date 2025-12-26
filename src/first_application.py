import tkinter as tk
from tkinter import ttk
import database_connection_playground as db
#import brick_and_color_detection as detector
import asyncio
import tk_async_execute as tae 
from working_and_displaying_camera_input import Capture

db.connect_to_rebrick()

color_theme = {
    "white" : "#ffffff",
    "yellow": "#f3cc6f",
    "orange": "#1234",
    "grey"  : "#f0eae0"
}

#Definiton des Root Verzeichnisses
root = tk.Tk()
root.title("Lego-Object-Detection")
root.geometry("1800x1200")
root.configure(bg=color_theme["yellow"])

screens = {}

#Definiton des Hauptscreens
frame = tk.Frame(root, width=200, height=200, bg=color_theme["white"])
screens["home"]=frame

frame2 = tk.Frame(frame, width=200, height=200, bg=color_theme["grey"])
frame2.place(relx=0.05, rely=0.6, relwidth=0.5, relheight=0.4, anchor = 'w')

tk.Label(frame2, text = "Choose your Legosets").place(relx=0.05, rely=0.6, anchor='nw')

label = tk.Label(frame,text="Bestimme das Legoset")
label.place(relx = 0.05, rely = 0.05, anchor = 'nw')

#Wird aus der Listbox aufgerufen, wenn ein Set ausgewählt wird und fügt es zur Liste der ausgewählten Sets hinzu
def on_select(item_idx):
    name = listbox.get(item_idx)
    listbox.delete(item_idx)
    i = len(setlist)
    tk.Label(frame2, text = name).place(relx = 0.05, rely = 0.2 + i * 0.1)
    tk.Button(frame2, image = image, command = lambda: remove_set(name)).place(relx = 0.6, rely = 0.2 + i * 0.1)
    setlist.append(name)

#TODO
def remove_set(name):
    setlist.remove(name)
    # Update the display
    for widget in frame2.winfo_children():
        if isinstance(widget, tk.Label) and widget.cget("text") == name:
            widget.destroy()
            break

listbox = tk.Listbox(frame)

#Wird aufgerufen, wenn im Entry ein Key gedrückt wird und sucht nach passenden Sets zur Eingabe 
# 
# Löschen der Listbox Elemente hinzufügen!!!

async def search(name):
    sets = db.search_sets(name)
    root.after(0, lambda: on_sets_loaded(sets))

def on_input(event):
    search_name = set_entry.get()
    tae.async_execute(search(search_name))

def on_sets_loaded(sets = None):
    print("Sets loaded:", sets)
    listbox.delete(0, tk.END)
    if not sets:
        return

    listbox.place(relx=0.05, rely=0.9,relwidth=0.3, anchor='nw')
    
    for name,_ in sets:
        listbox.insert(tk.END, name)

    listbox.bind("<<ListboxSelect>>", lambda event: on_select(listbox.curselection()))


set_entry = tk.Entry(frame, bg = color_theme["grey"], fg = "black", width = 30)
set_entry.insert(0,"Set hinzufügen...")
set_entry.bind("<FocusIn>", lambda args: set_entry.delete('0', 'end'))
set_entry.bind("<KeyRelease>", func = on_input)
set_entry.place(relx=0.05, rely=0.9, anchor='sw')


image = tk.PhotoImage(file="LEgo-object-detection.png").subsample(5,5)
setlist = ["Legoset1", "Legoset2", "Legoset3", "Legoset4", "Legoset5"]
for i in range(0,len(setlist)):
    tk.Label(frame2, text = setlist[i]).place(relx = 0.05, rely = 0.2 + i * 0.1)
    tk.Button(frame2, image = image).place(relx = 0.6, rely = 0.2 + i * 0.1)

#Startet die Ausführung des Programms
def on_click():
    label.config(text="Ausführung gestartet!")
    tae.async_execute(display_caputure(), callback=start_camera)

async def display_caputure():
    cap = Capture(root)
    global capture
    capture = cap
    return cap

def start_camera(cap = None):
    if capture is None:
        return
    cap = capture
    cap.start_camera()

def display_bricks(detected_bricks):
    for i in range(0,len(detected_bricks)):
        brick,color,amount = detected_bricks[i]
        tk.Label(detection_frame, text = f"{brick} in {color}: {amount} Stück").place(relx = 0.05, rely = 0.1 + i * 0.1, anchor='nw')
        task = asyncio.create_task(get_brick_image(brick,color,(0.6,0.1 + i * 0.1)))
        task.add_done_callback(visualise_brick_image)

async def get_brick_image(brick,color,position):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, db.get_brick_image, brick, color)
    return(result,position)

def visualise_brick_image(fut):
    result,pos = fut.result()
    root.after(0, lambda: tk.Button(detection_frame, image = result).place(relx = pos[0], rely = pos[1], anchor='nw'))

tk.Button(frame, text="Ausführung starten!", command = on_click).place(relx = 0.9, rely = 0.9, anchor = 'sw')

#Definition des Detection Screens
detection_frame = tk.Frame(root, width=200, height=200, bg=color_theme["white"])
screens["main"] = detection_frame





def show_screen(name):
    frame = screens[name]
    frame.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor="center")

show_screen("home")

tae.start()    
db.connect_to_rebrick()
root.mainloop()
capture.close_camera()
tae.stop()
