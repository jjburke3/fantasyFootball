import pymysql
import pandas as pd
import statistics as s


##Pull in weekly results


def pullResults(season, week, conn):
    sql = '''select winSeason, winWeek, winTeam, 
		case when winWeek <= 13 or winWeek < %d then winOpp end as winOpp,
        case when winWeek < %d then winPoints end as winPoints, 
        case when winWeek < %d then winPointsAgs end winPointsAgs, 
        case when winWeek < %d then winWin end winWin, 
        case when winWeek < %d then winLoss end winLoss, 
        case when winWeek < %d then winTie end winTie
		from la_liga_data.wins
        where winSeason = %d
        union
        select matchYear, matchWeek, matchTeam, matchOpp, null, null, null, null, null
         from la_liga_data.matchups where matchYear = %d and matchWeek not in 
			(select distinct winWeek from la_liga_data.wins where winSeason = %d)
         union select %d, weekNum, winTeam,
         null,null,null,null,null,null
         from (select distinct winTeam from la_liga_data.wins where winSeason = %d) a
         join refData.seasonWeeks b on weekNum between 1 and 16
         where weekNum not in
             (select distinct winWeek from la_liga_data.wins where winSeason = %d)
             and weekNum not in
             (select distinct matchWeek from la_liga_data.matchups where matchYear = %d)
         '''

    return pd.read_sql(sql % (week,week,week,week,week,week,season,
                              season,season,
                              season,season,season,season),con=conn)

def pullSchedule(season, conn):
    sql = ''' '''


def pullModelData(season,position, conn):
    sql = ''' select null as id,
a.predictionSeason,
a.chartVersion,
a.playerId,
a.playerName,
a.playerTeam,
a.playerPosition,

a.playerStatus,
a.chartPosition,
a.chartRank,
a.chartRole,
a.thirdDownBack,
a.goalLineBack,
a.pr,
a.kr,

a.age,
a.experience,
sameTeam,
actualPoints,
gamesPlayed,




a.playerRating,
a.playerSpeed,
a.playerAgility,
a.playerCatch,
a.playerCarrying,
a.playerBCVision,
a.playerRouteRunning,
a.playerThrowPower,
a.playerThrowAccuracy,
a.playerAwareness,
	
	
a.playerInjury,
	
case when chartPosition = 'QB' and chartRank = 0 then t1.qb2 else t1.qb1 end as qb1Rating,
case when chartPosition = 'QB' and chartRank = 0 then t1.qb2Inj else t1.qb1Inj end as qb1Injury,
case when chartPosition = 'QB' and chartRank = 0 then t1.qb2Status else t1.qb1Status end as qb1Status,
	
case when chartPosition = 'RB' and chartRank = 0 then t1.rb2 else t1.rb1 end as rb1Rating,
case when chartPosition = 'RB' and chartRank <= 1 then t1.rb3 else t1.qb2 end as rb2Rating,
case when chartPosition = 'RB' and chartRank = 0 then t1.rb2Status else t1.rb1Status end as rb1Status,
case when chartPosition = 'RB' and chartRank <= 1 then t1.rb3Status else t1.rb2Status end as rb2Status,
	
case when chartPosition = 'WR' and chartRank = 0 then t1.wr2 else t1.wr1 end as wr1Rating,
case when chartPosition = 'WR' and chartRank <= 1 then t1.wr3 else t1.wr2 end as wr2Rating,
case when chartPosition = 'WR' and chartRank <= 2 then t1.wr4 else t1.wr3 end as wr3Rating,
case when chartPosition = 'WR' and chartRank = 0 then t1.wr2Status else t1.wr1Status end as wr1Status,
case when chartPosition = 'WR' and chartRank <= 1 then t1.wr3Status else t1.wr2Status end as wr2Status,
case when chartPosition = 'WR' and chartRank <= 2 then t1.wr4Status else t1.wr3Status end as wr3Status,
	
case when chartPosition = 'TE' and chartRank = 0 then t1.te2 else t1.te1 end as te1Rating,
case when chartPosition = 'TE' and chartRank = 0 then t1.te2Status else t1.te1Status end as te1Status,
	
t1.lt as ltRating,
t1.lg as lgRating,
t1.c as cRating,
t1.rg as rgRating,
t1.rt as rtRating,
	
t1.de1 as de1Rating,
t1.de2 as de2Rating,
t1.dt1 as dt1Rating,
t1.dt2 as dt2Rating,
	
t1.mlb1 as mlb1Rating,
t1.mlb2 as mlb2Rating,
t1.olb1 as olb1Rating,
t1.olb2 as olb2Rating,
	
t1.cb1 as cb1Rating,
t1.cb2 as cb2Rating,
t1.cb3 as cb3Rating,
	
t1.s1 as s1Rating,
t1.s2 as s2Rating,
t1.s3 as s3Rating,

t1.k as kRating,
	
	


t1.hasThirdDownBack,
t1.hasGoalLineBack,
ifnull(rankingRank,9999) as rankingRank,
ifnull(rankingTier,9999) as rankingTier,
ifnull(rankingPosRank,9999) as rankingPosRank




from seasonPredictions.modelPlayerData a


left join seasonPredictions.chartVerionPlayers t1 on a.predictionSeason = t1.cvSeason and a.chartVersion = t1.cvVersion and a.playerTeam = t1.cvTeam
left join scrapped_data2.fantasyProsRankings on a.predictionSEason = rankingSeason and
	a.playerId = rankingPlayer and
    ((a.chartVersion = rankingVersion and rankingSeason >= 2021) or
    (rankingWeek = 0 and rankingSeason < 2021))
where a.predictionSeason between %d and %d
	and a.playerPosition= '%s' '''

    return pd.read_sql(sql % (season-3,season,position),con=conn)

    


def pullCurrentRosters(season, week, conn):
    if week > 1:
        sql = ''' select playerTeam, a.playerId,
                    case a.playerPosition when 'QB' then 0
                    when 'RB' then 1 when 'WR' then 2
                    when 'TE' then 3 when 'D/ST' then 4
                    when 'K' then 5 else 10 end as playerPosition, 
                    predictedWeek, 
                    ifnull(modelPrediction,0) as predictionValue,
                    ifnull(modelPossibleValues,0) as predictionDistr,
                ifnull(modelPlayProb,0) as playProb
                from la_liga_data.playerPoints a
                left join leagueSims.modelPredictions b on playerWeek = predictionWeek - 1 and modelSeason = playerSeason
                                    and a.playerId = b.playerId
                where playerSeason = %d and playerWeek = %d - 1'''

        return pd.read_sql(sql %(season,week),con=conn)
    else:
        sql = ''' select selectingTeam as playerTeam, player as playerId,
                    case a.playerPosition when 'QB' then 0
                    when 'RB' then 1 when 'WR' then 2
                    when 'TE' then 3 when 'D/ST' then 4
                    when 'K' then 5 else 10 end as playerPosition, 
                    predictedWeek, 
                    ifnull(modelPrediction,0) as predictionValue,
                    ifnull(modelPossibleValues,0) as predictionDistr,
                    ifnull(modelPlayProb,0) as playProb
                from la_liga_data.draftedPlayerData a
                left join leagueSims.modelPredictions b on predictionWeek = %d and draftYear = modelSeason
                        and a.player = b.playerId
                where draftYear = %d;'''

        return pd.read_sql(sql %(week,season),con=conn)
        

def pullReplacementNumbers(season,week,conn):
    sql = '''select predictedWeek, playerPosition,
            substring_index(group_concat(case when modelPlayProb > .5 then modelPrediction end  order by modelPrediction desc),',',
				case when playerPosition in ('QB','D/ST','K') then 5 when playerPosition = 'TE' then 6 else 10 end) as replaceMean,
            replace(substring_index(group_concat(case when modelPlayProb > .5 then modelPossibleValues end  order by modelPrediction desc separator '|'),'|',
				case when playerPosition in ('QB','D/ST','K') then 5 when playerPosition = 'TE' then 6 else 10 end),'|',',') as replaceDistr
            from leagueSims.modelPredictions 
            where modelSeason = %d and predictionWeek = %d
                    and playerId not in %s
            group by 1,2
union all
select predictedWeek, 'RBWR',
            substring_index(group_concat(case when modelPlayProb > .5 then modelPrediction end  order by modelPrediction desc),',',10) as replaceMean,
            replace(substring_index(group_concat(case when modelPlayProb > .5 then modelPossibleValues end  order by modelPrediction desc separator '|'),'|',
				10),'|',',') as replaceDistr
            from leagueSims.modelPredictions 
            where modelSeason = %d and predictionWeek = %d
                    and playerId not in %s
					and playerPosition in ('RB','WR')
            group by 1,2
union all
select predictedWeek, 'Flex',
            substring_index(group_concat(case when modelPlayProb > .5 then modelPrediction end  order by modelPrediction desc),',',10) as replaceMean,
            replace(substring_index(group_concat(case when modelPlayProb > .5 then modelPossibleValues end  order by modelPrediction desc separator '|'),'|',
				10),'|',',') as replaceDistr
            from leagueSims.modelPredictions 
            where modelSeason = %d and predictionWeek = %d
                    and playerId not in %s
					and playerPosition in ('RB','WR','TE')
            group by 1,2

            '''
    if week > 1:
        notInString = '(select distinct playerId from la_liga_data.playerPoints where modelSeason = playerSeason and predictionWeek = playerWeek + 1)'
    else:
        notInString = '(select distinct player from la_liga_data.draftedPlayerData where modelSeason = draftYear)'
    with conn.cursor() as c:
        c.execute("SET SESSION group_concat_max_len = 1000000;")
    table = pd.read_sql(sql %(season,week,notInString,season,week,notInString,season,week,notInString),con=conn)
    table['replaceMean'] = table.apply(lambda x: s.mean(map(float,x.replaceMean.split(','))),axis=1)
    return table
