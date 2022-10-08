# Yoga Coach web

A computer vision based yoga coach web app

![logo](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/img/logo.svg)

## About

*Yoga Coach web* is a web app that allows you to record your body pose with your webcam and will give you real-time feedback how good your doing on a certain exercise based on coputer vision analysis. This app was developed as my final project during the data science bootcamp at [Spiced Academy](https://www.spiced-academy.com/de/program/data-science) in Berlin. If you don't want to setup by yourself, you can have a look at the [screenshots](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/screenshots/) or the [presentation](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/docs/presentation.pdf).

![userinterface](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/screenshots/userinterface.png)

The picture in this screenshot was taken from [commons.wikimedia.org](https://upload.wikimedia.org/wikipedia/commons/8/8c/Mr-yoga-boat-pose2.jpg) on 03/10/2022.

## Credits

I thank all people from [Spiced Academy](https://www.spiced-academy.com/de/about) and [Bundesagentur f&uuml;r Arbeit](https://www.arbeitsagentur.de/) that supported me. Images for exercises were taken from [commons.wikimedia.org](https://commons.wikimedia.org/). The respective URL and date of access are shown in the app. Descriptions of exercises are taken from the [en.wikipedia.org](https://en.wikipedia.org/wiki/) JSON API and a respective link given to further read the article. The image or video stream processing was followed from the [MediaPipe Pose python API](https://google.github.io/mediapipe/solutions/pose.html) and [this pyshine tutorial](https://pyshine.com/Online-Video-Processing-From-Client-Camera/). The script for plotting of body pose landmarks is based on these two threads [1](https://stackoverflow.com/questions/69265059/is-it-possible-to-create-a-plotly-animated-3d-scatter-plot-of-mediapipes-body-p), [2](https://community.plotly.com/t/3d-scatter-animation/46368). The angles were calculated following [this thread](https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python).

## How to setup (Linux)

1) Go to folder you want to have it, e.g. home with: `cd ~/`
2) Clone the repository: `git clone https://github.com/klmhsb42/yoga_coach_web.git`
3) Go inside the repository folder: `cd yoga_coach_web`
4) Create a virtual envrionment e.g. with [Anaconda](https://www.anaconda.com/): `conda create --name yogacoach`
5) Activate the virtual envrionment: `conda activate yogacoach`
6) Update pip in the virtual envrionment: `python -m pip install -U pip`
7) Install required python packages inside the virtual envrionment: `pip install -r requirements.txt`
8) Run the app: `python app.py`
9) Close the app: `Ctrl + C`
10) To re-run go to 8), you might have to activate the virtual envrionment again if you are in a new terminal.

## How to use

To use *Yoga Coach web* is intuitive. To start, just select the exercise you want to start with using the *Prev*/*Next* buttons and press the *Start* button. Place your computer so that your full body is visible in the webcam. Then, try to perform the exercise and listen to the feedback.

## Technical background

### Workflow

*Yoga Coach web* is based on the webframework [Flask](https://palletsprojects.com/p/flask/) and [Jinja](https://palletsprojects.com/p/jinja/). Most data is send through a websocket using [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/). The body pose detection is performed by [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html) live in the backend using python. The [pose landmarks](https://google.github.io/mediapipe/solutions/pose.html#pose_landmarks) from MediaPipe Pose are used to calculate their angles. For this project, 16 angles were considered to be relevant and defined in [this .csv file](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/angles.csv). These angles were calculated for each exercise with a python script. The difference between of the correct angles and the current angles is caluclated. Then, a feedback text is created based on these differences. The text-to-speech (TTS) for feedback is performed by [gTTS](https://github.com/pndurette/gTTS).

### Scientific reading

The workflow was inspired by [Muley et. al 2020](https://www.irjmets.com/uploadedfiles/paper/volume2/issue_9_september_2020/4037/1628083159.pdf) and [Thoutam et. al 2022](https://doi.org/10.1155/2022/4311350).

### Prediction of landmarks

About *MediaPipe Pose*:
* [Models](https://google.github.io/mediapipe/solutions/pose.html#models) are based on:
    * BlazePose Detector to detect the person/pose in general (using two extra virtual keypoints), see also [BlazeFace model](https://arxiv.org/abs/1907.05047)
    * [BlazePose GHUM 3D](https://github.com/google-research/google-research/tree/master/ghum) to predict the landmarks, based on Deep Learning using 3D scans (question which version is used, heavy, full, or lite)
* [View source code](https://github.com/google/mediapipe)
* [View performance](https://google.github.io/mediapipe/solutions/pose.html#pose-estimation-quality)

Relevant properties:
* 2D images are sufficient
* Returns the ID and 3D coordinates of 33 landmarks including their level of visibility
* Distinguishes between left and right
* Relations between key landmarks and joints are known
* Prediction in real-time

Interesting but not relevant for this project (yet):
* Scales the coordinates regarding the size of a person and distance to the camera (not relevant for calculation of angles)
* Forcasts landmarks of unvisible body parts

### EDA of landmarks and calculation of angles

The EDA of the returned pose landmarks is documented in [this Jupyter Notebook](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/analysis.ipynb). Furthermore, how the angles were calculated and compared between correct and wrong pose by one example exercise. 

* First, the connecting vectors for both key landmarks with their joint are calculated by subtraction: (key vector) - (joint vector)
* Next, the [unit vectors](https://en.wikipedia.org/wiki/Unit_vector) are calculated for both resulting vectors with: (vector) / ([np.linalg.norm](https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html)(vector))
* The [dot product](https://en.wikipedia.org/wiki/Dot_product) of both vectors is the calculated
* The [arccosine](https://en.wikipedia.org/wiki/Inverse_trigonometric_functions) of the result is calculated to get the angle as radian
* The [radian](https://en.wikipedia.org/wiki/Radian) is calculated in degree with: (value) * (180/np.pi)
* The correctness of the current angle and the default angle was calculated by substraction: (default angle) - (current angle)
* Positive or negative sign of angle differences tell if clockwise or anticlockwise. 

### Feedback generation

* For now, there are just simple sentences which will be made more complex in future [#13](https://github.com/klmhsb42/yoga_coach_web/issues/13)
* *gTTS* uses the Google Translate's text-to-speech API with no further documentation, see [here](https://github.com/pndurette/gTTS#disclaimer)

## How to add new exercises

### Edit dictionary of exercises

To add new exercises you have to modify [exercises.json](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/exercises.json). You can either create a new category and add the new exercise there or you can add it dirrectly to an exsisting category. You can also add an image of the exercise into the [static/exercises](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/exercises/) folder respectively to the system in the JSON file. Please, insert it's origin and respect copyrights.

### Collect data

First, you need gather landmarks as JSON file of the new excercise. Yo can do so by either:

1) Use the image which you have added in the previous step.
2) Or record yourself with your webcam and perform the exercise correctly.

For 1):

Use [gather_from_image.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/gather_from_image.py) by running `python gather_from_image.py` inside the `artifacts/` folder. Before running, setup the path to the image you want to use. The script will calculate body pose landmarks and save them as JSON file under `artifacts/collect/` folder as well as a new image file with the landmarks printed in the same directory as your input image. 

For 2):

Use [gather_from_webcam.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/gather_from_webcam.py) by running `python gather_from_webcam.py` inside the `artifacts/` folder. Your webcam will open and start capturing your body pose landmarks per frame and save them as JSON files under `artifacts/collect/` folder. To gather correct landmarks, place your computer so that your full body is visible in the webcam and then, perform the excersice correctly. You can stop the script by pressing `Ctrl + C`. Remove files from `artifacts/collect/` folder if you re-run the script.

### Select correct data

Next, if you have used your webcam, you need to select one body pose with the landmarks represting this excersice best. To select the right one, you can plot the landmarks using [plot.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/plot.py). For that, run `python plot.py` inside the `artifacts/` folder.

### Calculate angles

To calculate the angles of these correct pose landmarks you can use [angles.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/angles.py) by running `python angles.py` inside the `artifacts/` folder. This will print an array of angle values inside the terminal. Copy this array and insert it in the following step.

### Add new exercises and insert data

The copied angles from the previous step must then be inserted into `"angles": []` for this new exercise in the [exercises.json](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/exercises.json) file. Now you are ready to re-run the server (see How to setup) and test your new created exercise.

