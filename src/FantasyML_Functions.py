#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 14:53:03 2020

@author: johnvorhies
"""

from datetime import datetime
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style

style.use("ggplot")

def downloadData(pos_list = ['rb','wr','te','flx'], scoring = ''):
    exp_filter = '22:64:113:120:125:127:317:406:534'
    this_week = '4'
    for mp in pos_list:
        position = mp.upper()
        
        url = ('https://www.fantasypros.com/nfl/rankings/' + mp +
            '.php?filters=' + exp_filter + '\\&week=' + this_week + 
            '\\&export=xls')
        head_dir = 'dat/2020/week-'
        if position == 'QB' or position == 'K' or position == 'DST':
            pos_scoring = position
        else: 
            pos_scoring = position + '-' + scoring
        
        dl_dest = head_dir + this_week + '-' + pos_scoring + '-raw.xls'
        csv_dest = head_dir + this_week + '-' + pos_scoring + '-raw.csv'
        
        print('url: ' + url)
        print('raw_csv_dest: ' + dl_dest)
        print('csv_dest: ' +  csv_dest)
        
        os.system(('/opt/anaconda3/bin/python3 src/fp_dl.py -u ' + url + 
                   ' -d ' + dl_dest + ' -c ' + csv_dest))
        
def drawTiers(position='qb', num_players=20, tiers=3, scoring='STD'):
    this_week = 4
    
    # import csv
    position = position.upper()
    
    if position == 'QB' or position == 'K' or position == 'DST':
        pos_scoring = position
    else: 
        pos_scoring = position + '-' + scoring
        
    head_dir = 'dat/2020/week-'
    csv_path = head_dir + str(this_week) + '-' + pos_scoring + '-raw.csv'
    data = pd.read_csv(csv_path)
    
    # format csv
    data.drop('WSIS', axis = 1, inplace = True)
    if 'Proj. Pts' in data.columns:
        data.drop('Proj. Pts', axis = 1, inplace = True)
    
    if this_week == 0:
        data.columns = (['Rank','Player Name','Position','Best Rank',
                        'Worst Rank','Avg Rank','Std Dev'])
    elif this_week > 0 and position == 'FLX':
        data.columns = (['Rank','Player Name','Position','Matchup',
                         'Best Rank','Worst Rank','Avg Rank','Std Dev'])
    else:
        data.columns = (['Rank','Player Name','Matchup','Best Rank',
                         'Worst Rank','Avg Rank','Std Dev'])
    
    data['Player Name'] = data['Player Name'].str.replace('\\|.*','').astype(str)
    data = data[0:num_players]
    
    # perform clustering
    
    # set plot properties based on how many players need to be displayed
    big_font = ['QB','K','DST','TE-STD','TE-HALF','TE-PPR']
    small_font = ['RB-STD','RB-PPR','RB-HALF']
    tiny_font = (['WR-STD','FLX-STD','WR-PPR','FLX-PPR','WR-HALF','FLX-HALF',
                 'ALL','ALL-PPR','ALL-HALF-PPR'])
    
    if pos_scoring in big_font:
        marker_size = 6
        font_size   = 6
        ticks       = np.arange(0,num_players+1,5)
        ticks[0]    = 1
    elif pos_scoring in small_font:
        marker_size = 5
        font_size   = 6
        ticks       = np.arange(0,num_players+1,10)
        ticks[0]    = 1
    elif pos_scoring in tiny_font:
        marker_size = 5
        font_size   = 5
        ticks       = np.arange(0,num_players+1,15)
        ticks[0]    = 1
    else:
        marker_size = 5
        font_size   = 6
        ticks       = np.arange(0,num_players+1,10)
        ticks[0]    = 1
    
    # set plot properties for each player
    fig = plt.figure()
    fig.set_size_inches(5.8, 7)
    plt.rcParams['font.sans-serif'] = "Arial"
    plt.rcParams['font.family'] = "sans-serif"
    
    for index, player in data.iterrows():
        plt.errorbar(player['Avg Rank'], player['Rank'], xerr=player['Std Dev'],
                     ls='none', elinewidth=2.5, marker='.', markersize=marker_size,
                     color='black', ecolor='red', alpha=0.4,
                     )
        plt.text(player['Avg Rank'] - player['Std Dev'] - 1, player['Rank'], 
                 player['Player Name'], size=font_size, ha="right",
                 va="center")
    
    # set plot properties
    plt.xlabel('Average Expert Rank',fontsize=7)
    plt.ylabel('Expert Consensus Rank',fontsize=7)
    
    if pos_scoring in big_font:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])/2 -2,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+3])
    elif pos_scoring in small_font:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])/1.5,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+2])
    elif pos_scoring in tiny_font:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])-2,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+2])
    else:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])/1.5,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+2])
    
    
    plt.xlim(xlimit)
    
    plt.xticks(ticks,fontsize=7)
    plt.yticks(ticks,fontsize=7)
    
    current_time = datetime.today()
    current_time = current_time.strftime("%A %b %d %Y %H:%M EST")
    title = ('Week ' + str(this_week) + ': ' + pos_scoring + " Tiers - " 
             + current_time)
    plt.title(title,fontsize=7)
    
    plt.gca().invert_yaxis()
    
    # save figure
    plot_file_path = ("out/week" + str(this_week) + "/png/week-" + 
                      str(this_week) + "-" + pos_scoring + '.png')
    plt.savefig(plot_file_path, dpi=300)
                      
    
    


