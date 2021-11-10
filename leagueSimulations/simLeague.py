import random
import numpy as np
import math
#from filterPlayer import returnPlayer, returnLineupValues



class leagueSimulation(object):

    def __init__(self, season, predictionValues, replacementValues, pastResults, week):
        self.season = season
        self.pastResults = pastResults
        self.predictionValues = predictionValues
        self.replacementValues = replacementValues
        self.week = week

        self.positions = [{'key' : 'QB', 'allow' : [0], 'replace' : 'QB'},
                     {'key' : 'RB', 'allow' : [1], 'replace' : 'RB'},
                     {'key' : 'WR', 'allow' : [2], 'replace' : 'WR'},
                     {'key' : 'TE', 'allow' : [3], 'replace' : 'TE'},
                     {'key' : 'D/ST', 'allow' : [4], 'replace' : 'DST'},
                     {'key' : 'K', 'allow' : [5], 'replace' : 'K'},
                     {'key' : 'RBWR1', 'allow' : [1,2], 'replace' : 'RBWR'},
                     {'key' : 'RBWR2', 'allow' : [1,2], 'replace' : 'RBWR'},
                     {'key' : 'FLEX', 'allow' : [1,2,3], 'replace' : 'Flex'}
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
        self.burkeAdjust = random.choice(range(1,6))/100
        self.burkeAdjust = 0
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
                                                  resultsTable[resultsTable.winWeek == 14].sort_values(by=['winPoints'],ascending=['False']).iloc[6,:]['winPoints'] if (x['winWeek'] == 14 and x['winSeason'] >= 2021)
                                                  else 0 if x['winOpp'] is None else
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
        playerTeams = resultsTable[resultsTable.winWeek <= 14].groupby('winTeam')['winWin','winLoss','winPoints'].sum()
        if self.season > 2017:
            playoffTeams = playerTeams.sort_values(by=['winWin','winLoss','winPoints'],ascending=[False,True,False]).iloc[0:5,:]
            pointsIn = playerTeams[~playerTeams.index.isin(playoffTeams.index)].sort_values(by=['winPoints'],ascending=[False]).iloc[0:1,:]
            playoffTeams = playoffTeams.append(pointsIn)
        else:
            playoffTeams = playerTeams.sort_values(by=['winWin','winLoss','winPoints'],ascending=[False,True,False]).iloc[0:6,:]
        
        playerTeams['highPoints'] = [int(x) for x in playerTeams['winPoints'] == playerTeams['winPoints'].max()]
        playerTeams['lowPoints'] = [int(x) for x in playerTeams['winPoints'] == playerTeams['winPoints'].min()]
        playerTeams['firstPlace'] = [int(x) for x in playerTeams.index == playoffTeams.index[0]]
        playerTeams['bye'] = [int(x) for x in playerTeams.index.isin(playoffTeams.index[0:2])]
        weeklyMaxes = resultsTable[resultsTable.winWeek <= 13].groupby('winWeek')['winPoints'].idxmax()

        playerTeams['weeklyHighPoints'] = playerTeams.apply(lambda x: resultsTable.iloc[weeklyMaxes]['winTeam'].to_list().count(x.name),axis=1)
        playerTeams['winPointsRemain'] = playerTeams.apply(lambda x: resultsTable.loc[resultsTable['winTeam']==x.name,['winPointsRemain']].sum(),axis=1)
        
        playerTeams['playoffs'] = [int(x) for x in playerTeams.index.isin(playoffTeams.index)]

        ##sim week 15
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[2]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[5]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints']):
            quarter1 = 2
        else:
            quarter1 = 5

        
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[3]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[4]) &
                               (resultsTable['winWeek']==15)].iloc[0]['winPoints']):
            quarter2 = 3
        else:
            quarter2 = 4
            
        ## sim week 16
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[0]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[quarter2]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints']):
            semi1 = 0
            semi1Loss = quarter2
        else:
            semi1 = quarter2
            semi1Loss = 0
            
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[1]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[quarter1]) &
                               (resultsTable['winWeek']==16)].iloc[0]['winPoints']):
            semi2 = 1
            semi2Loss = quarter1
        else:
            semi2 = quarter1
            semi2Loss = 1

        ## sim week 17
        
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi1]) &
                               (resultsTable['winWeek']==17)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi2]) &
                               (resultsTable['winWeek']==17)].iloc[0]['winPoints']):
            champ = semi1
            runup = semi2
        else:
            champ = semi2
            runup = semi1
            
        
        if (resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi1Loss]) &
                               (resultsTable['winWeek']==17)].iloc[0]['winPoints'] >
            resultsTable.loc[(resultsTable['winTeam']==playoffTeams.index[semi2Loss]) &
                               (resultsTable['winWeek']==17)].iloc[0]['winPoints']):
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
        weekRoster['totalRoster']['randNum'] = np.random.uniform(0,1,size=len(weekRoster['totalRoster'].index))
        self.playersUsed = []
        lineup = [self._bestPlayer(pos,weekRoster,replacement[week],team) for pos in self.positions]
        #return sum([x['value'] for x in lineup])
        return sum(lineup)

    def _bestPlayer(self, pos,roster,replace,team):
        randMean = replace[pos['replace']]['replaceMean']
        randDistr = replace[pos['replace']]['replaceDistr']
        rosIndex = roster['totalRoster'].apply(lambda x: self._returnPlayer(x.name,
                                                                            x['predictionValue'],
                                                                            x['playProb'],
                                                                            x['randNum'],
                                                                            x['playerPosition'],
                                                                            randMean,
                                                                            pos['allow'],#dtype=np.int32),
                                                                            self.playersUsed#dtype=np.int32)
                                                                                   ),axis=1)
        avail = roster['totalRoster'][rosIndex]
        if avail.empty:
            #playerName = 'replace-'+pos['key']
            playerValue = random.choice(randDistr)
        else:
            bestPlayer = avail.loc[avail['predictionValue'].idxmax()]
            #playerName = str(bestPlayer['playerId'])+"-"+pos['key']
            self.playersUsed.append(bestPlayer.name)
            if team == 'JJ Burke':
                adjust = 1 - (self.burkeAdjust * (random.uniform(0.5,2)))
            else:
                adjust = 1
            playerValue = random.choice([float(x)*float(adjust) for x in bestPlayer['predictionDistr']])
        #return {'player' : playerName, 'value' : playerValue}
        return playerValue

    def _returnPlayer(self, playerId, predictionValue, playProb, randNum, playerPosition, randMean,
                      allowedPos, usedPlayers):
        if playerPosition not in allowedPos:
            return False
        if predictionValue < randMean:
            return False
        if playProb < randNum:
            return False
        if playerId in usedPlayers:
            return False
        return True

