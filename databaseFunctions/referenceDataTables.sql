


create table refData.playerIds
(
	playerId int primary key,
    espnId int,
	statsId int,
    depthChartsId varchar(10),
    injuryId int,
	pfrId varchar(15),
    playerName varchar(50),
    index(espnId), index(depthChartsId), index(injuryId), index(statsId), index(pfrId)
);

create table refData.playerNames
(
	playerId int,
    playerName varchar(50),
	playerApprox varchar(50),
    playerYear smallint,
    playerTeam tinyint,
    playerPosition varchar(15),
	playerString varchar(750),
	multipleSameName boolean,
	primary key(playerId, playerString),
    index(playerName,playerYear,playerTeam, playerPosition),
	index(playerString),
	index(playerId)
);

create table refData.nflTeams
(
	teamId Int primary key,
	teamName varchar(25),
	teamAbbrv varchar(7)
);

create table refData.nflTeamVariations
(
	teamId tinyint,
	teamVariation varchar(35),
	primary key(teamId, teamVariation),
	index(teamVariation), index(teamId)
);

create table refData.playerName_errors
(
	errorId int primary key auto_increment,
	error_desc text,
	error_player text,
	espnId int,
	statsId int,
	dcId varchar(15),
	injuryId int,
	pfrId varchar(15),
	error_datetime datetime
);