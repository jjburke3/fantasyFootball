


create table refData.playerIds
(
	playerId int primary key auto_increment,
    espnId int,
	statsId int,
    depthChartsId int,
    injuryId int,
    playerName varchar(50),
    index(espnId), index(depthChartsId), index(injuryId)
);

create table refData.playerNames
(
	playerId int,
    playerName varchar(50),
	playerApprox varchar(50),
    playerYear smallint,
    playerTeam tinyint,
    playerPosition varchar(15),
	playerString varchar(75),
	multipleSameName boolean,
    index(playerName,playerYear,playerTeam, playerPosition),
	index(playerString)
);

create table refData.nflTeams
(
	teamId tinyInt primary key auto_increment,
	teamName varchar(25),
	teamAbbrv varchar(7)
);

create table refData.nflTeamVariations
(
	teamId tinyint,
	teamVariation varchar(35),
	index(teamVariation)
);