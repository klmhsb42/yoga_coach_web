
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

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


##### INIT AND GLOBALS #####

# ***APP***

Payload.max_decode_packets = 2048
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'                                            
socketio = SocketIO(app)


# ***VIDEO***

global fps,prev_recv_time,cnt,fps_array
fps=30
prev_recv_time = 0
cnt=0
fps_array=[0]
framecount = 0


# ***TIMER***

timer_length = 3 # in minutes
time_timer_started = datetime(1, 1, 1, 0, 0, 0)
timer_diff = timedelta(minutes=timer_length)
time_timer_ended = datetime(1, 1, 1, 0, 0, 0)
time_difference = timedelta(minutes=(timer_length+1))


# ***EXERCISES***

exercise_id = 0
category_id = 0
scoremax = 0
df_angle_matrix_global = pd.DataFrame()
exercises_data = {}
load_angles = pd.DataFrame()

# ***ANALYSIS***

user_in_camera_once = 0
user_not_in_camera = 0


# ***FEEDBACK***

ready_for_next_feedback = True



##### TEST SOCKET #####

@socketio.on('connect')                                                         
def connect():                                                                  
    emit('message', {'text': "True"})   


##### INITIALIZE INDEX PAGE #####

@app.route('/', methods=["GET"])
def index():
    global exercises_data, load_angles

    exercises_file = open('static/exercises.json',)
    exercises_data = json.load(exercises_file)

    load_angles = pd.read_csv('static/angles.csv', sep=',')

    # add wikipedia text for description from the internet
    wikipedia_data = exercises_data

    for cat_idx, any_category in enumerate(exercises_data['category']):
        for exec_idx, any_exercises in enumerate(any_category['exercise']):
            wiki_api_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles="+any_exercises["description-api"]
            with urllib.request.urlopen(wiki_api_url) as wiki_url:
                wiki_data = json.load(wiki_url)
                wikipedia_data['category'][cat_idx]['exercise'][exec_idx]['description'] = list(wiki_data['query']['pages'].values())[0]['extract']

    return render_template('index.html', exercises_data=wikipedia_data)


##### START / STOP EXERCISE #####

@socketio.on('run')  
def run(startdata):
    global exercise_id, category_id, df_angle_matrix_global, exercises_data, load_angles, user_in_camera_once

    exercise_id = startdata[0]
    category_id = startdata[1]
    run_state = startdata[2]

    # if started in frontend
    if run_state == 1:

        # get correct angles of exercise and add to index dataframe

        exercise_id_low = exercise_id - 1

        correct_angles_of_current_exercise = exercises_data["category"][category_id]["exercise"][exercise_id_low]["angles"]

        df_angle_matrix = load_angles.copy(deep=True)
        df_angle_matrix['angle_correct'] = correct_angles_of_current_exercise

        df_angle_matrix_global = df_angle_matrix.copy(deep=True)


        #give start feedback
        set_feedback_text = 'Namasté, happy to see you!'
        feedback_text(set_feedback_text)

        


        #start the analysis (triggered by the video) if start feedback is out (maybe with some sleep or if/else)
        #...

        

        # start timer (should be removed and in the video or analysis function)
        timer_start()




    # if stopped in frontend
    elif run_state == 0:
        
        # stop timer
        timer_stop()

        #give final feedback
        set_feedback_text = "I'm happy that you did it! See you in the next exercise."
        feedback_text(set_feedback_text)

        # set user_in_camera_once
        user_in_camera_once = 0
         


# if stopped in backend, sent to frontend and stop from there
def exercise_stop():
    socketio.emit('exercisestop', {'stopetheexercise': True})



##### ANALYZE POSITION #####

# https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def calculate_angles(df_angle_global_array):
    # Calculate and list angles
    angle_list_current = []

    for angle_cal in df_angle_global_array:
        getangle = angle_between((angle_cal[0],angle_cal[1],angle_cal[2]), (angle_cal[3],angle_cal[4],angle_cal[5]))
        getangle = getangle * (180/np.pi)
        angle_list_current.append(getangle)
    
    return angle_list_current






def analyze(gettheposelandmarks, gettheposeworldlandmarks, gettheposeconnections):

    global user_in_camera_once

    # if the user was at least once completely in the camera, start the timer
    # if user_in_camera_once == 1:
        # timer_start()
        # set_feedback_text = 'Timer started'
        # feedback_text(set_feedback_text)

    # start analysis
    
    df_keypoints = get_landmarks(gettheposelandmarks)

    if isinstance(df_keypoints, pd.DataFrame):

        
        is_user_in_camera(list(df_keypoints['visibility']))

        get_df_angle_global = landmarks_to_angles(df_keypoints)
        get_diff_per100_abs = calculate_angles_difference(get_df_angle_global)

        get_the_instruction = create_instruction(get_diff_per100_abs)

        # send feedback about instruction
        if get_the_instruction != False:
            feedback_text(get_the_instruction)

        get_correctness = calculate_score(get_diff_per100_abs)
        # send feedback about score
        feedback_score(get_correctness)





def get_landmarks(gettheposelandmarks):
    
    # if landmarks are set for current pose
    if hasattr(gettheposelandmarks, 'landmark'):
        
        # get landmarks of current pose
        keypoints = []
        for data_point in gettheposelandmarks.landmark:
            keypoints.append({
                                'x': data_point.x,
                                'y': data_point.y,
                                'z': data_point.z,
                                'visibility': data_point.visibility,
                                })

        # current landmarks to dataframe
        df_keypoints = pd.DataFrame(keypoints)
        return df_keypoints
    else:
        return False





def landmarks_to_angles(df_keypoints):

    # this dataframe matrix contains the correct angles
    df_angle_global = df_angle_matrix_global.copy(deep=True)

    # Merge X,Y,Z to the respective indicies
    df_angle_global = df_angle_global.merge(df_keypoints, how="left", left_on='vector_1_idx', right_on=df_keypoints.index)
    df_angle_global.rename(columns={'z':'vector_1_z','x':'vector_1_x','y':'vector_1_y'}, inplace=True)

    df_angle_global = df_angle_global.merge(df_keypoints, how="left", left_on='vector_2_idx', right_on=df_keypoints.index)
    df_angle_global.rename(columns={'z':'vector_2_z','x':'vector_2_x','y':'vector_2_y'}, inplace=True)

    df_angle_global = df_angle_global.merge(df_keypoints, how="left", left_on='join_idx', right_on=df_keypoints.index)
    df_angle_global.rename(columns={'z':'join_z','x':'join_x','y':'join_y'}, inplace=True)

    # Get X,Y,Z of connectors
    df_angle_global['connector_1_x'] = df_angle_global['vector_1_x'] - df_angle_global['join_x']
    df_angle_global['connector_1_y'] = df_angle_global['vector_1_y'] - df_angle_global['join_y']
    df_angle_global['connector_1_z'] = df_angle_global['vector_1_z'] - df_angle_global['join_z']

    df_angle_global['connector_2_x'] = df_angle_global['vector_2_x'] - df_angle_global['join_x']
    df_angle_global['connector_2_y'] = df_angle_global['vector_2_y'] - df_angle_global['join_y']
    df_angle_global['connector_2_z'] = df_angle_global['vector_2_z'] - df_angle_global['join_z']

    # Make array of connector coordinates
    df_angle_global_array = df_angle_global[['connector_1_z','connector_1_x','connector_1_y','connector_2_z','connector_2_x','connector_2_y']].to_numpy()

    # Calculate and list angles
    angle_list_current = calculate_angles(df_angle_global_array)

    df_angle_global['angle_current'] = angle_list_current

    return df_angle_global
    


def calculate_angles_difference(df_angle_global):
    # Calculate the difference between correct and current angles
    df_angle_global['diff'] = df_angle_global['angle_correct'] - df_angle_global['angle_current']

    df_angle_global['diff_per100'] = (df_angle_global['diff'] / 180) * 100

    df_angle_global['diff_per100_abs'] = abs(df_angle_global['diff_per100'])

    diff_per100_abs = df_angle_global['diff_per100_abs']

    return diff_per100_abs
    



def calculate_score(diff_per100_abs):
    # Calculations imoprtant for score
    list_of_angle_diff_length = len(list(diff_per100_abs))

    # How much difference in % is allowed between correct and current angle
    angle_threshold = 7

    # How many angles are below this threshold
    list_of_angle_diff_threshold = sum(i < angle_threshold for i in list(diff_per100_abs))

    # How much in %
    correctness = list_of_angle_diff_threshold / list_of_angle_diff_length * 100

    return correctness




def is_user_in_camera(visibility_df_series):

    global user_in_camera_once, user_not_in_camera

    #check if the user is in the camera completely (distinguish between this and empty camera = no landmarks; to do)

    
    # group numbers: 0 = head; 1 = left arm; 2 = right arm; 3 = chest; 4 = left leg; 5 = right leg
    # values of groups represent the indices of visibility_df_series (= pose index 0-32)

    # landmark_grps = {
    #     "0": [0,1,2,3,4,5,6,7,8,9,10],
    #     "1": [13,15,17,19,21],
    #     "2": [14,16,18,20,22],
    #     "3": [11,12,23,24],
    #     "4": [25,27,29,31],
    #     "5": [26,28,30,32],
    # }

    # index in template represents index in visibility_df_series
    groupby_index_template = [0,0,0,0,0,0,0,0,0,0,0,3,3,1,2,1,2,1,2,1,2,1,2,3,3,4,5,4,5,4,5,4,5]

    # fill dict with values regarding indices
    groupby_index_dict = {
        "0": [],
        "1": [],
        "2": [],
        "3": [],
        "4": [],
        "5": [],
    }

    
    for visibility_df_series_idx, visibility_df_series_value in enumerate(visibility_df_series):
        get_the_group_num = str(groupby_index_template[visibility_df_series_idx])
        groupby_index_dict[get_the_group_num].append(visibility_df_series_value)

    # check for each group if there is at least one landmark more visible than the threshold
    set_visibility_threshold = 0.5 # 50 % visibility

    groupby_index_results = []

    for groupby_index_dict_entry in groupby_index_dict.values():
        if any(groupby_index_dict_entry_val > set_visibility_threshold for groupby_index_dict_entry_val in groupby_index_dict_entry):
            groupby_index_results.append(True)
        else:
            groupby_index_results.append(False)

    # if this is true for all groups
    if all(groupby_index_results) == True:
        user_in_camera_once = user_in_camera_once + 1
        return True
    else:
        user_not_in_camera = user_not_in_camera - 1
        return False




def user_in_camera_time_sufficient():

    global user_not_in_camera

    #check if user was in the camera for enough time (here 5 * seconds per frame (30 sec?) = ... sec)

    if user_not_in_camera > -5:
        return True
    else:
        # reset user_not_in_camera count
        user_not_in_camera = 0
        return False



 


##### FEEDBACK #####


def create_instruction(diff_per100_abs):

    global user_in_camera_once, scoremax

    get_user_in_camera_time_sufficient = user_in_camera_time_sufficient()

    # if the user is completely in the camera for enough time and the pose was not correct yet, start to give detailed instructions
    if get_user_in_camera_time_sufficient == True and scoremax < 8:
        # create detailed instructions like 'Please, raise your right arm a bit higher.'
        # use >>diff_per100_abs<<
        the_instruction = 'Please, change your body pose.' 
        the_instruction = False
    # if the user is not completely in the camera since the start OR for too much time
    elif user_in_camera_once == 0 or get_user_in_camera_time_sufficient == False:
        the_instruction = 'I can not see you.'
    # no instruction
    else:
        the_instruction = False

    return the_instruction
    


def feedback_score(correctness):
    global score, scoremax

    score = correctness / 10
    score = int(score)

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
        socketio.emit('score_max', {'score_max_val': scoremax, 'score_max_message': score_max_message, 'score_max_color': score_max_color})
        if scoremax > 8:
            set_feedback_text = 'New score, good job!'
            feedback_text(set_feedback_text)
        

def feedback_text(feedback_text):
    global ready_for_next_feedback
    if ready_for_next_feedback == True:
        socketio.emit('instruction', {'instruction_txt': feedback_text})
        audio_func(feedback_text)
        ready_for_next_feedback = False


@socketio.on('feedback_waiting_loop')  
def run(feedback_waiting_result):
    global ready_for_next_feedback

    if feedback_waiting_result == 'True':
        ready_for_next_feedback = True


##### TIMER #####

def timer_start():
    global time_timer_started
    time_timer_started = datetime.now()


def timer_print(time_countdown):
        mins, secs = divmod(time_countdown, 60)
        timerstr = '{:02d}:{:02d}'.format(mins, secs)
        socketio.emit('timer_socket', {'time': timerstr})

def timer_diff_func():
    global time_timer_started, timer_diff, time_difference

    time_difference = datetime.now() - time_timer_started
    #time_difference_seconds = time_difference.seconds
    time_countdown = timer_diff.seconds - time_difference.seconds

    if time_difference <= timer_diff:
        return True, time_countdown
    else:
        return False, time_countdown

 
def timer_stop():
    global time_timer_started, time_timer_ended, time_difference, timer_length
    #time_timer_started = datetime(1, 1, 1, 0, 0, 0) # set to 0 min 0 sec so that the time_difference is 0
    time_difference = timedelta(minutes=(timer_length+1))
    time_timer_ended = datetime.now() # not used yet
    timer_print(0)
    #timerstr = '{:02d}:{:02d}'.format(0, 0)
    #socketio.emit('timer_socket', {'time': timerstr})


##### AUDIO #####

def audio_func(audiotext):
    tts = gTTS(text=audiotext, lang='en')
    # make this check just once (to do)
    if not os.path.exists('static/audio/'):
        os.mkdir('static/audio/')
    filename = "static/audio/feedback.mp3"
    tts.save(filename)
    urlstr = 'http://127.0.0.1:5000/'+filename
    bloburl = 'http://127.0.0.1:5000/static/'
    socketio.emit('audio_socket', {'audiofile': "feedback.mp3", 'audio_url': urlstr, 'bloburl': bloburl})


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
    global fps, cnt, prev_recv_time, fps_array, framecount, user_in_camera_once
    data_image = getdata_image[0]
    camera_run = getdata_image[1]

    framecount = framecount + 1

    #if camera_run == 1:

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:

        

        # if Timer could have been started
        if user_in_camera_once != 0:
            if user_in_camera_once == 1:
                print('function on fire')
                set_feedback_text = 'Timer started'
                feedback_text(set_feedback_text)
            else:
                # check Timer 
                timer_state, timer_num = timer_diff_func()    
                if timer_state == True:   
                    timer_print(timer_num)
                elif timer_state == False:
                    exercise_stop()
        

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

        #if text should be added to the video

        #frame = ps.putBText(frame,text,text_offset_x=20,text_offset_y=30,vspace=20,hspace=10, font_scale=1.0,background_RGB=(10,20,222),text_RGB=(255,255,255))
        
        #flip
        frame = cv2.flip(frame, 1)

        # CV2 to jpeg
        imgencode = cv2.imencode('.jpeg', frame,[cv2.IMWRITE_JPEG_QUALITY,100])[1]
        # imgencode = cv2.imencode('.png', frame,[cv2.IMWRITE_PNG_COMPRESSION, 9])[1]

        # base64 encode
        stringData = base64.b64encode(imgencode).decode('utf-8')
        b64_src = 'data:image/jpeg;base64,'
        # b64_src = 'data:image/png;base64,'
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


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=2204, threaded=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 
