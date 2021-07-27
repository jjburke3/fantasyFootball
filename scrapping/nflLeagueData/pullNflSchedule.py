import requests
import traceback
from bs4 import BeautifulSoup as bs
import sys
sys.path.insert(0,'..')
sys.path.insert(0,'..\..')
sys.path.insert(0,'../../dbConn')

from dbFuncs import *


def pullLeagueSchedule(conn, year):
    teams = getTeamId(conn)

    sql = InsertTable("scrapped_data2.nflSchedule")

    sql.updateStatement(['nflDate','nflTime','nflHomeTeam','nflRoadTeam',
                         'nflHomeScore','nflRoadScore',
                         'nflHomeYards','nflRoadYards',
                         'nflHomeTO','nflRoadTO',
                         'createDateTime'])

    months = {'January' : 1,
              'February' : 2,
              'March' : 3,
              'April' : 4,
              'May' : 5,
              'June' : 6,
              'July' : 7,
              'August' : 8,
              'September' : 9,
              'October' : 10,
              'November' : 11,
              'December' : 12}

    weeks = {'Pre0' : -4,
             'Pre1' : -3,
             'Pre2' : -2,
             'Pre3' : -1,
             'WildCard' : 18,
             'Division' : 19,
             'ConfChamp' : 20,
             'SuperBowl' : 21}

    url = 'https://www.pro-football-reference.com/years/%d/games.htm' % year
    r = requests.get(url)

    soup = bs(r.content,'html.parser')

    table = soup.find('div',{"id":"all_games"}).find('table',{'id':'games'})
    gameNum = 0
    rows = table.find_all('tr')
    priorWeek = None
    for row in rows:
        try:
            week = row.find('th',{'data-stat':'week_num'}).text
            if(priorWeek == week):
                gameNum += 1
            else:
                gameNum = 0
                
            day = row.find('td',{'data-stat':'game_day_of_week'}).text
            date = row.find('td',{'data-stat':'game_date'}).text
            time = row.find('td',{'data-stat':'gametime'}).text
            location = row.find('td',{'data-stat':'game_location'}).text
            if location == '@':
                homeTeam = row.find('td',{'data-stat':'loser'}).text
                roadTeam = row.find('td',{'data-stat':'winner'}).text
                homePoints = row.find('td',{'data-stat':'pts_lose'}).text
                roadPoints = row.find('td',{'data-stat':'pts_win'}).text
                homeYards = row.find('td',{'data-stat':'yards_lose'}).text
                roadYards = row.find('td',{'data-stat':'yards_win'}).text
                homeTO = row.find('td',{'data-stat':'to_lose'}).text
                roadTO = row.find('td',{'data-stat':'to_win'}).text
            else:
                homeTeam = row.find('td',{'data-stat':'winner'}).text
                roadTeam = row.find('td',{'data-stat':'loser'}).text
                homePoints = row.find('td',{'data-stat':'pts_win'}).text
                roadPoints = row.find('td',{'data-stat':'pts_lose'}).text
                homeYards = row.find('td',{'data-stat':'yards_win'}).text
                roadYards = row.find('td',{'data-stat':'yards_lose'}).text
                homeTO = row.find('td',{'data-stat':'to_win'}).text
                roadTO = row.find('td',{'data-stat':'to_lose'}).text


            if week not in ('Week',''):
                if date[:3] in ('Jan','Feb','Mar'):
                    date = (str(year+1) + "-" +
                            str(months[date.split(' ')[0]]).zfill(2) + "-" +
                            str(date.split(' ')[1]).zfill(2))
                else:
                    date = (str(year) + "-" +
                            str(months[date.split(' ')[0]]).zfill(2) + "-" +
                            str(date.split(' ')[1]).zfill(2))

                if (time[-2:] == 'PM') & (time[:2] != '12'):
                    time = (str(int(time.split(':')[0])+12).zfill(2) + ":" +
                            str(time.split(':')[1][:-2]).zfill(2) + ":" +
                                "00")
                else:
                    time = (str(int(time.split(':')[0])).zfill(2) + ":" +
                            str(time.split(':')[1][:-2]).zfill(2) + ":" +
                                "00")

                if week in weeks:
                    weekInt = weeks[week]
                else:
                    weekInt = week

                #sql.updateStatement(['nflDate'])
                def replaceBlank(string):
                    if string == '':
                        string = 'NULL'
                    return string

                sql.appendRow([
                        [str(year),''],
                        [str(weekInt),''],
                        [str(gameNum),''],
                        [date,'string'],
                        [time,'string'],
                        [teams.teamId(homeTeam,conn),''],
                        [teams.teamId(roadTeam,conn),''],
                        [replaceBlank(homePoints),''],
                        [replaceBlank(roadPoints),''],
                        [replaceBlank(homeYards),''],
                        [replaceBlank(roadYards),''],
                        [replaceBlank(homeTO),''],
                        [replaceBlank(roadTO),''],
                        ['current_timestamp()','']
                    ])
                priorWeek = week
        except Exception as e:
            traceback.print_exc()
    return [sql.returnStatement()]

