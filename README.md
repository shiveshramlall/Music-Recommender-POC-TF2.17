# Music-Recommender-POC-TF2.17

Modified code of my other project, ["Music-Recommender-POC"] (https://github.com/shiveshramlall/Music-Recommender-POC/blob/main/README.md)

Previous code uses an older Tensorflow package with some things now deprecated, and some methods work differently. 
- Loading the module
- Retrieving predictions
    - This [TF Quickstart Tutorial](https://www.tensorflow.org/recommenders/examples/quickstart) also fails with the newer TF versions
- Previously experimental functions

Spotipy API no longer allows you to retrieve audio features. Therefore content based filtering can no long ber used. 

To make sure the code ccan utilize the Spoitpy package, create a spotify_auth.py file in root folder with:

```python
import os
os.enviro n["CLIENT_ID"] = ...
os.environ["CLIENT_SECRET"] = ...
os.environ["REDIRECT_URI"] = ...
```
