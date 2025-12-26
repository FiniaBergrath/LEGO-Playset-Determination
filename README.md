# LEGO-ObjectDetection

In this Project I am training a object-detection-model to detect a selection of common Lego bricks in order to assign multiple Bricks to the most plaussible Legoset.

Images and Annotations for the training are currently from the b100-lego-detection-dataset by Korra P. and I am using the yolov8 pre trained model by ultralytics. 

Try out my current state of progress:
    1. Install the dependencies 
    2. Run 'application.py'
    --> Since I have not uploaded the trained model yet, this will use a pretrainded yolov8 model by ultralytics detecting persons and objects as a bottle etc

How to replicate training with the b100 Dataset:
    1. After cloning this repository create a 'data' directory
    2. Download the current dataset here: https://www.kaggle.com/datasets/ronanpickell/b100-lego-detection-dataset
    3. Unzip the data into the data-directory
    4. Run 'data_loading.py' - This will format the dataset according to the yolov8 format
    5. Run 'training_w_yolo_model.py' - This will start a basic training with the dataset using the pretrained model by ultralytics