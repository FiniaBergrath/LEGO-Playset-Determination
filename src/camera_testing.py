import cv2
import tkinter as tk
from PIL import Image, ImageTk
from ultralytics import YOLO
import json

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

root = tk.Tk()
label = tk.Label(root)
label.pack()

def draw_boxes(frame, results):
    json_format_data = results[0].to_json()
    data = json.loads(json_format_data)
    for object in data:
        box = object["box"]
        x_start = int(box['x1'])
        y_start = int(box['y1'])
        x_end = int(box['x2'])
        y_end = int(box['y2'])
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        return frame

def update():
    ret, frame = cap.read()
    if not ret:
        root.after(30, update)
        return

    results = model.predict(frame, verbose=False)
    frame = draw_boxes(frame, results)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(frame))
    label.config(image=img)
    label.image = img

    root.after(30, update)

update()
root.mainloop()
cap.release()
