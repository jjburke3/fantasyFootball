
import sys
import requests
import base64
import time

sys.path.insert(0,'..')
sys.path.insert(0,'..\..')
sys.path.insert(0,'../../dbConn')

from security import MSF_CRED
from dbFuncs import *

username = MSF_CRED['key']
password = MSF_CRED['pass2']

def attemptStat(stat,obj):
    try:
        return int(obj[stat]['#text'])
    except:
        return 0


def returnWeekStats(conn,
                    week,
                    year,
                    week_range="from-5-days-ago-to-today"):
    teams = getTeamId(conn)
    players = getPlayerId(year,conn,stats=True)
    sql = InsertTable("scrapped_data2.playerStats")
    deleteSql = ''' delete from scrapped_data2.playerStats where
                    statYear = %s and statWeek = %s ''' % (str(year),str(week))
    
    season = str(year)+"-regular"
    params = {}
    
    headers = {'Authorization' : ('Basic ' +
                                  base64.b64encode('{}:{}'.format(username,password).encode('utf-8')).decode('ascii')
                )}
    url = "https://api.mysportsfeeds.com/v2.1/pull/nfl/%s/week/%s/player_gamelogs.json"
    teamUrl = "https://api.mysportsfeeds.com/v2.1/pull/nfl/%s/week/%s/team_gamelogs.json"
    for i in range(48,80,8):
        print(year,week,i)
        params['team'] = str(i)
        for j in range(1,8):
            params['team'] += "," + str(i+j)
        status = True
        while status:
            r = requests.get(url % (season,str(week)),
                             params=params,
                             headers=headers)
            print('players',r)
            if r.status_code != 200:
                time.sleep(10)
            else:
                status = False
        try:
            output = r.json()
            for player in output['gamelogs']:
                try:
                    sportsFeedsId = player['player']['id']
                    name = player['player']['firstName'] + " " + player['player']['lastName']
                    name = name.replace("'","\\'")
                    team = player['team']['abbreviation']
                    pos = player['player']['position']
                    obj = player['stats']
                    games = 1
                    if 'passing' in obj:
                        comp = obj['passing']['passCompletions']
                        attempt = obj['passing']['passAttempts']
                        passYard = obj['passing']['passYards']
                        passTd = obj['passing']['passTD']
                        passInt = obj['passing']['passInt']
                        passTD40bonus = obj['passing']['pass40Plus']
                    else:
                        comp = 0
                        attempt = 0
                        passYard = 0
                        passTd = 0
                        passInt = 0
                        passTD40bonus = 0
                    if 'rushing' in obj:
                        rushAtt = obj['rushing']['rushAttempts']
                        rushYard = obj['rushing']['rushYards']
                        rushTD = obj['rushing']['rushTD']
                        rushTD40bonus = obj['rushing']['rush40Plus']
                    else:
                        rushAtt = 0
                        rushYard = 0
                        rushTD = 0
                        rushTD40bonus = 0
                    if 'receiving' in obj:
                        target = obj['receiving']['targets']
                        recept = obj['receiving']['receptions']
                        receivYard = obj['receiving']['recYards']
                        receivTD = obj['receiving']['recTD']
                        receivTD40bonus = obj['receiving']['rec40Plus']
                    else:
                        target = 0
                        recept = 0
                        receivYard = 0
                        receivTD = 0
                        receivTD40bonus = 0
                    if 'fumble' in obj:
                        fumble = obj['fumbles']['fumbles']
                        fumbleLoss = obj['fumbles']['fumLost']
                    else:
                        fumble = 0
                        fumbleLoss = 0
                    if 'fieldGoals' in obj:
                        fgMade = obj['fieldGoals']['fgMade']
                        fgAttmpt = obj['fieldGoals']['fgAtt']
                        fg40_49made = obj['fieldGoals']['fgMade40_49']
                        fg40_49miss = obj['fieldGoals']['fgAtt40_49'] - obj['fieldGoals']['fgMade40_49']
                        fg50made = obj['fieldGoals']['fgMade50Plus']
                        fg50miss = obj['fieldGoals']['fgAtt50Plus'] - obj['fieldGoals']['fgMade50Plus']
                    else:
                        fgMade = 0
                        fgAttmpt = 0
                        fg40_49made = 0
                        fg40_49miss = 0
                        fg50made = 0
                        fg50miss = 0
                    if 'extraPointAttempts' in obj:
                        xPointMade = obj['extraPointAttempts']['xpMade']
                        xPointAttmpt = obj['extraPointAttempts']['xpAtt']
                    else:
                        xPointMade = 0
                        xPointAttmpt = 0
                    defSack = "null"
                    qbHit = "null"
                    forceFumble = "null"
                    fumbleRecov = "null"
                    defInt = "null"
                    passDef = "null"
                    defTD = "null"
                    fumbleTD = "null"
                    intTD = "null"
                    if 'kickoffReturns' in obj:
                        kickTD = obj['kickoffReturns']['krTD']
                    else:
                        kickTD - 0
                    if 'puntReturns' in obj:
                        puntTD = obj['puntReturns']['prTD']
                    else:
                        puntTD
                    pointsAgainst = "null"
                    defPassYards = "null"
                    defRunYards = "null"
                    safety = "null"
                    blockkick = "null"
                    blockTD = "null"
                    if pos in ['QB','RB','WR','TE','K','RB/WR','WR/TE','TE/WR','WR/RB']:
                        

                        teamId = teams.teamId(team,conn)
                        playerId = players.playerId([
                                    name,
                                    str(teamId),
                                    pos,
                                    str(year)],
                                    conn,
                                    statsId = sportsFeedsId
                                    )
                        sql.appendRow([
                                [str(year),''],
                                [str(week),''],
                                [str(playerId),''],
                                [pos,'string'],
                                [str(teamId),''],
                                [str(games),''],
                                [str(comp),''],
                                [str(attempt),''],
                                [str(passYard),''],
                                [str(passTd),''],
                                [str(passInt),''],
                                [str(passTD40bonus),''],
                                [str(rushAtt),''],
                                [str(rushYard),''],
                                [str(rushTD),''],
                                [str(rushTD40bonus),''],
                                [str(target),''],
                                [str(recept),''],
                                [str(receivYard),''],
                                [str(receivTD),''],
                                [str(receivTD40bonus),''],
                                [str(fumble),''],
                                [str(fumbleLoss),''],
                                [str(fgMade),''],
                                [str(fgAttmpt),''],
                                [str(xPointMade),''],
                                [str(xPointAttmpt),''],
                                [str(fg40_49made),''],
                                [str(fg40_49miss),''],
                                [str(fg50made),''],
                                [str(fg50miss),''],
                                [str(defSack),''],
                                [str(qbHit),''],
                                [str(forceFumble),''],
                                [str(fumbleRecov),''],
                                [str(defInt),''],
                                [str(passDef),''],
                                [str(defTD),''],
                                [str(fumbleTD),''],
                                [str(intTD),''],
                                [str(puntTD),''],
                                [str(kickTD),''],
                                [str(pointsAgainst),''],
                                [str(defPassYards),''],
                                [str(defRunYards),''],
                                [str(safety),''],
                                [str(blockkick),''],
                                [str(blockTD),''],
                                ["null",""],
                                ["null",""],
                                ["null",""],
                                ["null",""],
                                ["null",""],
                                ["null",""],
                                ["null",""],
                                ["null",""],
                                ["current_timestamp()",""]
                            ])
                except Exception as e:
                    print(str(e))
            time.sleep(0)
        except Exception as e:
            print(str(e))
        status = True
        while status:
            
            r2 = requests.get(teamUrl % (season,str(week)),
                         params=params,
                         headers=headers)
            print('teams',r2)
            if r2.status_code != 200:
                time.sleep(10)
            else:
                status = False  
        try:
            output = r2.json()
            references = output['references']
            for teamData in output['gamelogs']:
                teamReference = [d for d in references['teamReferences'] if d['id'] == teamData['team']['id']][0]
                name = (teamReference['name'] + " D/ST")
                team = teamData['team']['abbreviation']
                pos = 'D/ST'
                obj = teamData['stats']
                games = 1
                defSack = obj['tackles']['sacks']
                qbHit = "NULL"
                forceFumble = obj['fumbles']['fumForced']
                fumbleRecov = obj['fumbles']['fumOppRec']
                defInt = obj['interceptions']['interceptions']
                passDef = obj['interceptions']['passesDefended']
                defTD = (obj['interceptions']['intTD'] +
                         obj['fumbles']['fumTD'])
                fumbleTD = obj['fumbles']['fumTD']
                intTD = obj['interceptions']['intTD']
                puntTD = obj['puntReturns']['prTD']
                kickTD = obj['kickoffReturns']['krTD']
                pointsAgainst = obj['standings']['pointsAgainst']
                defPassYards = "NULL"
                defRunYards = "NULL"
                safety = obj['interceptions']['safeties']
                blockkick = obj['interceptions']['kB']
                blockTD = "NULL"

                teamId = teams.teamId(team,conn)
                playerId = players.playerId([
                            name,
                            str(teamId),
                            pos,
                            str(year)],
                            conn,
                            statsId = teamReference['id']
                            )

                sql.appendRow([
                    [str(year),''],
                    [str(week),''],
                    [str(playerId),''],
                    [pos,'string'],
                    [str(teamId),''],
                    [str(games),''],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    [str(defSack),""],
                    [str(qbHit),""],
                    [str(forceFumble),""],
                    [str(fumbleRecov),""],
                    [str(defInt),""],
                    [str(passDef),""],
                    [str(defTD),""],
                    [str(fumbleTD),""],
                    [str(intTD),""],
                    [str(puntTD),""],
                    [str(kickTD),""],
                    [str(pointsAgainst),""],
                    [str(defPassYards),""],
                    [str(defRunYards),""],
                    [str(safety),""],
                    [str(blockkick),""],
                    [str(blockTD),""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["null",""],
                    ["current_timestamp()",""]                    
                    ])


            time.sleep(0)
        except Exception as e:
            print(str(e))

    return [deleteSql, sql.returnStatement()]
    


