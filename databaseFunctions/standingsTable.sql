
drop table if exists leagueSims.standings;
create table leagueSims.standings
(
	standYear smallint,
    standWeek tinyint,
    standRunCount int,
    standTeam varchar(25),
    standWins int,
	standWinsArry mediumtext,
    standLosses int,
	standLossesArray mediumtext,
    standPoints decimal(12,2),
    standPointsArray mediumtext,
    standPlayoffs int,
    standChamp int,
	standRunnerUp int,
	standThirdPlace int,
    standHighPoints int,
    standLowPoints int,
    standFirstPlace int,
    standBye int,
    standWeeklyHighPoints int,
	standWeeklyHighPointsArray mediumtext,
    primary key (standYear, standWeek, standTeam)
);