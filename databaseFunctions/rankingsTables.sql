
-- table for depthchart data

create table scrapped_data2.fantasyProsRankings
(
	id int primary key auto_increment,
	rankingVersion int,
	rankingSeason int,
	rankingWeek smallint,
	rankingDay varchar(10),
	rankingTime varchar(25),
	rankingTeam smallint,
	rankingPosition varchar(7),
	rankingPlayer int,
	rankingFantasyProsId varchar(12),
	rankingRank int,
	rankingTier int,
	rankingPosRank int,
	dataDateTime timestamp DEFAULT current_timestamp(),
	
	index(rankingVersion),
	index(rankingSeason,rankingWeek),
	index(rankingPlayer)
);
