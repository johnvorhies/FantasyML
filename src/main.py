#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 17:12:02 2020

@author: johnvorhies
"""

#--------------- TO-DO -----------------
#   * Call main from command line w/ args?
#   * Should main make the dat, out folders?
#---------------------------------------

from fantasyml import downloadData as dl
from fantasyml import drawTiers
import os

download = True
week = 13

os.chdir('../') 

if download == True:
    dl(['qb','k','dst'], scoring = 'STD', this_week = week)
    if week == 0:
        dl(['rb','wr','te'], scoring = 'STD', this_week = week)
        dl(['rb','wr','te'], scoring = 'PPR', this_week = week)
        dl(['rb','wr','te'], scoring = 'HALF', this_week = week)
    elif (week > 0):
        dl(['flx','rb','wr','te'], scoring = 'STD', this_week = week)
        dl(['flx','rb','wr','te'], scoring = 'PPR', this_week = week)
        dl(['flx','rb','wr','te'], scoring = 'HALF', this_week = week)

drawTiers(position='qb',  num_players=26, tiers=5, this_week = week)
drawTiers(position='rb',  num_players=40, tiers=7,  scoring='STD', this_week = week) 
drawTiers(position='wr',  num_players=60, tiers=8, scoring='STD', this_week = week)
drawTiers(position='te',  num_players=24, tiers=5,  scoring='STD', this_week = week)
drawTiers(position='k',   num_players=20, tiers=5, this_week = week)
drawTiers(position='dst', num_players=20, tiers=6, this_week = week)

drawTiers(position='rb', num_players=40, tiers=7, scoring='PPR', this_week = week)
drawTiers(position='wr', num_players=60, tiers=8, scoring='PPR', this_week = week)
drawTiers(position='te', num_players=25, tiers=5,  scoring='PPR', this_week = week)

drawTiers(position='rb', num_players=40, tiers=7,  scoring='HALF', this_week = week)
drawTiers(position='wr', num_players=60, tiers=8, scoring='HALF', this_week = week)
drawTiers(position='te', num_players=25, tiers=5,  scoring='HALF', this_week = week)

if week > 0:
	drawTiers(position='flx', num_players=75, tiers=9, scoring='STD', this_week = week)
	drawTiers(position='flx', num_players=75, tiers=9, scoring='PPR', this_week = week)
	drawTiers(position='flx', num_players=75, tiers=9, scoring='HALF', this_week = week)
 