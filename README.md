# Music-Recommender-POC-TF2.17

Modified code of my other project, ["Music-Recommender-POC"] (https://github.com/shiveshramlall/Music-Recommender-POC/blob/main/README.md)
- please see original repo for a more detailed overview

There has been changes with Tensorflow in newer versions and the Spotipy API which is no longer valid with the original solution.

## Tensorflow Problems

Previous code uses an older Tensorflow package with some things now deprecated, and some methods work differently: 
- Loading the module
- Retrieving predictions
- Previously experimental functions

Following this [TF Quickstart Tutorial](https://www.tensorflow.org/recommenders/examples/quickstart) no longer works with newer Tensorflow versions, which is why this codebase has made updates to the original code
- The tutorial worked with TF 2.13. It may continue to work up to version 2.15 (this needs to be confirmed, as I can't remember exactly which versions I tested)
- 2.17 needed some important code changes

As a POC, I've created some workarounds loading the module and retrieving predictions. Recommendations are stored in a JSON file for now, but ideally the model needs to be saved and reloaded.

## Spoitpy Problems

Spotipy API no longer allows you to retrieve audio features. Therefore content based filtering can no longer be used.
- https://developer.spotify.com/documentation/web-api/reference/get-audio-features

To make sure the code can utilize the Spoitpy package, create a spotify_auth.py file in root folder with:

```python
import os
os.enviro n["CLIENT_ID"] = ...
os.environ["CLIENT_SECRET"] = ...
os.environ["REDIRECT_URI"] = ...
```

# Objective

This codebase was mainly to test the differences with the Tensorflow versions and see which parts of the old code (TF 2.13) still works. But with the limitation around collecting song audio features, it was not worth polishing the solution further. 
