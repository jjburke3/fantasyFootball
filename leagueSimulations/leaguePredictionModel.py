from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

import pandas as pd
import numpy as np

import statistics as s

from sklearn import preprocessing as pp

from sklearn.model_selection import train_test_split

import math

import sys

class leaguePredictionTree():

    def __init__(self, predictionData,treeCount):
        self.catVariables = ['playerPosition',
                             'playerStatus',
                             'chartPosition',
                             'chartRank',
                             'chartRole',
                             'thirdDownBack',
                             'goalLineBack',
                             'pr',
                             'kr',
                             'byeWeek',
                             'predictPriorBye',
                             'homeTeam',
                             'priorWeekBye',
                             'followWeekBye',
                             'oppPriorWeekBye',
                             'oppFollowWeekBye',
                             'sameTeam',
                             'priorWeekPlayerStatus',
                             'priorWeekChartPosition',
                             'priorWeekChartRank',
                             'qb1Status',
                             'rb1Status',
                             'rb2Status',
                             'wr1Status',
                             'wr2Status',
                             'wr3Status',
                             'te1Status',
                             'hasThirdDownBack',
                             'hasGoalLineBack']
        self.numReplaceZeroVariables = ['seasonPoints',
                                        'priorWeekPoints',
                             'seasonGames',
                             'priorGame',
                             'seasonTargets',
                             'priorWeekTargets',
                             'seasonRushes',
                             'priorWeekRushes',
                             'weeksUntil'
                             ]
        self.numReplaceOtherVariables = ['age',
                                         'experience',
                                         'playerRating',
                                         'playerSpeed',
                                         'playerAgility',
                                         'playerCatch',
                                         'playerCarrying',
                                         'playerBCVision',
                                         'playerRouteRunning',
                                         'playerThrowPower',
                                         'playerThrowAccuracy',
                                         'playerAwareness',
                                         'playerInjury',

                                         'qb1Rating',
                                         'rb1Rating',
                                         'rb2Rating',
                                         'wr1Rating',
                                         'wr2Rating',
                                         'wr3Rating',
                                         'te1Rating',
                                         'ltRating',
                                         'lgRating',
                                         'cRating',
                                         'rgRating',
                                         'rtRating',
                                         'de1Rating',
                                         'de2Rating',
                                         'dt1Rating',
                                         'dt2Rating',
                                         'mlb1Rating',
                                         'mlb2Rating',
                                         'olb1Rating',
                                         'olb2Rating',
                                         'cb1Rating',
                                         'cb2Rating',
                                         'cb3Rating',
                                         's1Rating',
                                         's2Rating',
                                         's3Rating',
                                         'kRating',

                                         'oppQb1Rating',
                                         'oppRb1Rating',
                                         'oppRb2Rating',
                                        
                                         'oppWr1Rating',
                                         'oppWr2Rating',
                                         'oppWr3Rating',
                                        
                                         'oppTe1Rating',
                                         'oppTe2Rating',
                                        
                                         'oppLtRating',
                                         'oppLgRating',
                                         'oppCRating',
                                         'oppRgRating',
                                         'oppRtRating',
                                        
                                         'oppDe1Rating',
                                         'oppDe2Rating',
                                         'oppDt1Rating',
                                         'oppDt2Rating',
                                        
                                         'oppMlb1Rating',
                                         'oppMlb2Rating',
                                         'oppOlb1Rating',
                                         'oppOlb2Rating',
                                        
                                         'oppCb1Rating',
                                         'oppCb2Rating',
                                         'oppCb3Rating',
                                        
                                         'oppS1Rating',
                                         'oppS2Rating',
                                         'oppS3Rating',
                                         'oppKRating'
                                         ]

        
        self.data = predictionData
        self.playedIndex = predictionData.gamePlayed==1
        self.encoder = pp.OneHotEncoder(handle_unknown='ignore',sparse=False)
        self.encoderPlayed = pp.OneHotEncoder(handle_unknown='ignore',sparse=False)
        self._encodeXSet(self.data,fit=True)
        self._encodePlayedModel(self.data,fit=True)
        self.pointsModel = RandomForestRegressor(n_estimators=treeCount,max_features="sqrt")
        self.playedModel = RandomForestClassifier(n_estimators=treeCount,max_features="sqrt")
        
        self._buildPlayedModel()
        print('played model built')
        self._buildPointsModel()
##        print('points model built')
##        self._buildVarModel()
##        print('var model built')
##        self._buildSkewModel()
##        print('skew model built')
##        self._buildKurtosisModel()
##        print('kurtosis model built')

        
        
    def _buildPointsModel(self):
        self.pointsModel.fit(self._encodeXSet(self.data.loc[(self.playedIndex)]),
                             self.data.loc[(self.playedIndex),['actualPoints']].fillna(0))

    def _buildVarModel(self):
        actuals = list(self.data.loc[(self.playedIndex),['actualPoints']].fillna(0).values)
        predictions = list(self.pointsModel.predict(self._encodeXSet(
            self.data.loc[(self.playedIndex)])))
        self.varModel.fit(self._encodeXSet(self.data.loc[(self.playedIndex)]),
                          [(x1 - x2)**2 for (x1,x2) in zip(predictions,
                                                           actuals)])

    def _buildSkewModel(self):
        actuals = list(self.data.loc[(self.playedIndex),['actualPoints']].fillna(0).values)
        predictions = list(self.pointsModel.predict(self._encodeXSet(
            self.data.loc[(self.playedIndex)])))
        variances = list(self.varModel.predict(self._encodeXSet(
            self.data.loc[(self.playedIndex)])))
        self.skewModel.fit(self._encodeXSet(self.data.loc[(self.playedIndex)]),
                          [0 if x3 <0 else ((x1 - x2)/math.sqrt(x3))**3 for (x1,x2,x3) in zip(predictions,
                                                              actuals,
                                                              variances)])

    def _buildKurtosisModel(self):
        actuals = list(self.data.loc[(self.playedIndex),['actualPoints']].fillna(0).values)
        predictions = list(self.pointsModel.predict(self._encodeXSet(
            self.data.loc[(self.playedIndex)])))
        variances = list(self.varModel.predict(self._encodeXSet(
            self.data.loc[(self.playedIndex)])))
        self.kurtosisModel.fit(self._encodeXSet(self.data.loc[(self.playedIndex)]),
                          [0 if x3 <0 else ((x1 - x2)/math.sqrt(x3))**4 for (x1,x2,x3) in zip(predictions,
                                                                           actuals,
                                                                           variances)]
                          )

    def _buildPlayedModel(self):
        self.playedModel.fit(self._encodePlayedModel(self.data),
                             self.data[['gamePlayed']].fillna(0))


    def returnSimsModels(self, predictedData):
        pointsModelPred = self.pointsModel.predict(self._encodeXSet(predictedData))
        #varianceModel = self.varModel.predict(self._encodeXSet(predictedData))
        #skewModel = self.skewModel.predict(self._encodeXSet(predictedData))
        #kurtosisModel = self.kurtosisModel.predict(self._encodeXSet(predictedData))
        predRange = self._pred_ints(self.pointsModel,self._encodeXSet(predictedData))
        playedModel = self.playedModel.predict_proba(self._encodePlayedModel(predictedData))
        seasonEndedModel = None
        playersData = pd.DataFrame({'playerId' : predictedData['playerId'],
                                    'modelSeason' : predictedData['predictionSeason'],
                                    'predictionWeek' : predictedData['predictionWeek'],
                                    'predictedWeek' : predictedData['predictedWeek'],
                                    'modelPrediction' : pointsModelPred,
                                    'predRange' : predRange,
                                    #'modelVariance' : varianceModel,
                                    #'modelSkew' : skewModel,
                                    #'modelKurtosis' : kurtosisModel,
                                    'modelPlayProb' : playedModel[:,self.playedModel.classes_.tolist().index(1)]})

        return playersData

    def _encodeXSet(self, predictedData,fit=False):
        catFrame = predictedData[self.catVariables].applymap(str).fillna('')
        if fit:
            catVars = self.encoder.fit_transform(catFrame)
        else:
            catVars = self.encoder.transform(catFrame)

        numVars1 = predictedData[self.numReplaceZeroVariables].fillna(0)
        numVars2 = predictedData[self.numReplaceOtherVariables].fillna(-9999)
            

        return np.concatenate((catVars,numVars1,numVars2),axis=1)

    def _encodePlayedModel(self,predictedData,fit=False):
        playedCatVariables = [
                             'playerStatus',
                             'chartPosition',
                             'chartRank',
                             'chartRole',
                             'byeWeek',
                             'predictPriorBye',
                             'homeTeam',
                             'priorWeekBye',
                             'followWeekBye',
                             'oppPriorWeekBye',
                             'oppFollowWeekBye',
                             'sameTeam',
                             'qb1Status',
                             'rb1Status',
                             'rb2Status',
                             'wr1Status',
                             'wr2Status',
                             'wr3Status',
                             'te1Status']
        catFramePlayed = predictedData[playedCatVariables].applymap(str).fillna('')
        if fit:
            catVarsPlayed = self.encoderPlayed.fit_transform(catFramePlayed)
        else:
            catVarsPlayed = self.encoderPlayed.transform(catFramePlayed)
        playerdNumReplaceZeroVariables = [
                             'seasonGames',
                             'gamePlayed',
                             'seasonTargets',
                             'priorWeekTargets',
                             'seasonRushes',
                             'priorWeekRushes',
                             'weeksUntil'
                             ]
        playedNumReplaceOtherVariables = [
            'age',
            'experience',
            'playerRating',
            'playerInjury'
            ]
        numVars1Played = predictedData[playerdNumReplaceZeroVariables].fillna(0)
        numVars2Played = predictedData[playedNumReplaceOtherVariables].fillna(-9999)
        return np.concatenate((catVarsPlayed,numVars1Played,numVars2Played),axis=1)

    def _pred_ints(self,model, X):
        columnRanges = []
        for x in range(len(X)):
            entryRange = []
            preds = []
            for pred in model.estimators_:
                preds.append(pred.predict(X[x].reshape(1, -1))[0])
            for i in range(2,100,2):
                entryRange.append(np.percentile(preds,i))
            columnRanges.append(','.join([str(round(n,2)) for n in entryRange]))
        return columnRanges
        
            
            
                             
