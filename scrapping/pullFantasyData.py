
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')
sys.path.insert(0,'./espnLeagueData')
sys.path.insert(0,'./nflLeagueData')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback


from DOConn import connection
from DOsshTunnel import DOConnect
from depthCharts import pullDepthCharts
from injuries import pullInjuries
from pullNflSchedule import pullLeagueSchedule

now = datetime.utcnow() - timedelta(hours=4)


year = (now - timedelta(days=60)).year

day = calendar.day_name[now.weekday()]

nowTime = now.time()
if now.hour > 3 and now.hour < 14:
    time = 'Morning'
elif now.hour < 18:
    time = 'Afternoon'
elif now.hour < 20:
    time = 'Evening'
else:
    time = 'Night'
if ((now.month in (8,9,10,11,12,1) and day == 'Wednesday' and time == 'Morning') or
        (now.day == 1 and time == 'Morning')):
## pull the nfl schedule on wednesdays in season, and the 1st of month out of season
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            sql = pullLeagueSchedule(conn,year)
            for statement in sql:
                try:
                    c.execute(statement)
                except:
                    print(statement)
                    traceback.print_exc()
            conn.commit()
        except Exception as e:
            print(str(e))
        conn.close()

## get nfl scheule to assign weeks
with DOConnect() as tunnel:
    c, conn = connection(tunnel)
    nflSched = pd.read_sql('''select nflSeason, nflWeek, min(nflDate) as minDate, max(nflDate) as maxDate
                 from scrapped_data2.nflSchedule
                 group by 1,2''',con=conn)
    conn.close()


finishedWeeks = nflSched.loc[nflSched.maxDate< now.date()].sort_values('maxDate',ascending=False)
comingWeeks = nflSched.loc[nflSched.maxDate>= now.date()].sort_values('maxDate')


currentWeek = comingWeeks.iloc[0].nflWeek
currentYear = comingWeeks.iloc[0].nflSeason


daysToWeekStart = (comingWeeks.iloc[0].minDate - now.date()).days
daysToWeekFinish = (comingWeeks.iloc[0].maxDate - now.date()).days
daysSinceWeekFinish = (now.date() - finishedWeeks.iloc[0].maxDate).days


## week end pull fantasy and stats data
if daysSinceWeekFinish == 1 and time == 'Night':
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            sql = returnWeekStats(conn,currentWeek-1,currentYear)
            for statement in sql:
                c.execute(statement)
                conn.commit()
        except Exception as e:
            print(str(e))
        if currentWeek <= 17:
            try:
                sql = temp
                for statement in pullLeagueData(currentYear,currentWeek-1,conn):
                    c.execute(statement)
                    conn.commit()
            except Exception as e:
                print(str(e)


## pull injury and depth chart data
    
