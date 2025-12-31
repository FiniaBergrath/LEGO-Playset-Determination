import numpy as np
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
from ultralytics import YOLO
import json
import tk_async_execute as tae 
import asyncio


class Capture:
    def __init__(self, root):
        print("Initializing camera...")
        print("Loading model...")
        self.model = YOLO("yolov8n.pt")
        self.root = root
        self.label = tk.Label(root)
        self.stopping_condition = False
        print("Starting VideoCapture...")
        self.cap = cv.VideoCapture(0, cv.CAP_DSHOW)
        root.after(0, self.label.place(relx=0.05, rely=0.03))
        self.results = None

    def pause_camera(self):
        self.stopping_condition = True
        self.label.config(text="Kamera pausiert")
                   
    def start_camera(self):
        self.results = None
        self.stopping_condition = False
        self.update_frame()

    def draw_boxes(self, frame, results):
        json_format_data = results[0].to_json()
        data = json.loads(json_format_data)
        for object in data:
            box = object["box"]
            x_start = int(box['x1'])
            y_start = int(box['y1'])
            x_end = int(box['x2'])
            y_end = int(box['y2'])
            cv.rectangle(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
        return frame

    def update_frame(self):
        if not self.cap.isOpened():
            print("Cannot open camera")
            return # Hier Exception werfen oder ähnliches

        # Capture frame-by-frame
        ret, frame = self.cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            return
        
        if cv.waitKey(1) == ord('q'):
            print("waiting for 'q' key press to exit")
            return

        results = self.model.predict(frame, verbose=False)
        frame = self.draw_boxes(frame, results)
        
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.config(image=imgtk)
        self.label.image = imgtk

        if not self.stopping_condition == True:
            self.root.after(30, self.update_frame)
            
        else:
            self.results = results
            

            
    async def get_results(self):
        if(self.results is None):
            print("No results available yet... Waiting...")
            for i in range(2):#Das Result wird erst im letzten Durchlauf nach pausierung gespeichert
                await asyncio.sleep(0.1)  #-Hier warte ich insgesamt 30ms um sicherzustellen, dass die results da sind
                if(self.results is not None):
                    return self.results
        print("Problem accured: Still no results available...")
        return self.results

    def close_camera(self):
        print("Releasing camera...")
        self.cap.release()
        cv.destroyAllWindows()
        self.stopping_condition = True
