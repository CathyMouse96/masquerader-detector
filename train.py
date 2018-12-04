""" Trains a GMM based on user behavior data. """

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
        help='The input data directory.')
    parser.add_argument('-m', '--model_dir', default='model', type=str,
        help='The output model directory')
    parser.add_argument('-t', '--train_frac', default=0.8, type=float,
        help='The fraction of the training data.')
    return parser.parse_args()

def main():
    args = parse_args()

    # Input data is numpy array with dimensions n_samples * n_features
    data = utils.load_data(args.data_dir)

    train_len = int(args.train_frac * len(data))

    # Train hyperparameters
    best_n = 1
    best_score = 0

    training_scores = []
    valid_scores = []
    nrange = range(1, 50)

    for n in nrange:
        
        # Split into training and valid
        np.random.shuffle(data)
        data_t, data_v = data[:train_len], data[train_len + 1:]

        # Create GMM
        gmm = GaussianMixture(n_components=n)
    
        # Train GMM
        gmm.fit(data_t)

        # Evaluate GMM
        score_t = gmm.score(data_t)
        score_v = gmm.score(data_v)

        training_scores.append(score_t)
        valid_scores.append(score_v)
        
        if score_v > best_score:
            best_n = n
            best_score = score_v
    
    logging.info("Optimal number of components in GMM is {}".format(best_n))

    plt.plot(nrange, training_scores)
    plt.plot(nrange, valid_scores)
    plt.title("Hyperparameter tuning (n_components)")
    plt.gca().legend(["Training", "Validation"])
    plt.show()
    
    # Split into training and valid
    np.random.shuffle(data)
    data_t, data_v = data[:train_len], data[train_len + 1:]

    # Create GMM with best_n components
    gmm = GaussianMixture(n_components=best_n)

    # Train GMM
    gmm.fit(data)

    # Save GMM
    with open(os.path.join(args.model_dir, 'gmm.pkl'), 'wb') as f:
        pickle.dump(gmm, f)
    
    logging.info("Model saved to {}".format(os.path.join(args.model_dir, 'gmm.pkl')))

if __name__ == "__main__":
    main()
