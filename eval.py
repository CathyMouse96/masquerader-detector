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
    parser.add_argument('-fd', '--fake_data_dir', default='fakedata', type=str, 
        help='The masquerader test data directory.')
    parser.add_argument('-m', '--model_dir', default='model', type=str,
        help='The saved model directory')
    parser.add_argument('-td', '--true_data_dir', default='truedata', type=str, 
        help='The authentic test data directory.')
    return parser.parse_args()

def main():
    args = parse_args()

    # Input data is numpy array with dimensions n_samples * n_features
    true_data = utils.load_data(args.true_data_dir)
    fake_data = utils.load_data(args.fake_data_dir)
    
    # Load model
    with open(os.path.join(args.model_dir, 'gmm.pkl'), 'rb') as f:
        gmm = pickle.load(f)
    
    logging.info("Model loaded from {}".format(os.path.join(args.model_dir, 'gmm.pkl')))

    logging.info("Score for authentic data set is {}".format(gmm.score(true_data)))
    logging.info("Score for masquerader data set is {}".format(gmm.score(fake_data)))

    # Train hyperparameters
    precisions = [] # defined here as tn / (fp + tn)
    recalls = []
    thresholds = list(map(lambda x: x * 0.1, range(-200, 200, 1)))

    best_threshold = thresholds[0]
    best_precision = 0 # defined here as tn / (fp + tn)
    best_recall = 0

    # Results for different thresholds
    for t in thresholds:
        # Evaluate GMM
        false_positive = 0
        true_positive = 0
        
        # if score < t, mark as positive
        true_test_scores = gmm.score_samples(true_data) # should have no positives
        for score in true_test_scores:
            if score < t: # is a false positive!
                false_positive += 1

        fake_test_scores = gmm.score_samples(fake_data) # should all be positives
        for score in fake_test_scores:
            if score < t: # is a true positive!
                true_positive += 1
        
        precision = 1 - (false_positive / len(true_data)) # defined here as tn / (fp + tn)
        recall = true_positive / len(fake_data)

        precisions.append(precision)
        recalls.append(recall)

        if precision + recall > best_precision + best_recall:
            best_threshold = t
            best_precision = precision
            best_recall = recall

    logging.info("Optimal threshold is {}".format(best_threshold))
    logging.info("Corresponding false positive rate is {}".format(1 - best_precision))
    logging.info("Corresponding true positive rate is {}".format(best_recall))

    # Plot graph
    plt.plot(thresholds, precisions)
    plt.plot(thresholds, recalls)
    plt.title("Hyperparameter tuning (threshold)")
    plt.gca().legend(["Precision (*)", "Recall"])
    plt.gcf().text(0.3, 0.02, "(*) Defined here as tn / (fp + tn)")
    plt.show()

if __name__ == "__main__":
    main()
