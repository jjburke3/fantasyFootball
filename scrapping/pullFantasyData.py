
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')
sys.path.insert(0,'./espnLeagueData')
sys.path.insert(0,'./nflLeagueData')
sys.path.insert(0,'./rankingsData')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback


from DOConn import connection
from DOsshTunnel import DOConnect
from depthCharts import pullDepthCharts, nbcChartAttr
from pullRankings import pullFPRankings
from injuries import pullInjuries
from mysportsfeeds import returnWeekStats
from pullNflSchedule import pullLeagueSchedule
from leagueResults import pullLeagueData
from updateQueries import updateFunc

now = datetime.utcnow() - timedelta(hours=4)


year = (now - timedelta(days=60)).year

day = calendar.day_name[now.weekday()]

nowTime = now.time()
if now.hour > 4 and now.hour < 12:
    time = 'Morning'
elif now.hour < 17 and now.hour >= 12:
    time = 'Afternoon'
elif now.hour < 22 and now.hour >= 17:
    time = 'Evening'
else:
    time = 'Night'
print(time)
print(now.month)
print(now.day)
    
if ((now.month in (8,9,10,11,12,1) and time == 'Morning') or
        (now.day == 1 and time == 'Morning')):
## pull the nfl schedule on every day in season, and the 1st of month out of season
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


## week end pull fantasy and stats data
if (daysSinceWeekFinish == 1 and time == 'Night'):
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            sql = returnWeekStats(conn,finishedWeek,finishedSeason)
            for statement in sql:
                c.execute(statement)
                conn.commit()
        except Exception as e:
            traceback.print_exc()
        
        try:
            sql = updateFunc()
            for sqlCode in sql:
                try:
                    c.execute(sqlCode)
                    conn.commit()
                except Exception as e:
                    print(str(e))
        except Exception as e:
            traceback.print_exc()
        if currentWeek <= 17:
            try:
                sql = pullLeagueData(finishedSeason,finishedWeek,conn)
                for statement in sql:
                    c.execute(statement)
                    conn.commit()
            except Exception as e:
                traceback.print_exc() 

        conn.close()


## pull injury and depth chart data
if daysToWeekStart <= 50 and time != 'Night':
    print('go')
    if daysToWeekStart > 10 and currentWeek != 21:
        weekUsed = 0
    else:
        weekUsed = currentWeek
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            sql = pullInjuries(conn,year,weekUsed,day,time)
            for statement in sql:
                c.execute(statement)
            conn.commit()
        except Exception as e:
            traceback.print_exc()
        try:
            c.execute('''select max(chartVersion) as version
                     from scrapped_data2.depthCharts''')
            versionNo = (c.fetchone()[0]) + 1
            sql = pullDepthCharts(conn,year,weekUsed,day,time,versionNo)
            for statement in sql:
                c.execute(statement)
            sql = nbcChartAttr(conn,year,versionNo)
            for statement in sql:
                c.execute(statement)
            conn.commit()
            
            try:
                sql = pullFPRankings(conn,year,weekUsed,day,time,versionNo)
                for statement in sql:
                    c.execute(statement)
                conn.commit()
            except Exception as e:
                traceback.print_exc()
        except Exception as e:
            traceback.print_exc() 
        conn.close()
