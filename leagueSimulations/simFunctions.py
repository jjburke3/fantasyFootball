import sys

sys.path.insert(0,'../scrapping')
sys.path.insert(0,'../dbConn')
sys.path.insert(0,'..')

from espnLeagueApi import League

from espnLeagueApi import ESPNFF

from security import fantasy_league, espn_cookie, swid

from dbFuncs import *

def pullCurrentLineups(year,conn,week):
    client = ESPNFF(swid=swid, s2=espn_cookie)
    try:
        client.authorize()
    except AuthorizationError:
        print('failed to authorize')

    teamIds = {1 : 'Andrew Lamb',
                  2 : 'Billy Beirne',
                  3 : 'Tom Buckley',
                  4 : 'JJ Burke',
                  5 : 'mike guiltinan',
                  6 : 'Chris Hammitt',
                  7 : 'Matthew Singer',
                  8 : 'Chris Curtin',
                  9 : 'Mike DeRusso',
                  10 : 'Joe Young',
                  11 : 'Ricky Garcia',
                  12 : 'Jordan Hiller',
                  13 : 'Parker King',
                  14 : 'Mark Krizmanich',
                  0 : ''}

    league = client.get_league(fantasy_league['league_id'], year)
    rosters = league.currentRosters()

    teams = getTeamId(conn)

    ## pull in current list of all players to get id numbers
    ## used espn ids if available
    players = getPlayerId(year,conn,espn=True)


    sql = InsertTable("la_liga_data.currentRoster")
    deleteSql = ('''delete from la_liga_data.currentRoster
                where rosterYear = %d and rosterWeek = %d;
                ''' % (year,week))

    for player in rosters:
        teamNumber = teams.teamId(player['playerTeam'],conn)
        playerNumber = players.playerId([player['playerName'],
                                                     str(teamNumber),
                                                     player['playerPosition'],
                                                     str(year)],
                                                      conn,espnId=player['playerESPNId'])
        sql.appendRow([["NULL",''],##rowId
                       [str(year),''],##rosterYear
                       [str(week),''],#rosterWeek
                       [teamIds[player['teamId']],'string'],#rosterTeam
                       [player['playerSlot'],'string'],#rosterSlot
                       [str(playerNumber),''],#playerId
                       [str(player['playerESPNId']),''],#espnId
                       [str(teamNumber),''],#nflteam
                       [player['playerPosition'],'string'],#position
                       ['current_timestamp()','']#data create date
                       
                       ])
        

    return [deleteSql,sql.returnStatement()]
