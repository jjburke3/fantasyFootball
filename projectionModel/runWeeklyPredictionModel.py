import leagueResultsMethods as meth
from leaguePredictionModel import leaguePredictionTree
import traceback


import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect
for season in range(2021,2022,1):
    ##pull all necessary data
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        c.execute("delete from seasonPredictions.modelPredictions where modelSeason = %d" % (season))
        conn.commit()
        conn.close()

        for pos in ['QB','RB','WR','TE','D/ST','K']:
            print(str(season)+"-"+pos)
            c, conn = connection(tunnel)
            modelData = meth.pullModelData(season,pos, conn)
            conn.close()

            trainIndex = ((modelData.predictionSeason < season))

            predictIndex = ((modelData.predictionSeason == season))

            treeCount = 500

            try:
                leagueModel = leaguePredictionTree(modelData[trainIndex],treeCount)
                predResults = leagueModel.returnSimsModels(modelData[predictIndex])
            except:
                traceback.print_exc()


            c,conn = connection(tunnel)
            sqlInsert = "insert into seasonPredictions.modelPredictions values "
            for i, row in predResults.iterrows():
                sqlAdd = "(%d, %d, '%s', %f, '%s', %f),"

                sqlInsert += sqlAdd % (
                        row['modelSeason'],
                        row['playerId'],
                        pos,
                        row['modelPrediction'],
                        row['predRange'],
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
            del modelData
            

            



