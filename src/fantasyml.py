#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 14:53:03 2020

@author: johnvorhies
"""

from bs4 import BeautifulSoup
from datetime import datetime
from lxml import html
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.pyplot import cm
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import re
import requests
from sklearn.cluster import KMeans


style.use("ggplot")

def convertXlsToCsv(infile, outfile):
    # Open xls file, parse headings and format each row, write to csv
    file = open(infile, 'r') 
    text = file.read() 
    soup = BeautifulSoup(text,features="html.parser")
    
    scripts = soup.findAll('script')
    pattern = re.compile('var ecrData = {(.*?)};')
    for script in scripts:
        if (pattern.search(str(script.string))):
            ecrData_found = True
            ecrData = pattern.search(script.string)
            pattern = re.compile('{\"player_id\":(.*?)}')
            data = pattern.findall(ecrData[1])
            
            fout = open(outfile, 'w')
            fout.write('Rank,Player Name,Avg Rank,Std Dev\n')
            for player in range(len(data)):
                pattern = re.compile('\"rank_ecr\":(.*?),')
                rank_ecr = pattern.findall(data[player])
                fout.write(rank_ecr[0] + ',')
                
                if "DST" in outfile:
                    data[player] = '\"player_name\":' + data[player]
                    pattern = re.compile('\"player_name\":\"(.*?)\"')
                else:
                    pattern = re.compile('\"player_short_name\":\"(.*?)\"')
                player_name = pattern.findall(data[player])
                fout.write(player_name[0] + ',')
                
                pattern = re.compile('\"rank_ave\":\"(.*?)\"')
                rank_ave = pattern.findall(data[player])
                fout.write(rank_ave[0] + ',')
                
                pattern = re.compile('\"rank_std\":\"(.*?)\"')
                rank_std = pattern.findall(data[player])
                fout.write(rank_std[0] + '\n')
                
    if (not ecrData_found):
        print("No data found in " + str(infile))
        return
    else:
        fout.close()
    return

def performSessionDownload(args, url, xls_file_name):
    """
    creates a session that allows the user to log in to FantasyPros and use the tokens
    :param args: list of parameters can be used to get data directories
    :param url: string of the export xls url
    :param xls_file_name: string of the full file path and name of file to be saved
    """
    # get payload values from command line parameters
    username, password, token = args['username'], args['password'], args['token']
    payload = {"username": username,
               "password": password,
               "csrfmiddlewaretoken": token}
    # start session
    print("Starting download session...")
    session_requests = requests.session()
    login_url = "https://secure.fantasypros.com/accounts/login/?"
    result = session_requests.get(login_url)
    # refresh token on new request
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]
    payload["csrfmiddlewaretoken"] = authenticity_token
    session_requests.post(login_url,
                          data=payload,
                          headers=dict(referer=login_url))
    # prepare to write data to file
    #logger.debug("Opening xls file to write data...")
    with open(xls_file_name, 'wb') as handle:
        response = session_requests.get(url)
        if not response.ok:
            print("Writing to xls failed...")
        for block in response.iter_content(1024):
            handle.write(block)

def downloadData(pos_list = ['rb','wr','te','flx'], scoring = 'STD', this_week = 1):
    exp_filter = '22:64:113:120:125:127:317:406:534'
    for mp in pos_list:
        position = mp.upper()
        
        if scoring == 'HALF':
            if position == 'FLX':
                pos_url = 'half-point-ppr-flex'
            else:
                pos_url = 'half-point-ppr-' + mp
        elif scoring == 'PPR':
            if position == 'FLX':
                pos_url = 'ppr-flex'
            else:
                pos_url = 'ppr-' + mp
        else:
            pos_url = mp
            
        url = ('https://www.fantasypros.com/nfl/rankings/' + pos_url +
                '.php?filters=' + exp_filter + '\\&week=' + str(this_week) +
                '\\&export=xls')
        
        head_dir = 'dat/2020/week-'
        if scoring == 'STD':
            pos_scoring = position
        else: 
            pos_scoring = position + '-' + scoring
        
        xls_dest = head_dir + str(this_week) + '-' + pos_scoring + '-raw.xls'
        csv_dest = head_dir + str(this_week) + '-' + pos_scoring + '-raw.csv'
        
        print('url: ' + url)
        print('raw_csv_dest: ' + xls_dest)
        print('csv_dest: ' +  csv_dest)
        
        userargs = {'username':'borischen003', 'password':'borischen1', 'token':'1'}
        performSessionDownload(userargs, url, xls_dest)
        convertXlsToCsv(xls_dest, csv_dest)
        
       
        
def drawTiers(position='qb', num_players=20, tiers=3, scoring='STD', this_week = 1):
    # import csv
    position = position.upper()
    
    if scoring == 'STD':
        pos_scoring = position
    else: 
        pos_scoring = position + '-' + scoring
        
    head_dir = 'dat/2020/week-'
    csv_path = head_dir + str(this_week) + '-' + pos_scoring + '-raw.csv'
    data = pd.read_csv(csv_path)
    
    data.columns = (['Rank', 'Player Name', 'Avg Rank', 'Std Dev'])
    data = data[0:num_players]
    
    # perform clustering
    X = np.array(data['Avg Rank'])
    X = X.reshape(-1,1)
    kmeans = KMeans(n_clusters=tiers)
    kmeans.fit(X)
    # sort labels and generate colormap
    idx = np.argsort(kmeans.cluster_centers_.sum(axis=1))
    lut = np.zeros_like(idx)
    lut[idx] = np.arange(tiers)
    labels = lut[kmeans.labels_]
    colors = []
    color_cycle = iter(cm.gist_rainbow(np.linspace(0, 1, tiers)))
    for i in range(tiers):
        c = next(color_cycle)
        colors.append(c)
    
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
                     color='Black', ecolor=colors[labels[index]], alpha=0.8,
                     )
        plt.text(player['Avg Rank'] - player['Std Dev'] - 1, player['Rank'], 
                 player['Player Name'], size=font_size, ha="right",
                 va="center")
    
    # set plot properties
    plt.xlabel('Average Expert Rank',fontsize=7)
    plt.ylabel('Expert Consensus Rank',fontsize=7)
    
    tier_patch = []
    for i in range(tiers):
        tier_label = "Tier " + str(i+1)
        patch = mpatches.Patch(color=colors[i], linewidth=3, label=tier_label)
        tier_patch.append(patch)
    
    plt.legend(handles=tier_patch,fontsize=8)
    
    if pos_scoring in big_font:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])/2 -2,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+3])
    elif pos_scoring in small_font:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])/1.5 - 2,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+4])
    elif pos_scoring in tiny_font:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])-3,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+4])
    else:
        xlimit = ([data.iloc[0].loc['Avg Rank']-data.iloc[0].loc['Std Dev'] - 
                   len(data.iloc[0].loc['Player Name'])/1.5 - 2,
                   data.iloc[num_players-1].loc['Avg Rank']+
                   data.iloc[num_players-1].loc['Std Dev']+4])
    
    
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
                      
    
    


