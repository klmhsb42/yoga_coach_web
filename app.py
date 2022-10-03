
##### IMPORTS #####

from distutils.log import debug
from flask import Flask, Response, jsonify, render_template, request, send_file, url_for
from flask_socketio import SocketIO, emit
from urllib.request import urlopen
import urllib.request#, json
#from time import sleep
import time
from datetime import datetime, timedelta
from gtts import gTTS
#import playsound
import os
import json
import cv2
import mediapipe as mp
import numpy as np
import base64
import imutils
import io
from io import StringIO
from PIL import Image
from engineio.payload import Payload
import re
import matplotlib.pyplot as plt
import pandas as pd


Payload.max_decode_packets = 2048

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

#from timer_func import timer_start, timer_stop







##### INIT AND GLOBALS #####

# ***APP***

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'                                            
socketio = SocketIO(app)



# ***VIDEO***

#video = cv2.VideoCapture(0)

global fps,prev_recv_time,cnt,fps_array
fps=30
prev_recv_time = 0
cnt=0
fps_array=[0]

# ***TIMER***

#current_time = 300
#runthetimer = True
#timer_loop = True

#timer_bridge_now = datetime.now()
#timer_bridge_time = timer_bridge_now.time()

time_timer_started = datetime(1, 1, 1, 0, 0, 0) #timer_bridge_time #datetime.time(0, 0, 0, 0)
#timer_diff = #timer_bridge_time #datetime.time(0, 3, 0, 0)
timer_diff = timedelta(minutes=3) #300 #datetime(1, 1, 1, 0, 3, 0) #(0, 3, 0, 0)
time_timer_ended = datetime(1, 1, 1, 0, 0, 0) #timer_bridge_time #datetime.time(0, 0, 0, 0)


# ***EXERCISES***

exercise_id = 0
category_id = 0

scoremax = 0

framecount = 0

df_angle_matrix_global = pd.DataFrame()


##### TEST SOCKET #####

@socketio.on('connect')                                                         
def connect():                                                                  
    emit('message', {'text': "True"})   


##### INITIALIZE INDEX PAGE #####

@app.route('/', methods=["GET"])
def index():
    exercises_file = open('static/exercises.json',)
    exercises_data = json.load(exercises_file)

    wikipedia_data = exercises_data

    for cat_idx, any_category in enumerate(exercises_data['category']):
        for exec_idx, any_exercises in enumerate(any_category['exercise']):
            wiki_api_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles="+any_exercises["description-api"]
            with urllib.request.urlopen(wiki_api_url) as wiki_url:
                wiki_data = json.load(wiki_url)
                wikipedia_data['category'][cat_idx]['exercise'][exec_idx]['description'] = list(wiki_data['query']['pages'].values())[0]['extract']

    return render_template('index.html', exercises_data=wikipedia_data)


##### START / STOP EXERCISE #####

#@app.route('/run', methods=["GET"])
@socketio.on('run')  
def run(startdata):
    global current_time, runthetimer, timer_loop, current_time, exercise_id, category_id, df_angle_matrix_global

    exercise_id = startdata[0] #request.args.get("exc")
    category_id = startdata[1] #request.args.get("cat")
    runthecode = startdata[2]
    getrunthetimer = startdata[3]

    # if start button was pressed
    if getrunthetimer == 1:



        #import of exercises.json also done in index, use global!

        exercises_file = open('static/exercises.json',)
        exercises_data = json.load(exercises_file)

        # initializes exercise

        exercise_id_low = exercise_id - 1

        get_the_current_angle = exercises_data["category"][category_id]["exercise"][exercise_id_low]["angles"]

        df_angle_matrix = pd.read_csv('static/angles.csv', sep=',')
        df_angle_matrix['angle_correct'] = get_the_current_angle

        df_angle_matrix_global = df_angle_matrix.copy(deep=True)




        
        #give start feedback
        #...

        #start the video stream
        #video_feed()

        #pre-analysis of feedback, if ready to start
        #...

        # if the timer should be started (because of video results)
        # if runthecode == 1:
        #     runthetimer = True
        #     timer_loop = True
        timer_start()

        # if the timer should be stopped
        # elif runthecode == 0:
        #     runthetimer = False
        #     timer_loop = False
        #     timer_stop()

        #start the timer
        
        #timer_loop = True
        #timer_result = timer_start()
        
        
        

    # if the stop button was pressed
    elif getrunthetimer == 0:
        #print('stop')
        
        timer_stop()

        #stop the video stream
        #...

        #give final feedback
        #...


# @app.route('/stop')
# def stop_exercise():
#     global runthetimer
#     runthetimer = False
#     timer_stop()
    
#     print('stop')
#     return 'Process stopped'


##### ANALYZE POSITION #####

# https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def analyze(gettheposelandmarks, gettheposeworldlandmarks, gettheposeconnections):
    global exercise_id, category_id, scoremax, df_angle_matrix_global

    
    if hasattr(gettheposelandmarks, 'landmark'):
        


        keypoints = []
        for data_point in gettheposelandmarks.landmark:
            keypoints.append({
                                'x': data_point.x,
                                'y': data_point.y,
                                'z': data_point.z,
                                'visibility': data_point.visibility,
                                })

        df_keypoints = pd.DataFrame(keypoints)

        # exercises_file = open('static/exercises.json',)
        # exercises_data = json.load(exercises_file)

        # exercise_id_low = exercise_id - 1

        # get_the_current_angle = exercises_data["category"][category_id]["exercise"][exercise_id_low]["angles"]

        # df_angle_matrix = pd.read_csv('static/angles.csv', sep=',')
        # df_angle_matrix['angle_correct'] = get_the_current_angle

        # df_angle_global = df_angle_matrix.copy(deep=True)

        df_angle_global = df_angle_matrix_global.copy(deep=True)

        # if df_angle_global.shape[1] > 8:
        #     print(df_angle_global.shape[1])
        #     df_angle_global.drop(df_angle_global.columns[len(df_angle_global.columns)-12], axis=1, inplace=True)
        #     print('remove')
        #     df_angle_global.shape[1]


        df_angle_global = df_angle_global.merge(df_keypoints, how="left", left_on='vector_1_idx', right_on=df_keypoints.index)
        df_angle_global.rename(columns={'z':'vector_1_z','x':'vector_1_x','y':'vector_1_y'}, inplace=True)

        df_angle_global = df_angle_global.merge(df_keypoints, how="left", left_on='vector_2_idx', right_on=df_keypoints.index)
        df_angle_global.rename(columns={'z':'vector_2_z','x':'vector_2_x','y':'vector_2_y'}, inplace=True)

        df_angle_global = df_angle_global.merge(df_keypoints, how="left", left_on='join_idx', right_on=df_keypoints.index)
        df_angle_global.rename(columns={'z':'join_z','x':'join_x','y':'join_y'}, inplace=True)

        df_angle_global['connector_1_x'] = df_angle_global['vector_1_x'] - df_angle_global['join_x']
        df_angle_global['connector_1_y'] = df_angle_global['vector_1_y'] - df_angle_global['join_y']
        df_angle_global['connector_1_z'] = df_angle_global['vector_1_z'] - df_angle_global['join_z']

        df_angle_global['connector_2_x'] = df_angle_global['vector_2_x'] - df_angle_global['join_x']
        df_angle_global['connector_2_y'] = df_angle_global['vector_2_y'] - df_angle_global['join_y']
        df_angle_global['connector_2_z'] = df_angle_global['vector_2_z'] - df_angle_global['join_z']

        df_angle_global_array = df_angle_global[['connector_1_z','connector_1_x','connector_1_y','connector_2_z','connector_2_x','connector_2_y']].to_numpy()

        angle_list_current = []

        for angle_cal in df_angle_global_array:
            getangle = angle_between((angle_cal[0],angle_cal[1],angle_cal[2]), (angle_cal[3],angle_cal[4],angle_cal[5]))
            getangle = getangle * (180/np.pi)
            angle_list_current.append(getangle)

        df_angle_global['angle_current'] = angle_list_current

        df_angle_global['diff'] = df_angle_global['angle_correct'] - df_angle_global['angle_current']

        df_angle_global['diff_per100'] = (df_angle_global['diff'] / 180) * 100

        df_angle_global['diff_per100_abs'] = abs(df_angle_global['diff_per100'])

        list_of_angle_diff_length = len(list(df_angle_global['diff_per100_abs']))

        angle_threshold = 5
        list_of_angle_diff_threshold = sum(i < angle_threshold for i in list(df_angle_global['diff_per100_abs']))

        correctness = list_of_angle_diff_threshold / list_of_angle_diff_length * 100

        feedback(correctness)


##### FEEDBACK #####

def feedback(correctness):
    global score, scoremax

    score = 10 - (correctness/10)

    if score >= 8:
        score_message = 'correct'
        score_color = 'green'
        score_max_message = 'correct'
        score_max_color = 'green'
    else:
        score_message = 'wrong'
        score_color = 'red'
        score_max_message = 'wrong'
        score_max_color = 'red'

    socketio.emit('score', {'score_val': score, 'score_message': score_message, 'score_color': score_color})

    if score > scoremax:
        scoremax = score
        socketio.emit('score_max', {'score_max': scoremax})
        setaudiotext = 'Good job!'
        socketio.emit('instruction', {'instruction_txt': setaudiotext, 'score_max_message': score_max_message, 'score_max_color': score_max_color})
        audio_func(setaudiotext)

    #give instructions and feedback
    #audio_func(analyze_result[1])
    #socketio.emit('score', {'score_val': analyze_result[0]})
    #socketio.emit('instruction', {'instruction_txt': analyze_result[1]}) 
    #setaudiotext = 'Please, raise your right arm 10% higher.'
    #return [score, scoremax, setaudiotext]
    #socketio.emit('instruction', {'instruction_txt': setaudiotext})


##### TIMER #####

def timer_start():
    global time_timer_started

    time_timer_started = datetime.now()


def timer_print():
    global time_timer_started, timer_diff

    time_difference = datetime.now() - time_timer_started
    #time_difference_seconds = time_difference.seconds
    time_countdown = timer_diff.seconds - time_difference.seconds

    if time_difference <= timer_diff:
        mins, secs = divmod(time_countdown, 60)
        timerstr = '{:02d}:{:02d}'.format(mins, secs)
        socketio.emit('timer_socket', {'time': timerstr})
    else:
        timer_stop()

 
def timer_stop():
    global time_timer_started, time_timer_ended

    time_timer_started = datetime(1, 1, 1, 0, 0, 0)
    time_timer_ended = datetime.now()

    timerstr = '{:02d}:{:02d}'.format(0, 0)
    socketio.emit('timer_socket', {'time': timerstr})


##### AUDIO #####

def audio_func(audiotext):
    tts = gTTS(text=audiotext, lang='en')
    filename = "static/speech.mp3"
    tts.save(filename)
    #with open(filename, "rb") as fwav:
        #audiofile = fwav.read(2048)
        #socketio.emit('audio_socket', {'audiofile': audiofile})
    #audiofile = open(filename,)

    #emit('add-wavefile', url_for('static',filename='_files/' + session['wavename']))
    #session['wavefile'].close()

    #audiofile = urlopen('http://127.0.0.1:5000/'+filename)
    #print('audiogot')
    #decoded_data = audiofile.read()
    urlstr = 'http://127.0.0.1:5000/'+filename
    bloburl = 'http://127.0.0.1:5000/static/'

    socketio.emit('audio_socket', {'audiofile': "speech.mp3", 'audio_url': urlstr, 'bloburl': bloburl})
    #socketio.emit('audio_socket', url_for('static',filename=filename))
    #filename.close()

'''
@app.route('/audio_feed', methods=["POST"])
def audio_feed():
    #text = 'Please, raise your right arm 10% higher.'
    text = request.get_json()
    gettxt = text[0]['settxt']
    #text = request.json
    #print(gettxt)
    
    tts = gTTS(text=gettxt, lang='en')
    filename = "static/speech.mp3"
    tts.save(filename)
    #return 'True'
    #return jsonify({"text": gettxt})
    
    #playsound.playsound(filename)
    
    return send_file(filename, mimetype="audio/mp3", as_attachment=True)
    
     
    
    #os.remove(filename)
    
    
    
    #tts = gTTS(text='', lang='en')
    #tts.save("static/good.mp3")
    #os.system("mpg321 static/good.mp3")
    #return Response("static/good.mp3")
   ''' 

    

##### VIDEO #####

#https://pyshine.com/Online-Video-Processing-From-Client-Camera/

def readb64(base64_string):
    idx = base64_string.find('base64,')
    base64_string  = base64_string[idx+7:]

    sbuf = io.BytesIO()

    sbuf.write(base64.b64decode(base64_string, ' /'))
    pimg = Image.open(sbuf)


    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


def moving_average(x):
    return np.mean(x)


@socketio.on('catch-frame')
def catch_frame(data):

    emit('response_back', data)  


@socketio.on('image')
def image(getdata_image):
    global fps,cnt, prev_recv_time,fps_array,framecount

    data_image = getdata_image[0]
    camera_run = getdata_image[1]

    
    framecount = framecount + 1

    #if camera_run == 1:

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:

        

    # pose = mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)

    # print(type(pose))
    # print(dir(pose))

    #pose.close()

    #test_count = 0

    # while test_count < 10:
    #     test_count += 1

    #with pose1 as pose:

        # if camera_run == 0:
        #     pose.close()
            #pose.close()#self.pose.close()

        
        timer_print()
        

        recv_time = time.time()
        text  =  'FPS: '+str(fps)
        frame = (readb64(data_image))

        results = pose.process(frame)

        # send the output for analysis
        # gettheposelandmarks = results.pose_landmarks
        # gettheposeworldlandmarks = results.pose_world_landmarks
        # gettheposeconnections = mp_pose.POSE_CONNECTIONS
        analyze(results.pose_landmarks, results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)


        

        
        # Draw the pose annotation on the image.
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        

        #frame = changeLipstick(frame,[255,0,0])
        #frame = ps.putBText(frame,text,text_offset_x=20,text_offset_y=30,vspace=20,hspace=10, font_scale=1.0,background_RGB=(10,20,222),text_RGB=(255,255,255))
        imgencode = cv2.imencode('.jpeg', frame,[cv2.IMWRITE_JPEG_QUALITY,40])[1]

        # base64 encode
        stringData = base64.b64encode(imgencode).decode('utf-8')
        b64_src = 'data:image/jpeg;base64,'
        stringData = b64_src + stringData

        # emit the frame back
        emit('response_back', stringData)
        
        fps = 1/(recv_time - prev_recv_time)
        fps_array.append(fps)
        fps = round(moving_average(np.array(fps_array)),1)
        prev_recv_time = recv_time
        #print(fps_array)
        cnt+=1
        if cnt==30:
            fps_array=[fps]
            cnt=0

 
'''
def gen(video):
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        while video.isOpened():
            success, image = video.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            # Draw the pose annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

            ret, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
'''
       

'''
@app.route('/video_feed')
def video_feed():
    global video
    #return Response(gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
    socketio.emit('video_socket', {'videodata': gen(video)})

'''

    

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=2204, threaded=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 
