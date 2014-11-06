'''
Reads in files scraped from projection sites and converts them to compact and
    usable dataframes/csvs.
'''
import pandas as pd
import requests
import simplejson as json

def get_numberfire(url_text_file='numberfire_url.txt'):
    '''
    Scrapes projections from numberfire, processes the dataframes properly,
        and returns them. (offense, kicker, defense)
    '''
    # get urls from text file
    with open(url_text_file) as rf:
        url_offense = rf.readline().strip('\n')
        url_kickers = rf.readline().strip('\n')
        url_defense = rf.readline().strip('\n')

    # request from urls, convert responses to dataframes
    oresponse = requests.get(url_offense)
    odf = pd.DataFrame(oresponse.json()['results'])
    kresponse = requests.get(url_kickers)
    kdf = pd.DataFrame(kresponse.json()['results'])
    dresponse = requests.get(url_defense)
    ddf = pd.DataFrame(dresponse.json()['results'])

    # clean dataframes, standardize formats and column names
    odf = _standard_numberfire_processing(odf)
    kdf = _standard_numberfire_processing(kdf)
    ddf = _standard_numberfire_processing(ddf)

    o_drops = ['rank', 'rank_number', 'ovr_number']
    o_column_map = {'att_number': 'rush_attempts',
                  'ints_number': 'interceptions',
                  'rec_number': 'receptions',
                  'tds_number': 'pass_tds',
                  'tds_number_2': 'rush_tds',
                  'tds_number_3': 'receiving_tds',
                  'yds_number': 'passing_yards',
                  'yds_number_2': 'rushing_yards',
                  'yds_number_3': 'receiving_yards'}

    k_drops = ['ci', 'ci_number', 'def_rank', 'def_rank_number', 'ovr_number']
    k_column_map = {'col_019_number': 'fgm_0_19',
                    'col_2029_number': 'fgm_20_29',
                    'col_3039_number': 'fgm_30_39',
                    'col_4049_number': 'fgm_40_49',
                    'col_50_number': 'fgm_50+',
                    'fga_number': 'fga',
                    'fgm_number': 'fgm',
                    'xpm_number': 'xpm'}

    d_drops = ['ci', 'ci_number']
    d_column_map = {'fumbles_number': 'fumbles',
                    'ints_number': 'interceptions',
                    'points_allowed_number': 'points_allowed',
                    'sacks_number': 'sacks',
                    'tds_number': 'tds',
                    'yards_allowed_number': 'yards_allowed'}

    odf = odf.drop(o_drops, axis=1)
    odf = odf.rename(columns = o_column_map)
    odf['name'] = odf['name'].apply(lambda x: x.lower())
    kdf = kdf.drop(k_drops, axis=1)
    kdf = kdf.rename(columns = k_column_map)
    kdf['name'] = kdf['name'].apply(lambda x: x.lower())
    ddf = ddf.drop(d_drops, axis=1)
    ddf = ddf.rename(columns = d_column_map)
    ddf['name'] = ddf['name'].apply(lambda x: x.lower())

    return odf.reset_index(), kdf.reset_index(), ddf.reset_index()

def _standard_numberfire_processing(df):
    source_drops = [c for c in df.columns if '/_source' in c]
    df['name'] = df['player_link/_text'].apply(lambda x: \
                    x.split('(')[0].strip())
    df['position'] = df['player_link/_text'].apply(lambda x: \
                        x.split('(')[1].split(',')[0])
    df['team'] = df['player_link/_text'].apply(lambda x: \
                    x.split(',')[1].strip().strip(')'))
    extra_drops = ['fp_number', 'pos_number', 'player_link',
                   'player_link/_title', 'player_link/_text']
    return df.drop(source_drops + extra_drops, axis=1)

def get_salaries_rotowire(url_text_file='salary_scrape.txt'):
    '''
    Scrapes salaries from rotowire, returns df of nothing more than name and
        salary. But doesn't have Defense. Harumph.
    '''
    with open(url_text_file) as rf:
        url_fanduel = rf.readline().strip('\n')

    fresponse = requests.get(url_fanduel)
    fdf = pd.DataFrame(fresponse.json()['results'])
    basics = fdf[['player_name_link/_text', 'salary_currency']]
    basics['name'] = basics['player_name_link/_text'].apply(_correct_name)
    basics = basics.drop('player_name_link/_text', axis=1)
    basics = basics.rename(columns = {'salary_currency': 'salary'})

    return basics

def _correct_name(s):
    n = s.split(', ')
    return n[1].lower() + ' ' + n[0].lower()

def direct_json_scrape_fanduel(url):
    '''
    For url, just input a simple url of a currently-running contest. Make sure
        to be logged in, I guess?
    '''
    r = requests.get(url)
    s = r.content
    start = s.find('FD.playerpicker.allPlayersFullData') + 37
    end = s.find('}', start) + 1
    j = s[start:end]
    d = json.loads(j)
    name_salary_o = [(v[0], v[1].lower(), float(v[5])) for k,v in d.iteritems() \
                     if v[0] != 'D']
    name_salary_d = [(v[0], ' '.join(v[1].lower().split()[:-1]) + ' d/st', \
                     float(v[5])) for k,v in d.iteritems() if v[0] == 'D']

    df = pd.DataFrame(name_salary_o + name_salary_d)
    df.columns = ['position', 'name', 'salary']
    return df.reset_index()
