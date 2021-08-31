## file returns sql statement text string run to pull drafted players
## file is passed year as integer, and the defined connection
import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
sys.path.insert(0,'..')

from espnLeagueApi import League

from espnLeagueApi import ESPNFF

from dbFuncs import *

from security import fantasy_league, espn_cookie, swid
from references import fullName

def pullDraftData(year,conn):
    client = ESPNFF(swid=swid, s2=espn_cookie)
    try:
        client.authorize()
    except AuthorizationError:
        print('failed to authorize')

    league = client.get_league(fantasy_league['league_id'], year)

    
    ## pull in current list of all teams to get id numbers
    teams = getTeamId(conn)

    ## pull in current list of all players to get id numbers
    ## used espn ids if available
    players = getPlayerId(year,conn,espn=True)

    sql = InsertTable("la_liga_data.draftedPlayerData")



    draft = league.draftData()
    for pick in draft:
        teamId = teams.teamId(pick['nflTeam'],conn)
        player = players.playerId([pick['playerName'],
                                   str(teamId),
                                   pick['playerPosition'],
                                   str(year)],
                                   conn,
                                   espnId = pick['playerId']
                                  )
                                   

        sql.appendRow([[str(year),''],#year
                       [str(pick['round']),''],#draftRound
                       [str(pick['pick']),''],#draftPick
                       [pick['teamId'],'string'],#selectingTeam
                       [str(player),''],#playerId
                       [str(pick['playerId']),''],#playerEspnId
                       [pick['playerPosition'],'string'],#playerPosition
                       [str(teamId),''],#playerteam
                       ['current_timestamp()',''],#create date time

            ])

    
    return [sql.returnStatement()]
    


