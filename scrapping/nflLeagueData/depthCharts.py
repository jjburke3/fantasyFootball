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
                    url = 'https://subscribers.footballguys.com/apps/depthchart.php?type=all',
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
    roles = {'brown' : 'Inj Replace','red' : 'Inj Replace', 'blue' : 'Starter', 'green': 'Situational', 'black' : 'Practice'}

    soup = bs(r.content, 'html.parser')
    ## pull all depth charts divs
    tables = soup.find_all('div', {"class":"depth-chart"})

    paren = re.compile(" \((.+)\)")
    
    for teamDiv in tables:
        teamName = teamDiv.find('span',{"class":"team-header"}).text
        positionList = teamDiv.find_all('li')
        for positionItem in positionList:
            position = positionItem.find('span',{'class':'pos-label'}).text
            position = position.split(':')[0]
            posRank = 0
            for playerEntry in positionItem.findChildren()[1:]:
                player = playerEntry.text
                dcId = ''
                if playerEntry.name=="a":
                    try:
                        dcId = playerEntry['href'].split("id=")[1]
                    except:
                        dcId = ''
                injuryStatus = ''
                tdb = 0
                gl = 0
                kr = 0
                pr = 0
                extra = paren.search(player)
                if extra:
                    extra = extra.group(1)
                    player = paren.sub('',player)
                else:
                    extra = ''
                if position == "Coaches":
                    role = extra
                else:
                    role = 'Practice'
                    if re.match('starter',str(playerEntry['class'])):
                        role = 'Starter'
                    
                    if re.match("IR",extra):
                        injuryStatus = 'IR'
                    if re.match("IR-R",extra):
                        injuryStatus = 'IR-R'
                    elif re.match('Q',extra):
                        injuryStatus = 'Q'
                    elif re.match('D',extra):
                        injuryStatus = 'D'
                    elif re.match('O',extra):
                        injuryStatus = 'O'
                    elif re.match('COV',extra):
                        injuryStatus = 'COV'
                    elif re.match('SUS',extra):
                        injuryStatus = 'Suspended'
                    elif re.match('NFI',extra):
                        injuryStatus = 'NFI'
                    elif re.match('PUP',extra):
                        injuryStatus = 'PUP'
                    elif re.match('CEL',extra):
                        injuryStatus = 'CEL'
                    elif re.match('EX',extra):
                        injuryStatus = 'EX'
                    if re.match("3RB",extra):
                        tdb = 1
                    if re.match("SD",extra):
                        gl = 1
                    if re.match("KR",extra):
                        kr = 1
                    if re.match("PR",extra):
                        pr = 1
                teamId = teams.teamId(teamName,conn)
                
                if len(player) > 65:
                    player = player[:65]
            

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


