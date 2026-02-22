import cv2 as cv
import customtkinter as ctk
from PIL import Image
from ultralytics import YOLO
import json
import asyncio
import configparser


class Capture:
    def __init__(self, root, camera_label):
        print("Initializing camera...")
        print("Loading model...")
        self.load_config()

        self.model = YOLO(self.model_path)
        self.root = root
        self.label = camera_label
        self.stopping_condition = False
        
        print("Starting VideoCapture...")
        self.cap = cv.VideoCapture(int(self.camera_index), cv.CAP_DSHOW)

        self.results = None
        self.result_frame = None

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.camera_index = config.get('Camera', 'camera_index')
        self.model_path = config.get('Model', 'model_path')

    def pause_camera(self):
        self.stopping_condition = True
                   
    def start_camera(self):
        self.results = None
        self.result_frame = None
        self.stopping_condition = False
        self.update_frame()

    #Zeichnet die erkannten BBoxen, den Klassennamen und die Confidence auf dem aktuellen Frame um die Prädiktion darzustellen
    def draw_boxes(self, frame, results):
        json_format_data = results[0].to_json()
        data = json.loads(json_format_data)
        for object in data:
            box = object["box"]
            name = object["name"]
            confidence = object["confidence"]
            x_start = int(box['x1'])
            y_start = int(box['y1'])
            x_end = int(box['x2'])
            y_end = int(box['y2'])
            cv.rectangle(frame, (x_start, y_start), (x_end, y_end), (226, 169, 241), 2)
            cv.putText(frame, f"{name}: {confidence:.2f}", (x_start, y_start - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (226, 169, 241), 2)
        return frame

    #Aktualisiert die Frames der Kamera und führt die Objekterkennung durch, bis die Stopping Condition erfüllt ist -> Algorithmus wird gestartet
    def update_frame(self):
        try:
            if not self.cap.isOpened():
                print("Cannot open camera")
                return 

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
            prediction_frame = self.draw_boxes(frame, results)
            
            prediction_frame = cv.cvtColor(prediction_frame, cv.COLOR_BGR2RGB)
            img = Image.fromarray(prediction_frame)
            frame_img = ctk.CTkImage(img, size=(640,640))
            self.label.configure(image = frame_img)
            self.label.image = frame_img


            if not self.stopping_condition == True:
                self.root.after(30, self.update_frame)
                
            else:
                self.results = results
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                self.result_frame = frame

        except Exception as e:
            print(e)

    #Liefert die Daten im json-Format zurück, sobald sie geladen sind        
    async def get_results(self):
        if(self.results is None):
            print("No results available yet... Waiting...")
            for i in range(3):#Das Result wird erst im letzten Durchlauf nach pausierung gespeichert
                await asyncio.sleep(0.1)  #-Hier warte ich insgesamt 40ms um sicherzustellen, dass die results da sind
                if(self.results is not None):
                    break
            if(self.results is None):#Ist nach dem warten immernoch kein Ergebnis vorhanden liegt ein Fehler vor
                print("Problem accured: Still no results available...")
                return self.results
        json_format_data = self.results[0].to_json()
        data = json.loads(json_format_data)
        print("Data:",data)
        return data

    #Liefert den angezeigten Frame zurück
    def get_result_frame(self):
        return self.result_frame

    def close_camera(self):
        print("Releasing camera...")
        self.cap.release()
        cv.destroyAllWindows()
        self.stopping_condition = True
