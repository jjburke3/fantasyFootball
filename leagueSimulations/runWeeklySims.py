import leagueResultsMethods as meth
from simLeague import leagueSimulation
import traceback
import time
import pandas as pd
import random
from timeit import timeit

import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect
from dbFuncs import InsertTable

runCount = 50
while True:
    season = 2021
    week = 0
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
        elif result[0] >= 5000:
            conn.close()
            break
        
        try:
            results = meth.pullResults(season,week,conn)
        except Exception as e:
            print(str(e))



        try:
            currentRosters = meth.pullCurrentRosters(season,week, conn)
            currentRosters['predictionDistr'] = currentRosters.apply(lambda x: x['predictionDistr'].split(',') ,axis=1)
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
                    rostersDict[team+"-"+str(int(weekNum))]['totalRoster'] = currentRosters.loc[
                        (currentRosters['playerTeam'] == team) &
                        (currentRosters['predictedWeek'] == weekNum),
                        ['playerId',
                         'playerPosition',
                         'predictionValue',
                         'predictionDistr',
                         'playProb'
                         ]]
                    rostersDict[team+"-"+str(int(weekNum))]['totalRoster']['randNum'] = None
        except Exception as e:
            traceback.print_exc()

        try:
            replaceValues = meth.pullReplacementNumbers(season,week,conn)
            replaceValues['replaceDistr'] = replaceValues.apply(lambda x: [float(y) if y != '' else 0 for y in x['replaceDistr'].split(',')] ,axis=1)
            replaceDict = {}
            for replaceWeek in replaceValues['predictedWeek'].unique():
                replaceDict[replaceWeek] = replaceValues[replaceValues['predictedWeek'] == replaceWeek].set_index('playerPosition').to_dict(orient='index')
        except Exception as e:
            traceback.print_exc() 

        conn.close()


    print('start sims')
    start = time.process_time()
    sim = leagueSimulation(season,rostersDict,replaceDict,results,week)
    status = True
    fails = 0
    try:
        sim.simSeason()
    except Exception as e:
        fails += 1
        traceback.print_exc()

    results = sim.leagueResults()
    resultsTable = results.copy()
    table2 = pd.DataFrame(data={'Names' : resultsTable.index, 'Points' : None, 'Wins' : None,
                                'Losses' : None, 'HighPoints' : None})
    table2['Points'] = [[round(x,2)] for x in results['winPoints']]
    table2['Wins'] = [[x] for x in results['winWin']]
    table2['Losses'] = [[x] for x in results['winLoss']]
    table2['HighPoints'] = [[x] for x in results['weeklyHighPoints']]
    print(time.process_time()-start)
    for i in range(1,runCount):
        start = time.process_time()
        status = True
        try:
            sim.simSeason()
            status = False
        except Exception as e:
            fails += 1
            with DOConnect() as tunnel:
                c, conn = connection(tunnel)
                c.execute('''insert into leagueSims.simErrors
                              values (%d, %d, %d, %d, '%s', current_timestamp());''' % (
                                  season, week, fails, i, str(e).replace("'","\'")))
                conn.commit()
                conn.close()
            
        results = sim.leagueResults()
        resultsTable = resultsTable.add(results,fill_value=0)
        table2['Points'] = table2.apply(lambda x: x['Points'] + [round(results.loc[results.index==x['Names']].iloc[0]['winPoints'],2)],axis=1)
        table2['Wins'] = table2.apply(lambda x: x['Wins'] + [results.loc[results.index==x['Names']].iloc[0]['winWin']],axis=1)
        table2['Losses'] = table2.apply(lambda x: x['Losses'] + [results.loc[results.index==x['Names']].iloc[0]['winLoss']],axis=1)
        table2['HighPoints'] = table2.apply(lambda x: x['HighPoints'] + [results.loc[results.index==x['Names']].iloc[0]['weeklyHighPoints']],axis=1)
        print(time.process_time()-start)


    sqlStatement = '''insert into leagueSims.standings values %s
                    on duplicate key update
                    standRunCount = standRunCount + values(StandRunCount),
                    standWins = standWins + values(standWins),
                    standWinsArray = concat(standWinsArray,',',values(standWinsArray)),
                    standLosses = standLosses + values(standLosses),
                    standLossesArray = concat(standLossesArray,',',values(standLossesArray)),
                    standPoints = standPoints + values(standPoints),
                    standPointsArray = concat(standPointsArray,',',values(standPointsArray)),
                    standPointsRemain = standPointsRemain + values(standPointsRemain),
                    standPlayoffs = standPlayoffs + values(standPlayoffs),
                    standChamp = standChamp + values(standChamp),
                    standHighPoints = standHighPoints + values(standHighPoints),
                    standLowPoints = standLowPoints + values(standLowPoints),
                    standFirstPlace = standFirstPlace + values(standFirstPlace),
                    standThirdPlace = standThirdPlace + values(standThirdPlace),
                    standBye = standBye + values(standBye),
                    standWeeklyHighPoints = standWeeklyHighPoints + values(standWeeklyHighPoints),
                    standWeeklyHighPointsArray = concat(standWeeklyHighPointsArray,',',values(standWeeklyHighPointsArray));


                '''

    sqlAdd = ''
    for i, row in resultsTable.iterrows():
        sqlAdd += ('''(%d,%d,%d,'%s',%d,'%s',%d,'%s',%f,
                        '%s',%f, %d,%d,%d,%d,%d,%d,%d,%d,%d,'%s'),''' %
                   (season,week,runCount,
                    row.name,row['winWin'], ','.join([str(int(x)) for x in table2.loc[table2['Names']==i].iloc[0]['Wins']]),
                    row['winLoss'], ','.join([str(int(x)) for x in table2.loc[table2['Names']==i].iloc[0]['Losses']]),
                    round(row['winPoints'],2),
                    ','.join([str(round(x,1)) for x in table2.loc[table2['Names']==i].iloc[0]['Points']]),
                    round(row['winPointsRemain'],2),
                    row['playoffs'],row['champ'],row['runnerup'],
                    row['thirdPlace'],row['highPoints'],row['lowPoints'],
                    row['firstPlace'],row['bye'],
                    row['weeklyHighPoints'],','.join([str(int(x)) for x in table2.loc[table2['Names']==i].iloc[0]['HighPoints']])))

    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            c.execute(sqlStatement % sqlAdd[:-1])
        except:
            traceback.print_exc()
            
        conn.commit()
        conn.close()
