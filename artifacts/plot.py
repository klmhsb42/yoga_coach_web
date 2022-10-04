#https://stackoverflow.com/questions/69265059/is-it-possible-to-create-a-plotly-animated-3d-scatter-plot-of-mediapipes-body-p
#https://community.plotly.com/t/3d-scatter-animation/46368

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import mediapipe as mp
import os


mp_pose = mp.solutions.pose

#_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5

mode = 'landmarks' # or 'world_landmarks'
mypath = 'collect'
onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

f_connections = open('connections.json')
data_connections = json.load(f_connections)
f_connections.close()

def frame_args(duration):
        return {
                "frame": {"duration": duration},
                "mode": "immediate",
                "fromcurrent": True,
                "transition": {"duration": duration, "easing": "linear"},
                }

def create_data(connections=None):

    global mypath, onlyfiles, data_connections

    landmarks_array = [] #["z","x","y","lm"]
    cn2 = {"xs": [], "ys": [], "zs": []}
    

    for fileidx, landmarkfile in enumerate(onlyfiles):
        
        filepath = mypath+'/'+landmarkfile
        f_landmarks = open(filepath)
        landmark_list = json.load(f_landmarks)
        f_landmarks.close()

        if not landmark_list:
            return

        plotted_landmarks = {}

        for idx, landmark in enumerate(landmark_list):
            ##if (
            ##    landmark['Visibility'] < _VISIBILITY_THRESHOLD
            ##):
            # or (
            #     landmark.HasField("presence") and landmark.presence < _PRESENCE_THRESHOLD
            # ):
            ##    continue
            plotted_landmarks[idx] = (-landmark['Z'], landmark['X'], -landmark['Y'])

        if connections:
            out_cn = []
            idx_pair_list = []
            num_landmarks = len(landmark_list)
            # Draws the connections if the start and end landmarks are both visible.
            for connection in connections:
                start_idx = connection[0]
                end_idx = connection[1]
                if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                    raise ValueError(
                        f"Landmark index is out of range. Invalid connection "
                        f"from landmark #{start_idx} to landmark #{end_idx}."
                    )
                if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
                    landmark_pair = [
                        plotted_landmarks[start_idx],
                        plotted_landmarks[end_idx],
                    ]
                    out_cn.append(
                        dict(
                            xs=[landmark_pair[0][0], landmark_pair[1][0]],
                            ys=[landmark_pair[0][1], landmark_pair[1][1]],
                            zs=[landmark_pair[0][2], landmark_pair[1][2]],
                        )
                    )
                    idx_pair_list.append(
                        dict(
                            start_idx=start_idx,
                            end_idx=end_idx,
                        )
                    )

            
            # df_conn = pd.DataFrame(out_cn)
            # df_conn_idx = pd.DataFrame(idx_pair_list)
    
            # #df_conn_idx["lm"] = idx_pair_list.map(lambda s: mp_pose.PoseLandmark(s).name).values[0]
            # df_conn_idx["start_name"] = df_conn_idx['start_idx'].map(lambda s: mp_pose.PoseLandmark(s).name).values
            # df_conn_idx["end_name"] = df_conn_idx['end_idx'].map(lambda s: mp_pose.PoseLandmark(s).name).values
            # df_conn_idx = df_conn_idx.merge(df_conn, left_index=True, right_index=True)
            
            # df_conn.to_csv('plot_df_conn.csv', sep='\t', encoding='utf-8')
            # df_conn_idx.to_csv('plot_df_conn_idx.csv', sep='\t', encoding='utf-8')


            #cn2 = {"xs": [], "ys": [], "zs": []}
            for pair in out_cn:
                for k in pair.keys():
                    cn2[k].append(pair[k][0])
                    cn2[k].append(pair[k][1])
                    cn2[k].append(None)


        df = pd.DataFrame(plotted_landmarks).T.rename(columns={0: "z", 1: "x", 2: "y"})

        df["lm"] = df.index.map(lambda s: mp_pose.PoseLandmark(s).name).values

        df["step"] = fileidx

        landmarks_array_values = df.to_numpy()

        for ln_a_val in landmarks_array_values:
            landmarks_array.append(ln_a_val)


    final_df = pd.DataFrame(landmarks_array).rename(columns={0: "z", 1: "x", 2: "y", 3: "lm", 4: "step"})
    
    '''
    create_plot(final_df, cn2)

    def create_plot(final_df, cn2):
    '''

    final_df.to_csv('plot_df.csv', sep='\t', encoding='utf-8')

    #.update_traces(marker={"color": "red"})

    fig = (
        px.scatter_3d(final_df, x="z", y="x", z="y", hover_name="lm", color="step")
        .update_layout(
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            scene={"camera": {"eye": {"x": 2.1, "y": 0, "z": 0}}},
        )
    )

    '''
    fig.add_traces(
        [
            go.Scatter3d(
                x=cn2["xs"],
                y=cn2["ys"],
                z=cn2["zs"],
                mode="lines",
                line={"color": "black", "width": 5},
                name="connections",
            )
        ]
    )
    '''
    # Frames
    frames = [go.Frame(data= [go.Scatter3d(x=cn2["xs"],
                                        y=cn2["ys"],
                                        z=cn2["zs"],
                                        mode="lines",
                                        line={"color": "black", "width": 5},
                                        name="connections",
                                        )
                            ],
                    traces= [0],
                    name=f'frame{k}'      
                    )for k  in  range(102) #len(33)-1 #hard coded!!!
            ]

    '''frames = [go.Frame(data= [go.Scatter3d(x=cn2[:k+1],
                                        y=cn2[:k+1],
                                        z=cn2[:k+1],
                                        mode="lines",
                                        line={"color": "black", "width": 5},
                                        name="connections",
                                        )
                            ],
                    traces= [0],
                    name=f'frame{k}'      
                    )for k  in  range(32) #len(33)-1
            ]'''

    fig.update(frames=frames)


    
    ''''''

    sliders = [
        {
        "pad": {"b": 10, "t": 60},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        
        "steps": [
                    {"args": [[f.name], frame_args(0)],
                    "label": str(k),
                    "method": "animate",
                    } for k, f in enumerate(fig.frames)
                ]
        }
            ]

    fig.update_layout(

        updatemenus = [{"buttons":[
                        {
                            "args": [None, frame_args(50)],
                            "label": "Play", 
                            "method": "animate",
                        },
                        {
                            "args": [[None], frame_args(0)],
                            "label": "Pause", 
                            "method": "animate",
                    }],
                        
                    "direction": "left",
                    "pad": {"r": 10, "t": 70},
                    "type": "buttons",
                    "x": 0.1,
                    "y": 0,
                }
            ],
            sliders=sliders
        )

    '''
    fig.update_layout(scene = dict(xaxis=dict(range=[min("x"), max("x")], autorange=False),
                                yaxis=dict(range=[min("y"), max("y")], autorange=False),
                                zaxis=dict(range=[min("z"), max("z")], autorange=False)
                                )
                    )
    '''

    fig.update_layout(sliders=sliders)

    

    return fig


getfig = create_data()
getfig.show()