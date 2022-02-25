import os 
import sys
from pathlib import Path
import argparse
from bs4 import BeautifulSoup
import json
import requests
import time
from datetime import datetime
import pandas as pd
import numpy as np 

hoops_dir = Path(os.path.abspath(__file__)).parent.parent
data_dir = hoops_dir / "data"
lines_dir = data_dir / "lines"
sys.path.append(hoops_dir.as_posix())

def track_lines(url, sleep=30, max_iter=1000):
    all_lines = pd.DataFrame(columns=['home', 'vis', 'home_score', 'vis_score', 'quarter', 'time', 'home_mline', 'vis_mline'])
    start_time = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    
    for i in range(max_iter):
        ## Parse the page
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        
        ## Get all Lines
        lines = soup.find_all("tbody", class_="sportsbook-table__body")[0].find_all("tr")

        ## Get the teams
        teams = [line.find("div", class_="event-cell__name-text").text.split(" ")[0] for line in lines]
        
        ## Get the time
        clocks = [line.find("div", class_='event-cell__clock') for line in lines[::2]]
        times = [clock.find_all("span")[0].string if clock else None for clock in clocks]
        quarters = [int(clock.find_all("span")[1].string[0]) if clock else None for clock in clocks] # TODO: OT?

        ## Get the scores
        scores = [line.find("span", class_="event-cell__score") for line in lines]
        scores = [int(score.text) if score else None for score in scores]

        ## Get the lines
        mlines = [int(line.find("span", class_="sportsbook-odds american no-margin default-color").text.replace("+", "")) for line in lines]        

        ## Update lines
        iter_lines = pd.DataFrame(columns=['home', 'vis', 'home_score', 'vis_score', 'quarter', 'time', 'home_mline', 'vis_mline'])
        iter_lines['home'] = teams[1::2]
        iter_lines['vis'] = teams[::2]
        iter_lines['home_score'] = scores[1::2]
        iter_lines['vis_score'] = scores[::2]
        iter_lines['quarter'] = quarters
        iter_lines['time'] = times
        iter_lines['home_mline'] = mlines[1::2]
        iter_lines['vis_mline'] = mlines[::2]        
        all_lines = pd.concat([all_lines, iter_lines]).drop_duplicates()
        all_lines.to_csv(lines_dir / (start_time + ".csv"), index=False)
        
        ## Sleep
        time.sleep(sleep)
        
        ## Break
        if len(lines) == 0:
            break
    
    ## Return
    return all_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sleep", type=int, default=30)
    parser.add_argument("-i", "--max_iter", type=int, default=1000)
    args = parser.parse_args()

    url = "https://sportsbook.draftkings.com/leagues/basketball/88670846" # TODO: does that URL change with the date?
    sleep = args.sleep
    max_iter = args.max_iter
    track_lines(url, sleep=sleep, max_iter=max_iter)
