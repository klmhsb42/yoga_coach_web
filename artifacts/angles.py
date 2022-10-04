# this will calculate angles

import pandas as pd
import numpy as np
import json
#import mediapipe as mp

#
df_angle_matrix = pd.read_csv('angles.csv', sep=',')

#df_angle_matrix_global = pd.DataFrame()

df_angle_matrix_global = df_angle_matrix.copy(deep=True)

f_landmarks = open('example/half_boat_wrong.json')
gettheposelandmarks = json.load(f_landmarks)
f_landmarks.close()

# https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def analyze(gettheposelandmarks):
    # get landmarks of current pose
    keypoints = []
    for data_point in gettheposelandmarks:
        keypoints.append({
                            'x': data_point['X'],
                            'y': data_point['Y'],
                            'z': data_point['Z'],
                            'visibility': data_point['Visibility'],
                            })

    #pre-analysis of feedback, if ready to start (most visible)
    #...

    # current landmarks to dataframe
    df_keypoints = pd.DataFrame(keypoints)

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
    angle_list_current = []

    for angle_cal in df_angle_global_array:
        getangle = angle_between((angle_cal[0],angle_cal[1],angle_cal[2]), (angle_cal[3],angle_cal[4],angle_cal[5]))
        getangle = getangle * (180/np.pi)
        angle_list_current.append(getangle)

    print(angle_list_current)

if __name__ == '__main__':
    analyze(gettheposelandmarks)