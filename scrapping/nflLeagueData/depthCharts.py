#file results sql statement text string run in injuriesAndDepthCharts
import sys

import requests
import re
from bs4 import BeautifulSoup as bs, Comment
from requests.structures import CaseInsensitiveDict
sys.path.insert(0,'..')
sys.path.insert(0,'..\..')
sys.path.insert(0,'../../dbConn')

from dbFuncs import *

from references import fullName, pfrAbbrName, fullToMascot, abbrToMascot, teamLocation

fullName = CaseInsensitiveDict(fullName)
def remove_non_ascii(text):
    return re.sub(r'[^\x20-\x7E]',r'_',text)

def pullDepthCharts(conn,
                    season, week, day, time,
                    versionNo = 'NULL',
                    url = 'https://subscribers.footballguys.com/apps/depthchart.php',
                    timestamp = 'NULL'):
    teams = getTeamId(conn)
    players = getPlayerId(season,conn,depthChart=True)
    sql = InsertTable("scrapped_data2.depthCharts")
    deleteSql = ''' delete from scrapped_data2.depthCharts where
                chartSeason = %s and chartWeek = %s and
                chartDay = '%s' and chartTime = '%s' ''' % (season, week,day,time)
    
    params = {'type': 'noidp', 'lite':'no','exclude_coaches':'yes'}
    #url = 'https://subscribers.footballguys.com/apps/depthchart.php'
    
    r = requests.get(url)
    roles = {'brown' : 'Injury Replacement','red' : 'Injury Replacement', 'blue' : 'Starter', 'green': 'Situational', 'black' : 'Practice'}

    soup = bs(r.content, 'html.parser')
    tables = soup.find_all('td', {"class":"la","width" : "50%"})

    paren = re.compile(" \((.+)\)")
    
    for column in tables:
        teamRows = column.find_all("tr")
        teamName = ''
        for i, team in enumerate(teamRows):
            if i % 2 == 0:
                teamName = team.find("b").text
            else:
                children = team.find("td").findChildren()
                position = ''
                posRank = 0
                dcId = ''
                
                for child in children:
                    if child.name == "b":
                        position = child.text[:-1]
                        posRank = 0
                    elif child.name == "font" or (position=="Coaches" and child.name=="a"):
                        player = child.text
                        if len(player) > 65:
                            player = player[:65]
                        if child.name == "font" and child.parent.name=="a":
                            dcId = child.parent['href'].split("id=")[1]
                        else:
                            dcId = ''
                        injuryStatus = ''
                        tdb = 0
                        gl = 0
                        kr = 0
                        pr = 0
                        if position =="Coaches":
                            role = re.sub(': ','',re.sub(', ','',child.previousSibling))
                        elif child.name == "font":
                            extra = paren.search(player)
                            if extra:
                                extra = extra.group(1)
                                player = paren.sub('',player)
                            else:
                                extra = ''
                            try:
                                role = roles[child['color']]
                            except:
                                role = "None"
                            if re.match("IR",extra):
                                injuryStatus = 'IR'
                            elif re.match('inj',extra):
                                injuryStatus = 'Injured'
                            elif re.match('susp',extra):
                                injuryStatus = 'Suspended'
                            elif re.match('res',extra):
                                injuryStatus = 'Reserve'
                            elif re.match('PUP',extra):
                                injuryStatus = 'PUP'
                            if re.match("3RB",extra):
                                tdb = 1
                            if re.match("SD",extra):
                                gl = 1
                            if re.match("KR",extra):
                                kr = 1
                            if re.match("PR",extra):
                                pr = 1
                        teamId = teams.teamId(teamName,conn)
                        playerId = players.playerId([
                            remove_non_ascii(player).replace("'","\\'"),
                            str(teamId),
                            position,
                            str(season)],
                            conn,
                            depthChartId = dcId
                            )
                        sql.appendRow([
                            ['NULL',''],
                            [str(versionNo),''],
                            [str(season),''],
                            [str(week),''],
                            [str(day),'string'],
                            [str(time),'string'],
                            [teamId,''],##teamId,
                            [position,'string'],
                            [str(posRank),''],
                            [playerId,''],##player
                            [dcId,'string'],##depth chart site player id
                            [role,'string'],
                            [injuryStatus,'string'],
                            [str(tdb),''],
                            [str(gl),''],
                            [str(kr),''],
                            [str(pr),''],
                            [str(timestamp),'']
                            ])
                        posRank += 1

    return [deleteSql,sql.returnStatement()]


