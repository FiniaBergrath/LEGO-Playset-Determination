# LEGO-ObjectDetection

In this Project I am trying to train a object-detection-model to detect a selection of common Lego bricks in order to assign multiple Bricks to the most plaussible Legoset.

Images and Annotations for the training are currently from the b100-lego-detection-dataset by Korra P. and I am using the yolov8 pre trained model by ultralytics. 

How to test my current state of progress:
    1. After cloning this repository create a 'data' directory
    2. Download the current dataset here:
    3. Unzip the data into the data-directory
    4. Run 'data_loading.py' - This will format the dataset according to the yolov8 format
    5. Run 'training_w_yolo_model.py' - For now this will just start a basic training with the dataset