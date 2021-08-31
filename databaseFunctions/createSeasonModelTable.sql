drop table if exists seasonPredictions.modelPlayerData;

create table seasonPredictions.modelPlayerData
(
	predictionSeason smallint,
	playerId int,
	playerName varchar(50),
	
	chartVersion int,
	playerTeam tinyint,
	playerPosition varchar(10),
	
	injDesignation varchar(10),
	playerStatus varchar(15),
	chartPosition varchar(7),
	chartRank tinyint,
	chartRole varchar(15),
	thirdDownBack tinyint,
	goalLineBack tinyint,
	pr tinyint,
	kr int,
	
	sameTeam tinyint,
	
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
	
	actualPoints decimal(4,1),
	gamesPlayed tinyint,
	
	primary key(predictionSeason,playerId)
);
