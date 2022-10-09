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

filemode = 0 # 1 = 'pose_world_landmarks' and 0 = 'pose_landmarks'
gather_type = 'img' # or 'video'
mypath = 'collect/'+gather_type+'/'+str(filemode)+'/'
onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

f_connections = open('connections.json')
connections = json.load(f_connections)
f_connections.close()

def frame_args(duration):
        return {
                "frame": {"duration": duration},
                "mode": "immediate",
                "fromcurrent": True,
                "transition": {"duration": duration, "easing": "linear"},
                }

def create_data():

    global mypath, onlyfiles, connections

    
    
    list_of_cn2 = []
    list_of_names = []
    

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
            for connection in connections['list']:
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
                            x=[landmark_pair[0][0], landmark_pair[1][0]],
                            y=[landmark_pair[0][1], landmark_pair[1][1]],
                            z=[landmark_pair[0][2], landmark_pair[1][2]],
                        )
                    )
                    idx_pair_list.append(
                        dict(
                            start_idx=start_idx,
                            end_idx=end_idx,
                        )
                    )

            

            # get landmark coordinates from out_cn
            cn2 = {"x": [], "y": [], "z": [],}
            for pair in out_cn:
                for k in pair.keys():
                    cn2[k].append(pair[k][0])
                    cn2[k].append(pair[k][1])
                    cn2[k].append(None)
            list_of_cn2.append(cn2)

            new_df = pd.DataFrame(plotted_landmarks).T.rename(columns={0: "z", 1: "x", 2: "y"})
            new_df["lm"] = new_df.index.map(lambda s: mp_pose.PoseLandmark(s).name).values
            landmarknames33 = list(new_df.index.map(lambda s: mp_pose.PoseLandmark(s).name).values)


            # get landmark names for labels from idx_pair_list
            get_names = {"names": []}
            for getpair in idx_pair_list:
                get_start_idx_val = getpair['start_idx']
                get_stop_idx_val = getpair['end_idx']
                get_names['names'].append(landmarknames33[get_start_idx_val])
                get_names['names'].append(landmarknames33[get_stop_idx_val])
                get_names['names'].append(None)
            list_of_names.append(get_names)

        
        
    
    
    fig = go.Figure(go.Scatter3d(x=[], y=[], z=[],
                             #mode="lines", #"markers",
                             marker=dict(color="red", size=5),
                             line={"color": "black", "width": 5},
                             #name="connections",
                             )
                )

    

    frames = [go.Frame(data= [go.Scatter3d(x=chunk['x'],
                                        y=chunk['y'],
                                        z=chunk['z'],
                                        hovertemplate="<br>".join([
                                                "X: %{x}",
                                                "Y: %{y}",
                                                "Z: %{z}",
                                                "Name: %{text}",
                                            ]),
                                        text = [textstr for textstr in list_of_names[0]['names']]
                                        )
                            ],
                    traces=[0],
                    name=f'frame{chunk_idx}',  
                    )for chunk_idx, chunk in enumerate(list_of_cn2)
            ]


    fig.update(frames=frames)


    
    

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
                            "args": [None, frame_args(120)],
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
            sliders=sliders,
            scene = {
                #'xaxis': {'range': [-5, 5], 'rangemode': 'tozero', 'tickmode': "linear", 'tick0': -5, 'dtick': 1},
                #'yaxis': {'range': [-5, 5], 'rangemode': 'tozero', 'tickmode': "linear", 'tick0': -5, 'dtick': 1},
                #'zaxis': {'range': [-5, 5], 'rangemode': 'tozero', 'tickmode': "linear", 'tick0': -5, 'dtick': 1},
                #'aspectratio': dict(x=4, y=4, z=4),
                'aspectmode': 'cube',
            },
            #margin={'autoexpand': False},
            #autosize=False,
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