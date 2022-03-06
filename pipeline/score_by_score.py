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
    sbs = pbp.groupby("score").first().reset_index().sort_values(['time']).copy(deep=True)[['game_id', 'date', 'home', 'vis', 'time', 'home_score', 'vis_score']]
    sbs['home_win'] = sbs['home_score'].iloc[-1] > sbs['vis_score'].iloc[-1]
    return sbs
    
def get_sbs(season):
    pbp_file_names = list(filter(lambda x: x.endswith(".csv"), os.listdir(data_dir / "play_by_play" / season)))
    sbss = list()
    for pbp_file_name in pbp_file_names:
        if not pbp_file_name.endswith(".csv"):
            continue
        pbp = pd.read_csv(data_dir / "play_by_play" / season / pbp_file_name)
        sbss.append(convert_play_by_play_to_score_by_score(pbp))
    sbs = pd.concat(sbss).reset_index(drop=True)
    return sbs

if __name__ == "__main__":
    season = sys.argv[1]
    # TODO: add command line arguments
    sbs = get_sbs(season)
    sbs_dir = data_dir / "score_by_score"
    os.makedirs(sbs_dir , exist_ok=True)
    sbs.to_csv(sbs_dir / (season + ".csv"), index=False)