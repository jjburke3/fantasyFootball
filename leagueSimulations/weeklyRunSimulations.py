
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback


from DOConn import connection
from DOsshTunnel import DOConnect

now = datetime.utcnow() - timedelta(hours=4)


year = (now - timedelta(days=60)).year

from runWeeklyPredictionModel import buildWeeklyModels
from runWeeklySims import runSims
from simFunctions import *




with DOConnect() as tunnel:
    c, conn = connection(tunnel)
    nflSched = pd.read_sql('''select nflSeason, nflWeek, min(nflDate) as minDate, max(nflDate) as maxDate
                 from scrapped_data2.nflSchedule
                 group by 1,2''',con=conn)
    conn.close()


finishedWeeks = nflSched.loc[nflSched.maxDate< now.date()].sort_values('maxDate',ascending=False)
comingWeeks = nflSched.loc[nflSched.maxDate>= now.date()].sort_values('maxDate')

if comingWeeks.shape[0] == 0:
    currentWeek = 0
    currentYear = year
    daysToWeekStart = 99999
    daysToWeekFinish = 99999
else:
    currentWeek = comingWeeks.iloc[0].nflWeek
    currentYear = comingWeeks.iloc[0].nflSeason
    daysToWeekStart = (comingWeeks.iloc[0].minDate - now.date()).days
    daysToWeekFinish = (comingWeeks.iloc[0].maxDate - now.date()).days
daysSinceWeekFinish = (now.date() - finishedWeeks.iloc[0].maxDate).days
finishedWeek = finishedWeeks.iloc[0].nflWeek
finishedSeason = finishedWeeks.iloc[0].nflSeason

print(year,'-',currentWeek)

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

## run projection models
buildWeeklyModels(year,currentWeek)
'''
## run simulations

runSims(year,currentWeek)
