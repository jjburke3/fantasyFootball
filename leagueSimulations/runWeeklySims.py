import leagueResultsMethods as meth
from simLeague import leagueSimulation
import traceback
import time
import pandas as pd

import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect

season = 2020
week = 2

pd.set_option('display.max_columns', 12)
with DOConnect() as tunnel:
    c, conn = connection(tunnel)
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
                     'predictionVar',
                     'predictionSkew',
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
sim.simSeason()

results = sim.leagueResults()
resultsTable = results.copy()
print(results)
print(time.clock()-start)
for i in range(1,10):
    start = time.clock()
    sim.simSeason()
    results = sim.leagueResults()
    resultsTable = resultsTable.add(results,fill_value=0)
    print(results)
    print(time.clock()-start)

print(resultsTable)
