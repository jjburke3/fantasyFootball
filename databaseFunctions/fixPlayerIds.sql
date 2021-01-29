select * from refData.playerIds where playerName like '';

select * from refData.playerNames where playerApprox like '';

set @newId = 0;
set @oldId = 0;
update la_liga_data.playerPoints 
set playerId = @newId
where playerId = @oldId;


update scrapped_data2.playerStats
set statPlayer = @newId
where statPlayer = @oldId;

update scrapped_data2.depthCharts
set chartPlayer = @newId
where chartPlayer = @oldId;

update scrapped_data2.injuries
set injPlayer = @newId
where injPlayer = @oldId;

update scrapped_data2.injuredStatus
set injPlayer = @newId
where injPlayer = @oldId;