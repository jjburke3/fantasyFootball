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

-- table for all payout info

-- table for all rule data

-- table for each yearly schedule

-- table for league teams