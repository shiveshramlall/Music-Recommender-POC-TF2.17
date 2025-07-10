# -- Imports

from collections import defaultdict
from scipy.spatial.distance import cdist
import difflib
from sklearn.decomposition import PCA
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np

# -- Methods

def cluster_pipeline(songs_with_features, no_clusters):
    """
    Creates a clustering pipeline using k-means 

    Args:
        songs_with_features (list): List of songs with their audio features
        no_clusters (int): No of clusters required for pipeline

    Returns:
        tuple consisting of:
            song_cluster_pipeline (sklearn.pipeline.Pipeline): Generated pipeline used for clustering
            number_cols (list): Contains column names for all the numerical features of a song
    """

    song_cluster_pipeline = Pipeline([('scaler', StandardScaler()), 
                                    ('kmeans', KMeans(n_clusters=no_clusters, 
                                    verbose=2))],verbose=True)

    # sf_df = pd.DataFrame(songs_with_features)
    sf_df = pd.DataFrame()
    for sf in songs_with_features:
        sf_df = sf_df.append(sf, ignore_index=True)

    # ensure there's not duplicates
    bool_series = sf_df.duplicated(keep='first')
    sf_df = sf_df[~bool_series]

    X = sf_df.select_dtypes(np.number)
    number_cols = list(X.columns)

    song_cluster_pipeline.fit(X)
    song_cluster_labels = song_cluster_pipeline.predict(X)
    sf_df['cluster_label'] = song_cluster_labels

    pca_pipeline = Pipeline([('scaler', StandardScaler()), ('PCA', PCA(n_components=2))])
    song_embedding = pca_pipeline.fit_transform(X)

    projection = pd.DataFrame(columns=['x', 'y'], data=song_embedding)
    projection = projection.set_index(sf_df.index)
    projection['title'] = sf_df['name']
    projection['cluster'] = sf_df['cluster_label']

    fig = px.scatter(projection, x='x', y='y', color='cluster', hover_data=['x', 'y', 'title'])
    fig.show()

    return song_cluster_pipeline, number_cols

def get_mean_vector(songs_list, number_cols):
    """
    Calculate the mean vector for a list of songs

    Args:
        songs_list (list): List of songs that recommendations will be based on
        number_cols (list): Contains column names for all the numerical features of a song

    Returns:
        [numpy.ndarray]: Array consisting of mean values
    """
    
    song_vectors = []
    
    for song in songs_list:
        song_vector = [song.get(nc) for nc in number_cols]
        song_vectors.append(song_vector)  
    
    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)

def flatten_dict_list(dict_list):
    """
    Utility function for flattening a list of dictionaries, to allow for easier access to items

    Args:
        dict_list (list): List containing dict items

    Returns:
        [collections.defaultdict]: Flattened representation of dict
    """
    
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
            
    return flattened_dict

def recommend_songs(orig_playlist, selected_recommendations, song_cluster_pipeline, number_cols, n_songs=100):
    """
    Recommends songs using a k means clustering pipeline to sort through the possible recommendations. 

    This can be used in conjunction with the collaborative model, to provide a ranking based on songs 
    similarity to the original playlist theme.

    Args:
        orig_playlist (list): List of songs, with audio features, from the orginal playlist to base recommendations off
        selected_recommendations (list): List of possible recommendations we are proving to the user
        song_cluster_pipeline (sklearn.pipeline.Pipeline): Generated pipeline used for clustering
        number_cols (list): Contains column names for all the numerical features of a song
        n_songs (int, optional): Number of top results to retrieve. Defaults to 100.

    Returns:
        [list]: List of dict items, containing the curated songs. Name, artist and release year fields are provided.
    """
    
    metadata_cols = ['name', 'artist', 'release_year']
    song_dict = flatten_dict_list(orig_playlist)

    numbers_sel_rec = []
    for song in selected_recommendations:
        numbers_sel_rec += [[song.get(nc) for nc in number_cols]]

    
    song_center = get_mean_vector(orig_playlist, number_cols)
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(numbers_sel_rec)
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])

    # selected_recommendations_df = pd.DataFrame(selected_recommendations)
    selected_recommendations_df = pd.DataFrame()
    for sr in selected_recommendations:
        selected_recommendations_df = selected_recommendations_df.append(sr, ignore_index=True)

    rec_songs = selected_recommendations_df.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]

    convert_dict = {'name': str, 'artist': str, 'release_year': int}
    rec_songs = rec_songs.astype(convert_dict)
    
    return rec_songs[metadata_cols].to_dict(orient='records')