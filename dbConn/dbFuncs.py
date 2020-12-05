import pandas as pd
import pymysql

class InsertTable:
    def __init__(self, tableName):
        ## declare initial statement that contains table to be inserted into
        self.sqlStatement = "insert into %s values " % tableName
        self.updateStatement = ""

    def appendRow(self, dataArray):
        ## function run on each row of data to be inserted
        sqlString = "("

        for column in dataArray:
            if column[1] == 'string':
                ## appends escape characters to quotes to run sql inserts
                sqlString += ("'" +
                              column[0].replace("'","\\'").replace("\"","\\\"") +
                              "'"
                              )
            else:
                sqlString += str(column[0])

            sqlString += ","

        sqlString += "),"

        self.sqlStatement += sqlString

    def updateStatement(self, columnArray):
        ## optional; only run if table has entries that might be updated
        self.updateStatement = " on duplicate key update "
        for column in columnArray:
            self.updateStatement += (" %s = value(%s)," % (column,column))

        

    def returnStatement(self):

        return self.sqlStatement[:-1] + self.updateStatement[:-1]

## return team ids for all data pulled
## attempts matches using all possible spellings of team names
## if no match, adds new team id to be fixed later
class getTeamId(object):
    def __init__(self,conn):
        self.teamDict = pd.read_sql("select teamVariation, teamId from refData.nflTeamVariations",con=conn,index_col='teamVariation').to_dict('index')
            


    def addTeam(self, teamName,conn):
        with conn.cursor() as c:
            sql = "select teamId from refData.nflTeamVariations where teamVariation = '%s'"

            c.execute(sql%teamName)
            result = c.fetchone()
            if result == None:
                c.execute("select max(teamId) from refData.nflTeams2")
                maxValue = (c.fetchone()[0]) + 1
                c.execute("insert into refData.nflTeams2 (teamId) values (%d)"%maxValue)
                c.execute("insert into refData.nflTeamVariations values(%d,'%s')"%(maxValue,teamName))
                self.teamDict[teamName] = maxValue
                conn.commit()
            else:
                self.teamDict[teamName] = {'teamId' : result[0]}

    def teamId(self, teamName,conn):
        if teamName in self.teamDict:
            return self.teamDict[teamName]['teamId']
        else:
            self.addTeam(teamName, conn)

            return self.teamDict[teamName]['teamId']

        

## return player id from database,
## using either player name/season/team/position combo,
## or some other id unique to player from pulled system
## attempts matches, if none exist new player id is created

class getPlayerId:
    def __init__(self, year, conn, espn=False, depthChart=False,injury=False,stats=False):
        self.playerDict = pd.get_sql("select playerString, playerId from refData.playerNames where playerYear = %d" % year,con=conn,index=teamVariation).to_dict('index')
        self.espnDict = {}
        self.depthDict = {}
        self.injuryDict = {}
        self.statsDict = {}

    def addPlayer(self, playerName,conn,espnId = None, depthChartId = None, injuryId = None, statsId = None):
        ## check if player exists in database

        ## check if similar spelling but same team and position and year

        ## check if same spelling but different team

        ## check if same spelling but different position

        ## check if similar spelling and no other similar spellings

        ## add player to database
        pass

    def playerId(self, playerName):
        if teamName in self.playerDict:
            return self.teamDict[teamName]
        else:
            addPlayer
