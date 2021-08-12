import sys
import requests
from bs4 import BeautifulSoup as bs, Comment
import sys
from requests.structures import CaseInsensitiveDict
sys.path.insert(0,'..')
sys.path.insert(0,'..\..')

from references import fullName, pfrAbbrName, fullToMascot, abbrToMascot, teamLocation

fullName = CaseInsensitiveDict(fullName)
sys.path.insert(0,'..')
sys.path.insert(0,'..\..')
sys.path.insert(0,'../../dbConn')

from dbFuncs import *


def pullInjuredStatus(conn,
                 year, week,teamNum):
    deleteSql = '''delete from scrapped_data2.injuredStatus
            where injSeason = %d and injWeek = %d ''' % (year, week)
    teams = getTeamId(conn)
    players = getPlayerId(year,conn,pfr=True)
    sql = InsertTable("scrapped_data2.injuredStatus")

    url = 'https://www.pro-football-reference.com/teams/%s/%d_injuries.htm'

    teamsList =  ['crd','atl','rav','buf','car','chi','cin',
                 'cle','dal','den','det','gnb','htx','clt','jax',
                 'kan','rai','sdg','ram','mia','min','nwe','nor',
                 'nyg','nyj','phi','pit','sfo','sea','tam','oti',
                 'was']
    team = teamsList[teamNum]
    print(team,year)
    teamId = teams.teamId(team,conn)

    r = requests.get(url % (team,year))

    soup = bs(r.content,'html.parser')

    table = soup.find_all('table',{'id':'team_injuries'})[0]

    headerRow = table.find_all('tr')[:1][0]
    playerRows = table.find_all('tr')[1:]


    for player in playerRows:
        headCell = player.find_all('th')[0]
        playerName = headCell.text
        print(playerName)
##            playerLink = headCell.find_all('a')[0]['href']
##            playerUrl = 'https://www.pro-football-reference.com/'+playerLink
##            rPlayer = requests.get(playerUrl)
##            playerSoup = bs(rPlayer.content,'html.parser')
##            posP = playerSoup.find_all('strong',text='Position')[0]
##            pos = posP.parent.text.split(': ')[1]
        pos = ''
        playerPFRId = headCell['data-append-csv'].replace("'","_")
        playerId = players.playerId([
                                        playerName.replace("'","\\'"),
                                        str(teamId),
                                        pos,
                                        str(year)
                                    ],
                                    conn,
                                    pfrId = playerPFRId)
        playerWeeks = player.find_all('td')
        for i, weekHeader in enumerate(headerRow.find_all('th')[1:]):
            if weekNum != weekHeader:
                continue
            weekNum = weekHeader['data-stat'].split('_')[-1]
            playerStatus = playerWeeks[i].text
            try:
                playerInjury = playerWeeks[i]['data-tip'].split(':')[1]
                playerInjury = playerInjury[:20] if len(playerInjury) > 20 else playerInjury
            except:
                playerInjury = ''
            sql.appendRow([
                [str(year),''],
                [str(weekNum),''],
                [str(playerId),''],
                [str(teamId),''],
                [playerStatus,'string'],
                [playerInjury,'string'],
                [(1 if 'dnp' in playerWeeks[i]['class'] else 0),'']
                ])


    return [deleteSql,sql.returnStatement()]




