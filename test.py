""" Evaluates a GMM based on user behavior data. """

""" ---- Created by CMouse (qt2126@columbia.edu) ---- """

import argparse
import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pickle
from sklearn.mixture import GaussianMixture

import utils

logging.basicConfig(level=logging.INFO)

def parse_args():
    """ Parse command line arguments. """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_dir', default='data', type=str, 
        help='The test data directory.')
    parser.add_argument('-m', '--model_dir', default='model', type=str,
        help='The saved model directory')
    return parser.parse_args()

def main():
    args = parse_args()

    # Input data is numpy array with dimensions n_samples * n_features
    data = utils.load_data(args.data_dir)

    # Load model
    with open(os.path.join(args.model_dir, 'gmm.pkl'), 'rb') as f:
        gmm = pickle.load(f)
    
    logging.info("Model loaded from {}".format(os.path.join(args.model_dir, 'gmm.pkl')))

    # Evaluate GMM
    test_scores = gmm.score_samples(data)
    print(test_scores)
    plt.plot(test_scores)
    plt.title("Scores for test data")
    plt.show()

if __name__ == "__main__":
    main()
