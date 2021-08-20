import sys
sys.path.insert(0,'../..')
sys.path.insert(0,'../../dbConn')
from datetime import date, datetime, timedelta
import calendar
import pandas as pd

import traceback

from DOConn import connection
from DOsshTunnel import DOConnect

from pullRankings import pullRankings


now = datetime.utcnow() - timedelta(hours=4)




rankingsList = [
        {'year' : 2016,
         'link' : 'https://web.archive.org/web/20160822171245/https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
         },
        {'year' : 2017,
         'link' : 'https://web.archive.org/web/20170830160039/https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
         },
        {'year' : 2018,
         'link' : 'https://web.archive.org/web/20180825115958/https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
         },
        {'year' : 2019,
         'link' : 'https://web.archive.org/web/20190903001905/https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
         },
        {'year' : 2020,
         'link' : 'https://web.archive.org/web/20200830104840/https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
         },
        {'year' : 2021,
         'link' : 'https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
         }
    ]


for rankingYear in rankingsList:
    with DOConnect() as tunnel:
        c, conn = connection(tunnel)
        try:
            c.execute('''select max(rankingVersion) as version
                     from scrapped_data2.fantasyProsRankings''')
            try:
                versionNo = (c.fetchone()[0]) + 1
            except:
                versionNo = 0
            print(versionNo)
            sql = pullFPRankings(conn,
                                  rankingYear['year'],
                                  0,
                                  '',
                                  '',
                                  versionNo,
                                  url=rankingYear['link'])
            for statement in sql:
                c.execute(statement)
            conn.commit()
        except Exception as e:
            traceback.print_exc() 
        conn.close()
