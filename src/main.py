#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 17:12:02 2020

@author: johnvorhies
"""

#--------------- TO-DO -----------------
#   * Re-define fp_dl.py in FantasyML as functions
#   * Re-name as fantasyml
#   * How to pass this_week to all functions
#   * Implement clustering
#   * Call main from command line w/ args?
#---------------------------------------

from FantasyML_Functions import downloadData as dl
from FantasyML_Functions import drawTiers
import os

download = False
this_week = 4

os.chdir('../') 

if download == True:
    dl(['qb','k','dst'])
    if this_week == 0:
        dl(['rb','wr','te'], scoring = 'STD')
        dl(['rb','wr','te'], scoring = 'PPR')
        dl(['rb','wr','te'], scoring = 'HALF')
    elif (this_week > 0):
        dl(['flx','rb','wr','te'], scoring = 'STD')
        dl(['flx','rb','wr','te'], scoring = 'PPR')
        dl(['flx','rb','wr','te'], scoring = 'HALF')

drawTiers(position='qb',  num_players=26, tiers=8)
drawTiers(position='rb',  num_players=40, tiers=9,  scoring='STD') 
drawTiers(position='wr',  num_players=60, tiers=12, scoring='STD')
drawTiers(position='te',  num_players=24, tiers=8,  scoring='STD')
drawTiers(position='k',   num_players=20, tiers=5)
drawTiers(position='dst', num_players=20, tiers=6)

drawTiers(position='rb', num_players=40, tiers=10, scoring='PPR')
drawTiers(position='wr', num_players=60, tiers=12, scoring='PPR')
drawTiers(position='te', num_players=25, tiers=8,  scoring='PPR')

drawTiers(position='rb', num_players=40, tiers=9,  scoring='HALF')
drawTiers(position='wr', num_players=60, tiers=10, scoring='HALF')
drawTiers(position='te', num_players=25, tiers=7,  scoring='HALF')

if this_week > 0:
	drawTiers(position='flx', num_players=90, tiers=14, scoring='STD')
	drawTiers(position='flx', num_players=90, tiers=14, scoring='PPR')
	drawTiers(position='flx', num_players=90, tiers=15, scoring='HALF')
 