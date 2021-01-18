drop procedure if exists refData.fillPlayerIds;
drop procedure if exists refData.addPlayerId;
drop procedure if exists refData.maddenIds;
drop procedure if exists refData.fantasyIds;
drop procedure if exists refData.statsIds;
drop procedure if exists refData.dcIds;
drop procedure if exists refData.dcVersion;
drop procedure if exists refData.injuryIds;
delimiter $$
create procedure refData.addPlayerId(playerName varchar(50), playerTeam int, playerPosition varchar(15), playerYear int, espnID int)
BEGIN
set @playerId = null;
set @playerName = trim(playerName);
set @approxName = replace(replace(replace(trim(playerName),'.',''),'_',''),"'",'');
set @approxName = case when @approxName like '% Jr' or @approxName like '% Sr' or @approxName like '% II'
	or @approxName like '% IV' or @approxName like '% VI' then substring(@approxName,1,(length(@approxName)-3))
	when @approxName like '% III' then substring(@approxName,1,(length(@approxName)-4))
	when @approxName like '% V' then substring(@approxName,1,(length(@approxName)-2))
	else @approxName end;
set @playerTeam = playerTeam;
set @playerPosition = trim(playerPosition);
set @playerYear = playerYear;
set @positionMatch = case when @playerPosition in ('HB','FB') then 'RB'
	when @playerPosition in ('FS','SS') then 'S'
    when @playerPosition in ('DST','Defense') then 'D/ST'
    when @playerPosition in ('NT') then 'DT'
    when @playerPosition in ('RE','LE') then 'DE'
    when @playerPosition in ('OLB','MLB','ROLB','LOLB') then 'LB'
    else @playerPosition end;
-- exact match
if (select count(*) from refData.playerIds a where a.espnID = espnID and a.espnID is not null) > 0 then
	set @playerId = (select playerId from refData.playerIds a where a.espnID = espnID);
    if (select count(*) from refData.playerNames a where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear = @playerYear) = 0 then
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
	end if;
else
	if (select count(*) from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear = @playerYear) >0 then
		set @playerId = (select a.playerId from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear = @playerYear
        limit 1);
        if espnID is not null then
			update refData.playerIds a set a.espnId = espnID where a.espnId is null and a.playerId = @playerId;
		end if;
	-- exact except year
	elseif (select count(*) from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear between  @playerYear - 2 and @playerYear
        ) > 0 then
		set @playerId = (select a.playerId from refData.playerNames a
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear between  @playerYear - 2 and @playerYear
        order by a.playerYear desc limit 1);
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
        if espnID is not null then
			update refData.playerIds a set a.espnId = espnID where a.espnId is null and a.playerId = @playerId;
		end if;
		
		

	-- check if similar spelling but same team and position and last two years
	elseif (select count(*) from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerApprox = @approxName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear between  @playerYear - 1 and @playerYear
        ) > 0 then
		set @playerId = (select a.playerId from refData.playerNames a
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerApprox = @approxName and a.playerTeam = @playerTeam
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear between  @playerYear - 1 and @playerYear
        order by a.playerYear desc limit 1);
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
        if espnID is not null then
			update refData.playerIds a set a.espnId = espnID where a.espnId is null and a.playerId = @playerId;
		end if;

	-- check if same spelling but different team

	elseif (select count(*) from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear = @playerYear
        ) > 0 then
		set @playerId = (select a.playerId from refData.playerNames a
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName
		and a.playerPosition in (@playerPosition,@positionMatch) and a.playerYear = @playerYear
        order by a.playerYear desc limit 1);
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
        if espnID is not null then
			update refData.playerIds a set a.espnId = espnID where a.espnId is null and a.playerId = @playerId;
		end if;
	-- check if same spelling but different position

	elseif (select count(*) from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerYear = @playerYear
        ) > 0 then
		set @playerId = (select a.playerId from refData.playerNames a
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerName = @playerName and a.playerTeam = @playerTeam
		and a.playerYear = @playerYear
        order by a.playerYear desc limit 1);
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
        if espnID is not null then
			update refData.playerIds a set a.espnId = espnID where a.espnId is null and a.playerId = @playerId;
		end if;
	-- check if similar spelling and no other similar spellings

	elseif (select count(*) from refData.playerNames a 
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerApprox = @approxName and  a.playerYear between  @playerYear - 2 and @playerYear
        ) > 0 and (select count(distinct(a.playerId)) from refData.playerNames a where a.playerApprox = @approxName) = 1
        and 
        
        (select max(maxCount) from refData.playerInstances where instanceName = @approxName
			and instanceYear between @playerYear - 1 and @playerYear) = 1
            then
		set @playerId = (select a.playerId from refData.playerNames a
		join refData.playerIds b on b.playerId = a.playerId and (b.espnId is null or espnID is null)
        where a.playerApprox = @approxName
		and a.playerYear between  @playerYear - 2 and @playerYear
        order by a.playerYear desc limit 1);
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
        if espnID is not null then
			update refData.playerIds a set a.espnId = espnID where a.espnId is null and a.playerId = @playerId;
		end if;
	-- create new playerId
	else
		if @positionMatch = 'D/ST' then
			set @playerId = (select min(a.playerId) from refData.playerIds a) - 1;
		else
			set @playerId = (select max(a.playerId) from refData.playerIds a) + 1;
		end if;
        insert into refData.playerIds values(@playerId, espnID, null,null,null,@playerName);
        insert into refData.playerNames values (@playerId, @playerName, @approxName,@playerYear, @playerTeam, @positionMatch, 
												concat_ws('-',@playerName,@playerTeam,@playerPosition,@playerYear),null);
	end if;
end if;
end$$


-- ------------------------------------------------------------------------------------------------------------------------------------

create procedure refData.maddenIds(maddenYear int)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  declare dataName varchar(75);
  declare dataYear int;
  declare dataTeam int;
  declare dataPos varchar(25);
  DECLARE cur CURSOR FOR select player_name, 
		season, teamId, pos
        from madden_ratings.playerRatings
		join refData.nflTeamVariations on team = teamVariation
        left join refData.playerNames a on playerName = player_name and playerTeam = teamId and playerPosition = pos and a.playerYear = season - 1
		where season = maddenYear and playerId is null;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;
  
  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO dataName, dataYear, dataTeam, dataPos;
    IF done THEN
      LEAVE testLoop;
    END IF;
    call refData.addPlayerId(dataName, dataTeam, dataPos, dataYear, null);
  END LOOP testLoop;

  CLOSE cur;
END$$

-- ------------------------------------------------------------------------------------------------------------------------------------

create procedure refData.statsIds(statsYear int, statsWeek int)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  declare dataName varchar(75);
  declare dataYear int;
  declare dataTeam int;
  declare dataPos varchar(25);
  DECLARE cur CURSOR FOR select statPlayer, 
		statYear, teamId, statPosition
        from scrapped_data.playerStats
		join refData.nflTeamVariations on statTeam = teamVariation
        left join refData.playerNames a on playerName = statPlayer and playerTeam = teamId and playerPosition = statPosition 
        and a.playerYear = statYear
		where statYear = statsYear and statWeek = statsWeek  and playerId is null;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;
  
  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO dataName, dataYear, dataTeam, dataPos;
    IF done THEN
      LEAVE testLoop;
    END IF;
    call refData.addPlayerId(dataName, dataTeam, dataPos, dataYear, null);
  END LOOP testLoop;

  CLOSE cur;
END$$

-- ------------------------------------------------------------------------------------------------------------------------------------

create procedure refData.fantasyIds(fantasyYear int, fantasyWeek int)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  declare dataName varchar(75);
  declare dataYear int;
  declare dataTeam int;
  declare dataPos varchar(25);
  declare dataEspnId int;
  DECLARE cur CURSOR FOR select player, 
		season, teamId, b.playerPosition, b.playerId
        from la_liga_data.pointsScored b
		join refData.nflTeamVariations on b.playerTeam = teamVariation
        left join refData.playerNames a on playerName = player and a.playerTeam = teamId and a.playerPosition = b.playerPosition 
        and a.playerYear = season
		where season = fantasyYear and week = fantasyWeek  
        and (a.playerId is null or (b.playerId is not null and b.playerId not in (select distinct espnId from refData.playerIds)));
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;
  
  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO dataName, dataYear, dataTeam, dataPos, dataEspnId;
    IF done THEN
      LEAVE testLoop;
    END IF;
    call refData.addPlayerId(dataName, dataTeam, dataPos, dataYear, dataEspnId);
  END LOOP testLoop;

  CLOSE cur;
END$$
-- ------------------------------------------------------------------------------------------------------------------------------------

create procedure refData.injuryIds(injuriesYear int, injuriesWeek int)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  declare dataName varchar(75);
  declare dataYear int;
  declare dataTeam int;
  declare dataPos varchar(25);
  DECLARE cur CURSOR FOR select injPlayer, 
		injSeason, teamId, injPosition
        from scrapped_data.injuries
		join refData.nflTeamVariations on injTeam = teamVariation
        left join refData.playerNames a on playerName = injPlayer and playerTeam = teamId and playerPosition = injPosition 
        and a.playerYear = injSeason
		where injSeason = injuriesYear and injWeek = injuriesWeek  and playerId is null;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;
  
  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO dataName, dataYear, dataTeam, dataPos;
    IF done THEN
      LEAVE testLoop;
    END IF;
    call refData.addPlayerId(dataName, dataTeam, dataPos, dataYear, null);
  END LOOP testLoop;

  CLOSE cur;
END$$
-- ------------------------------------------------------------------------------------------------------------------------------------
create procedure refData.dcVersion(dcYear int, dcWeek int)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  declare dataVersion int;
  DECLARE cur CURSOR FOR select distinct chartVersion
		from scrapped_data.depthCharts
		where chartSeason = dcYear and chartWeek = dcWeek;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;
  
  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO dataVersion;
    IF done THEN
      LEAVE testLoop;
    END IF;
    call refData.dcIds(dataVersion);
  END LOOP testLoop;

  CLOSE cur;
END$$
-- ------------------------------------------------------------------------------------------------------------------------------------

create procedure refData.dcIds(dcVersion int)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  declare dataName varchar(75);
  declare dataYear int;
  declare dataTeam int;
  declare dataPos varchar(25);
  DECLARE cur CURSOR FOR select chartPlayer, 
		chartSeason, teamId, chartPosition
        from scrapped_data.depthCharts
		join refData.nflTeamVariations on chartTeam = teamVariation
        left join refData.playerNames a on playerName = chartPlayer and playerTeam = teamId and playerPosition = chartPosition 
        and a.playerYear = chartSeason
		where chartVersion = dcVersion and playerId is null;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;
  
  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO dataName, dataYear, dataTeam, dataPos;
    IF done THEN
      LEAVE testLoop;
    END IF;
    call refData.addPlayerId(dataName, dataTeam, dataPos, dataYear, null);
  END LOOP testLoop;

  CLOSE cur;
END$$
-- ------------------------------------------------------------------------------------------------------------------------------------


create procedure refData.fillPlayerIds(startYear int)
BEGIN
declare loopYear int;
declare loopWeek int;

truncate refData.playerIdsStatus;

drop table if exists refData.playerInstances;
create table refData.playerInstances
(instanceYear int, tableSource varchar(50), instanceName varchar(50), maxCount int,
primary key(instanceYear, tableSource, instanceName));
insert into refData.playerInstances
select season, 'madden', case when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% Jr' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% Sr' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% II'
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% IV' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% VI' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-3))
		when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% III' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-4))
		when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% V' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-2))
		else replace(replace(replace(player_name,'.',''),'_',''),"'",'') end, count(*)
        from madden_ratings.playerRatings
        group by 1,3;
	
insert into refData.playerInstances
select season, 'espn', playerName, max(max_count) from (
select season, week, case when replace(replace(replace(player,'.',''),'_',''),"'",'') like '% Jr' 
			or replace(replace(replace(player,'.',''),'_',''),"'",'') like '% Sr' 
			or replace(replace(replace(player,'.',''),'_',''),"'",'') like '% II'
			or replace(replace(replace(player,'.',''),'_',''),"'",'') like '% IV' 
			or replace(replace(replace(player,'.',''),'_',''),"'",'') like '% VI' 
				then substring(replace(replace(replace(player,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player,'.',''),'_',''),"'",''))-3))
		when replace(replace(replace(player,'.',''),'_',''),"'",'') like '% III' 
				then substring(replace(replace(replace(player,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player,'.',''),'_',''),"'",''))-4))
		when replace(replace(replace(player,'.',''),'_',''),"'",'') like '% V' 
				then substring(replace(replace(replace(player,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player,'.',''),'_',''),"'",''))-2))
		else replace(replace(replace(player,'.',''),'_',''),"'",'') end as playerName, count(*) as max_count
        from la_liga_data.pointsScored
        group by 1,2,3) b group by 1,3;
        
insert into refData.playerInstances
select statYear, 'stats', playerName, max(max_count) from
(select statYear, statWeek, 
case when replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% Jr' 
			or replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% Sr' 
			or replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% II'
			or replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% IV' 
			or replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% VI' 
				then substring(replace(replace(replace(statPlayer,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(statPlayer,'.',''),'_',''),"'",''))-3))
		when replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% III' 
				then substring(replace(replace(replace(statPlayer,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(statPlayer,'.',''),'_',''),"'",''))-4))
		when replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') like '% V' 
				then substring(replace(replace(replace(statPlayer,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(statPlayer,'.',''),'_',''),"'",''))-2))
		else replace(replace(replace(statPlayer,'.',''),'_',''),"'",'') end as playerName,count(*) as max_count
 from scrapped_data.playerStats
 group by 1,2,3) b group by 1,3;
        
insert into refData.playerInstances
select chartSeason, 'depthCharts', playerName, max(max_count) from
(select chartSeason, chartVersion, 
case when replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% Jr' 
			or replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% Sr' 
			or replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% II'
			or replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% IV' 
			or replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% VI' 
				then substring(replace(replace(replace(chartPlayer,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(chartPlayer,'.',''),'_',''),"'",''))-3))
		when replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% III' 
				then substring(replace(replace(replace(chartPlayer,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(chartPlayer,'.',''),'_',''),"'",''))-4))
		when replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') like '% V' 
				then substring(replace(replace(replace(chartPlayer,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(chartPlayer,'.',''),'_',''),"'",''))-2))
		else replace(replace(replace(chartPlayer,'.',''),'_',''),"'",'') end as playerName,count(*) as max_count
 from scrapped_data.depthCharts
 group by 1,2,3) b group by 1,3;
        
set loopYear = startYear - 1;
year_loop: LOOP
	if loopYear > 2020 then
		LEAVE year_loop;
	end if;
    
    set loopYear = loopYear + 1;
    if loopYear = 2007 then
		insert into refData.playerNames
        select @row := @row + 1, player_name, 
		case when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% Jr' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% Sr' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% II'
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% IV' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% VI' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-3))
		when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% III' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-4))
		when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% V' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-2))
		else replace(replace(replace(player_name,'.',''),'_',''),"'",'') end, 
		season, teamId, 
        case when pos in ('HB','FB') then 'RB'
	when pos in ('FS','SS') then 'S'
    when pos in ('DST','Defense') then 'D/ST'
    when pos in ('NT') then 'DT'
    when pos in ('RE','LE') then 'DE'
    when pos in ('OLB','MLB','ROLB','LOLB') then 'LB'
    else pos end
        , concat_ws('-',player_name, teamId, pos, season),
		null from madden_ratings.playerRatings
		join (select @row := -1) t
		join refData.nflTeamVariations on team = teamVariation where season = loopYear;
        insert into refData.playerIds
        select distinct playerId,null,null,null,null, playerName
        from refData.playerNames;
        commit;
	else
		insert into refData.playerNames
        select playerId, player_name, 
		case when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% Jr' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% Sr' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% II'
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% IV' 
			or replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% VI' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-3))
		when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% III' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-4))
		when replace(replace(replace(player_name,'.',''),'_',''),"'",'') like '% V' 
				then substring(replace(replace(replace(player_name,'.',''),'_',''),"'",''),1,
					(length(replace(replace(replace(player_name,'.',''),'_',''),"'",''))-2))
		else replace(replace(replace(player_name,'.',''),'_',''),"'",'') end, 
		season, teamId, 
        case when pos in ('HB','FB') then 'RB'
	when pos in ('FS','SS') then 'S'
    when pos in ('DST','Defense') then 'D/ST'
    when pos in ('NT') then 'DT'
    when pos in ('RE','LE') then 'DE'
    when pos in ('OLB','MLB','ROLB','LOLB') then 'LB'
    else pos end
        , concat_ws('-',player_name, teamId, pos, season),
		null from madden_ratings.playerRatings
		join refData.nflTeamVariations on team = teamVariation
        join refData.playerNames a on playerName = player_name and playerTeam = teamId and playerPosition = pos and a.playerYear = season - 1
		where season = loopYear;
        insert into refData.playerIds
        select distinct playerId,null,null,null,null, playerName
        from refData.playerNames a
        where playerId not in (select distinct playerId from refData.playerIds);
        commit;
        call refData.maddenIds(loopYear);
        commit;
        
	end if;
    insert into refData.playerIdsStatus values(loopYear,null,'madden numbers',current_timestamp());
    commit;
    set loopWeek = 0;
    week_loop: LOOP
		if loopWeek > 17 then
			LEAVE week_loop;
		end if;
		-- do nfl stats
        call refData.statsIds(loopYear, loopWeek);
		insert into refData.playerIdsStatus values(loopYear,loopWeek,'stats numbers',current_timestamp());
        commit;
		-- do fantasy stats
        call refData.fantasyIds(loopYear, loopWeek);
		insert into refData.playerIdsStatus values(loopYear,loopWeek,'fantasy numbers',current_timestamp());
        commit;
        -- do depth charts
        call refData.dcVersion(loopYear, loopWeek);
		insert into refData.playerIdsStatus values(loopYear,loopWeek,'depth numbers',current_timestamp());
        commit;
        -- do injuries
        call refData.injuryIds(loopYear, loopWeek);
		insert into refData.playerIdsStatus values(loopYear,loopWeek,'injury numbers',current_timestamp());
        commit;
        set loopWeek = loopWeek + 1;
        iterate week_loop;
	end LOOP;
    select loopYear;
    iterate year_loop;
end LOOP;

END$$
delimiter ;