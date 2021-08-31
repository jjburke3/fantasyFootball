-- populate table initially with all new entries for current week
set @maxSeason = (select max(predictionSeason) from seasonPredictions.modelPlayerData);

delete from seasonPredictions.modelPlayerData
where predictionSeason = @maxSeason;
 

insert into seasonPredictions.modelPlayerData(
	predictionSeason,
	playerId, playerName,playerPosition, playerTeam)

select playerYear, playerId,
playerName, pPosition,
case when pPosition = 'D/ST' then pTeam end
from refData.playerIds
join (select playerId as nameId, playerYear, 
	substring_index(group_concat(playerPosition),',',1) as pPosition,
	substring_index(group_concat(playerTeam),',',1) as pTeam
	from refData.playerNames
	where playerPosition in ('D/ST','QB','RB','FB','TE','WR','HB','K')
	group by 1,2)  b on nameId = playerId
where playerYear >= 2012 and playerName != ''
	and ( playerYear <= (select max(winSeason)+1 from la_liga_data.wins)
			and playerYear > ifnull((select max(predictionSeason) from seasonPredictions.modelPlayerData),0)
        )
        
group by 1,2,3;

-- get player madden numbers
drop table if exists seasonPredictions.tempMadden;
create table seasonPredictions.tempMadden
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

insert into seasonPredictions.tempMadden
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

update seasonPredictions.modelPlayerData
join seasonPredictions.tempMadden on maddenPlayerId = playerId and maddenSeason = predictionSeason
set age = maddenAge, experience = maddenExperience,
	playerRating = maddenRating, playerSpeed = maddenSpeed, playerAgility = maddenAgility,
	playerCatch = maddenCatch, playerCarrying = maddenCarrying, playerBCVision = maddenBCVision,
	playerRouteRunning = maddenRouteRunning, playerThrowPower = maddenThrowPower, 
	playerThrowAccuracy = maddenThrowAccuracy, playerAwareness = maddenAwareness,
	playerInjury = maddenInjury;
	
update seasonPredictions.modelPlayerData b
join (
select predictionSeason, playerId,
round(sum(totalPoints),1) as pointsScored,
sum(gamePlayed) as playedGames,
null
from seasonPredictions.modelPlayerData
left join scrapped_data2.playerStats on predictionSeason = statYear and statWeek <= 16 and statPlayer = playerId
group by predictionSeason, playerId) a on a.predictionSeason = b.predictionSeason and a.playerId = b.playerId
set actualPoints = pointsScored,
	gamesPlayed = playedGames;
	
-- get latest preseason depth chart
update seasonPredictions.modelPlayerData
join (select chartSeason, max(chartVersion) as maxChart
from scrapped_data2.depthCharts
where chartWeek <= 0
group by 1) b on chartSeason = predictionSeason
set chartVersion = maxChart;


-- match weeks to proper depth chart
SET @@group_concat_max_len = 9999999;

drop table if exists seasonPredictions.chartVersion;
create table seasonPredictions.chartVersion
(chartSeason int, predWeek tinyint, chartTeam tinyint, chartVersion int,
primary key (chartSeason, predWeek,chartTeam), index(predWeek), index(chartTeam));
insert into seasonPredictions.chartVersion
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

update seasonPredictions.modelPlayerData b
join scrapped_data2.depthCharts a
on b.chartVersion = a.chartVersion and b.playerId = chartPlayer
set playerTeam = chartTeam, 
 playerStatus =case when injuryStatus in ('','IR','PUP','Suspended') then injuryStatus
 else 'Injured' end, 
 b.chartPosition = a.chartPosition,
b.chartRank = a.chartRank , b.chartRole = case when a.chartRole = 'Starter' then 'Starter' else 'Non-Starter' end, 
b.thirdDownBack = a.thirdDownBack,
b.goalLineBack = a.goalLine, pr = puntReturner, kr = kickReturner;


drop table if exists seasonPredictions.chartVerionPlayers;
create table seasonPredictions.chartVerionPlayers
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
insert into seasonPredictions.chartVerionPlayers
select chartSeason, chartVersion, chartTeam,
ifnull(qb1,avgQb1) as qb1, ifnull(qb2,avgQb2) as qb2, ifnull(qb1Inj,avgQb1Inj) as qb1Inj, ifnull(qb2Inj,avgQb2Inj) as qb2Inj,
qb1Status, qb2Status,

ifnull(rb1,avgRb1) as rb1, ifnull(rb2,avgRb2) as rb2, ifnull(rb3,avgRb3) as rb3,
ifnull(rb1Inj,avgRb1Inj) as rb1Inj, ifnull(rb2Inj,avgRb2Inj) as rb2Inj, ifnull(rb3Inj,avgRb3Inj) as rb3Inj,
rb1Status, rb2Status, rb3Status,

ifnull(wr1,avgWr1) as wr1, ifnull(wr2,avgWr2) as wr2, ifnull(wr3,avgWr3) as wr3, ifnull(wr4,avgWr4) as wr4,
ifnull(wr1Inj,avgWr1Inj) as wr1Inj, ifnull(wr2Inj,avgWr2Inj) as wrInj, ifnull(wr3Inj,avgWr3Inj) as wr3Inj, ifnull(wr4Inj,avgWr4Inj) as wr4Inj,
wr1Status, wr2Status, wr3Status, wr4Status,

ifnull(te1,avgTe1) as te1, ifnull(te2,avgTe2) as te2, ifnull(te1Inj,avgTe1Inj) as te1Ink, ifnull(te2Inj,avgTe2Inj) as te2Inj,
te1Status, te2Status,

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
left join seasonPredictions.tempMadden on chartSeason = maddenSeason and chartPlayer = maddenPlayerId
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
	left join seasonPredictions.tempMadden on chartSeason = maddenSeason and chartPlayer = maddenPlayerId
    group by 1,2
	) a on chartSeason = avgSeason and chartVersion = avgVersion;

drop table if exists seasonPredictions.tempMadden;
drop table if exists seasonPredictions.tempChartData;
drop table if exists seasonPredictions.playerStats;
drop table if exists seasonPredictions.chartVersion;
