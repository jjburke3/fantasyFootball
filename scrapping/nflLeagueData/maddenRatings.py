#file results sql statement text string run in injuriesAndDepthCharts
import sys

import requests
import json
import re
import statistics as s
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

def pullMaddenRatings(conn,
                    season,
                    url = 'https://ratings-api.ea.com/v2/entities/m22-ratings?filter=iteration:launch-ratings&sort=overall_rating:DESC,firstName:ASC&limit=1000&offset=2000',
                    timestamp = 'NULL'):
    teams = getTeamId(conn)
    players = getPlayerId(season,conn)
    sql = InsertTable("madden_ratings.playerRatings")
    
    r = requests.get(url)
    data = r.json()
    ## pull all depth charts divs
    
    for playerEntry in data['docs']:
        teamName = playerEntry['team']
        playerName = playerEntry['fullNameForSearch']
        position = playerEntry['position']
        teamId = teams.teamId(teamName,conn)

    

        playerId = players.playerId([
            remove_non_ascii(playerName),
            str(teamId),
            position,
            str(season)],
            conn
            )
        routeRunning = s.mean([
                int(playerEntry['mediumRouteRunning_rating']),
                int(playerEntry['deepRouteRunning_rating']),
                int(playerEntry['shortRouteRunning_rating'])
            ])
        throwAccuracy = s.mean([
                int(playerEntry['throwAccuracyShort_rating']),
                int(playerEntry['throwAccuracyDeep_rating']),
                int(playerEntry['throwAccuracyMid_rating'])
            ])
        print(playerId,'-',playerName)
        sql.appendRow([
            ['NULL',''],## id
            [remove_non_ascii(playerName).replace("'","\'"),'string'],##playerName
            [str(playerId),''],##playerId
            [str(season),''],##season
            [teamName,'string'],## team
            [teamId,''],##teamId,
            [position,'string'],#position
            [playerEntry['height'],''],#height
            [playerEntry['weight'],''],##weight
            [playerEntry['overall_rating'],''],##overall
            [playerEntry['speed_rating'],''],##speed
            [playerEntry['acceleration_rating'],''],##acceleration
            [playerEntry['strength_rating'],''],##strenght
            [playerEntry['agility_rating'],''],##agility
            [playerEntry['awareness_rating'],''],##awareness
            [playerEntry['throwPower_rating'],''],##throw_power
            [str(throwAccuracy),''],##throw_accuracy
            [playerEntry['kickPower_rating'],''],##kick_power
            [playerEntry['kickAccuracy_rating'],''],##kick_accuracy
            [playerEntry['passBlock_rating'],''],##pass_block
            [playerEntry['runBlock_rating'],''],##run_block
            [playerEntry['catching_rating'],''],##catch
            [playerEntry['carrying_rating'],''],##carrying
            [playerEntry['bCVision_rating'],''],##bc_vision
            [playerEntry['injury_rating'],''],##injury
            [playerEntry['toughness_rating'],''],##toughness
            [playerEntry['stamina_rating'],''],##stamina
            [str(routeRunning),''],##route_running
            [playerEntry['age'],''],##experience
            [playerEntry['yearsPro'],''],##age
            ])

    return [sql.returnStatement()]


