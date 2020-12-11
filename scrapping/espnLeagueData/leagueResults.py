
import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
sys.path.insert(0,'..')

from espnLeagueApi import League

from espnLeagueApi import ESPNFF

from dbFuncs import *

from security import fantasy_league, espn_cookie, swid
from references import fullName



def pullLeagueData(year,week,conn):
    client = ESPNFF(swid=swid, s2=espn_cookie)
    try:
        client.authorize()
    except AuthorizationError:
        print('failed to authorize')

    teams = getTeamId(conn)
    players = getPlayerId(year,conn,espn=True)
    league = client.get_league(fantasy_league['league_id'], year)
    sql1 = InsertTable("la_liga_data.playerPoints")
    sql = """insert into la_liga_data.pointsScored values %s
            on duplicate key update
            vsTeam = values(vsTeam),
            player = values(player),
            playerTeam = values(playerTeam),
            playerId = values(playerId),
            playerSlot = values(playerSlot),
            playerPosition = values(playerPosition),
            playerPosition2 = values(playerPosition2),
            opponent = values(opponent),
            points = values(points),
            dataCreate = current_timestamp();"""
    sql2 = """insert into la_liga_data.wins values %s
            on duplicate key update
            winPoints = values(winPoints),
            winPointsAgs = values(winPointsAgs),
            winWin = values(winWin),
            winLoss = values(winLoss),
            winTie = values(winTie),
            dataCreate = current_timestamp();"""
    sqlInsert = ''
    sqlInsert2 = ''
    for team in range(1,15):
        matchup = league.boxscore(week=week,team=team)
        teamId = {1 : 'Andrew Lamb',
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

        teamName = teamId[matchup['teamId']]
        season = matchup['season']
        week = matchup['week']
        teamPoints = matchup['teamPoints']
        opp = matchup['opponentName']
        oppPoints = matchup['opponentPoints']
        win = int(teamPoints > oppPoints)
        loss = int(teamPoints < oppPoints)
        tie = int(teamPoints == oppPoints)

        sqlInsert2 += ("(" + str(season) + "," +
                       str(week) + "," +
                       "'" + teamName + "'," +
                       "'" + opp + "'," +
                       str(teamPoints) + "," +
                       str(oppPoints) + "," +
                       str(win) + "," +
                       str(loss) + "," +
                       str(tie) + "," +
                       "null," +
                       "current_timestamp()),")

        for i, player in enumerate(matchup['playerList']):
            try:
                teamNumber = teams.teamId(player['playerTeam'],conn)
                playerNumber = players.playerId([player['playerName'].replace("'","\\'"),
                                                     str(teamNumber),
                                                     player['playerPos'],
                                                     str(season)],
                                                      conn,espnId=player['playerId'])

                sql1.appendRow([[str(season),''], ##season value
                                [str(week),''], ## week value
                                [teamNumber,''], ## team value
                                [str(i),''], ## player slot number
                                [opp,'string'],## vs team
                                [playerNumber,''],## playerId
                                [str(player['playerId']),''],## playerEspnId
                                [str(teams.teamId(player['playerTeam'],conn)),''],## playerNfl Team
                                [player['slot'],'string'],## player slot
                                [player['playerPos'],'string'],## player position
                                [str(player['Points']),''],## player points
                                ['current_timestamp()','']## create date time
                                ])
                print(sql1.returnStatement())

                                
                sqlInsert += ("(" + str(season) + "," +
                             str(week) + "," +
                             "'" + teamName + "'," +
                             str(i) + "," +
                             "'" + opp + "'," +
                             "'" + player['playerName'].replace("'","_") + "'," +
                             str(player['playerId']) + "," +
                             "'" + fullName[player['playerTeam']] + "'," +
                              "'" + player['slot'] + "'," +
                              "'" + player['playerPos'] + "'," +
                              "null," +
                              "null," +
                              "null," +
                              "null," +
                              str(player['Points']) + "," +
                              "current_timestamp()),")
            except Exception as e:
                print(str(e))

        
                             
                
            

            


    sqlInsert = sqlInsert[:-1]
    sqlInsert2 = sqlInsert2[:-1]
    print(sql1.returnStatement())
    return [sql % sqlInsert, sql2 % sqlInsert2]

