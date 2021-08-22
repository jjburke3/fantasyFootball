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
                    role = 'Non-starter'
                    if 'starter' in playerEntry['class']:
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

def nbcChartAttr(conn,
                 season,
                 versionNo,
                 url = "https://www.nbcsportsedge.com/edge/api/team/depth_chart/"):
    teams = getTeamId(conn)
    players = getPlayerId(season,conn,nbc=True)
    updateStatements = []
    ## uuids found on NBC website, not sure if will remain valid
    teamUUIDs = ["58a589f2-bb57-4002-b693-a7d4b0cc8454",
                 "9cd298fc-afb0-43cf-9b48-37c897ab7be2",
                 "10d0310b-d3a7-4944-979f-d32979267245",
                 "21fe462d-7814-4a40-a5a7-85c199f176d8",
                 "61bccd8c-d448-4287-ab5a-3a36504e47dd",
                 "49e47174-8e87-48a4-9dc8-0757887f96f6",
                 "e666d58b-a08e-4a95-804b-0e4c91026e88",
                 "a537e4e6-61ad-40a9-a2ae-b576263754f8",
                 "3262f813-42c8-497d-9199-a24af7400111",
                 "2154898a-6830-49d8-a97e-fa3bb1a20698",
                 "0f13a8cc-e316-4e98-a087-957e27aeca4e",
                 "45f94267-2bcd-4658-ac5f-600eb9f93638",
                 "46729892-9b7c-446f-8ff9-446693fc3341",
                 "5cd71064-4206-4582-ab9e-669a8b21a7c7",
                 "a4e8194a-68ff-4be4-bba4-93a22ea0c546",
                 "9487063c-5464-4f25-bfa3-0f987352ce19",
                 "c7478dfc-20ac-4bfc-9ade-f692bf80ca14",
                 "1df34ace-5719-4a0a-9439-a85f6dca82ac",
                 "ad3ed90e-fa46-4dc1-819b-e6a8ca45259e",
                 "a00c8633-98e0-4fd5-a016-7cf7e9188973",
                 "4a4837fe-861f-4da5-946b-47bc6fdc0256",
                 "7a476557-40f2-4860-94da-1594f608052e",
                 "92d23f94-2cbc-4a13-8af5-aace480c4290",
                 "70e261bc-5424-4a05-b368-d6848a051fbf",
                 "297d912f-ec4b-4a85-b9ee-7605cd4d54c6",
                 "c1b015ed-6cc1-4b3e-83ad-8f26d593f23a",
                 "fe7219ec-ca0b-40e3-a5f7-4377fb34abd3",
                 "18fcbd9d-5fe8-4393-a71a-49e1db2e7cec",
                 "b1d24b2c-7442-4917-bf69-d415a990ff95",
                 "83b9ba4e-72ca-4693-87cc-d217afa04942",
                 "d0d84237-2856-4c5d-be5f-07aef78d5eb0",
                 "06a63a2e-fca6-4061-ba73-381d6bb47e49"]
    
    for uuid in teamUUIDs:
        r = requests.get(url+uuid)
        data = r.json()
        teamName = data['team']['label']
        teamId = teams.teamId(teamName,conn)
        for position in data['categories'][0]['slots']:
            if (position['position']['label'] in ['Goal-line Back','Third-down Running Back'] and
                len(position['players']) > 0):
                player = position['players'][0]['label']
                nId = int(position['players'][0]['id'])
                playerId = players.playerId([
                    remove_non_ascii(player).replace("'","\\'"),
                    str(teamId),
                    'RB',
                    str(season)],
                    conn,
                    nbcId = nId
                    )
                if position['position']['label'] == 'Goal-line Back':
                    sqlStatement = '''update scrapped_data2.depthCharts
                        set goalLine = 1
                        where chartVersion = %s and chartPlayer = %s and
                        chartTeam = %s'''
                else:
                    sqlStatement = '''update scrapped_data2.depthCharts
                        set thirdDownBack = 1
                        where chartVersion = %s and chartPlayer = %s and
                        chartTeam = %s'''
                updateStatements.append(sqlStatement % (str(versionNo),str(playerId),str(teamId)))
            
        
    return updateStatements


