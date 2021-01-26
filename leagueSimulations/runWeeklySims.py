import leagueResultsMethods as meth
from simLeague import leagueSimulation
import traceback
import time
import pandas as pd
import random

import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect
from dbFuncs import InsertTable

season = 2020
week = 12

pd.set_option('display.max_columns', 12)
while True:
    season = random.choice(range(2017,2021))
    week = random.choice(range(0,17))
    print(season,week)
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        c.execute('''select standRunCount
                     from leagueSims.standings
                     where standYear = %d
                     and standWeek = %d''' % (season,week))
        result = c.fetchone()
        if result is None:
            None
        elif result[0] >= 10000:
            conn.close()
            continue
        
        try:
            results = meth.pullResults(season,week,conn)
        except Exception as e:
            print(str(e))



        try:
            currentRosters = meth.pullCurrentRosters(season,week, conn)
            positions = [{'key' : 'QB', 'allow' : ['QB']},
                         {'key' : 'RB', 'allow' : ['RB']},
                         {'key' : 'WR', 'allow' : ['WR']},
                         {'key' : 'TE', 'allow' : ['TE']},
                         {'key' : 'D/ST', 'allow' : ['D/ST']},
                         {'key' : 'K', 'allow' : ['K']},
                         {'key' : 'RBWR', 'allow' : ['RB','WR']},
                         {'key' : 'Flex', 'allow' : ['RB','WR','TE']}
                         ]

            rostersDict = {}
            for weekNum in currentRosters['predictedWeek'].dropna().unique():
                for team in currentRosters['playerTeam'].unique():
                    rostersDict[team+"-"+str(int(weekNum))] = {}
                    for pos in positions:
                     rostersDict[team+"-"+str(int(weekNum))][pos['key']] = currentRosters.loc[
                        (currentRosters['playerTeam'] == team) &
                        (currentRosters['predictedWeek'] == weekNum) &
                        (currentRosters['playerPosition'].isin(pos['allow'])),
                        ['playerId',
                         'playerPosition',
                         'predictionValue',
                         'predictionDistr',
                         'playProb'
                         ]]
        except Exception as e:
            print(str(e))

        try:
            replaceValues = meth.pullReplacementNumbers(season,week,conn)
        except Exception as e:
            traceback.print_exc() 

        conn.close()


    #predictions, replacementValues = leagueModel
    print('start sims')
    start = time.clock()
    sim = leagueSimulation(rostersDict,replaceValues,results)
    status = True
    fails = 0
    while status and fails < 100:
        try:
            sim.simSeason()
            status = False
        except Exception as e:
            fails += 1
            with DOConnect() as tunnel:
                c, conn = connection(tunnel)
                c.execute('''insert intoleagueSims.simErrors
                              values (%d, %d, '%s', current_timestamp());''' % (
                                  season, week, str(e)))
                conn.commit()
                conn.close()
    if fails >= 100:
        continue

    results = sim.leagueResults()
    resultsTable = results.copy()
    table2 = pd.DataFrame(data={'Names' : resultsTable.index, 'Points' : None, 'Wins' : None,
                                'Losses' : None, 'HighPoints' : None})
    table2['Points'] = [[round(x,2)] for x in results['winPoints']]
    table2['Wins'] = [[x] for x in results['winWin']]
    table2['Losses'] = [[x] for x in results['winLoss']]
    table2['HighPoints'] = [[x] for x in results['weeklyHighPoints']]
    print(time.clock()-start)
    runCount = 10
    for i in range(1,runCount):
        start = time.clock()
        status = True
        while status and fails < 100:
            try:
                sim.simSeason()
                status = False
            except Exception as e:
                fails += 1
                with DOConnect() as tunnel:
                    c, conn = connection(tunnel)
                    c.execute('''insert intoleagueSims.simErrors
                                  values (%d, %d, '%s', current_timestamp());''' % (
                                      season, week, str(e)))
                    conn.commit()
                    conn.close()
        if fails >= 100:
            continue
            
        results = sim.leagueResults()
        resultsTable = resultsTable.add(results,fill_value=0)
        table2['Points'] = table2.apply(lambda x: x['Points'] + [round(results.loc[results.index==x['Names']].iloc[0]['winPoints'],2)],axis=1)
        table2['Wins'] = table2.apply(lambda x: x['Wins'] + [results.loc[results.index==x['Names']].iloc[0]['winWin']],axis=1)
        table2['Losses'] = table2.apply(lambda x: x['Losses'] + [results.loc[results.index==x['Names']].iloc[0]['winLoss']],axis=1)
        table2['HighPoints'] = table2.apply(lambda x: x['HighPoints'] + [results.loc[results.index==x['Names']].iloc[0]['weeklyHighPoints']],axis=1)
        print(time.clock()-start)
    if fails >= 100:
        continue

    sqlStatement = '''insert into leagueSims.standings values %s
                    on duplicate key update
                    standRunCount = standRunCount + values(StandRunCount),
                    standWins = standWins + values(standWins),
                    standWinsArray = concat(standWinsArray,',',values(standWinsArray)),
                    standLosses = standLosses + values(standLosses),
                    standLossesArray = concat(standLossesArray,',',values(standLossesArray)),
                    standPoints = standPoints + values(standPoints),
                    standPointsArray = concat(standPointsArray,',',values(standPointsArray)),
                    standPlayoffs = standPlayoffs + values(standPlayoffs),
                    standChamp = standChamp + values(standChamp),
                    standHighPoints = standHighPoints + values(standHighPoints),
                    standLowPoints = standLowPoints + values(standLowPoints),
                    standFirstPlace = standFirstPlace + values(standFirstPlace),
                    standBye = standBye + values(standBye),
                    standWeeklyHighPoints = standWeeklyHighPoints + values(standWeeklyHighPoints),
                    standWeeklyHighPointsArray = concat(standWeeklyHighPointsArray,',',values(standWeeklyHighPointsArray));


                '''

    sqlAdd = ''
    for i, row in resultsTable.iterrows():
        sqlAdd += ('''(%d,%d,%d,'%s',%d,'%s',%d,'%s',%f,
                        '%s',%d,%d,%d,%d,%d,%d,%d,%d,%d,'%s'),''' %
                   (season,week,runCount,
                    row.name,row['winWin'], ','.join([str(int(x)) for x in table2.loc[table2['Names']==i].iloc[0]['Wins']]),
                    row['winLoss'], ','.join([str(int(x)) for x in table2.loc[table2['Names']==i].iloc[0]['Losses']]),
                    round(row['winPoints'],2),','.join([str(round(x,1)) for x in table2.loc[table2['Names']==i].iloc[0]['Points']]),
                    row['playoffs'],row['champ'],row['runnerup'],
                    row['thirdPlace'],row['highPoints'],row['lowPoints'],
                    row['firstPlace'],row['bye'],
                    row['weeklyHighPoints'],','.join([str(int(x)) for x in table2.loc[table2['Names']==i].iloc[0]['HighPoints']])))

    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        c.execute(sqlStatement % sqlAdd[:-1])
        conn.commit()
        conn.close()
