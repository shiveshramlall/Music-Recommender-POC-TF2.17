# -- Imports

import os
import spotipy
import spotify_auth # Credentials needed to access Spotify API
import pandas as pd
from collections import defaultdict
import json 
import string

# -- Methods

def authenticate_spotipy():
    """
    Method to connect to spotipy API using auth credentials.
    Scope defines the level of access to the spotify API.

    Returns:
        sp (spotipy.client.Spotify): library that provides access to Spotify data
    """

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")

    scope = "user-library-read user-follow-read user-top-read playlist-read-private user-read-private user-read-recently-played" 
    sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,    
        scope=scope,)
    )
    return sp

sp = authenticate_spotipy()

def collect_user_playlists(user_id):
    """
    Collects all public playlists for a specifc user

    Args:
        user_id ([type]): [description]

    Returns:
        [type]: [description]
    """

    user_playlists = sp.user_playlists(user=user_id)

    user_playlist_ids = []
    for c in user_playlists['items']:
        user_playlist_ids = user_playlist_ids + [c['id']]

    return user_playlist_ids

def get_playlist_name(playlist_id, ep_user):

    results = sp.user_playlist(user=ep_user, playlist_id=playlist_id, fields="name")
    return results["name"]

def collect_tracks(user_playlist_ids, user_id, max_id):

    new_id = max_id
    pl_songs = []

    playlist_id_ref = {}
    playlist_users_ref = {}
    playlist_users_ref[user_id] = {}

    for upid in user_playlist_ids:
        
        results = sp.user_playlist_tracks(user=user_id, playlist_id=upid)
        tracks = results['items']

        # Spotfy results are paginated 
        # (https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist)
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        for r in tracks:
            # print(r)
            pl_songs = pl_songs + [[str(new_id), f'''{r['track']['name'].lower()} --- {r['track']['artists'][0]['name'].lower()}''']]

        playlist_name = get_playlist_name(upid, user_id)
        playlist_id_ref[new_id] = {"name": playlist_name.lower(), "owner": user_id}
        playlist_users_ref[user_id].update({new_id: playlist_name.lower()})

        new_id += 1

    return pl_songs, playlist_id_ref, playlist_users_ref

def collect_tracks_with_metadata(user_playlist_ids, user_id, max_id):

    new_id = max_id
    pl_songs = []

    for upid in user_playlist_ids:
        
        results = sp.user_playlist_tracks(user=user_id, playlist_id=upid)
        tracks = results['items']

        # Spotfy results are paginated 
        # (https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist)
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        for r in tracks:
            # print(r)
            pl_songs = pl_songs + [[new_id,  r['track']['name'].lower(), r['track']['artists'][0]['name'].lower(), r['track']['album']['name'].lower(), r['track']['duration_ms']]]
        
        new_id += 1

    return pl_songs

def collect_dict_tracks(user_playlist_ids, user_id, max_id):

    new_id = max_id
    collect_songs_dict = {}

    for upid in user_playlist_ids:

        collect_songs_dict[new_id] = {}

        results = sp.user_playlist_tracks(user=user_id, playlist_id=upid)
        tracks = results['items']

        # Spotfy results are paginated 
        # (https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist)
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        for r in tracks:
            # print(r)

            collect_songs_dict[new_id][r['track']['name'].lower()]  = r['track']['artists'][0]['name'].lower()

        new_id += 1

    return collect_songs_dict

def find_song(name, artist):
    """
        ...
    """
    
    song_data = {}
    name = name.translate(str.maketrans('', '', string.punctuation))

    try:
        results = sp.search(q= f'''track: {name} artist: {artist}''', type="track", limit=1)

        if results['tracks']['items'] == []:
            name = name[0: int(len(name)/2)]
            results = sp.search(q= f'''track: {name} artist: {artist}''', type="track", limit=1)
        
        if results['tracks']['items'] == []:
            return None
    
    except Exception as e:
        # print("Excpetion occured when searching for song:" + str(e))
        return None

    results = results['tracks']['items'][0]
    # print(json.dumps(results, indent = 2))
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    if(audio_features is None):
        return None

    song_data['name'] = name
    song_data['artist'] = artist
    song_data['release_year'] = int(results['album']['release_date'].split("-")[0])
    song_data['explicit'] = int(results['explicit'])
    song_data['duration_ms'] = results['duration_ms']
    song_data['popularity'] = results['popularity']
    
    for key, value in audio_features.items():
        song_data[key] = value
    
    return song_data

def get_song_data(full_song, cached_songs):
    """
        Retrieve song from data
    """
    split = (full_song.split("---"))
    artist = split[1].strip()
    song_name = split[0].strip()

    try:
        song_data = cached_songs[(cached_songs['name'] == song_name) 
                                & (cached_songs['artist'] == artist)].iloc[0]
        return song_data, False
    
    except Exception:
        searched_song = find_song(song_name, artist)

        if not searched_song:
            return None, False

        return searched_song, True