-- table structures for all data pulled from ESPN league


-- table for each individual players points weekly on each team
create table la_liga_data.playerPoints
(
	playerSeason smallint,
    playerWeek tinyint,
    playerTeam tinyint,
    playerTeamSlot tinyint,
    playerVsTeam tinyint,
    playerId int,
    playerESPNId int,
    playerNFLTeam tinyint,
    playerSlot varchar(5),
    playerPosition varchar(5),
    playerPoints decimal(5,1),
    dataCreateDate datetime,
primary key (playerSeason, playerWeek, playerTeam, playerTeamSlot),
index(playerId), index(playerESPNId)
);


-- table for win/loss results

-- table for waiver wire claims

-- table for all transaction records

-- table for all keeper data

-- table for all drafted player data


create table la_liga_data.draftedPlayerData
(
	draftYear smallint,
    draftRound tinyint,
    draftPick smallint,
    selectingTeam varchar(20),
    player int,
    playerESPNId int,
    playerPosition varchar(12),
    playerTeam int,
    dataCreate datetime,
primary key (draftYear, draftRound, draftPick),
index(selectingTeam),
index(player)
);

-- table for all payout info

-- table for all rule data

-- table for each yearly schedule

-- table for league teams

-- table for current roster

create table la_liga_data.currentRoster
(
	rosterId int auto_increment primary key,
	rosterYear smallint,
	rosterWeek tinyint,
	rosterTeam varchar(20),
	rosterSlot varchar(12),
	rosterPlayer int,
	rosterESPNId int,
	rosterNflTeam int,
	rosterPosition varchar(12),
	dataCreate datetime,
	index(rosterPlayer),
	index(rosterYear, rosterWeek)
);