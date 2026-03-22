# import modules
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os
from dash_holoniq_wordcloud import DashWordcloud
import numpy as np


#Initalize dataframe with all seasons
total_df = pd.DataFrame()

files = sorted(os.listdir('Champions_League/Geocoded'))
for file in files:
    data = pd.read_csv('Champions_League/Geocoded/'+file)
            
    total_df = pd.concat([total_df,data],ignore_index=True)


#Wordcloud data
games_for_each_team = total_df['home_team'].value_counts() + total_df['away_team'].value_counts()
wordcloud_list = games_for_each_team.to_frame().reset_index().values.tolist()


#Dash instatiation
app = dash.Dash(__name__)

#app layout
app.layout = html.Div([
        html.H1("Plotting the Champions League data set"),
        html.Div([
            dcc.Graph(id='scatterplot_geo') 
        ]),
        html.Div([
            dcc.Graph(id='heatmap')
        ]),
        html.Div([
                DashWordcloud(
                    id='cloud',
                    list=wordcloud_list,
                    width=1000, height=800,
                    gridSize=50,
                    color='#f0f0c0',
                    backgroundColor='#001f00',
                    shuffle=False,
                    rotateRatio=0.5,
                    shrinkToFit=True,
                    # Ciklen fremgår ikke på hjemmesiden. Kilde til mulig problem?
                    shape='circle',
                    hover=True
                    ),
            ],style={'text-align': 'center'}),
        ])


#callback function for worldmap with input from the wordcloud
@app.callback(
    Output(component_id='scatterplot_geo', component_property='figure'),
    Input(component_id='cloud', component_property='click'))

def update_worldmap(team):
    #Finals/games played on neutral sites are not included in ALL view
    mydata = total_df[~total_df['venue'].str.contains("Neutral Site")]
    
    if team != None:
        mydata = total_df[(total_df['home_team'] == team[0]) | (total_df['away_team'] == team[0])]
       
    #Games on each venue
    games_on_each_venue = mydata['venue'].value_counts()
    
    #Wins on each venue for the home team
    wins = mydata['venue'][mydata['winning_team'] == mydata['home_team']].value_counts()
    
    if team != None:
        #Wins on each venue for the chosen team
        wins = mydata['venue'][mydata['winning_team'] == team[0]].value_counts()
        
    
    #Creating df by combining two series
    venue_df = pd.concat({"games played": games_on_each_venue, "wins" : wins}, axis = 1)

    #Changing None-values to 0
    #None-values are presensent because teams can play and not win
    venue_df["wins"] = venue_df["wins"].fillna(0)

    #Calculating win % for the chosen team on each venue
    venue_df["win %"] = venue_df['wins'] / venue_df['games played'] * 100
    
    #Temporary df
    #temp df contains lat and lon which are not present in venue_df
    #temp_df-index is set to "venue" to mtach and concat with venue_df
    temp_df = mydata[['venue' , 'latitude', 'longitude']].drop_duplicates('venue').set_index("venue")
    
    #lat and lon are concated
    venue_df = pd.concat([venue_df,temp_df], axis = 1)
    
    #Rest index for venue_df in order to use venue-name in plot
    venue_df.reset_index(inplace=True)

    map_figure = px.scatter_geo(venue_df, 
                       lat="latitude",
                       lon="longitude",
                       hover_name="venue",
                       # scope='europe'
                       size = 'games played',
                       color = "win %",
                       )       
    
    return map_figure


#callback function for heatmap with input from the wordcloud
@app.callback(
    Output(component_id='heatmap', component_property='figure'),
    Input(component_id='cloud', component_property='click'))
def update_heatmap(team):
    mydata = total_df[~total_df['venue'].str.contains("Neutral Site")]

    if team != None:
        mydata = total_df[(total_df['home_team'] == team[0]) | (total_df['away_team'] == team[0])]
      
    #New df
    #Value_counts used to count how often different score occurs
    #Series (returned by Value_counts) is change to df and index is rest
    score_count_df = mydata['result_90_min'].value_counts().to_frame().reset_index()

    #String scores is split into 2 collums on for homegoals and one for awaygoals
    #This is nessesary for max function
    score_count_df['home_goals'] = score_count_df['result_90_min'].str.split("-").str[0].astype(int)
    score_count_df['away_goals'] = score_count_df['result_90_min'].str.split("-").str[1].astype(int)


    #Creating df with all 0's
    #The size is determined by the maximum home and away goals
    df_0 = pd.DataFrame(np.zeros((max(score_count_df['away_goals']+1),max(score_count_df['home_goals']+1))))

    #Looping through score_count_df
    #for every score, eg. 0-0, the count is added at the corresponding location in df_0
    for score in score_count_df.iterrows():
        df_0.at[score[1]['away_goals'],score[1]['home_goals']] = score[1]['count']

    heatmap_figure = px.imshow(df_0,
                        origin='lower',
                        labels={'x': 'Home goals',
                                'y': 'Away goals',
                                'color': 'Number of games'
                                }
                        )
    
    return heatmap_figure

    
#Running the script
if __name__ == '__main__':
    # app.run_server(debug=False, port=8100)
    app.run(debug=False, port=8100)
