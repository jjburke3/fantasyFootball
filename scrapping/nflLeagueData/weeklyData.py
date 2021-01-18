
import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
from datetime import date, datetime, timedelta, time
import calendar




from DOConn import connection
from DOsshTunnel import DOConnect
from updateQueries import updateFunc
from mysportsfeeds import returnWeekStats

now = datetime.utcnow() - timedelta(hours=4)


year = (now - timedelta(days=20)).year
yearStart = date(year,9,9)
if now.date() < yearStart:
    week = 0
elif now.date() <= yearStart + timedelta(days=(7*1)):
    week = 1
elif now.date() <= yearStart + timedelta(days=(7*2)):
    week = 2
elif now.date() <= yearStart + timedelta(days=(7*3)):
    week = 3
elif now.date() <= yearStart + timedelta(days=(7*4)):
    week = 4
elif now.date() <= yearStart + timedelta(days=(7*5)):
    week = 5
elif now.date() <= yearStart + timedelta(days=(7*6)):
    week = 6
elif now.date() <= yearStart + timedelta(days=(7*7)):
    week = 7
elif now.date() <= yearStart + timedelta(days=(7*8)):
    week = 8
elif now.date() <= yearStart + timedelta(days=(7*9)):
    week = 9
elif now.date() <= yearStart + timedelta(days=(7*10)):
    week = 10
elif now.date() <= yearStart + timedelta(days=(7*11)):
    week = 11
elif now.date() <= yearStart + timedelta(days=(7*12)):
    week = 12
elif now.date() <= yearStart + timedelta(days=(7*13)):
    week = 13
elif now.date() <= yearStart + timedelta(days=(7*14)):
    week = 14
elif now.date() <= yearStart + timedelta(days=(7*15)):
    week = 15
elif now.date() <= yearStart + timedelta(days=(7*16)):
    week = 16
elif now.date() <= yearStart + timedelta(days=(7*17)):
    week = 17
#elif now.date() > yearStart + timedelta(days=(7*17)):
#    sys.exit()
else:
    week = 0

day = calendar.day_name[now.weekday()]

week = 13
for week in range(18,19):
    print('week',week)
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            sql = returnWeekStats(conn,week,year)
            for statement in sql:
                try:
                    c.execute(statement)
                    conn.commit()
                except Exception as e:
                    print(str(e))
        except Exception as e:
            print(str(e))
        try:
            sql = updateFunc()
            for sqlCode in sql:
                try:
                    temp = 1
                    c.execute(sqlCode)
                    conn.commit()
                except Exception as e:
                    print(str(e))
        except Exception as e:
            print(str(e))




        conn.close()
