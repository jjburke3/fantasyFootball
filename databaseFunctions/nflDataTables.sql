-- table for nfl schedule

-- table for weekly player stats

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