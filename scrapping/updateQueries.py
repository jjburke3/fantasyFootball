

def updateFunc():
    pointAmounts1 = '''
update scrapped_data2.playerStats 
set passPoints = floor(ifnull(comp,0)/5)*.5 +
	floor(ifnull(passYard,0)/5)*.2 +
    ifnull(passTd,0)*4 +
    ifnull(passInt,0)*-2 +
    ifnull(passTD40Bonus,0)*1,
runPoints = ifnull(rushYard,0)*.1 +
	ifnull(rushTD,0)*6 +
    ifnull(rushTD40bonus,0)*1,
receivPoints = ifnull(recept,0)*1 +
	ifnull(receivYard,0)*.1 +
    ifnull(receivTD,0)*6 +
    ifnull(receivTD40bonus,0)*1,
fumblePoints = ifnull(fumbleLoss,0)*-2,
stPoints = ifnull(puntTD,0)*6 +
	ifnull(kickTD,0)*6 +
    ifnull(blockTD,0)*6,
kickPoints = ifnull(fgMade,0)*3 +
	ifnull(xPointMade,0)*1 +
    ifnull(fg40_49made,0)*.5 +
    ifnull(fg50made,0)*1 +
    (ifnull(fgAttmpt,0)-ifnull(fgMade,0))*-1,
defPoints = ifnull(defSack,0)*1 +
	ifnull(fumbleRecov,0)*2 +
    ifnull(defInt,0)*2 +
    ifnull(defTD,0)*6 +
    ifnull(safety,0)*2 +
    ifnull(blockKick,0)*2 +
    case when pointsAgainst = 0 then 10
    when pointsAgainst between 1 and 6 then 7
    when pointsAgainst between 7 and 13 then 4
    when pointsAgainst between 14 and 17 then 1
    when pointsAgainst between 18 and 27 then 0
    when pointsAgainst between 28 and 34 then -2
    when pointsAgainst between 35 and 45 then -5
    when pointsAgainst > 45 then -7  else 0 end;'''

    pointAmounts2 = '''
update scrapped_data2.playerStats
set totalPoints = passPoints + runPoints +
	receivPoints + fumblePoints + stPoints + kickPoints + defPoints; '''

    replacementValue1 = '''delete from analysis.replacementValue;'''

    replacementValue2 = '''
insert into analysis.replacementValue
 select statYear, statPosition, round(totalPoints,2) as totalPoints, rank
 from (
 select statYear, statPlayer, statPosition, totalPoints,
 @row := if(concat(statYear,statPosition)=@label,@row,0)+1 as rank,
 
 @label := concat(statYear,statPosition)
 from (
 select statYear, statPlayer, statPosition, sum(totalPoints) as totalPoints
 from scrapped_data.playerStats
 where statYear > 2010 and statWeek < 17
 group by 1,2,3
 order by statYear, statPosition, totalPoints desc) a, (select @row := 0, @label := cast('' as char)) t) a
 join (select season, playerPosition, (avg(playerCount)
 +avg(playingCount))/2 as rosterPlayers
from (
select distinct season, week, playerPosition, count(*) as playerCount,
count(case when playerSlot not in ('Bench','IR') then season end) as playingCount
 from la_liga_data.pointsScored where week <= 13 and season > 2014
	
 group by 1,2,3) a group by 1,2) b on (season = statYear or (season = 2015 and statYear < 2015))
	and statPosition = playerPosition and ceil(rosterPlayers) = rank '''

    return [pointAmounts1,pointAmounts2,replacementValue1,replacementValue2]
