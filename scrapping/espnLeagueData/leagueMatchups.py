## file returns sql statement text string run to pull matchups
## file is passed year as integer
import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
sys.path.insert(0,'..')

from espnLeagueApi import League

from espnLeagueApi import ESPNFF

from dbFuncs import *

from security import fantasy_league, espn_cookie, swid
from references import fullName

def pullMatchupData(year):
    client = ESPNFF(swid=swid, s2=espn_cookie)
    try:
        client.authorize()
    except AuthorizationError:
        print('failed to authorize')

    league = client.get_league(fantasy_league['league_id'], year)

    sql = InsertTable("la_liga_data.matchups")

    for week in range(1,14):
        for team in range(1,15):
            matchup = league.matchup(week=week,team=team)

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
                      14 : 'Mark Krizmanich'}

            sql.appendRow([
                    [str(year),''],#year
                    [str(week),''],#week
                    [teamId[team],'string'],#team
                    [teamId[matchup],'string']#opp

                ])
    return [sql.returnStatement()]

