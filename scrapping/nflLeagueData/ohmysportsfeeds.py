
import sys
import requests
import base64
import time

sys.path.insert(0,'../..')

from security import MSF_CRED

username = MSF_CRED['key']
password = MSF_CRED['pass']

def attemptStat(stat,obj):
    try:
        return int(obj[stat]['#text'])
    except:
        return 0


def returnWeekStats(week,year=2019,week_range="from-5-days-ago-to-today"):
    sql = "insert into scrapped_data.playerStats values "
    
    season = str(year)+"-regular"
    params = {'date':week_range}
    
    headers = {'Authorization' : ('Basic ' +
                                  base64.b64encode('{}:{}'.format(username,password).encode('utf-8')).decode('ascii')
                )}
    url = "https://api.mysportsfeeds.com/v1.2/pull/nfl/%s/player_gamelogs.json"
    teamUrl = "https://api.mysportsfeeds.com/v1.2/pull/nfl/%s/team_gamelogs.json"

    for i in range(48,80,4):
        print(year,week,i)
        params['team'] = str(i)
        for j in range(1,4):
            params['team'] += "," + str(i+j)
        status = True
        while status:
            r = requests.get(url % season,
                         params=params,
                         headers=headers)
            print('players',r)
            if r.status_code != 200:
                time.sleep(10)
            else:
                status = False
        try:
            output = r.json()
            for player in output['playergamelogs']['gamelogs']:
                name = player['player']['FirstName'] + " " + player['player']['LastName']
                team = player['team']['Abbreviation']
                pos = player['player']['Position']
                obj = player['stats']
                games = 1
                comp = attemptStat("PassCompletions",obj)
                attempt = attemptStat("PassAttempts",obj)
                passYard = attemptStat("PassYards",obj)
                passTd = attemptStat("PassTD",obj)
                passInt = attemptStat("PassInt",obj)
                passTD40bonus = attemptStat("Pass40Plus",obj)
                rushAtt = attemptStat("RushAttempts",obj)
                rushYard = attemptStat("RushYards",obj)
                rushTD = attemptStat("RushTD",obj)
                rushTD40bonus = attemptStat("Rush40Plus",obj)
                target = attemptStat("Targets",obj)
                recept = attemptStat("Receptions",obj)
                receivYard = attemptStat("RecYards",obj)
                receivTD = attemptStat("RecTD",obj)
                receivTD40bonus = attemptStat("Rec40Plus",obj)
                fumble = attemptStat("Fumbles",obj)
                fumbleLoss = attemptStat("FumLost",obj)
                fgMade = attemptStat("FgMade",obj)
                fgAttmpt = attemptStat("FgAtt",obj)
                xPointMade = attemptStat("XpMade",obj)
                xPointAttmpt = attemptStat("XpAtt",obj)
                fg40_49made = attemptStat("FgMade40_49",obj)
                fg40_49miss = attemptStat("FgAtt40_49",obj) - attemptStat("FgMade40_49",obj)
                fg50made = attemptStat("FgMade50Plus",obj)
                fg50miss = attemptStat("FgAtt50Plus",obj) - attemptStat("FgMade50Plus",obj)
                defSack = "null"
                qbHit = "null"
                forceFumble = "null"
                fumbleRecov = "null"
                defInt = "null"
                passDef = "null"
                defTD = "null"
                fumbleTD = "null"
                intTD = "null"
                puntTD = attemptStat("PrTD",obj)
                kickTD = attemptStat("KrTD",obj)
                pointsAgainst = "null"
                defPassYards = "null"
                defRunYards = "null"
                safety = "null"
                blockkick = "null"
                blockTD = "null"
                if pos in ['QB','RB','WR','TE','K','RB/WR','WR/TE','TE/WR','WR/RB']:
                    sql += ("( " +
                            str(year) + "," +
                            str(week) + "," +
                            "'" + name.replace("'","_") + "'," +
                            "'" + pos + "'," +
                            "'" + team + "'," +
                            str(games) + "," +
                            str(comp) + "," +
                            str(attempt) + "," +
                            str(passYard) + "," +
                            str(passTd) + "," +
                            str(passInt) + "," +
                            str(passTD40bonus) + "," +
                            str(rushAtt) + "," +
                            str(rushYard) + "," +
                            str(rushTD) + "," +
                            str(rushTD40bonus) + "," +
                            str(target) + "," +
                            str(recept) + "," +
                            str(receivYard) + "," +
                            str(receivTD) + "," +
                            str(receivTD40bonus) + "," +
                            str(fumble) + "," +
                            str(fumbleLoss) + "," +
                            str(fgMade) + "," +
                            str(fgAttmpt) + "," +
                            str(xPointMade) + "," +
                            str(xPointAttmpt) + "," +
                            str(fg40_49made) + "," +
                            str(fg40_49miss) + "," +
                            str(fg50made) + "," +
                            str(fg50miss) + "," +
                            str(defSack) + "," +
                            str(qbHit) + "," +
                            str(forceFumble) + "," +
                            str(fumbleRecov) + "," +
                            str(defInt) + "," +
                            str(passDef) + "," +
                            str(defTD) + "," +
                            str(fumbleTD) + "," +
                            str(intTD) + "," +
                            str(puntTD) + "," +
                            str(kickTD) + "," +
                            str(pointsAgainst) + "," +
                            str(defPassYards) + "," +
                            str(defRunYards) + "," +
                            str(safety) + "," +
                            str(blockkick) + "," +
                            str(blockTD) + "," +
                            "null,null,null,null,null,null,null,null,current_timestamp() " +
                            "),")
            time.sleep(10)
        except Exception as e:
            None
        status = True
        while status:
            
            r2 = requests.get(teamUrl % season,
                         params=params,
                         headers=headers)
            print('teams',r2)
            if r2.status_code != 200:
                time.sleep(10)
            else:
                status = False  
        try:
            output = r2.json()
            for teamData in output['teamgamelogs']['gamelogs']:
                name = teamData['team']['Name'] + " D/ST"
                team = teamData['team']['Abbreviation']
                pos = 'D/ST'
                obj = teamData['stats']
                games = 1
                defSack = attemptStat("Sacks",obj)
                qbHit = attemptStat("",obj)
                forceFumble = attemptStat("FumForced",obj)
                fumbleRecov = attemptStat("FumOppRec",obj)
                defInt = attemptStat("Interceptions",obj)
                passDef = attemptStat("PassesDefended",obj)
                defTD = attemptStat("FumTD",obj)+attemptStat("IntTD",obj)
                fumbleTD = attemptStat("FumTD",obj)
                intTD = attemptStat("IntTD",obj)
                puntTD = attemptStat("PrTD",obj)
                kickTD = attemptStat("KrTD",obj)
                pointsAgainst = attemptStat("PointsAgainst",obj)
                defPassYards = attemptStat("",obj)
                defRunYards = attemptStat("",obj)
                safety = attemptStat("Safeties",obj)
                blockkick = attemptStat("PuntBlk",obj)+attemptStat("FgBlk",obj)+attemptStat("XpBlk",obj)
                blockTD = 0

                sql += ("( " +
                        str(year) + "," +
                        str(week) + "," +
                        "'" + name.replace("'","_") + "'," +
                        "'" + pos + "'," +
                        "'" + team + "'," +
                        str(games) + "," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        "null," +
                        str(defSack) + "," +
                        str(qbHit) + "," +
                        str(forceFumble) + "," +
                        str(fumbleRecov) + "," +
                        str(defInt) + "," +
                        str(passDef) + "," +
                        str(defTD) + "," +
                        str(fumbleTD) + "," +
                        str(intTD) + "," +
                        str(puntTD) + "," +
                        str(kickTD) + "," +
                        str(pointsAgainst) + "," +
                        str(defPassYards) + "," +
                        str(defRunYards) + "," +
                        str(safety) + "," +
                        str(blockkick) + "," +
                        str(blockTD) + "," +
                        "null,null,null,null,null,null,null,null,current_timestamp() " +
                        "),")
            time.sleep(10)
        except Exception as e:
            print(str(e))

    return sql[:-1]
    


