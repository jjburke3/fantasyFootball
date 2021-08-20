#file results sql statement text string run in injuriesAndDepthCharts
import sys

import requests
import re
import json
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

def pullFPRankings(conn,
                season, week, day, time,
                versionNo = 'NULL',
                url = 'fantasyProsRankings',
                timestamp = 'NULL'):
    teams = getTeamId(conn)
    players = getPlayerId(season,conn,fp=True)
    sql = InsertTable("scrapped_data2.fantasyProsRankings")
    deleteSql = ''' delete from scrapped_data2.fantasyProsRankings where
                rankingSeason = %s and rankingWeek = %s and
                rankingDay = '%s' and rankingTime = '%s' ''' % (season, week,day,time)

    tier = 0
    r = requests.get(url)

    soup = bs(r.content, 'html.parser')
    if season <= 2017:
        tableId = 'data'
    elif season <= 2020:
        tableId = 'rank-data'
    elif season >= 2021:
        m = re.search(r'var ecrData = (.*?);',str(soup))
        playerList = json.loads(m.groups()[0])['players']
    if season < 2021:
        table = soup.find('table', {"id":tableId})
        rankingList = table.find('tbody')
        playerList = rankingList.find_all("tr")
    paren = re.compile(" \((.+)\)")

    
    for player in playerList:
        if season < 2021:
            if 'tier-row' in player['class']:
                tier = tier + 1
                continue
            cells = player.find_all("td")
            if not (re.match("mpb",player['class'][0])):
                continue
            nameCell = player.find("td",{"class","player-label"})
            ranking = cells[0].text
            fpId = player['class'][0].split('-')[2]
            if season < 2018:
                playerName = nameCell.find("a").text
            else:
                playerName = nameCell.find("a").find("span").text
            try:
                team = nameCell.find("small").text
            except:
                if re.search(r"(?<=\()(.*)(?=\))",playerName):
                    team = re.search(r"(?<=\()(.*)(?=\))",playerName).group(0)
                else:
                    team = playerName
            positionRanking = nameCell.find_next("td").text
            position = re.sub(r"[0-9]","",positionRanking)
        else:
            playerName = player['player_name']
            team = player['player_team_id']
            fpId = player['player_id']
            position = player['player_position_id']
            ranking = player['rank_ecr']
            tier = player['tier']
            positionRanking = player['pos_rank']
        positionRanking = re.sub(r"[A-Za-z]","",positionRanking)
        print(season,ranking,tier,playerName,team,positionRanking,fpId,position)
        teamId = teams.teamId(team,conn)
        #teamId
        playerId = players.playerId([
            remove_non_ascii(playerName).replace("'","\\'"),
            str(teamId),
            position,
            str(season)],
            conn,
            fpId = int(fpId)
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
                    [playerId,''],##player
                    [fpId,''],##fantasy pros site player id
                    [ranking,''],
                    [tier,''],
                    [positionRanking,''],
                    [str(timestamp),'']
                    ])

    return [deleteSql,sql.returnStatement()]


