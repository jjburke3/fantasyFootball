
import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
from datetime import date, datetime, timedelta
import calendar
import traceback




from DOConn import connection
from DOsshTunnel import DOConnect
from depthCharts import pullDepthCharts
from injuredStatus import pullInjuredStatus
#from nnClass import fantasyModel

year = 2020
week = 16

for year in range(2014,2021):
    print(year)
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        for teamNum in range(0,32):
            try:
                sql = pullInjuredStatus(conn,year,week,teamNum)
                for statement in sql:
                    try:
                        pass
                        c.execute(statement)
                    except:
                        traceback.print_exc()
                        print(statement)

                conn.commit()
            except Exception as e:
                traceback.print_exc() 



        conn.close()
