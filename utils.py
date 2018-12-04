import logging
import os

import numpy as np

def load_data(path):
    """ Load and combine .log files at specific path. """
    logging.info("Loading data at {}...".format(path))
    data = []
    datalen = 0
    for filename in os.listdir(path):
        if filename.endswith(".log"):
            with open(os.path.join(path, filename), 'r') as f:
                for line in f.readlines():
                    data.append([int(x) for x in line.strip()[1:-1].split(', ')])
                    datalen += 1
    logging.info("Loaded {} samples from {}.".format(datalen, path))
    # Apply log(x+1) to all samples
    data = np.log(np.array(data) + 1)
    return data
