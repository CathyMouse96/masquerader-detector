""" Trains a GMM based on user behavior data. """

""" ---- Created by CMouse (qt2126@columbia.edu) ---- """

import argparse
import logging

import matplotlib.pyplot as plt
import numpy as np
from sklearn.mixture import GaussianMixture

import utils

logging.basicConfig(level=logging.INFO)

def parse_args():
    """ Parse command line arguments. """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_dir', default='data', type=str, 
        help='The input data directory.')
    parser.add_argument('-m', '--model_dir', default='model', type=str,
        help='The output model directory')
    return parser.parse_args()

def main():
    args = parse_args()

    # Input data is numpy array with dimensions n_samples * n_features
    data = utils.load_data(args.data_dir)

    # Create GMM
    gmm = GaussianMixture(n_components=1)

    # Train GMM
    gmm.fit(data)

    # Save GMM
    test_scores = gmm.score_samples(data)
    plt.plot(test_scores)
    plt.title("Scores")
    plt.show()

if __name__ == "__main__":
    main()
