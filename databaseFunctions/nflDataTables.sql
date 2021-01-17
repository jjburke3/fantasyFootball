-- table for nfl schedule
create table scrapped_data2.nflSchedule
(
	nflSeason int,
	nflWeek int,
	nflWeekId int,
	nflDate date,
	nflTime time,
	nflHomeTeam int,
	nflRoadTeam int,
	nflHomeScore int,
	nflRoadScore int,
	nflHomeYards int,
	nflRoadYards int,
	nflHomeTO int,
	nflRoadTO int,
	createDateTime datetime,
	primary key (nflSeason, nflWeek,nflWeekId),
	index(nflHomeTeam),
	index(nflRoadTeam)
);

-- table for weekly player stats

create table scrapped_data2.playerStats
(
	statYear smallint,
	statWeek tinyint,
	statPlayer int,
	statPosition varchar(7),
	statTeam tinyint,
	gamePlayed tinyint,
	comp smallint,
	attempt smallint,
	passYard smallint,
	passTD tinyint,
	passInt tinyint,
	passTD40bonus tinyint,
	rushAtt smallint,
	rushYard smallint,
	rushTD tinyint,
	rushTD40bonus tinyint,
	target smallint,
	recept smallint,
	receivYard smallint,
	receivTD tinyint,
	receivTD40bonus tinyint,
	fumble tinyint,
	fumbleLoss tinyint,
	fgMade tinyint,
	fgAttmpt tinyint,
	xPointMade tinyint,
	xPointAttmpt tinyint,
	fg40_49made tinyint,
	fg40_49miss tinyint,
	fg50made tinyint,
	fg50miss tinyint,
	defSack smallint,
	qbHit smallint,
	forceFumble tinyint,
	fumbleRecov tinyint,
	defInt tinyint,
	passDef smallint,
	defTD tinyint,
	fumbleTD tinyint,
	intTd tinyint,
	puntTD tinyint,
	kickTD tinyint,
	pointsAgainst smallint,
	defPassYards smallint,
	defRunYards smallint,
	safety tinyint,
	blockKIck tinyint,
	blockTD tinyint,
	passPoints decimal(4,1),
	runPoints decimal(4,1),
	receivPoints decimal(4,1),
	fumblePoints decimal(4,1),
	stPoints decimal(4,1),
	kickPoints decimal(4,1),
	defPoints decimal(4,1),
	totalPoints decimal(4,1),
	dataCreateDate dateTime,
	primary key(statYear,statWeek,statPlayer),
	index(statTeam),
	index(statPlayer)
);

-- table for injury data

create table scrapped_data2.injuries
(
	id int primary key auto_increment,
	injSeason int,
	injWeek int,
	injDay varchar(12),
	injTime varchar(15),
	injId varchar(255),
	injTeam smallint,
	injPlayer int,
	injPlayerId int,
	injPosition varchar(25),
	injInjury varchar(50),
	injGameStatus varchar(100),
	statDate date,
	endDate date,
	outlook varchar(100),
	createDateTime datetime,
	index(injSeason),
	index(injWeek),
	index(injTeam),
	index(injPlayer)
);

-- table for depthchart data

create table scrapped_data2.depthCharts
(
	id int primary key auto_increment,
	chartVersion int,
	chartSeason int,
	chartWeek smallint,
	chartDay varchar(10),
	chartTime varchar(25),
	chartTeam smallint,
	chartPosition varchar(7),
	chartRank smallint,
	chartPlayer int,
	chartPlayerId varchar(12),
	chartRole varchar(15),
	injuryStatus varchar(15),
	thirdDownBack tinyint,
	goalLine tinyint,
	kickReturner tinyint,
	puntReturner tinyint,
	dataDateTime timestamp DEFAULT current_timestamp(),
	
	index(chartVersion),
	index(chartSeason,chartWeek)
);

-- table for madden data