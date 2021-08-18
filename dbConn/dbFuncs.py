import pandas as pd
import numpy as np
import math
import pymysql
import re
import traceback

class InsertTable:
    ## initilize with table name to be inserted into
    ## add rows with appendRow funciton, with a list of lists,
    ## containing datastring and whether its inserted as string or number
    
    def __init__(self, tableName):
        ## declare initial statement that contains table to be inserted into
        self.sqlStatement = "insert into %s values " % tableName
        self.rows = ""
        self.updateStatementText = ""

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

        sqlString = sqlString[:-1] + "),"

        self.rows += sqlString

    def clearRows(self):
        self.rows = ""

    def updateStatement(self, columnArray):
        ## optional; only run if table has entries that might be updated
        self.updateStatementText = " on duplicate key update "
        for column in columnArray:
            self.updateStatementText += (" %s = values(%s)," % (column,column))

        

    def returnStatement(self):

        return self.sqlStatement + self.rows[:-1] + self.updateStatementText[:-1]

## return team ids for all data pulled
## attempts matches using all possible spellings of team names
## if no match, adds new team id to be fixed later
class getTeamId(object):
    ## class inializes by pulling all available team name variations, with connection as variable
    ## when returning team id use teamId function; if not available one will be created
    def __init__(self,conn):
        self.teamDict = pd.read_sql("select lower(teamVariation) as teamVariation, teamId from refData.nflTeamVariations",
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
        if teamName.lower() in self.teamDict:
            return self.teamDict[teamName.lower()]['teamId']
        else:
            self._addTeam(teamName.lower(), conn)

            return self.teamDict[teamName.lower()]['teamId']

        

## return player id from database,
## using either player name/season/team/position combo,
## or some other id unique to player from pulled system
## attempts matches, if none exist new player id is created

class getPlayerId:
    def __init__(self, year, conn, espn=False, depthChart=False,
                 injury=False,stats=False,pfr=False,nbc=False):
        self.playerDict = pd.read_sql('''select lower(playerString) as playerString, max(b.playerId) as playerId,
                                        cast(substring_index(group_concat(espnId),',',1) as SIGNED) as espnId,
                                        cast(substring_index(group_concat(statsId),',',1) as SIGNED) as statsId,
                                        substring_index(group_concat(depthChartsId),',',1) as depthChartsId,
                                        cast(substring_index(group_concat(injuryId),',',1) as SIGNED) as injuryId,
                                        cast(substring_index(group_concat(nbcId),',',1) as SIGNED) as nbcId,
                                       substring_index(group_concat( pfrId),',',1) as pfrId

                                      from refData.playerNames b
                                      join refData.playerIds a on a.playerId = b.playerId

                                      where playerYear = %d
                                      group by 1''' % year,
                                     con=conn,index_col='playerString').to_dict('index')

        self.espnDict = {}
        self.depthDict = {}
        self.injuryDict = {}
        self.statsDict = {}
        self.pfrDict = {}
        self.nbcDict = {}
        if espn:
            self.espnDict = pd.read_sql('''select espnId, substring_index(group_concat(playerId),',',1) as playerId
                                            from refData.playerIds
                                            where espnId is not null and espnId != ''
                                            group by 1 having count(*) = 1''',
                                       con=conn,index_col='espnId').to_dict('index')

        if depthChart:
            self.depthDict = pd.read_sql('''select depthChartsId, substring_index(group_concat(playerId),',',1) as playerId
                                            from refData.playerIds
                                         where depthChartsId is not null and depthChartsId != ''
                                        group by 1 having count(*) = 1''',
                                       con=conn,index_col='depthChartsId').to_dict('index')
        if injury:
            self.injuryDict = pd.read_sql('''select injuryId, substring_index(group_concat(playerId),',',1) as playerId
                                            from refData.playerIds
                                          where injuryId is not null and injuryId != ''
                                            group by 1 having count(*) = 1''',
                                       con=conn,index_col='injuryId').to_dict('index')
        if stats:
            self.statsDict = pd.read_sql('''select statsId, substring_index(group_concat(playerId),',',1) as playerId
                                            from refData.playerIds
                                         where statsId is not null and statsId != ''
                                            group by 1 having count(*) = 1''',
                                       con=conn,index_col='statsId').to_dict('index')
        if pfr:
            self.pfrDict = pd.read_sql('''select pfrId, substring_index(group_concat(playerId),',',1) as playerId
                                            from refData.playerIds
                                         where pfrId is not null and pfrId != ''
                                            group by 1 having count(*) = 1''',
                                       con=conn,index_col='pfrId').to_dict('index')
        if nbc:
            self.nbcDict = pd.read_sql('''select nbcId, substring_index(group_concat(playerId),',',1) as playerId
                                            from refData.playerIds
                                         where nbcId is not null and nbcId != ''
                                            group by 1 having count(*) = 1''',
                                       con=conn,index_col='nbcId').to_dict('index')

    def _addPlayer(self, playerName,conn,espnId = 'NULL', depthChartId = 'NULL',
                   injuryId = 'NULL', statsId = 'NULL', pfrId = 'NULL',nbcId = 'NULL'):
        removeString = [r'\\',r'\.',"'","_",' Jr$',' JR$',' Sr$',' SR$',' III$',' II$',' IV$',' V$',' VI$']
        
        playerApprox = playerName[0]
        if playerName[2] in ['HB','FB']:
            positionMatch = 'RB'
        elif playerName[2] in ['FS','SS']:
            positionMatch = 'S'
        elif playerName[2] in ['DST','Defense']:
            positionMatch = 'D/ST'
        elif playerName[2] in ['NT']:
            positionMatch = 'DT'
        elif playerName[2] in ['RE','LE']:
            positionMatch = 'DE'
        elif playerName[2] in ['OLB','MLB','ROLB','LOLB']:
            positionMatch = 'LB'
        else:
            positionMatch = playerName[2]

            
        for s in removeString:
            playerApprox = re.sub(s,'',playerApprox)
        anyId = False
        idCheck = 'join refData.playerIds b on b.playerId = a.playerId'
        idUpdate = "update refData.playerIds set "
        if espnId != 'NULL' and espnId != '':
            anyId = True
            idCheck += " and (espnId is null or espnId = '')"
            idUpdate += " espnId = %s " % str(espnId)
        if depthChartId != 'NULL' and depthChartId != '':
            anyId = True
            idCheck += " and (depthChartsId is null or depthChartsId = '')"
            idUpdate += " depthChartsId = '%s' " % str(depthChartId)
        if injuryId != 'NULL' and injuryId != '':
            anyId = True
            idCheck += " and (injuryId is null or injuryId = '')"
            idUpdate += " injuryId = %s " % str(injuryId)
        if statsId != "NULL" and statsId != '':
            anyId = True
            idCheck += " and (statsId is null or statsId = '')"
            idUpdate += " statsId = %s " % str(statsId)
        if pfrId != "NULL" and pfrId != '':
            anyId = True
            idCheck += " and (pfrId is null or pfrid = '')"
            idUpdate += " pfrId = '%s' " % str(pfrId)
        if nbcId != "NULL" and nbcId != '':
            anyId = True
            idCheck += " and (nbcId is null or nbcId = '')"
            idUpdate += " nbcId = %s " % str(pfrId)

        idUpdate += " where playerId = %d"

        if not anyId:
            idCheck = ""
        
        
        c = conn.cursor()
        playerId = None
        try:
            ## check if player exists in database for different year
            c.execute('''select a.playerId from refData.playerNames a
                        %s
                        where a.playerName = '%s'
                        and playerTeam = %s
                        and playerPosition in ('%s','%s')
                        and playerYear between %s - 2 and %s''' %
                      (idCheck, re.sub(r"(?<!\\)(')","\\'",playerName[0]), str(playerName[1]),
                       positionMatch,playerName[2], str(playerName[3]), str(playerName[3])))
            result = c.fetchone()
            if result != None:
                playerId = result[0]
                c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                           str(playerName[1]), positionMatch, '-'.join(playerName), "NULL"))
                if anyId:
                    c.execute(idUpdate % playerId)
                conn.commit()
                return playerId
            ## check if similar spelling but same team and position and last two years
            c.execute('''select a.playerId from refData.playerNames a
                        %s
                        where a.playerApprox = '%s'
                        and playerTeam = %s
                        and playerPosition in ('%s','%s')
                        and playerYear between  %s - 1 and %s''' %
                      (idCheck, playerApprox, str(playerName[1]),
                       positionMatch,playerName[2], str(playerName[3]),str(playerName[3])))
            result = c.fetchone()
            if result != None:
                playerId = result[0]
                c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                           str(playerName[1]), positionMatch, '-'.join(playerName), "NULL"))
                if anyId:
                    c.execute(idUpdate % playerId)
                conn.commit()
                return playerId
            ## check if same spelling but different team
            c.execute('''select a.playerId from refData.playerNames a
                        %s
                        where a.playerName = '%s'
                        and playerPosition in ('%s','%s')
                        and playerYear = %s''' %
                      (idCheck, re.sub(r"(?<!\\)(')","\\'",playerName[0]), 
                       positionMatch,playerName[2], str(playerName[3])))
            result = c.fetchone()
            if result != None:
                playerId = result[0]
                c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                           str(playerName[1]), positionMatch, '-'.join(playerName), "NULL"))
                if anyId:
                    c.execute(idUpdate % playerId)
                conn.commit()
                return playerId

            ## check if same spelling but different position
            c.execute('''select a.playerId from refData.playerNames a
                        %s
                        where a.playerName = '%s'
                        and playerTeam = %s
                        and playerYear = %s''' %
                      (idCheck, re.sub(r"(?<!\\)(')","\\'",playerName[0]), 
                       str(playerName[1]), str(playerName[3])))
            result = c.fetchone()
            if result != None:
                playerId = result[0]
                c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                           str(playerName[1]), positionMatch, '-'.join(playerName), "NULL"))
                if anyId:
                    c.execute(idUpdate % playerId)
                conn.commit()
                return playerId

            ## check if similar spelling and no other similar spellings
            c.execute('''select a.playerId from refData.playerNames a
                        %s
                        where a.playerApprox = '%s' and a.playerYear between %s - 2 and %s
                        and (select count(distinct playerId) from refData.playerNames c
                            where a.playerApprox = c.playerApprox) = 1
                        and (select max(maxCount) from refData.playerInstances where instanceName = a.playerApprox
                        and instanceYear between %s - 1 and %s) = 1
                        ''' %
                      (idCheck, playerApprox,str(playerName[3]),str(playerName[3]),
                       str(playerName[3]),str(playerName[3])))
            result = c.fetchone()
            if result != None:
                playerId = result[0]
                c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                           str(playerName[1]), positionMatch, '-'.join(playerName), "NULL"))
                if anyId:
                    c.execute(idUpdate % playerId)
                conn.commit()
                return playerId

            ## add player to database
            c.execute("select max(playerId) from refData.playerIds")
            result = c.fetchone()
            if result[0] != None:
                playerId = result[0] + 1
            else:
                playerId = 0
            if depthChartId != 'NULL':
                dcId = "'" + depthChartId + "'"
            else:
                dcId = depthChartId
            if pfrId != 'NULL':
                pId = "'" + pfrId + "'"
            else:
                pId = pfrId
            c.execute("insert into refData.playerIds values (%s, %s, %s, %s, %s, %s, %s, '%s')" %
                      (str(playerId), str(espnId), str(statsId), str(dcId),
                       str(injuryId), str(pId), str(nbcId), re.sub(r"(?<!\\)(')","\\'",playerName[0])))
            c.execute(self._insertNameString(str(playerId), playerName[0], playerApprox, str(playerName[3]),
                       str(playerName[1]), positionMatch, '-'.join(playerName), "NULL"))
            conn.commit()
        
            return playerId
        except Exception as e:
            traceback.print_exc()
            c.execute("insert into refData.playerName_errors values (null, '%s', '%s', %s, %s, '%s',%s, '%s', %s, current_timestamp())" %
                      (re.sub(r"(?<!\\)(')","\\'",str(e)), re.sub(r"(?<!\\)(')","\\'",'-'.join(playerName)),
                           str(espnId), str(statsId), str(depthChartId), str(injuryId), str(pfrId), str(nbcId)))
            conn.commit()
            c.execute("select max(errorId) from refData.playerName_errors")
            result = c.fetchone()
            return result[0]-999999

    def _insertNameString(self, id, name, approx, year, team, position, totalString, multiSameName):
        return ("insert into refData.playerNames values(%s, '%s', '%s', %s, %s, '%s', '%s', %s)" %
                (id, re.sub(r"(?<!\\)(')","\\'",name), approx, year, team, position, re.sub(r"(?<!\\)(')","\\'",totalString), multiSameName))

    def playerId(self, playerName, conn, espnId = 'NULL', depthChartId = 'NULL',
                 injuryId = 'NULL', statsId = 'NULL', pfrId = 'NULL', nbcId = 'NULL'):
        ## playerName is list containing name, team, position, and year
        if espnId in self.espnDict:
            return self.espnDict[espnId]['playerId']
        elif depthChartId in self.depthDict:
            return self.depthDict[depthChartId]['playerId']
        elif injuryId in self.injuryDict:
            return self.injuryDict[injuryId]['playerId']
        elif statsId in self.statsDict:
            return self.statsDict[statsId]['playerId']
        elif pfrId in self.pfrDict:
            return self.pfrDict[pfrId]['playerId']
        elif nbcId in self.nbcDict:
            return self.nbcDict[nbcId]['playerId']
        elif re.sub(r"\\\'","\'",'-'.join(playerName).lower()) in self.playerDict:
            playerEntry = self.playerDict[re.sub(r"\\\'","\'",'-'.join(playerName).lower())]
            c = conn.cursor()
            if statsId != 'NULL' and statsId != '':
                if playerEntry['statsId'] is None or math.isnan(playerEntry['statsId']):
                    c.execute("update refData.playerIds set statsId = %d where playerId = %d" % (statsId,playerEntry['playerId']))
                    conn.commit()
                    return playerEntry['playerId']
                else:
                    return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            elif espnId != 'NULL' and statsId != '':
                if playerEntry['espnId'] is None or math.isnan(playerEntry['espnId']):
                    c.execute("update refData.playerIds set espnId = %d where playerId = %d" % (espnId,playerEntry['playerId']))
                    conn.commit()
                    return playerEntry['playerId']
                else:
                    return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            elif depthChartId != 'NULL' and depthChartId != '':
                if playerEntry['depthChartsId'] is None:
                    c.execute("update refData.playerIds set depthChartsId = '%s' where playerId = %d" % (depthChartId,playerEntry['playerId']))
                    conn.commit()
                    return playerEntry['playerId']
                else:
                    return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            elif injuryId != 'NULL' and injuryId != '':
                if playerEntry['injuryId'] is None or math.isnan(playerEntry['injuryId']):
                    c.execute("update refData.playerIds set injuryId = %d where playerId = %d" % (injuryId,playerEntry['playerId']))
                    conn.commit()
                    return playerEntry['playerId']
                else:
                    return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            elif pfrId != 'NULL' and pfrId != '':
                if playerEntry['pfrId'] is None:
                    c.execute("update refData.playerIds set pfrId = '%s' where playerId = %d" % (pfrId,playerEntry['playerId']))
                    conn.commit()
                    return playerEntry['playerId']
                else:
                    return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            elif nbcId != 'NULL' and nbcId != '':
                if playerEntry['nbcId'] is None or math.isnan(playerEntry['nbcId']):
                    c.execute("update refData.playerIds set nbcId = %s where playerId = %d" % (nbcId,playerEntry['playerId']))
                    conn.commit()
                    return playerEntry['playerId']
                else:
                    return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            else:
                return playerEntry['playerId']
        else:
            try:
                return self._addPlayer(playerName, conn, espnId, depthChartId, injuryId, statsId, pfrId, nbcId)
            except Exception as e:
                c = conn.cursor()
                traceback.print_exc() 
                c.execute("insert into refData.playerName_errors values (null, '%s', '%s', %s, %s, '%s', %s, '%s',%s, current_timestamp())" %
                          (re.sub(r"(?<!\\)(')","\\'",str(e)), re.sub(r"(?<!\\)(')","\\'",'-'.join(playerName)),
                           str(espnId), str(statsId), str(depthChartId), str(injuryId), str(pfrId), str(nbcId)))
                conn.commit()
                c.execute("select max(errorId) from refData.playerName_errors")
                result = c.fetchone()
                return result[0]-999999
