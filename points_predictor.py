'''
FanDuel Scoring rules:
Scoring Categories
Offense:
Rushing yards made = 0.1pts
Rushing touchdowns = 6pts
Passing yards = 0.04pts
Passing touchdowns = 4pts
Interceptions = -1pt
Receiving yards = 0.1pts
Receiving touchdowns = 6pts
Receptions = 0.5pts
Kickoff return touchdowns = 6pts
Punt return touchdowns = 6pts
Fumbles lost = -2pts
Own fumbles recovered touchdowns = 6pts
Two-point conversions scored = 2pts
Two-point conversion passes = 2pts
Field-goals from 0-19 yards = 3pts
Field-goals from 20-29 yards = 3pts
Field-goals from 30-39 yards = 3pts
Field-goals from 40-49 yards = 4pts
Field-goals from 50+ yards = 5pts
Extra-point conversions = 1ptDefense:
Sacks = 1pt
Opponent-fumbles recovered = 2pts
Return touchdowns = 6pts
Fumble return touchdowns = 6pts
Safeties = 2pts
Blocked kicks = 2pts
Interceptions made = 2pts
Note: For purposes of FanDuel defensive scoring, points allowed are calculated as: 6 * (Rushing TD + Receiving TD + Own fumbles recovered for TD ) + 2 * (Two point conversions) + Extra points + 3 * (Field Goals)
'''
import pandas as pd

def fanduel_offense_points(odf):
    '''
    Converts an odf's statistical columns to predicted fantasy points and
        returns only the necessary columns.
    '''
    odf['points'] = odf['rushing_yards'] * .1 + odf['rush_tds'] * 6.0 + \
                    odf['passing_yards'] * .04 + odf['pass_tds'] * 4.0 + \
                    odf['interceptions'] * -1 + odf['receiving_yards'] * .1 + \
                    odf['receiving_tds'] * 6 + odf['receptions'] * .5
    return odf[['name', 'salary', 'points', 'position']]

def fanduel_kicker_points(kdf):
    '''
    Converts a kdf's statistical columns to predicted fantasy points and
        returns only the necessary columns.
    '''
    kdf['points'] = (kdf['fgm_0_19'] + kdf['fgm_20_29'] + kdf['fgm_30_39']) \
                    * 3 + kdf['fgm_40_49'] * 4 + kdf['fgm_50+'] * 5 + \
                    kdf['xpm']
    return kdf[['name', 'salary', 'points', 'position']]

def fanduel_defense_points(ddf):
    '''
    Converts a ddf's statistical columns to predicted fantasy points and
        returns only the necessary columns.
    '''
    ddf['mostpoints'] = ddf['fumbles'] * 2 + ddf['interceptions'] * 2 + \
                        ddf['tds'] * 6 + ddf['sacks']
    ddf['allowpoints'] = ddf['points_allowed'].apply(_points_allowed)
    ddf['points'] = ddf['mostpoints'] + ddf['allowpoints']
    return ddf[['name', 'salary', 'points', 'position']]

def _points_allowed(x):
    '''
    How many fantasy points a defense gets for allowing this many points.
    0 points allowed = 10pts
    1-6 points allowed = 7pts
    7-13 points allowed = 4pts
    14-20 points allowed = 1pt
    28-34 points allowed = -1pt
    35+ points allowed = -4pts
    '''
    if x == 0:
        return 10
    if x < 6.5:
        return 7
    if x < 13.5:
        return 4
    if x < 20.5:
        return 1
    if x < 34.5:
        return -1
    return -4
