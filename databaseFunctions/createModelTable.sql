drop table if exists leagueSims.weeklyModelPlayerData;

create table leagueSims.weeklyModelPlayerData
(
	predictionSeason smallint,
	playerId int,
	playerName varchar(50),
	
	age tinyint,
	experience tinyint,
		
	playerRating tinyint,
	playerSpeed tinyint,
	playerAgility tinyint,
	playerCatch tinyint,
	playerCarrying tinyint,
	playerBCVision tinyint,
	playerRouteRunning tinyint,
	playerThrowPower tinyint,
	playerThrowAccuracy tinyint,
	playerAwareness tinyint,
	playerInjury tinyint,
	
	primary key(predictionSeason,playerId)
);

drop table if exists leagueSims.weeklyModelPredictWeekData;

create table leagueSims.weeklyModelPredictWeekData
(
	predictionSeason smallint,
	predictionWeek tinyint,
	chartVersion int,
	playerId int,
	playerTeam tinyint,
	playerPosition varchar(10),
	
	playerStatus varchar(15),
	chartPosition varchar(7),
	chartRank tinyint,
	chartRole varchar(15),
	thirdDownBack tinyint,
	goalLineBack tinyint,
	pr tinyint,
	kr int,
	
	sameTeam tinyint,
	
	priorWeekBye tinyint,
	
	priorWeekPlayerStatus varchar(15),
	priorWeekChartPosition varchar(7),
	priorWeekChartRank tinyint,
	
	seasonPoints decimal(4,1),
	priorWeekPoints decimal(4,1),
	seasonGames tinyint,
	priorGame tinyint,
	
	seasonTargets int,
	priorWeekTargets tinyint,
	seasonRushes int,
	priorWeekRushes tinyint,
	
	primary key(predictionSeason, predictionWeek, playerId
	index(playerId),
	index(playerTeam),
	index(playerPosition),
	index(chartVersion),
	index(priorWeekBye)
);
	
drop table if exists leagueSims.weeklyModelPredictedWeekData;

create table leagueSims.weeklyModelPredictedWeekData
(
	predictionSeason smallint,
	predictedWeek tinyint,
	playerId int,
		
	actualPoints decimal(4,1),
	gamePlayed tinyint,
	seasonDone tinyint,
	
	primary key(predictionSeason,predictedWeek,playerId),
	index(playerId)
);

drop table if exists leagueSims.weeklyModelPredictedWeekOppTeamData;

create table leagueSims.weeklyModelPredictedWeekOppTeamData
(
	predictionSeason smallint,
	predictionWeek tinyint,
	predictedWeek tinyint,
	playerId int,
	chartVersion int,
	playerTeam tinyint,
	
	oppTeam tinyint,
	byeWeek tinyint,
	homeTeam tinyint,
	
	priorWeekBye tinyint,
	followWeekBye tinyint,
	
	oppPriorWeekBye tinyint,
	oppFollowWeekBye tinyint,
	
	primary key(predictionSeason,predictionWeek,predictedWeek,playerId),
	index(playerId),
	index(chartVersion),
	index(playerTeam),
	index(oppTeam)
);
	
