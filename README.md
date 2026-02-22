# LEGO Setdetection
The _LegoSetDetection_ application provides an algorithm to determine the most likely playset for a given collection of LEGO Bricks.
By using the Yolov8 object detection model developed by Ultralytics, the application is able to detect LEGO parts in realtime from a camera feed.
The Yolov8 model is trained on the **b200-lego-detection-dataset** by Korra P., which contains annotations for the 200 most common LEGO Parts.

Within the Application, users can select mutliple LEGO Sets available on **Rebrickable.com** and position the LEGO pieces in front of a camera. Running the algorithm then compares the detected parts with the inventories of the selected sets. In addition to direct element matches, the algorithm includes indirect similarities such as shared part types or colors to improve rubustness. The user is then presented with the detected LEGO parts, a similarity score for each selected set and the most probable set based on the detected components.

When working with modular construction system such as LEGO, individual parts are often stored together in a single container to save space. As a result, assigning each piece back to its original set becomes a tedious and time-consuming task. This application is designed to simplify this sorting progress.

#Demo
![Projektdemo](https://github.com/user-attachments/assets/e2418178-c5fb-41fe-ad67-103b9b9df3ef)

# Try out the Application:
1. Install the dependencies by running 'pip install -r requirements.txt' in a venv or conda environment
2. Create an Rebrickable Account and generate an API Key: https://rebrickable.com/register/
3. Insert your API Key and account information into the 'config.ini'-File
4. Run 'application.py' to start the application

# How to replicate training with the b200 Dataset:
1. After cloning this repository create a 'data' directory
2. Download the current dataset here: https://www.kaggle.com/datasets/ronanpickell/b100-lego-detection-dataset
3. Unzip the data into the data-directory
4. Run 'data_loading.py' - This will format the dataset according to the yolov8 format
5. Run 'training_w_yolo_model.py' - This will start a basic training with the dataset using the pretrained model by ultralytics

# Resources
Yolov8 by Ultralytics: https://docs.ultralytics.com/models/yolov8/
Rebrickable Database: https://rebrickable.com/home/
Rebrick Library: https://github.com/xxao/rebrick
B200-lego-detection-dataset: https://www.kaggle.com/datasets/ronanpickell/b100-lego-detection-dataset
CustomTkinter: https://customtkinter.tomschimansky.com
