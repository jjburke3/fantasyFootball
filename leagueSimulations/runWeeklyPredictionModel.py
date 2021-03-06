import leagueResultsMethods as meth
from leaguePredictionModel import leaguePredictionTree
import traceback


import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect
for week in range(16,-1,-1):
    for season in range(2020,2016,-1):
        ##pull all necessary data
        with DOConnect() as tunnel:
            c, conn = connection(tunnel)
            c.execute("delete from leagueSims.modelPredictions where modelSeason = %d and predictionWeek = %d" % (season,week))
            conn.commit()
            conn.close()

            for pos in ['QB','RB','WR','TE','D/ST','K']:
                print(str(season)+"-"+str(week)+"-"+pos)
                c, conn = connection(tunnel)
                modelData = meth.pullModelData(season,week,pos, conn)
                conn.close()

                trainIndex = ((modelData.predictionSeason < season) & (modelData.predictionWeek == week))

                predictIndex = ((modelData.predictionSeason == season) &
                                (modelData.predictionWeek == week))

                treeCount = 200

                try:
                    leagueModel = leaguePredictionTree(modelData[trainIndex],treeCount)
                    predResults = leagueModel.returnSimsModels(modelData[predictIndex])
                except:
                    traceback.print_exc()


                c,conn = connection(tunnel)
                sqlInsert = "insert into leagueSims.modelPredictions values "
                for i, row in predResults.iterrows():
                    sqlAdd = "(%d, %d, %d, %d, '%s', %f, '%s', %f),"

                    sqlInsert += sqlAdd % (
                            row['modelSeason'],
                            row['predictedWeek'],
                            row['predictionWeek'],
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
                

                



