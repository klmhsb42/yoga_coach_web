# Yoga Coach web

A computer vision based yoga coach web app

![logo](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/img/logo.svg)

## About

*Yoga Coach web* is a web app that allows you to record your body pose with your webcam and will give you feedback how good your doing on a certain exercise based on coputer vision analysis. This app was developed as my final project during the data science bootcamp at [Spiced Academy](https://www.spiced-academy.com/de/program/data-science) in Berlin. If you don't want to setup by yourself, you can have a look at the [screenshots](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/screenshots/) or the [presentation](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/docs/presentation.pdf).

![userinterface](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/screenshots/userinterface.png)

## Credits

I thank all people from [Spiced Academy](https://www.spiced-academy.com/de/about) and [Bundesagentur f&uuml;r Arbeit](https://www.arbeitsagentur.de/) that supported me. Images for exercises were taken from [commons.wikimedia.org](https://commons.wikimedia.org/). The respective URL and date of access are shown in the app. Descriptions of exercises are taken from the [en.wikipedia.org](https://en.wikipedia.org/wiki/) JSON API and a respective link given to further read the article. The video stream processing was followed from the MediaPipe Pose [python API](https://google.github.io/mediapipe/solutions/pose.html) and [this](https://pyshine.com/Online-Video-Processing-From-Client-Camera/) pyshine tutorial.

## How to setup

1) Create a virtual envrionment e.g. with [Anaconda](https://www.anaconda.com/): `conda create --name yogacoach`
2) Update pip in the virtual envrionment: `python -m pip install -U pip`
3) Install required python packages inside the virtual envrionment: `pip install`
4) Clone the repository: `git clone https://github.com/klmhsb42/yoga_coach_web.git`
5) Go inside the repository folder: `cd yoga_coach_web`
6) Run the app: `python app.py`
7) Close the app: `Ctrl + C`

## How to use

To use *Yoga Coach web* is intuitive. To start, just select the exercise you want to start with using the "Prev"/"Next" buttons and press the "Start" button. Place your computer so that your full body is visible in the webcam. Then, try to perform the exercise and listen to the feedback.

## Technical background

### Workflow

*Yoga Coach web* is based on the webframework [Flask](https://palletsprojects.com/p/flask/) and [Jinja](https://palletsprojects.com/p/jinja/). Most data is send through a websocket using [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/). The body pose detection is performed by [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html) live in the backend using python. The [pose landmarks](https://google.github.io/mediapipe/solutions/pose.html#pose_landmarks) from MediaPipe Pose are used to calculate their angles. These angles were calculated for each exercise with a python script. The difference between of the correct angles and the current angles is caluclated. Then, a feedback text is created based on these differences. The text-to-speech (TTS) for feedback is performed by [gTTS](https://github.com/pndurette/gTTS).

### Scientific reading

The workflow was inspired by [Muley et. al 2020](https://www.irjmets.com/uploadedfiles/paper/volume2/issue_9_september_2020/4037/1628083159.pdf) and [Thoutam et. al 2022](https://doi.org/10.1155/2022/4311350).

MediaPipe Pose is based on ... and has advantages ...

gTTS is based on ...

### EDA and calculation of angles

The EDA of the returned pose landmarks is documented in [this](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/analysis.ipynb) Jupyter Notebook. Furthermore, how the angles were calculated and compared between correct and wrong pose by one example exercise. The angles were calculated following this thread [here](https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python).

## How to add new exercises

### Collect data

First, you need to collect data of your body pose. For that, you can use [gather.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/gather.py) by running `python gather.py` inside the `yoga_coach_web/artifacts/` folder. Your webcam will open and start capturing your body pose landmarks per frame and save them as JSON file under `yoga_coach_web/artifacts/collect/` folder. To gather correct landmarks, place your computer so that your full body is visible in the webcam and then, perform the excersice correctly. You can stop the script by pressing `Ctrl + C`.

### Select correct data

Next, you need to select one body pose with the landmarks represting this excersice best. To select the right one, you can plot the landmarks using [plot.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/plot.py). For that, run `python plot.py` inside the `yoga_coach_web/artifacts/` folder.

### Calculate angles

To calculate the angles of these correct pose landmarks you can use [angles.py](https://github.com/klmhsb42/yoga_coach_web/blob/main/artifacts/angles.py) by running `python angles.py` inside the `yoga_coach_web/artifacts/` folder. This will print an array of angle values inside the terminal. Copy this array and insert it in the following step.

### Add new exercises and insert data

To add new exercises you have to modify [exercises.json](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/exercises.json). You can either create a new category and add the new exercise there or you can add it dirrectly to an exsisting category. The copied angles from the previous step must then be inserted into `"angles": []` for this new exercise. Now you are ready to re-run the server (see How to setup) and test your new created exercise.

