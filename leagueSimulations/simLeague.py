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

    def simSeason(self):
        resultsTable = self.pastResults.copy()
        resultsTable['winPoints'] = resultsTable.apply(lambda x:
                                                     x['winPoints'] if not np.isnan(x['winPoints'])
                                                     #else random.uniform(100,120),
                                                     else self._bestLineup(x['winTeam'],x['winWeek'],self.predictionValues,self.replacementValues),
                                                     axis=1)
        
        resultsTable['winPointsAgs'] = resultsTable.apply(lambda x:
                                                  0 if x['winOpp'] is None else
                                                  x['winPointsAgs'] if not np.isnan(x['winPointsAgs'])
                                                  else resultsTable[(
                                                      (resultsTable['winSeason'] == x['winSeason']) &
                                                      (resultsTable['winWeek'] == x['winWeek']) &
                                                      (resultsTable['winTeam'] == x['winOpp'])
                                                      )].winPoints.values[0],
                                                  axis=1)
        resultsTable['winWin'] = resultsTable.apply(lambda x:
                                                  x['winWin'] if not np.isnan(x['winWin'])
                                                  else 1 if x['winPoints'] > x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        resultsTable['winLoss'] = resultsTable.apply(lambda x:
                                                  x['winLoss'] if not np.isnan(x['winLoss'])
                                                  else 1 if x['winPoints'] < x['winPointsAgs']
                                                  else 0,
                                                  axis=1)
        resultsTable['winTie'] = resultsTable.apply(lambda x:
                                                  x['winTie'] if not np.isnan(x['winTie'])
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
        
        playerTeams['playoffs'] = [int(x) for x in playerTeams.index.isin(playoffTeams.index)]

        ##sim week 14
##        print(resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[2]) &
##                               (resultsTable['winWeek']==14),['winPoints']].get_value())
##        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[2]) &
##                               (resultsTable['winWeek']==14),['winPoints']].values()[0] >
##            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[5]) &
##                               (resultsTable['winWeek']==14),['winPoints']].values()[0]):
##            quarter1 = 2
##        else:
##            quarter1 = 5
                
            

        ## sim week 15

        ## sim week 16

        #playerTeams['firstPlace'] = 0
        #playerTeams['secondPlace'] = 0
        #playerTeams['thirdPlace'] = 0
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
        randVar = replace[pos['replace']]['replaceVar']
        randSkew = replace[pos['replace']]['replaceSkew']
        posRoster = roster[pos['replace']]
        randNumbs = [random.uniform(0,1) for x in posRoster.index]
        avail = posRoster[(posRoster.playProb.gt(randNumbs)) &
                        (~posRoster.playerId.isin(self.playersUsed)) &
                        (posRoster.predictionValue >= randMean)
                          ]
        if avail.empty:
            playerValue = skewnorm.rvs(a=randSkew,
                                              loc=randMean,
                                              scale=math.sqrt(randVar))
        else:
            bestPlayer = avail.loc[avail['predictionValue'].idxmax()]
            self.playersUsed.append(bestPlayer['playerId'])
            playerValue = skewnorm.rvs(a=bestPlayer['predictionSkew'],
                                              loc=bestPlayer['predictionValue'],
                                              scale=math.sqrt(bestPlayer['predictionVar'])*2)
        return playerValue

