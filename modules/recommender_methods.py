# -- Imports

import json
import numpy as np
import os
import tensorflow as tf

# -- Methods

def load_model():

    cwd = os.getcwd()
    path = os.path.join(cwd, "model")
    loaded = tf.saved_model.load(path)
    print(f'''Model loaded from {path}''')
    return loaded

def show_playlist(pid, playlist_songs):

    out = []
    for p in playlist_songs:

        if(p[0] == str(pid)):
            out.append(p[1])

    out_array = np.array(out, dtype=str)
    out_array = np.char.lower(out_array)
    print(f"""Orginal Playlist (Showing {max}): """)
    print(out_array)
    return out_array

def decode_and_select(song_names, num):

    recommended_songs = song_names.numpy()
    decoder = np.vectorize(lambda x: x.decode('UTF-8'))
    decoded = decoder(recommended_songs)
    out_array = np.char.lower(decoded[0])
    out_array = out_array[0:num]
    print("Selected decoded results: ")
    print(out_array)
    return out_array
    
def remove_known_positives(recommendations, original_playlist):

    de_duped = np.setdiff1d(recommendations, original_playlist)
    print(f'''Number of recommended songs: {len(recommendations)}''')
    print(f'''Number of songs in orginal playlist: {len(original_playlist)}''')
    print(f'''Number of recommendations: {len(de_duped)}''')
    print(f"Recommendations: ")
    print(de_duped)
    return de_duped


        