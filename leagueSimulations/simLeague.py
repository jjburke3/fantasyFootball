import random
import numpy as np
import math
from ctypes import *
from scipy.stats import skewnorm



class leagueSimulation(object):

    def __init__(self, predictionValues, replacementValues, pastResults):
        self.playerTeams = list(predictionValues.playerTeam.unique())
        

        self.positions = [{'key' : 'QB', 'allow' : ['QB']},
                     {'key' : 'RB', 'allow' : ['RB']},
                     {'key' : 'WR', 'allow' : ['WR']},
                     {'key' : 'TE', 'allow' : ['TE']},
                     {'key' : 'D/ST', 'allow' : ['D/ST']},
                     {'key' : 'K', 'allow' : ['K']},
                     {'key' : 'RBWR1', 'allow' : ['RBWR']},
                     {'key' : 'RBWR2', 'allow' : ['RBWR']},
                     {'key' : 'FLEX', 'allow' : ['Flex']}
                     ]
        print(pastResults)
        pastResults['winPoints'] = pastResults.apply(lambda x:
                                                     x['winPoints'] if not np.isnan(x['winPoints'])
                                                     else self._bestLineup(x['winTeam'],x['winWeek'],predictionValues,replacementValues),
                                                     axis=1)
        
        pastResults['winPointsAgs'] = pastResults.apply(lambda x:
                                                  x['winPointsAgs'] if not np.isnan(x['winPointsAgs'])
                                                  else pastResults[(
                                                      (pastResults['winSeason'] == x['winSeason']) &
                                                      (pastResults['winWeek'] == x['winWeek']) &
                                                      (pastResults['winTeam'] == x['winOpp'])
                                                      )].winPoints.values[0],
                                                  axis=1)
        pastResults['winWin'] = pastResults.apply(lambda x:
                                                  x['winWin'] if not np.isnan(x['winWin'])
                                                  else 1 if x['winPoints'] > x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        pastResults['winLoss'] = pastResults.apply(lambda x:
                                                  x['winLoss'] if not np.isnan(x['winLoss'])
                                                  else 1 if x['winPoints'] < x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        pastResults['winTie'] = pastResults.apply(lambda x:
                                                  x['winTie'] if not np.isnan(x['winTie'])
                                                  else 1 if x['winPoints'] == x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        
        print(pastResults.loc[:,['winSeason','winWeek','winTeam','winPoints','winPointsAgs','winWin']])

    def _bestLineup(self, team, week, rosters, replacement):
        weekTeam = ((rosters.playerTeam == team) &
                    (rosters.predictedWeek == week))
        weekRoster = rosters[weekTeam]
        weekRoster['randNum'] = weekRoster.apply(lambda x: random.uniform(0,1),axis=1)
        playersUsed = []
        lineup = {}
        replace = replacement[replacement.predictedWeek == week]
        for pos in self.positions:
            randMean = replace[replace.playerPosition.isin(pos['allow'])].sort_values(
                'replaceMean',ascending=False).replaceMean.values[0]
            randVar = replace[replace.playerPosition.isin(pos['allow'])].sort_values(
                'replaceMean',ascending=False).replaceVar.values[0]
            randSkew = replace[replace.playerPosition.isin(pos['allow'])].sort_values(
                'replaceMean',ascending=False).replaceSkew.values[0]
            bestPlayer = weekRoster[(weekRoster.playerPosition.isin(pos['allow'])) &
                        (weekRoster.playProb.gt(weekRoster.randNum)) &
                                    (~weekRoster.playerId.isin(playersUsed)) &
                                    (weekRoster.predictionValue >= randMean)].sort_values(
                        'predictionValue',ascending=False)
            if bestPlayer.empty:
                lineup[pos['key']] = skewnorm.rvs(a=randSkew,
                                                  loc=randMean,
                                                  scale=math.sqrt(randVar))
            else:
                lineup[pos['key']] = skewnorm.rvs(a=bestPlayer.predictionSkew.values[0],
                                                  loc=bestPlayer.predictionValue.values[0],
                                                  scale=math.sqrt(bestPlayer.predictionVar.values[0]))
        return sum(lineup.values())

