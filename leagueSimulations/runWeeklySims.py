import leagueResultsMethods as meth
from simLeague import leagueSimulation
import traceback

import sys
sys.path.insert(0,'..')
sys.path.insert(0,'../dbConn')

from DOConn import connection
from DOsshTunnel import DOConnect

season = 2020
week = 2


with DOConnect() as tunnel:
    c, conn = connection(tunnel)
    try:
        results = meth.pullResults(season,week,conn)
    except Exception as e:
        print(str(e))



    try:
        currentRosters = meth.pullCurrentRosters(season,week, conn)
    except Exception as e:
        print(str(e))

    try:
        replaceValues = meth.pullReplacementNumbers(season,week,conn)
    except Exception as e:
        traceback.print_exc() 

    conn.close()


#predictions, replacementValues = leagueModel


for i in range(0,1):

    sim = leagueSimulation(currentRosters,replaceValues,results)
