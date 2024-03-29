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
         join refData.seasonWeeks b on weekNum between 1 and 17
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


def pullModelData(season,week,position, conn):
    sql = ''' select null as id,
a.predictionSeason,
b.predictionWeek,
c.predictedWeek,
b.chartVersion,
a.playerId,
a.playerName,
b.playerTeam,
b.playerPosition,
c.predictedWeek - b.predictionWeek as weeksUntil,

ifnull(case when b.predictionWeek = 0 then playerStatus
else b.injDesignation end,'') as playerStatus,
b.chartPosition,
b.chartRank,
b.chartRole,
b.thirdDownBack,
b.goalLineBack,
b.pr,
b.kr,

a.age,
a.experience,
sameTeam,

ifnull(case when b.predictionWeek = 1 then priorWeekPlayerStatus
else priorWeekInjDesignation end,'') as priorWeekPlayerStatus,
priorWeekChartPosition,
priorWeekChartRank,

case when ifnull(seasonGames,0) = 0 then 0
    else seasonPoints/seasonGames end as seasonPoints,
priorWeekPoints,
seasonGames,
priorGame,

case when ifnull(seasonGames,0) = 0 then 0
    else seasonTargets/seasonGames end as seasonTargets,
priorWeekTargets,
case when ifnull(seasonGames,0) = 0 then 0
    else seasonRushes/seasonGames end as seasonRushes,
priorWeekRushes,

oppTeam,
byeWeek,

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
	
t2.qb1 as oppQb1Rating,
	
t2.rb1 as oppRb1Rating,
t2.rb2 as oppRb2Rating,
	
t2.wr1 as oppWr1Rating,
t2.wr2 as oppWr2Rating,
t2.wr3 as oppWr3Rating,
	
t2.te1 as oppTe1Rating,
t2.te2 as oppTe2Rating,
	
t2.lt as oppLtRating,
t2.lg as oppLgRating,
t2.c as oppCRating,
t2.rg as oppRgRating,
t2.rt as oppRtRating,
	
t2.de1 as oppDe1Rating,
t2.de2 as oppDe2Rating,
t2.dt1 as oppDt1Rating,
t2.dt2 as oppDt2Rating,
	
t2.mlb1 as oppMlb1Rating,
t2.mlb2 as oppMlb2Rating,
t2.olb1 as oppOlb1Rating,
t2.olb2 as oppOlb2Rating,
	
t2.cb1 as oppCb1Rating,
t2.cb2 as oppCb2Rating,
t2.cb3 as oppCb3Rating,
	
t2.s1 as oppS1Rating,
t2.s2 as oppS2Rating,
t2.s3 as oppS3Rating,
	
t2.k as oppKRating,	
	
c.actualPoints,
c.gamePlayed,
c.seasonDone,

t1.hasThirdDownBack,
t1.hasGoalLineBack,

b.priorWeekBye as predictPriorBye,

d.homeTeam,
d.priorWeekBye,
d.followWeekBye,
d.oppPriorWeekBye,
d.oppFollowWeekBye


from leagueSims.weeklyModelPlayerData a
join leagueSims.weeklyModelPredictWeekData b on b.predictionSeason = a.predictionSeason 
	and b.playerId = a.playerId
join leagueSims.weeklyModelPredictedWeekData c on c.predictionSeason = a.predictionSeason
	and c.playerId = a.playerId and c.predictedWeek >= b.predictionWeek
join leagueSims.weeklyModelPredictedWeekOppTeamData d on a.predictionSeason = d.predictionSeason
	and a.playerId = d.playerId and b.predictionWeek = d.predictionWeek and c.predictedWeek = d.predictedWeek
left join leagueSims.chartVerionPlayers t1 on a.predictionSeason = t1.cvSeason and b.chartVersion = t1.cvVersion and b.playerTeam = t1.cvTeam
left join leagueSims.chartVerionPlayers t2 on a.predictionSeason = t2.cvSeason and b.chartVersion = t2.cvVersion and d.oppTeam = t2.cvTeam
where a.predictionSeason between %d and %d
	and (b.predictionWeek = %d)
	and a.fantasyPosition= '%s' '''

    return pd.read_sql(sql % (season-3,season,week,position),con=conn)

    


def pullCurrentRosters(season, week, conn):
    if week > 1:
        if season >= 2021:
            sql = '''select rosterTeam as playerTeam, a.rosterPlayer as playerId,
                    case a.rosterPosition when 'QB' then 0
                    when 'RB' then 1 when 'WR' then 2
                    when 'TE' then 3 when 'D/ST' then 4
                    when 'K' then 5 else 10 end as playerPosition, 
                    predictedWeek, 
                    ifnull(modelPrediction,0) as predictionValue,
                    ifnull(modelPossibleValues,0) as predictionDistr,
                ifnull(modelPlayProb,0) as playProb
                from la_liga_data.currentRoster a
                left join leagueSims.modelPredictions b on rosterWeek = predictionWeek and modelSeason = rosterYear
                                    and a.rosterPlayer = b.playerId
                where rosterYear = %d and rosterWeek = %d '''
        else:
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
