#https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
import json
import numpy as np

# For static images:
IMAGE_FILES = []
BG_COLOR = (192, 192, 192) # gray

path_train_save = 'collect/'
#os.mkdir(path_train_save)

framecount = 0

with mp_pose.Pose(
    static_image_mode=True,
    model_complexity=2,
    enable_segmentation=True,
    min_detection_confidence=0.5) as pose:
  for idx, file in enumerate(IMAGE_FILES):
    image = cv2.imread(file)
    image_height, image_width, _ = image.shape
    # Convert the BGR image to RGB before processing.
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
      continue
    print(
        f'Nose coordinates: ('
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height})'
    )

  

    # save data for training
    gettheposelandmarks = results.pose_landmarks
    gettheposeworldlandmarks = results.pose_world_landmarks
    gettheposeconnections = mp_pose.POSE_CONNECTIONS

    keypoints = []
    for data_point in gettheposelandmarks.landmark:
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


    # keypoints2 = []
    # for data_point2 in gettheposeworldlandmarks.landmark:
    #     keypoints2.append({
    #                         'X': data_point2.x,
    #                         'Y': data_point2.y,
    #                         'Z': data_point2.z,
    #                         'Visibility': data_point2.visibility,
    #                         })

    # worldposelandmarks_jsonString = json.dumps(keypoints2)

    ##with open(path_train_save+'world_landmarks_'+str(framecount)+'.json', 'w') as f:
    ##    f.write(worldposelandmarks_jsonString)

    # print(gettheposeconnections)
    # print(gettheposeconnections.copy)
    # print(dir(gettheposeconnections.difference))
    # print(gettheposeconnections.intersection)
    # print(gettheposeconnections.isdisjoint)
    # print(gettheposeconnections.issubset)
    # print(gettheposeconnections.issuperset)
    # print(gettheposeconnections.symmetric_difference)
    # print(gettheposeconnections.union)

    #data = pd.DataFrame(training_data, columns=columns)
    #data['label'] = 'somelabel'
    #data.to_csv('Data/filename.csv', index=False)

    framecount = framecount + 1

    annotated_image = image.copy()
    # Draw segmentation on the image.
    # To improve segmentation around boundaries, consider applying a joint
    # bilateral filter to "results.segmentation_mask" with "image".
    condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
    bg_image = np.zeros(image.shape, dtype=np.uint8)
    bg_image[:] = BG_COLOR
    annotated_image = np.where(condition, annotated_image, bg_image)


    # Draw pose landmarks on the image.
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)
    # Plot pose world landmarks.
    mp_drawing.plot_landmarks(
        results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

# For webcam input:
cap = cv2.VideoCapture(0)

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
