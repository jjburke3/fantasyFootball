cdef bint returnPlayer(playerId, predictionValue, playProb, randNum, playerPosition, randMean,
                  allowedPos, usedPlayers):
    if playerPosition not in allowedPos:
        return False
    if predictionValue < randMean:
        return False
    if playProb < randNum:
        return False
    if playerId in usedPlayers:
        return False
    return True
