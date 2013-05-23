# astro

Detecting Asteroids with Neural Networks, as presented at the May 2013 Philly PUG meetup.

Extended presentation available at: https://www.youtube.com/watch?v=o-OF85H3gwI

# Running

Training and trial data are in the `/training_data` and `/test_data/trial*`
directories. Training data is sorted into `valid` and `invalid` data sets.
When running the script, it must be pointed to an unsorted trial directory. It
will sort the data into `valid` and `invalid` directories. For example:

    python brain.py test_data/trial1/

# Training

A pre-trained and pickle'd network is stored as the file `_learned`. No
additional training is necessary. The script checks for this file when starting.
If you want to re-train the network, simply remove this file, and run the
script.
