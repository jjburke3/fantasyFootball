
import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
from datetime import date, datetime, timedelta
import calendar
import traceback




from DOConn import connection
from DOsshTunnel import DOConnect
from leagueResults import pullLeagueData

now = datetime.utcnow() - timedelta(hours=4)


year = (now - timedelta(days=20)).year

yearStart = date(year,9,8)
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

else:
    week = 0

week = 2
for week in range(7,8):
    print('week-',week)
    day = calendar.day_name[now.weekday()]

    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            sql = pullLeagueData(year,week,conn)
            try:
                c.execute(sql[0])
                conn.commit()
            except Exception as e:
                print(str(e))
            try:
                c.execute(sql[1])
                conn.commit()
            except Exception as e:
                print(str(e))
            try:
                c.execute('''update la_liga_data.wins
                        join (
                            select winSeason as oppSeason, winWeek as oppWeek, winTeam as opp, winPoints as oppPoint from la_liga_data.wins
                            where winSeason = %d and winWeek = %d) a on winSeason = oppSeason and winWeek = oppWeek
                            and winOpp = opp
                            set winPointsAgs = oppPoint, 
                            winWin = case when winPoints > oppPoint then 1 else 0 end, 
                            winLoss = case when winPoints < oppPoint then 1 else 0 end, 
                            winTie = case when winPoints = oppPoint then 1 else 0 end''' % (year,week))
            except Exception as e:
                print(str(e))
            conn.commit()
        except Exception as e:
            traceback.print_exc() 




        conn.close()
