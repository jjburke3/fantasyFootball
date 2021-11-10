
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback


from DOConn import connection
from DOsshTunnel import DOConnect



from runWeeklyPredictionModel import buildWeeklyModels
from runWeeklySims import runSims
from simFunctions import *


year = 2021
for currentWeek in range(9,-1,-1):

    print(year,'-',currentWeek)
    '''
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        sql = delete from leagueSims.standings
                 where standYear = %d
                 and standWeek = %d%(year,currentWeek)
        c.execute(sql)
        conn.commit()
        conn.close()
    '''

    ## get current rosters
    '''
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        sql = pullCurrentLineups(year,conn,currentWeek)
        try:
            for statement in sql:
                c.execute(statement)
        except Exception as e:
            print(str(e))
            traceback.print_exc()
        conn.commit()
        conn.close()

    ## build sim data tables
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            c.execute("call leagueSims.modelDataTables(%d,%d);" % (year,currentWeek))
            conn.commit()
        except Exception as e:
            print(str(e))
            traceback.print_exc()
        conn.close()
    '''
    ## run projection models
    #buildWeeklyModels(year,currentWeek)

    ## run simulations
    runSims(year,currentWeek)
