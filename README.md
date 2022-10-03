# Yoga Coach web

A coputer vision based yoga coach web app

![logo](https://github.com/klmhsb42/yoga_coach_web/blob/main/static/img/logo.svg)

## Abstract

*Yoga Coach web* is a web app that allows you to record your body pose with your webcam and will give you feedback how good your doing on a certain exercise based on coputer vision analysis. This app was developed as my final project during the data science bootcamp at [Spiced Academy](https://www.spiced-academy.com/de/program/data-science) in Berlin. If you dont' want to setup by yourself, you can have a look at the screenshots.

## Credits

I thank all [people from Spiced Academy](https://www.spiced-academy.com/de/about) that supported me.

## How to setup

1) Create a virtual envrionment e.g. with [Anaconda](https://www.anaconda.com/): `conda create --name yogacoach`
2) Update pip in the virtual envrionment: `python -m pip install -U pip`
3) Install required python packages inside the virtual envrionment: `pip install`
4) Clone the repository: `git clone https://github.com/klmhsb42/yoga_coach_web.git`
5) Go inside the repository folder: `cd yoga_coach_web`
6) Run the app: `python app.py`

## How to use

To use *Yoga Coach web* is intuitive. To start, just select the exercise you want to start with using the "Prev"/"Next" buttons and press the "Start" button. Place your computer so that your full body is visible in the webcam. Then, try to perform the exercise and listen to the feedback.

## Technical background

*Yoga Coach web* is based on the webframework [Flask](https://palletsprojects.com/p/flask/) and [Jinja](https://palletsprojects.com/p/jinja/). Most data is send through a websocket using [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/). The body pose detection is performed by [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html). The text-to-speech (TTS) is performed by [gTTS](https://github.com/pndurette/gTTS).

## How to add new exercises

