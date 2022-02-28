import os
import sys
from collections import defaultdict
from pathlib import Path
import pandas as pd
import numpy as np
import ipdb
from scipy.stats import norm
hoops_dir = Path(os.path.abspath(__file__)).parent.parent
data_dir = hoops_dir / "data"
sys.path.append(hoops_dir.as_posix())

from pipeline import team_metadata


def sigmoid(x, a=0, b=1):
    return 1/(1+np.exp(-(a + b*x)))

def get_rankings(season=None, n_iters=2, sigmoid_a=0.28, sigmoid_b=1, games=None):
    ## Get games (if not provided)
    if games is None: 
        games = team_metadata.get_game_by_game(season)

    ## Get ranking
    ranking_distns = defaultdict(lambda: {'mu':0, 'sigma':1}) # team ranking distributions
    for i in range(n_iters):
        for _, game in games.iterrows():
            home, vis, home_win = game[['home', 'vis', 'home_win']]

            # Get prior dist'ns
            w = .01
            qh = np.arange(-5, 5, w)
            qv = np.arange(-5, 5, w)
            h_prior = norm.pdf(qh, loc=ranking_distns[home]['mu'], scale=ranking_distns[home]['sigma'])
            v_prior = norm.pdf(qv, loc=ranking_distns[vis]['mu'], scale=ranking_distns[vis]['sigma'])

            # Get posterior
            meshgrid = np.meshgrid(qh, qv)
            qh_minus_qv = meshgrid[0] - meshgrid[1] # matrix of quality differences
            outcome_probs = sigmoid(qh_minus_qv, a=sigmoid_a, b=sigmoid_b) # row represents qv (lowest to highest), col represents qh (lowest to highest)
            outcome_probs = outcome_probs if home_win else 1-outcome_probs
            h_post_over_v = h_prior * outcome_probs # posteriors—row represents qv, column represents qh
            v_post_over_h = v_prior[:,np.newaxis] * outcome_probs # posteriors—row represents qv, column represents qh        
            h_post = (h_post_over_v * v_prior[:, np.newaxis]).sum(0)
            v_post = (v_post_over_h * h_prior).sum(1)
            h_post /= (h_post*w).sum()
            v_post /= (v_post*w).sum()
            ranking_distns[home] = {'mu': w*(qh*h_post).sum(), 'sigma': np.sqrt(w*np.sum((qh**2)*h_post) - (w*np.sum(qh*h_post))**2)}
            ranking_distns[vis] = {'mu': w*(qv*v_post).sum(), 'sigma': np.sqrt(w*np.sum((qv**2)*v_post) - (w*np.sum(qv*v_post))**2)}
    return dict(sorted({k:v['mu'] for k, v in ranking_distns.items()}.items(), key=lambda x: x[1]))

