import os
import sys
from pathlib import Path
import pandas as pd
import ipdb
from nba_api.stats.endpoints import playbyplayv2
from nba_api.stats.endpoints import leaguegamefinder
hoops_dir = Path(os.path.abspath(__file__)).parent.parent
data_dir = hoops_dir / "data"
sys.path.append(hoops_dir.as_posix())

def convert_play_by_play_to_score_by_score(pbp):
    sbs = pbp.groupby("score").first().reset_index().sort_values(['time']).copy(deep=True)[['game_id', 'home', 'vis', 'time', 'home_score', 'vis_score']]
    sbs['home_win'] = sbs['home_score'].iloc[-1] > sbs['vis_score'].iloc[-1]
    return sbs

def get_sbs(seasons): # get combined score by score
    sbs = list()
    for season in seasons:
        pbp_file_names = list(filter(lambda x: x.endswith(".csv"), os.listdir(data_dir / season)))
        for pbp_file_name in pbp_file_names:
            if not pbp_file_name.endswith(".csv"):
                continue
            pbp = pd.read_csv(data_dir / season / pbp_file_name)
            sbs.append(convert_play_by_play_to_score_by_score(pbp))
    sbs = pd.concat(sbs)
    return sbs


