from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from sklearn.metrics import r2_score

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
                             'sameTeam',
                             'qb1Status',
                             'rb1Status',
                             'rb2Status',
                             'wr1Status',
                             'wr2Status',
                             'wr3Status',
                             'te1Status',
                             'hasThirdDownBack',
                             'hasGoalLineBack']
        self.numReplaceZeroVariables = [
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
                                         'rankingPosRank',
                                         'rankingRank',
                                         'rankingTier'
                                         ]

        
        self.data = predictionData
        self.encoder = pp.OneHotEncoder(handle_unknown='ignore',sparse=False)
        self.encoderPlayed = pp.OneHotEncoder(handle_unknown='ignore',sparse=False)
        self._encodeXSet(self.data,fit=True)
        self._encodePlayedModel(self.data,fit=True)
        self.pointsModel = RandomForestRegressor(n_estimators=treeCount,max_features="sqrt",min_samples_leaf=5)
        self.playModel = RandomForestRegressor(n_estimators=treeCount,max_features="sqrt",min_samples_leaf=5)
        
        self._buildPlayModel()
        print('played model built')
        self._buildPointsModel()
        print('points model built')

        
        
    def _buildPointsModel(self):
        self.pointsModel.fit(self._encodeXSet(self.data),
                             self.data[['actualPoints']].fillna(0))

    def _buildPlayModel(self):
        self.playModel.fit(self._encodePlayedModel(self.data),
                             self.data[['gamesPlayed']].fillna(0))


    def returnSimsModels(self, predictedData):
        pointsModelPred = self.pointsModel.predict(self._encodeXSet(predictedData))
        predRange = self._pred_ints(self.pointsModel,self._encodeXSet(predictedData))
        playModel = self.playModel.predict(self._encodePlayedModel(predictedData))
        seasonEndedModel = None
        try:
            print("points r2:",r2_score(predictedData[['actualPoints']].fillna(0),pointsModelPred))
            print("played r2:",r2_score(predictedData[['gamesPlayed']].fillna(0),playModel))
        except:
            print("no actual data")
        playersData = pd.DataFrame({'playerId' : predictedData['playerId'],
                                    'modelSeason' : predictedData['predictionSeason'],
                                    'modelPrediction' : pointsModelPred,
                                    'predRange' : predRange,
                                    'modelPlayProb' : playModel})

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
        
            
            
                             
