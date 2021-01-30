import random
import numpy as np
import math
from ctypes import *
from scipy.stats import skewnorm



class leagueSimulation(object):

    def __init__(self, predictionValues, replacementValues, pastResults):
        self.pastResults = pastResults
        self.predictionValues = predictionValues
        self.replacementValues = replacementValues

        self.positions = [{'key' : 'QB', 'allow' : ['QB'], 'replace' : 'QB'},
                     {'key' : 'RB', 'allow' : ['RB'], 'replace' : 'RB'},
                     {'key' : 'WR', 'allow' : ['WR'], 'replace' : 'WR'},
                     {'key' : 'TE', 'allow' : ['TE'], 'replace' : 'TE'},
                     {'key' : 'D/ST', 'allow' : ['D/ST'], 'replace' : 'D/ST'},
                     {'key' : 'K', 'allow' : ['K'], 'replace' : 'K'},
                     {'key' : 'RBWR1', 'allow' : ['RB','WR'], 'replace' : 'RBWR'},
                     {'key' : 'RBWR2', 'allow' : ['RB','WR'], 'replace' : 'RBWR'},
                     {'key' : 'FLEX', 'allow' : ['RB','WR','TE'], 'replace' : 'Flex'}
                     ]

    def _isNoneNa(self,x):
        if x is None:
            return True
        elif np.isnan(x):
            return True
        else:
            return False

    def simSeason(self):
        resultsTable = self.pastResults.copy()
        resultsTable['winPointsInitial'] = resultsTable['winPoints'].copy()
        resultsTable['winPoints'] = resultsTable.apply(lambda x:
                                                     x['winPoints'] if not self._isNoneNa(x['winPoints'])
                                                     #else random.uniform(100,120),
                                                     else self._bestLineup(x['winTeam'],x['winWeek'],self.predictionValues,self.replacementValues),
                                                     axis=1)
        resultsTable['winPointsRemain'] = resultsTable.apply(lambda x:
                                                           x['winPoints'] if self._isNoneNa(x['winPointsInitial']) else 0,
                                                           axis=1)
        
        resultsTable['winPointsAgs'] = resultsTable.apply(lambda x:
                                                  0 if x['winOpp'] is None else
                                                  x['winPointsAgs'] if not self._isNoneNa(x['winPointsAgs'])
                                                  else resultsTable[(
                                                      (resultsTable['winSeason'] == x['winSeason']) &
                                                      (resultsTable['winWeek'] == x['winWeek']) &
                                                      (resultsTable['winTeam'] == x['winOpp'])
                                                      )].winPoints.values[0],
                                                  axis=1)
        resultsTable['winWin'] = resultsTable.apply(lambda x:
                                                  x['winWin'] if not self._isNoneNa(x['winWin'])
                                                  else 1 if x['winPoints'] > x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        resultsTable['winLoss'] = resultsTable.apply(lambda x:
                                                  x['winLoss'] if not self._isNoneNa(x['winLoss'])
                                                  else 1 if x['winPoints'] < x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        resultsTable['winTie'] = resultsTable.apply(lambda x:
                                                  x['winTie'] if not self._isNoneNa(x['winTie'])
                                                  else 1 if x['winPoints'] == x['winPointsAgs']
                                                  else 0,
                                                  axis=1)

        playerTeams = resultsTable[resultsTable.winWeek <= 13].groupby('winTeam')['winWin','winLoss','winPoints'].sum()
        playoffTeams = playerTeams.sort_values(by=['winWin','winLoss','winPoints'],ascending=[False,True,False]).iloc[0:5,:]
        pointsIn = playerTeams[~playerTeams.index.isin(playoffTeams.index)].sort_values(by=['winPoints'],ascending=[False]).iloc[0:1,:]
        playoffTeams = playoffTeams.append(pointsIn)
        playerTeams['highPoints'] = [int(x) for x in playerTeams['winPoints'] == playerTeams['winPoints'].max()]
        playerTeams['lowPoints'] = [int(x) for x in playerTeams['winPoints'] == playerTeams['winPoints'].min()]
        playerTeams['firstPlace'] = [int(x) for x in playerTeams.index == playoffTeams.index[0]]
        playerTeams['bye'] = [int(x) for x in playerTeams.index.isin(playoffTeams.index[0:2])]
        weeklyMaxes = resultsTable[resultsTable.winWeek <= 13].groupby('winWeek')['winPoints'].idxmax()

        playerTeams['weeklyHighPoints'] = playerTeams.apply(lambda x: resultsTable.iloc[weeklyMaxes]['winTeam'].to_list().count(x.name),axis=1)
        playerTeams['winPointsRemain'] = playerTeams.apply(lambda x: resultsTable.loc[resultsTable['winTeam']==x.name,['winPointsRemain']].sum(),axis=1)
        
        playerTeams['playoffs'] = [int(x) for x in playerTeams.index.isin(playoffTeams.index)]

        ##sim week 14
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[2]) &
                               (resultsTable['winWeek']==14)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[5]) &
                               (resultsTable['winWeek']==14)].iloc[0]['winPoints']):
            quarter1 = 2
        else:
            quarter1 = 5

        
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[3]) &
                               (resultsTable['winWeek']==14)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[4]) &
                               (resultsTable['winWeek']==14)].iloc[0]['winPoints']):
            quarter2 = 3
        else:
            quarter2 = 4
            
        ## sim week 15
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[0]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[quarter2]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints']):
            semi1 = 0
            semi1Loss = quarter2
        else:
            semi1 = quarter2
            semi1Loss = 0
            
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[1]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[quarter1]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints']):
            semi2 = 1
            semi2Loss = quarter1
        else:
            semi2 = quarter1
            semi2Loss = 1

        ## sim week 16
        
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi1]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi2]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints']):
            champ = semi1
            runup = semi2
        else:
            champ = semi2
            runup = semi1
            
        
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi1Loss]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi2Loss]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints']):
            thirdplace = semi1Loss
        else:
            thirdplace = semi2Loss
            
        playerTeams['firstPlace'] = [int(x) for x in playerTeams.index == playoffTeams.index[0]]

        playerTeams['champ'] = [int(x) for x in playerTeams.index == playoffTeams.index[champ]]
        playerTeams['runnerup'] = [int(x) for x in playerTeams.index == playoffTeams.index[runup]]
        playerTeams['thirdPlace'] = [int(x) for x in playerTeams.index == playoffTeams.index[thirdplace]]
        self.playerTeams = playerTeams

    def leagueResults(self):
        return self.playerTeams
        

    def _bestLineup(self, team, week, rosters, replacement):
        weekRoster = rosters[team+"-"+str(int(week))]
        self.playersUsed = []
        replace = replacement[replacement.predictedWeek == week]
        replaceDict = replace.set_index('playerPosition').to_dict(orient='index')
        lineup = [self._bestPlayer(pos,weekRoster,replaceDict) for pos in self.positions]
        return sum(lineup)

    def _bestPlayer(self, pos,roster,replace):
        randMean = replace[pos['replace']]['replaceMean']
        randDistr = [float(x) if x != '' else 0 for x in replace[pos['replace']]['replaceDistr'].split(',')]
        posRoster = roster[pos['replace']]
        randNumbs = [random.uniform(0,1) for x in posRoster.index]
        avail = posRoster[(posRoster.playProb.gt(randNumbs)) &
                        (~posRoster.playerId.isin(self.playersUsed)) &
                        (posRoster.predictionValue >= randMean)
                          ]
        if avail.empty:
            playerValue = random.choice(randDistr)
        else:
            bestPlayer = avail.loc[avail['predictionValue'].idxmax()]
            self.playersUsed.append(bestPlayer['playerId'])
            playerValue = random.choice([float(x) for x in bestPlayer['predictionDistr'].split(',')])
        return playerValue

