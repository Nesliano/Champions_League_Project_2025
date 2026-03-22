# import required modules
from bs4 import BeautifulSoup
import os
import pandas as pd


if not os.path.exists('Champions_League/Results'):
    os.mkdir("Champions_League/Results")

files = sorted([f for f in os.listdir('Champions_League') if f.endswith('.html')])
for file in files:
    data = []
    page = open('Champions_League/'+file,'r',encoding='utf-8').read()
    soup = BeautifulSoup(page,features="lxml")
    
    tabel = soup.find('table',attrs={'id':'sched_all'}).find('tbody').findAll('tr', class_ = None)
    
    for game in tabel:        
        round_of_comp_a = game.find('th').find('a')
        date_td = game.find('td',attrs={'data-stat':'date'})
        home_team_td = game.find('td',attrs={'data-stat':'home_team'})
        away_team_td = game.find('td',attrs={'data-stat':'away_team'})
        score_both = game.find('td',attrs={'data-stat':'score'})
        venue_td = game.find('td',attrs={'data-stat':'venue'})
        # required = [round_of_comp_a, date_td, home_team_td, away_team_td, score_both]
        # if all(required):
        round_of_comp = round_of_comp_a.text
        date = date_td.text
        home_team = home_team_td.find('a').text
        away_team = away_team_td.find('a').text
        home_nation = home_team_td.find('span').get('title')
        away_nation = away_team_td.find('span').get('title')

        if len(score_both.text) > 3:
            home_goals = score_both.text.split()[1].split("–")[0]
            home_penalties = score_both.text.split()[0].replace('(', '').replace(')','')
            away_goals = score_both.text.split()[1].split("–")[1]
            away_penalties = score_both.text.split()[2].replace('(', '').replace(')','')
            
            if home_penalties > away_penalties:
                winning_team = home_team
            else:
                winning_team = away_team
            
        else:
            home_goals = score_both.text.split("–")[0]
            away_goals = score_both.text.split("–")[1]
            home_penalties = None
            away_penalties = None
            
            if home_goals > away_goals:
                winning_team = home_team
            elif home_goals == away_goals:
                winning_team = None
            else:
                winning_team = away_team
            
            
        venue = venue_td.text
        
        #Heatmap
        #combining home and away goals as a string for use with value count function
        result_90_min = str(home_goals)+"-"+str(away_goals)
        
        
        data.append([round_of_comp, date, home_team, away_team, home_nation, away_nation, home_goals, away_goals, home_penalties, away_penalties, venue, winning_team, result_90_min])
            
    df = pd.DataFrame(data,columns = ['round_of_comp','date', 'home_team', 'away_team', 'home_nation', 'away_nation', 'home_goals', 'away_goals', 'home_penalties', 'away_penalties', 'venue', 'winning_team', 'result_90_min'])   
    df.to_csv('Champions_League/Results/' + file[:-5] + ' results.csv', index=False, encoding='utf-8')
    # Splicing. Starter fra starten og kører indtil det 5. sidste bogstav og underlader denne. "1990-1991.html"
    print(file, "parsed")
    