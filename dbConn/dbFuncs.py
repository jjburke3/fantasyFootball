import pandas as pd
import pymysql
import re

class InsertTable:
    ## initilize with table name to be inserted into
    ## add rows with appendRow funciton, with a list of lists,
    ## containing datastring and whether its inserted as string or number
    
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
    ## class inializes by pulling all available team name variations, with connection as variable
    ## when returning team id use teamId function; if not available one will be created
    def __init__(self,conn):
        self.teamDict = pd.read_sql("select teamVariation, teamId from refData.nflTeamVariations",
                                    con=conn,index_col='teamVariation').to_dict('index')
            


    def _addTeam(self, teamName,conn):
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
            self._addTeam(teamName, conn)

            return self.teamDict[teamName]['teamId']

        

## return player id from database,
## using either player name/season/team/position combo,
## or some other id unique to player from pulled system
## attempts matches, if none exist new player id is created

class getPlayerId:
    def __init__(self, year, conn, espn=False, depthChart=False,injury=False,stats=False):
        self.playerDict = pd.get_sql("select playerString, playerId from refData.playerNames where playerYear = %d" % year,
                                     con=conn,index_col='playerString').to_dict('index')
        self.espnDict = {}
        self.depthDict = {}
        self.injuryDict = {}
        self.statsDict = {}
        if espn:
            self.espnDict = pd.get_sql("select espnId, playerId from refData.playerIds where espnId is not null",
                                       con=conn,index_col='espnId').to_dict('index')
        if depthChart:
            self.depthDict = pd.get_sql("select depthChartsId, playerId from refData.playerIds where depthChartsId is not null",
                                       con=conn,index_col='depthChartsId').to_dict('index')
        if injury:
            self.injuryDict = pd.get_sql("select injuryId, playerId from refData.playerIds where injuryId is not null",
                                       con=conn,index_col='injuryId').to_dict('index')
        if stats:
            self.statsDict = pd.get_sql("select statsId, playerId from refData.playerIds where statsId is not null",
                                       con=conn,index_col='statsId').to_dict('index')

    def _addPlayer(self, playerName,conn,espnId = 'NULL', depthChartId = 'NULL',
                   injuryId = 'NULL', statsId = 'NULL'):
        removeString = ['\.',"'","_",' Jr$',' JR$',' Sr$',' SR$',' III$',' II$',' IV$',' V$',' VI$']
        
        playerApprox = playerName[0]
        for s in removeString:
            playerApprox = re.sub(s,'',playerApprox)
        anyID = False
        idCheck = 'join refData.playerIds b on b.playerId = a.playerId'
        idUpdate = "update refData.playerids set "
        if espnId != 'NULL':
            anyId = True
            idCheck += " and espnId is null"
            idUpdate += " espnId = %s " % espnId
        if depthChartId != 'NULL':
            anyId = True
            idCheck += " and depthChartId is null"
            idUpdate += " depthChartId = %s " % depthChartId
        if injuryId != 'NULL':
            anyId = True
            idCheck += " and injuryId is null"
            idUpdate += " injuryId = %s " % injuryId
        if statsId != "NULL":
            anyId = True
            idCheck += " and statsId is null"
            idUpdate += " statsId = %s " % statsId

        idUpdate += " where playerId = %d"

        if !anyId:
            idCheck = ""
        
        
        c = conn.cursor()
        playerId = None
        ## check if player exists in database for different year
        c.execute('''select a.playerId from refData.playerNames a
                    %s
                    where a.playerName = '%s'
                    and playerTeam = %s
                    and playerPosition = '%s'
                    and playerYear between %s - 3 and %s''' %
                  (idCheck, playerName[0], str(playerName[1]),
                   playerName[2], str(playerName[3]), str(playerName[3])))
        playerId = c.fetchone()
        if playerId != None:
            c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                       str(playerName[1]), playerName[2], '-'.join(playerName), "NULL"))
            if anyId:
                c.execute(idUpdate % playerId)
            return playerId
        ## check if similar spelling but same team and position and year
        c.execute('''select a.playerId from refData.playerNames a
                    %s
                    where a.playerApprox = '%s'
                    and playerTeam = %s
                    and playerPosition = '%s'
                    and playerYear = %s''' %
                  (idCheck, playerApprox, str(playerName[1]),
                   playerName[2], str(playerName[3])))
        playerId = c.fetchone()
        if playerId != None:
            c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                       str(playerName[1]), playerName[2], '-'.join(playerName), "NULL"))
            if anyId:
                c.execute(idUpdate % playerId)
            return playerId
        ## check if same spelling but different team
        c.execute('''select a.playerId from refData.playerNames a
                    %s
                    where a.playerName = '%s'
                    and playerPosition = '%s'
                    and playerYear = %s''' %
                  (idCheck, playerName[0], 
                   playerName[2], str(playerName[3])))
        playerId = c.fetchone()
        if playerId != None:
            c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                       str(playerName[1]), playerName[2], '-'.join(playerName), "NULL"))
            if anyId:
                c.execute(idUpdate % playerId)
            return playerId

        ## check if same spelling but different position
        c.execute('''select a.playerId from refData.playerNames a
                    %s
                    where a.playerName = '%s'
                    and playerTeam = %s
                    and playerYear = %s''' %
                  (idCheck, playerName[0], 
                   str(playerName[1]), str(playerName[3])))
        playerId = c.fetchone()
        if playerId != None:
            c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                       str(playerName[1]), playerName[2], '-'.join(playerName), "NULL"))
            if anyId:
                c.execute(idUpdate % playerId)
            return playerId

        ## check if similar spelling and no other similar spellings
        c.execute('''select a.playerId from refData.playerNames a
                    %s
                    where a.playerApprox = '%s'
                    and (select count(distinct playerId) from refData.playerNames c
                        where a.playerApprox = c.playerApprox) = 1

                    ''' %
                  (idCheck, playerApprox))
        playerId = c.fetchone()
        if playerId != None:
            c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                       str(playerName[1]), playerName[2], '-'.join(playerName), "NULL"))
            if anyId:
                c.execute(idUpdate % playerId)
            return playerId

        ## add player to database
        c.execute("select max(playerId) from refData.playerIds")
        playerId = (c.fetchone()[0]) + 1
        c.execute("insert into refData.playerIds values (%s, %s, %s, %s, %s, '%s')" %
                  (str(playerId), str(espnId), str(statsId), str(depthChartsId),
                   str(injuryId), playerName[0]))
        c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                   str(playerName[1]), playerName[2], '-'.join(playerName), "NULL"))
        conn.commit()
    
        return playerId


    def _insertNameString(id, name, approx, year, team, position, totalString):
        return ("insert into refData.playerNames values(%s, '%s', '%s', %s, %s, '%s', '%s', %s)" %
                (id, name, approx, year, team, position, totalString))

    def playerId(self, playerName, conn, espnId = 'NULL', depthChartId = 'NULL',
                 injuryId = 'NULL', statsId = 'NULL'):
        ## playerName is list containing name, team, position, and year
        if espnId in self.espnDict:
            return self.espnDict[espnId]
        elif depthChartId in self.depthDict:
            return self.depthChartId[depthChartId]
        elif injuryId in self.injuryDict:
            return self.injuryDict[injuryId]
        elif statsId in self.statsDict:
            return self.statsDict[statsId]
        elif playerName in self.playerDict:
            return self.playerDIct['-'.join(playerName)]
        else:
            return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId)
