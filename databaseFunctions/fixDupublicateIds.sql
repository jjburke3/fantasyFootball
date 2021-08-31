select playerName, count(*),group_concat(playerId) from refData.playerIds
group by 1
order by count(*) desc;
select * from refData.playerIds where playerName = 'Michael Walker';
select * from refData.playerNames where playerName = 'Michael Walker';
set @playerName = 'Michael Walker';
set @playerId = 12447;
update la_liga_data.draftedPlayerData set player = @playerId 
where player in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update la_liga_data.keepers set player = @playerId 
where player in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update la_liga_data.playerPoints set playerId = @playerId 
where playerId in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update scrapped_data2.depthCharts set chartPlayer = @playerId 
where chartPlayer in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update scrapped_data2.fantasyProsRankings set rankingPlayer = @playerId 
where rankingPlayer in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update scrapped_data2.injuries set injPlayer = @playerId 
where injPlayer in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update scrapped_data2.injuredStatus set injPlayer = @playerId 
where injPlayer in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update scrapped_data2.playerStats set statPlayer = @playerId 
where statPlayer in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);
update madden_ratings.playerRatings set maddenPlayerId = @playerId 
where maddenPlayerId in (select playerId from refData.playerIds where playerName = @playerName and playerId != 9216);