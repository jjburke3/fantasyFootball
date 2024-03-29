-- populate table initially with all new entries for current week


delimiter //
drop procedure if exists leagueSims.modelDataTables//
create procedure leagueSims.modelDataTables(maxSeason int, maxWeek int)
begin
set @maxSeason = maxSeason;
set @maxWeek = maxWeek;
delete from leagueSims.weeklyModelPredictWeekData
where predictionSeason = @maxSeason
 and predictionWeek = @maxWeek;
 
delete from leagueSims.weeklyModelPredictedWeekData
where predictionSeason = @maxSeason
 and predictedWeek = @maxWeek;
 
delete from leagueSims.weeklyModelPredictedWeekOppTeamData
where predictionSeason = @maxSeason
 and predictionWeek = @maxWeek;

insert into leagueSims.weeklyModelPlayerData(
	predictionSeason,
	playerId, playerName,
	fantasyPosition)

select rankingSeason, rankingPlayer, 
substring_index(group_concat(distinct playerName),',',1) as playerName, 
substring_index(group_concat(distinct rankingPosition order by 
	rankingVersion desc),',',1) as rankingPosition 
from scrapped_data2.fantasyProsRankings
left join refData.playerIds on playerId = rankingPlayer
group by 1,2
on duplicate key update 
playerName = values(playerName),
fantasyPosition = values(fantasyPosition);

-- get player madden numbers
drop table if exists leagueSims.tempMadden;
create table leagueSims.tempMadden
(
	id int primary key,
	maddenPlayerId int,
	maddenTeamId int,
	maddenSeason int,
	maddenAge int,
	maddenExperience int,
	maddenRating int,
	maddenSpeed int,
	maddenAgility int,
	maddenCatch int,
	maddenCarrying int,
	maddenBCVision int,
	maddenRouteRunning int,
	maddenThrowPower int,
	maddenThrowAccuracy int,
	maddenAwareness int,
	maddenInjury int,
	index(maddenPlayerId),
	index(maddenSeason)
);

insert into leagueSims.tempMadden
select id, 
min(playerId), 
min(teamId), 
min(season), 
min(age), 
min(experience),
min(overall), min(speed), min(agility), min(catch), min(carrying), min(bc_vision),
min(route_running), min(throw_power), min(throw_accuracy),
min(awareness), min(injury)
from (
select distinct ifnull(maddenPlayerId,playerId) as playerId, ifnull(maddenTeamId,teamId) as teamId, a.* from madden_ratings.playerRatings a
left join refData.nflTeamVariations on team = teamVariation and maddenPlayerId is null
left join refData.playerNames on player_name = playerName and playerYear = season and maddenPlayerId is null
	and playerTeam = teamId
	and (playerPosition = pos or playerPosition = 
    case when pos in ('HB','FB') then 'RB'
	when pos in ('FS','SS') then 'S'
    when pos in ('DST','Defense') then 'D/ST'
    when pos in ('NT') then 'DT'
    when pos in ('RE','LE') then 'DE'
    when pos in ('OLB','MLB','ROLB','LOLB') then 'LB'
    else pos end))b
group by 1;

update leagueSims.weeklyModelPlayerData
join leagueSims.tempMadden on maddenPlayerId = playerId and maddenSeason = predictionSeason
set age = maddenAge, experience = maddenExperience,
	playerRating = maddenRating, playerSpeed = maddenSpeed, playerAgility = maddenAgility,
	playerCatch = maddenCatch, playerCarrying = maddenCarrying, playerBCVision = maddenBCVision,
	playerRouteRunning = maddenRouteRunning, playerThrowPower = maddenThrowPower, 
	playerThrowAccuracy = maddenThrowAccuracy, playerAwareness = maddenAwareness,
	playerInjury = maddenInjury;
	
insert into leagueSims.weeklyModelPredictedWeekData
select predictionSeason, listWeek, playerId,
round(totalPoints,1),
gamePlayed,
null
from leagueSims.weeklyModelPlayerData
join (select distinct playerYear as listYear from refData.playerNames) b on predictionSeason = listYear
join (select 1 as listWeek 
		union select 2 union select 3 union select 4 union select 5 union select 6 union select 7
			union select 8 union select 9 union select 10 union select 11 union select 12 union select 13
			union select 14 union select 15 union select 16 union select 17) week on 1 = 1
left join scrapped_data2.playerStats on predictionSeason = statYear and listWeek = statWeek and statPlayer = playerId
on duplicate key update actualPoints = values(actualPoints),
	gamePlayed = values(gamePlayed),
	seasonDone = values(seasonDone);
	



-- match weeks to proper depth chart
SET @@group_concat_max_len = 9999999;

drop table if exists leagueSims.chartVersion;
create table leagueSims.chartVersion
(chartSeason int, predWeek tinyint, chartTeam tinyint, chartVersion int,
primary key (chartSeason, predWeek,chartTeam), index(predWeek), index(chartTeam));
insert into leagueSims.chartVersion
select chartSeason, weekNum as predWeek, chartTeam,
convert(substring_index(
	group_concat(distinct b.chartVersion order by abs(chartWeek - weekNum) + if(chartWeek > weekNum,2,0),
		case when chartWeek <= weekNum then dataDateTime else -dataDateTime end desc
),',',1),unsigned integer) as chartVersion
from (select distinct chartSeason, c.chartVersion, c.chartTeam,
	ifnull(if(date_sub(dataDateTime,interval 4 hour) > concat(nflDate,' ',nflTime),1,0)+chartWeek,chartWeek) as chartWeek, 
    dataDateTime from scrapped_data2.depthCharts c
	left join scrapped_data2.nflSchedule on chartSeason = nflSeason and
    chartWeek = nflWeek and (chartTeam = nflRoadTeam or chartTeam = nflHomeTeam) ) b
join refData.seasonWeeks
group by 1,2,3;

-- build data specific to prediction week

insert into leagueSims.weeklyModelPredictWeekData
(predictionSeason, predictionWeek, chartVersion,
playerId)
select predictionSeason, 
weekNum as predictionWeek,
min(a.chartVersion),
playerId

from leagueSims.weeklyModelPlayerData
join refData.seasonWeeks on 
	(predictionSeason < ifnull((select max(winSeason) from la_liga_data.wins),0) or 
	weekNum <= 1 + ifnull((select right(max(winSeason*100+winWeek),2) from la_liga_data.wins),0))
left join leagueSims.chartVersion a on predictionSeason = chartSeason and 
	weekNum = predWeek
group by predictionSeason, weekNum, playerId
on duplicate key update chartVersion = values(chartVersion);


update leagueSims.weeklyModelPredictWeekData a
join (
select chartVersion, chartPlayer,
substring_index(group_concat(distinct chartTeam),',',1) as chartTeam
from scrapped_data2.depthCharts 
group by 1,2) b on a.chartVersion = b.chartVersion and playerId = chartPlayer
set playerTeam = chartTeam;


update leagueSims.weeklyModelPredictWeekData b
join leagueSims.chartVersion a on predictionSeason = chartSeason and 
	predictionWeek = predWeek and playerTeam = chartTeam
set b.chartVersion = a.chartVersion;
	
update leagueSims.weeklyModelPredictWeekData a
join (
select chartVersion, chartPlayer,
substring_index(group_concat(distinct chartTeam),',',1) as chartTeam,
substring_index(group_concat(distinct chartPosition),',',1) as playerPos,
substring_index(group_concat(distinct injuryStatus),',',1) as injuryStatus,
substring_index(group_concat(distinct chartPosition),',',1)  as chartPosition,
substring_index(group_concat(distinct chartRank),',',1)  as chartRank,
substring_index(group_concat(distinct chartRole),',',1)  as chartRole,
case when sum(thirdDownBack) >=1 then 1 else 0 end as thirdDownBack, 
case when sum(goalLine) >= 1 then 1 else 0 end as goalLine, 
case when sum(puntReturner) >= 1 then 1 else 0 end as puntReturner,
case when sum(kickReturner) >= 1 then 1 else 0 end as kickReturner
from scrapped_data2.depthCharts 
group by 1,2) b on a.chartVersion = b.chartVersion and playerId = chartPlayer
set playerTeam = chartTeam, 
playerPosition = case when playerPos = 'PK' then 'K' else playerPos end, 
a.chartPosition = case when b.chartPosition = 'PK' then 'K' else b.chartPosition end, 
 playerStatus =case when injuryStatus in ('','IR','PUP','Suspended') then injuryStatus
 else 'Injured' end, 
 injDesignation = case when predictionSeason = @maxSeason and predictionWeek = @maxWeek
 then 
 case when injuryStatus = 'Suspended' then 'S'
	when injuryStatus = 'COV' then 'C19'
 else injuryStatus end
 end,
 a.chartRank = b.chartRank, 
  a.chartRole = case when b.chartRole = 'Starter' then 'Starter' else 'Non-Starter' end,
    a.thirdDownBack = b.thirdDownBack, goalLineBack = goalLine,
    pr = puntReturner, kr = kickReturner;
	
update leagueSims.weeklyModelPredictWeekData a
join (select injSeason, injWeek, injPlayer,
		ifnull(substring_index(group_concat(case when injDesignation = 'IR' and injDNP = 0 then 'Off-IR' 
		when injDesignation != '' then injDesignation end separator '|'),'|',1),'') as injDesignation
	  from scrapped_data2.injuredStatus
	  group by 1,2,3 ) b on injSeason = predictionSeason and injWeek = predictionWeek
	and injPlayer = playerId
set a.injDesignation = b.injDesignation;

update leagueSims.weeklyModelPredictWeekData a
join (select injSeason, injWeek, injPlayer,
		substring_index(group_concat(case when injDesignation = 'IR' and injDNP = 0 then 'Off-IR' 
		when injDesignation != '' then injDesignation end separator '|'),'|',1) as injDesignation
	  from scrapped_data2.injuredStatus
	  group by 1,2,3 ) b on injSeason = predictionSeason and injWeek + 1 = predictionWeek
	and injPlayer = playerId
set a.priorWeekInjDesignation = b.injDesignation;


	
update leagueSims.weeklyModelPredictWeekData
set playerPosition = case 
	when playerPosition in ('HB','FB') then 'RB'
	else playerPosition end;
	
update leagueSims.weeklyModelPredictWeekData
set playerPosition = 'D/ST'
where playerId between -150 and -1;
	
update leagueSims.weeklyModelPredictWeekData a
join leagueSims.weeklyModelPredictWeekData b on a.predictionSeason = b.predictionSeason
	and a.predictionWeek = b.predictionWeek + 1 and a.playerId = b.playerId
set a.priorWeekPlayerStatus = b.playerStatus, a.priorWeekChartPosition = b.chartPosition,
	a.priorWeekChartRank = b.chartRank,
	a.priorWeekInjDesignation = case when a.predictionSeason >= 2021 then b.injDesignation else a.priorWeekInjDesignation end;
	
update leagueSims.weeklyModelPredictWeekData a
left join refData.playerNames b on a.playerId = b.playerId and a.playerTeam = b.playerTeam 
	and a.predictionSeason = b.playerYear + 1
set sameTeam = case when b.playerId is null then 0 else 1 end;

update leagueSims.weeklyModelPredictWeekData a
JOin (select distinct playerId, playerTeam from refData.playerNames where playerPosition = 'D/ST') b on a.playerId = b.playerId
set a.playerTeam = b.playerTeam;

update leagueSims.weeklyModelPredictWeekData a
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and predictionWeek = nflWeek + 1
	and (playerTeam = nflHomeTeam or playerTeam = nflRoadTeam)
set priorWeekBye = case when nflSeason is null then 1 else 0 end;


-- build prediction and predicted specific data

insert into leagueSims.weeklyModelPredictedWeekOppTeamData
(predictionSeason, predictionWeek, predictedWeek,
playerId, chartVersion, playerTeam)
select predictionSeason, 
predictionWeek,
b.weekNum as predictedWeek,
playerId,
chartVersion,
playerTeam
from leagueSims.weeklyModelPredictWeekData
join refData.seasonWeeks b on predictionWeek <= b.weekNum and b.weekNum > 0
on duplicate key update chartVersion = values(chartVersion),
	playerTeam = values(playerTeam);



-- get schedule data
update leagueSims.weeklyModelPredictedWeekOppTeamData
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and predictedWeek = nflWeek
	and (nflHomeTeam = playerTeam or nflRoadTeam = playerTeam)
set oppTeam = case when nflHomeTeam = playerTeam then nflRoadTeam else nflHomeTeam end;

update leagueSims.weeklyModelPredictedWeekOppTeamData
set byeWeek = case when oppTeam is null then 1 else 0 end;


update leagueSims.weeklyModelPredictedWeekOppTeamData
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and nflWeek = predictedWeek
and (nflHomeTeam = playerTeam)
set homeTeam = case when nflSeason is not null then 1 else 0 end;


update leagueSims.weeklyModelPredictedWeekOppTeamData
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and nflWeek = (predictedWeek - 1)
and (nflHomeTeam = playerTeam or nflRoadTeam = playerTeam)
set priorWeekBye = case when nflSeason is null then 1 else 0 end;

update leagueSims.weeklyModelPredictedWeekOppTeamData
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and nflWeek = (predictedWeek + 1)
and (nflHomeTeam = playerTeam or nflRoadTeam = playerTeam)
set followWeekBye = case when nflSeason is null then 1 else 0 end;


update leagueSims.weeklyModelPredictedWeekOppTeamData
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and nflWeek = (predictedWeek - 1)
and (nflHomeTeam = oppTeam or nflRoadTeam = oppTeam)
set oppPriorWeekBye = case when nflSeason is null and oppTeam is not null then 1 else 0 end;

update leagueSims.weeklyModelPredictedWeekOppTeamData
left join scrapped_data2.nflSchedule on nflSeason = predictionSeason and nflWeek = (predictedWeek + 1)
and (nflHomeTeam = oppTeam or nflRoadTeam = oppTeam)
set oppFollowWeekBye = case when nflSeason is null and oppTeam is not null then 1 else 0 end;

update 
leagueSims.weeklyModelPredictedWeekData a
join leagueSims.weeklyModelPredictedWeekOppTeamData b
on a.predictionSeason = b.predictionSeason and a.playerId = b.playerId
	and a.predictedWeek = b.predictedWeek and b.predictionWeek = b.predictedWeek

set a.gamePlayed = 0
where a.playerId between -150 and -1 and b.byeWeek = 1;

update leagueSims.weeklyModelPredictedWeekData
join scrapped_data2.injuredStatus on injSeason = predictionSeason and injWeek = predictedWeek
 and injPlayer = playerId
 set gamePlayed = 0
 where gamePlayed = 1 and injDNP = 1 and actualPoints = 0;
 
 -- get player stats
update leagueSims.weeklyModelPredictWeekData a
join (
select playerYear as statYear, weekNum as statWeek, playerId as statPlayer,
ifnull(totalPoints,0) as priorWeekPoints,
ifnull(rushAtt,0) as priorWeekRushes,
ifnull(gamePlayed,0) as priorGame,
ifnull(target,0) as priorWeekTargets,
@seasonPoints := if(@match = concat_ws('-',playerId,playerYear),@seasonPoints,0)+ifnull(totalPoints,0) as seasonPoints,
@seasonRushes := if(@match = concat_ws('-',playerId,playerYear),@seasonRushes,0)+ifnull(rushAtt,0) as seasonRushes,
@seasonGames := if(@match = concat_ws('-',playerId,playerYear),@seasonGames,0)+ifnull(gamePlayed,0) as seasonGames,
@seasonTargets := if(@match = concat_ws('-',playerId,playerYear),@seasonTargets,0)+ifnull(target,0) as seasonTargets,
@match := concat_ws('-',playerId,playerYear)

 from (select *
 from (select distinct playerId, playerYear from refData.playerNames where playerId in 
			(select distinct statPlayer from scrapped_data2.playerStats)
		) b
		join refData.seasonWeeks on weekNum between 1 and 17
        left join scrapped_data2.playerStats on statYear = playerYear and statWeek = weekNum
        and statPlayer = playerId) a, (select @match := '', @seasonPoints := 0, @seasonRushes := 0,
	@seasonGames := 0, @seasonTargets := 0) t 
order by 3,1,2) b on statYear = predictionSeason and 
	statWeek = predictionWeek - case when priorWeekBye = 1 then 2 else 1 end 
	and statPlayer = playerId
set a.priorWeekPoints = b.priorWeekPoints, a.priorWeekRushes = b.priorWeekRushes, a.priorGame = b.priorGame,
	a.priorWeekTargets = b.priorWeekTargets,
    a.seasonPoints = b.seasonPoints, a.seasonRushes = b.seasonRushes, a.seasonGames = b.seasonGames,
    a.seasonTargets = b.seasonTargets;

drop table if exists leagueSims.chartVerionPlayers;
create table leagueSims.chartVerionPlayers
(
	cvSeason int, cvVersion int, cvTeam tinyint,
	qb1 decimal(4,1), qb2 decimal(4,1),
	qb1Inj decimal(4,1), qb2Inj decimal(4,1),
	qb1Status varchar(10), qb2Status varchar(10),
	rb1 decimal(4,1), rb2 decimal(4,1), rb3 decimal(4,1),
	rb1Inj decimal(4,1), rb2Inj decimal(4,1), rb3Inj decimal(4,1),
	rb1Status varchar(10), rb2Status varchar(10), rb3Status varchar(10),
	wr1 decimal(4,1), wr2 decimal(4,1),
	wr3 decimal(4,1), wr4 decimal(4,1),
	wr1Inj decimal(4,1), wr2Inj decimal(4,1),
	wr3Inj decimal(4,1),wr4Inj decimal(4,1),
	wr1Status varchar(10), wr2Status varchar(10),
	wr3Status varchar(10), wr4Status varchar(10),
	te1 decimal(4,1), te2 decimal(4,1),
	te1Inj decimal(4,1), te2Inj decimal(4,1),
	te1Status varchar(10), te2Status varchar(10),
	lt decimal(4,1), lg decimal(4,1), c decimal(4,1), rg decimal(4,1),rt decimal(4,1),
	de1 decimal(4,1),de2 decimal(4,1), dt1 decimal(4,1), dt2 decimal(4,1),
	mlb1 decimal(4,1), mlb2 decimal(4,1),
	olb1 decimal(4,1), olb2 decimal(4,1),
	cb1 decimal(4,1), cb2 decimal(4,1), cb3 decimal(4,1),
	s1 decimal(4,1), s2 decimal(4,1), s3 decimal(4,1),
	k decimal(4,1),
	hasThirdDownBack tinyint, hasGoalLineBack tinyint,
	primary key(cvSeason,cvVersion,cvTeam)
);
insert into leagueSims.chartVerionPlayers
select chartSeason, chartVersion, chartTeam,
ifnull(qb1,avgQb1) as qb1, ifnull(qb2,avgQb2) as qb2, ifnull(qb1Inj,avgQb1Inj) as qb1Inj, ifnull(qb2Inj,avgQb2Inj) as qb2Inj,
case when qb1Status in ('','IR','PUP','Suspended') then qb1Status
 else 'Injured' end as qb1Status, 
 case when qb2Status in ('','IR','PUP','Suspended') then qb2Status
 else 'Injured' end as qb2Status,

ifnull(rb1,avgRb1) as rb1, ifnull(rb2,avgRb2) as rb2, ifnull(rb3,avgRb3) as rb3,
ifnull(rb1Inj,avgRb1Inj) as rb1Inj, ifnull(rb2Inj,avgRb2Inj) as rb2Inj, ifnull(rb3Inj,avgRb3Inj) as rb3Inj,
case when rb1Status in ('','IR','PUP','Suspended') then rb1Status
 else 'Injured' end as rb1Status, 
case when rb2Status in ('','IR','PUP','Suspended') then rb2Status
 else 'Injured' end as rb2Status, 
case when rb3Status in ('','IR','PUP','Suspended') then rb3Status
 else 'Injured' end as rb3Status,

ifnull(wr1,avgWr1) as wr1, ifnull(wr2,avgWr2) as wr2, ifnull(wr3,avgWr3) as wr3, ifnull(wr4,avgWr4) as wr4,
ifnull(wr1Inj,avgWr1Inj) as wr1Inj, ifnull(wr2Inj,avgWr2Inj) as wrInj, ifnull(wr3Inj,avgWr3Inj) as wr3Inj, ifnull(wr4Inj,avgWr4Inj) as wr4Inj,
case when wr1Status in ('','IR','PUP','Suspended') then wr1Status
 else 'Injured' end as wr1Status, 
case when wr2Status in ('','IR','PUP','Suspended') then wr2Status
 else 'Injured' end as wr2Status, 
case when wr3Status in ('','IR','PUP','Suspended') then wr3Status
 else 'Injured' end as wr3Status, 
case when wr4Status in ('','IR','PUP','Suspended') then wr4Status
 else 'Injured' end as wr4Status,

ifnull(te1,avgTe1) as te1, ifnull(te2,avgTe2) as te2, ifnull(te1Inj,avgTe1Inj) as te1Ink, ifnull(te2Inj,avgTe2Inj) as te2Inj,
case when te1Status in ('','IR','PUP','Suspended') then te1Status
 else 'Injured' end as te1Status, 
case when te2Status in ('','IR','PUP','Suspended') then te2Status
 else 'Injured' end as te2Status,

ifnull(lt1,avgLt1) as lt1, ifnull(lg1,avgLg1) as lg1, ifnull(c1,avgC1) as c1, ifnull(rg1,avgRg1) as rg1, ifnull(rt1,avgRt1) as rt1,

greatest(ifnull(de1,avgDe1),ifnull(de2,avgDe2)) as de1, least(ifnull(de1,avgDe1),ifnull(de2,avgDe2)) as de2, 
greatest(ifnull(dt1,avgDt1),ifnull(dt2,avgDt2)) as dt1, least(ifnull(dt1,avgDt1),ifnull(dt2,avgDt2)) as dt2,

greatest(ifnull(mlb1,avgMlb1),ifnull(mlb2,avgMlb2)) as mlb1, least(ifnull(mlb1,avgMlb1),ifnull(mlb2,avgMlb2)) as mlb2, 
greatest(ifnull(olb1,avgOlb1),ifnull(olb2,avgOlb2)) as olb1, least(ifnull(olb1,avgOlb1),ifnull(olb2,avgOlb2)) as olb2,


greatest(ifnull(cb1,avgCb1),ifnull(cb2,avgCb2),ifnull(cb3,avgCb3)) as cb1, 
case when ifnull(cb1,avgCb1) != greatest(ifnull(cb1,avgCb1),ifnull(cb2,avgCb2),ifnull(cb3,avgCb3))
	and ifnull(cb1,avgCb1) != least(ifnull(cb1,avgCb1),ifnull(cb2,avgCb2),ifnull(cb3,avgCb3)) then ifnull(cb1,avgCb1)
	when ifnull(cb2,avgCb2) != greatest(ifnull(cb1,avgCb1),ifnull(cb2,avgCb2),ifnull(cb3,avgCb3))
		and ifnull(cb2,avgCb2) != least(ifnull(cb1,avgCb1),ifnull(cb2,avgCb2),ifnull(cb3,avgCb3)) then ifnull(cb2,avgCb2)
		else ifnull(cb3,avgCb3) end
	as cb2, 
least(ifnull(cb1,avgCb1),ifnull(cb2,avgCb2),ifnull(cb3,avgCb3)) as cb3,

greatest(ifnull(s1,avgS1),ifnull(s2,avgS2),ifnull(s3,avgS3)) as s1, 
case when ifnull(s1,avgS1) != greatest(ifnull(s1,avgS1),ifnull(s2,avgS2),ifnull(s3,avgS3))
	and ifnull(s1,avgS1) != least(ifnull(s1,avgS1),ifnull(s2,avgS2),ifnull(s3,avgS3)) then ifnull(s1,avgS1)
	when ifnull(s2,avgS2) != greatest(ifnull(s1,avgS1),ifnull(s2,avgS2),ifnull(s3,avgS3))
	and ifnull(s2,avgS2) != least(ifnull(s1,avgS1),ifnull(s2,avgS2),ifnull(s3,avgS3)) then ifnull(s2,avgS2)
		else ifnull(s3,avgS3) end as s2, 
least(ifnull(s1,avgS1),ifnull(s2,avgS2),ifnull(s3,avgS3)) as s3,

ifnull(k1,avgK1) as k1,
hasThirdDownBack, hasGoalLineBack
from (select chartSeason, chartVersion, chartTeam,
substring_index(group_concat(case when chartPosition = 'QB' and chartRank = 0 then maddenRating end),',',1) as qb1,
substring_index(group_concat(case when chartPosition = 'QB' and chartRank = 1 then maddenRating end),',',1) as qb2,
substring_index(group_concat(case when chartPosition = 'QB' and chartRank = 0 then maddenInjury end),',',1) as qb1Inj,
substring_index(group_concat(case when chartPosition = 'QB' and chartRank = 1 then maddenInjury end),',',1) as qb2Inj,
substring_index(group_concat(case when chartPosition = 'QB' and chartRank = 0 then injuryStatus end),',',1) as qb1Status,
substring_index(group_concat(case when chartPosition = 'QB' and chartRank = 1 then injuryStatus end),',',1) as qb2Status,

substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 0 then maddenRating end),',',1) as rb1,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 1 then maddenRating end),',',1) as rb2,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 2 then maddenRating end),',',1) as rb3,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 0 then maddenInjury end),',',1) as rb1Inj,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 1 then maddenInjury end),',',1) as rb2Inj,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 2 then maddenInjury end),',',1) as rb3Inj,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 0 then injuryStatus end),',',1) as rb1Status,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 1 then injuryStatus end),',',1) as rb2Status,
substring_index(group_concat(case when chartPosition = 'RB' and chartRank = 2 then injuryStatus end),',',1) as rb3Status,

substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 0 then maddenRating end),',',1) as wr1,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 1 then maddenRating end),',',1) as wr2,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 2 then maddenRating end),',',1) as wr3,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 3 then maddenRating end),',',1) as wr4,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 0 then maddenInjury end),',',1) as wr1Inj,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 1 then maddenInjury end),',',1) as wr2Inj,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 2 then maddenInjury end),',',1) as wr3Inj,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 3 then maddenInjury end),',',1) as wr4Inj,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 0 then injuryStatus end),',',1) as wr1Status,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 1 then injuryStatus end),',',1) as wr2Status,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 2 then injuryStatus end),',',1) as wr3Status,
substring_index(group_concat(case when chartPosition = 'WR' and chartRank = 3 then injuryStatus end),',',1) as wr4Status,

substring_index(group_concat(case when chartPosition = 'TE' and chartRank = 0 then maddenRating end),',',1) as te1,
substring_index(group_concat(case when chartPosition = 'TE' and chartRank = 1 then maddenRating end),',',1) as te2,
substring_index(group_concat(case when chartPosition = 'TE' and chartRank = 0 then maddenInjury end),',',1) as te1Inj,
substring_index(group_concat(case when chartPosition = 'TE' and chartRank = 1 then maddenInjury end),',',1) as te2Inj,
substring_index(group_concat(case when chartPosition = 'TE' and chartRank = 0 then injuryStatus end),',',1) as te1Status,
substring_index(group_concat(case when chartPosition = 'TE' and chartRank = 1 then injuryStatus end),',',1) as te2Status,

substring_index(group_concat(case when chartPosition = 'LT' and chartRank = 0 then maddenRating end),',',1) as lt1,
substring_index(group_concat(case when chartPosition = 'LG' and chartRank = 0 then maddenRating end),',',1) as lg1,
substring_index(group_concat(case when chartPosition = 'C' and chartRank = 0 then maddenRating end),',',1) as c1,
substring_index(group_concat(case when chartPosition = 'RG' and chartRank = 0 then maddenRating end),',',1) as rg1,
substring_index(group_concat(case when chartPosition = 'RT' and chartRank = 0 then maddenRating end),',',1) as rt1,

substring_index(group_concat(case when chartPosition in ('DE','RDE') and chartRank = 0 then maddenRating end),',',1) as de1,
substring_index(group_concat(case when (chartPosition = 'LDE' and chartRank = 0)
											or (chartPosition = 'DE' and chartRank = 1 ) then maddenRating end),',',1) as de2,
substring_index(group_concat(case when (chartPosition in ('DT','NT') and chartRank = 0) or
										(chartPosition = 'RDT' and chartRank = 0)then maddenRating end),',',1) as dt1,
substring_index(group_concat(case when (chartPosition in ('DT','NT') and chartRank = 1) or
										(chartPosition = 'LDT' and chartRank = 0) then maddenRating end),',',1) as dt2,

substring_index(group_concat(case when chartPosition in ('MLB','RILB') and chartRank = 0 then maddenRating end),',',1) as mlb1,
substring_index(group_concat(case when (chartPosition = 'MLB' and chartRank = 1) or
										(chartPosition = 'LILB' and chartRank = 0) then maddenRating end),',',1) as mlb2,
substring_index(group_concat(case when chartPosition in ('OLB','SLB') and chartRank = 0 then maddenRating end),',',1) as olb1,
substring_index(group_concat(case when (chartPosition = 'OLB' and chartRank = 1) or
										(chartPosition = 'WLB' and chartRank = 0) then maddenRating end),',',1) as olb2,

substring_index(group_concat(case when chartPosition in ('RCB','CB') and chartRank = 0 then maddenRating end),',',1) as cb1,
substring_index(group_concat(case when (chartPosition = 'CB' and chartRank = 1) or
										(chartPosition = 'LCB' and chartRank = 0) then maddenRating end),',',1) as cb2,
substring_index(group_concat(case when (chartPosition = 'CB' and chartRank = 2) or
										(chartPosition = 'RCB' and chartRank = 1) then maddenRating end),',',1) as cb3,

substring_index(group_concat(case when chartPosition in ('SS','S') and chartRank = 0 then maddenRating end),',',1) as s1,
substring_index(group_concat(case when (chartPosition = 'S' and chartRank = 1) or
										(chartPosition = 'FS' and chartRank = 0) then maddenRating end),',',1) as s2,
substring_index(group_concat(case when (chartPosition = 'S' and chartRank = 2) or
										(chartPosition = 'SS' and chartRank = 1) then maddenRating end),',',1) as s3,

substring_index(group_concat(case when chartPosition in ('K','PK') and chartRank = 0 then maddenRating end),',',1) as k1,

case when sum(thirdDownBack) > 0 then 1 else 0 end as hasThirdDownBack,
case when sum(goalLine) >0 then 1 else 0 end as hasGoalLineBack


from scrapped_data2.depthCharts
left join leagueSims.tempMadden on chartSeason = maddenSeason and chartPlayer = maddenPlayerId
group by 1,2,3) b
left join (select chartSeason as avgSeason, chartVersion as avgVersion,
	avg(case when chartPosition = 'QB' and chartRank = 0 then maddenRating end) as avgQb1,
	avg(case when chartPosition = 'QB' and chartRank = 1 then maddenRating end) as avgQb2,
	avg(case when chartPosition = 'QB' and chartRank = 0 then maddenInjury end) as avgQb1Inj,
	avg(case when chartPosition = 'QB' and chartRank = 1 then maddenInjury end) as avgQb2Inj,
    
	avg(case when chartPosition = 'RB' and chartRank = 0 then maddenRating end) as avgRb1,
	avg(case when chartPosition = 'RB' and chartRank = 1 then maddenRating end) as avgRb2,
	avg(case when chartPosition = 'RB' and chartRank = 2 then maddenRating end) as avgRb3,
	avg(case when chartPosition = 'RB' and chartRank = 0 then maddenInjury end) as avgRb1Inj,
	avg(case when chartPosition = 'RB' and chartRank = 1 then maddenInjury end) as avgRb2Inj,
	avg(case when chartPosition = 'RB' and chartRank = 2 then maddenInjury end) as avgRb3Inj,
    
	avg(case when chartPosition = 'WR' and chartRank = 0 then maddenRating end) as avgWr1,
	avg(case when chartPosition = 'WR' and chartRank = 1 then maddenRating end) as avgWr2,
	avg(case when chartPosition = 'WR' and chartRank = 2 then maddenRating end) as avgWr3,
	avg(case when chartPosition = 'WR' and chartRank = 3 then maddenRating end) as avgWr4,
	avg(case when chartPosition = 'WR' and chartRank = 0 then maddenInjury end) as avgWr1Inj,
	avg(case when chartPosition = 'WR' and chartRank = 1 then maddenInjury end) as avgWr2Inj,
	avg(case when chartPosition = 'WR' and chartRank = 2 then maddenInjury end) as avgWr3Inj,
	avg(case when chartPosition = 'WR' and chartRank = 3 then maddenInjury end) as avgWr4Inj,
    
	avg(case when chartPosition = 'TE' and chartRank = 0 then maddenRating end) as avgTe1,
	avg(case when chartPosition = 'TE' and chartRank = 1 then maddenRating end) as avgTe2,
	avg(case when chartPosition = 'TE' and chartRank = 0 then maddenInjury end) as avgTe1Inj,
	avg(case when chartPosition = 'TE' and chartRank = 1 then maddenInjury end) as avgTe2Inj,
    
	avg(case when chartPosition = 'LT' and chartRank = 0 then maddenRating end) as avgLt1,
	avg(case when chartPosition = 'LG' and chartRank = 0 then maddenRating end) as avgLg1,
	avg(case when chartPosition = 'C' and chartRank = 0 then maddenRating end) as avgC1,
	avg(case when chartPosition = 'RG' and chartRank = 0 then maddenRating end) as avgRg1,
	avg(case when chartPosition = 'RT' and chartRank = 0 then maddenRating end) as avgRt1,
    
	avg(case when chartPosition in ('DE','RDE') and chartRank = 0 then maddenRating end) as avgDe1,
	avg(case when (chartPosition = 'LDE' and chartRank = 0)
					or (chartPosition = 'DE' and chartRank = 1 ) then maddenRating end) as avgDe2,
	avg(case when (chartPosition in ('DT','NT') and chartRank = 0) or
										(chartPosition = 'RDT' and chartRank = 0)then maddenRating end) as avgDt1,
	avg(case when (chartPosition in ('DT','NT') and chartRank = 1) or
										(chartPosition = 'LDT' and chartRank = 0) then maddenRating end) as avgDt2,
    
	avg(case when chartPosition in ('MLB','RILB') and chartRank = 0 then maddenRating end) as avgMlb1,
	avg(case when (chartPosition = 'MLB' and chartRank = 1) or
										(chartPosition = 'LILB' and chartRank = 0) then maddenRating end) as avgMlb2,
	avg(case when chartPosition in ('OLB','SLB') and chartRank = 0 then maddenRating end) as avgOlb1,
	avg(case when (chartPosition = 'OLB' and chartRank = 1) or
										(chartPosition = 'WLB' and chartRank = 0) then maddenRating end) as avgOlb2,
    
	avg(case when chartPosition in ('RCB','CB') and chartRank = 0 then maddenRating end) as avgCb1,
	avg(case when (chartPosition = 'CB' and chartRank = 1) or
										(chartPosition = 'LCB' and chartRank = 0) then maddenRating end) as avgCb2,
	avg(case when (chartPosition = 'CB' and chartRank = 2) or
										(chartPosition = 'RCB' and chartRank = 1) then maddenRating end) as avgCb3,
    
	avg(case when chartPosition in ('SS','S') and chartRank = 0  then maddenRating end) as avgS1,
	avg(case when (chartPosition = 'S' and chartRank = 1) or
										(chartPosition = 'FS' and chartRank = 0) then maddenRating end) as avgS2,
	avg(case when (chartPosition = 'S' and chartRank = 2) or
										(chartPosition = 'SS' and chartRank = 1) then maddenRating end) as avgS3,
    
	avg(case when chartPosition in ('K','PK') and chartRank = 0 then maddenRating end) as avgK1
	from scrapped_data2.depthCharts
	left join leagueSims.tempMadden on chartSeason = maddenSeason and chartPlayer = maddenPlayerId
    group by 1,2
	) a on chartSeason = avgSeason and chartVersion = avgVersion;

drop table if exists leagueSims.tempMadden;
drop table if exists leagueSims.tempChartData;
drop table if exists leagueSims.playerStats;
drop table if exists leagueSims.chartVersion;

end//

delimiter ;