""" Trains a GMM based on user behavior data. """

# Created by CMouse (qt2126@columbia.edu)

import matplotlib.pyplot as plt
import numpy as np

from sklearn.mixture import GaussianMixture

# Create GMM
gmm = GaussianMixture(n_components=10)
# Train GMM
gmm.fit(digits.data)
# Save GMM
test_scores = gmm.score_samples(digits.data)
plt.plot(test_scores)
plt.title("Scores")
plt.show()