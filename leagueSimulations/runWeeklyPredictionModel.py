import leagueResultsMethods as meth
from leaguePredictionModel import leaguePredictionTree
import traceback


import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect

season = 2020
week = 2

##pull all necessary data
with DOConnect() as tunnel:
    c, conn = connection(tunnel)
    c.execute("delete from leagueSims.modelPredictions where modelSeason = %d and predictionWeek = %d" % (season,week))
    conn.commit()
    conn.close()

    for pos in ['RB','QB','TE','WR','D/ST','K']:
        print(pos)
        c, conn = connection(tunnel)
        modelData = meth.pullModelData(season,week,pos, conn)
        conn.close()

        trainIndex = ((modelData.predictionSeason < season) & (modelData.predictionWeek == week)# | (
                #(modelData.predictionSeason == season) &
                #(modelData.predictionWeek < week) &
                #(modelData.predictedWeek < week)
            )#)

        predictIndex = ((modelData.predictionSeason == season) &
                        (modelData.predictionWeek == week))

        try:
            leagueModel = leaguePredictionTree(modelData[trainIndex])
            predResults = leagueModel.returnSimsModels(modelData[predictIndex])
        except:
            traceback.print_exc() 

        c,conn = connection(tunnel)
        sqlInsert = "insert into leagueSims.modelPredictions values "
        for i, row in predResults.iterrows():
            sqlAdd = "(%d, %d, %d, %d, '%s', %f, %f, %f, %f, %f),"

            sqlInsert += sqlAdd % (
                    row['modelSeason'],
                    row['predictedWeek'],
                    row['predictionWeek'],
                    row['playerId'],
                    pos,
                    row['modelPrediction'],
                    row['modelVariance'],
                    row['modelSkew'],
                    row['modelKurtosis'],
                    row['modelPlayProb']
                )
        try:
            c.execute(sqlInsert[:-1])
            conn.commit()
        except Exception as e:
            print(str(e))
        conn.close()
        print('end')

        del predResults
        del leagueModel
        del sqlInsert
        

        



