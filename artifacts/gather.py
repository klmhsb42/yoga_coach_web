#https://google.github.io/mediapipe/solutions/pose.html

import os
import json
from venv import create
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

framecount = 0
path_train_save = 'collect/'
create_folder = 'collect'

# For webcam input:
cap = cv2.VideoCapture(0)

def gather():

  global cap, framecount, create_folder, path_train_save

  if not os.path.exists(create_folder):
    os.mkdir(create_folder)

  with mp_pose.Pose(
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      results = pose.process(image)

      # Save the landmarks to JSON file

      keypoints = []
      for data_point in results.pose_landmarks.landmark:
          keypoints.append({
                              'X': data_point.x,
                              'Y': data_point.y,
                              'Z': data_point.z,
                              'Visibility': data_point.visibility,
                              })

      #print(keypoints)
      poselandmarks_jsonString = json.dumps(keypoints)
      #print(poselandmarks_jsonString)
      #print(framecount)
      
      with open(path_train_save+'landmarks_'+str(framecount)+'.json', 'w') as f:
          f.write(poselandmarks_jsonString)

      framecount = framecount + 1

      # Draw the pose annotation on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      mp_drawing.draw_landmarks(
          image,
          results.pose_landmarks,
          mp_pose.POSE_CONNECTIONS,
          landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
      # Flip the image horizontally for a selfie-view display.
      cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
      if cv2.waitKey(5) & 0xFF == 27:
        break
  cap.release()

if __name__ == '__main__':
  gather()
