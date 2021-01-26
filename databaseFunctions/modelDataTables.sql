drop table if exists leagueSims.modelPredictions;
create table leagueSims.modelPredictions
(
	modelSeason	smallint,
	predictedWeek	tinyint,
	predictionWeek	tinyint,
	playerId	int,
	playerPosition	varchar(10),
	modelPrediction	double,
    modelPossibleValues text,
	modelPlayProb	float,
	primary key (modelSeason,predictedWeek,predictionWeek,playerId),
	index(predictedWeek),
	index(predictionWeek),
	index(playerId),
	index(playerPosition)
);