## file returns sql statement text string run in weeklyDataLeague file
## file is passed year and week as integers, and the defined connection
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

    ## pull in current list of all teams to get id numbers
    teams = getTeamId(conn)

    ## pull in current list of all players to get id numbers
    ## used espn ids if available
    players = getPlayerId(year,conn,espn=True)
    
    league = client.get_league(fantasy_league['league_id'], year)

    ## create insert objects for both individual player scores table
    ## and weekly wins table
    sql1 = InsertTable("la_liga_data.playerPoints")
    sqlWins = InsertTable("la_ligaData.wins")

    sql1.updateStatement['playerVsTeam','playerId','playerESPNId',
                         'playerFNLTeam','playerSlot','playerPosition',
                         'playerPoints','dataCreateDate']

    sqlWins.updateStatement['winPoints','winPointsAgs','winWin',
                            'winLoss','winTie','dataCreate']

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

        sqlWins.appendRow([[str(season),''],
                           [str(week),''],
                           [teamName,'string'],
                           [opp,'string'],
                           [str(teamPoints),''],
                           [str(oppPoints),''],
                           [str(win),''],
                           [str(loss),''],
                           [str(tie),''],
                           ['NULL',''],
                           ['current_timestamp()','']
                           ])

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
            except Exception as e:
                print(str(e))

        
                             
                
            

            


    sqlInsert = sqlInsert[:-1]
    sqlInsert2 = sqlInsert2[:-1]
    print(sql1.returnStatement())
    return [sql1.returnStatement(), sqlWins.returnStatement()]

