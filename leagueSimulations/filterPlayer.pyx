
cimport cython
import random
import pandas as pd
from libc.stdlib cimport rand, RAND_MAX

cpdef bint returnPlayer(int playerId,
                 double predictionValue,
                 double playProb,
                 double randNum,
                 int playerPosition,
                 double randMean,
                 list allowedPos,
                 list usedPlayers):
    if predictionValue < randMean:
        return False
    if playProb < randNum:
        return False
    if not inPosList(playerPosition,allowedPos):
        return False
    if playerUsed(playerId,usedPlayers):
        return False
    return True

cdef bint inPosList(int pos,
                    list posList):
    cdef int i, n = len(posList)
    for i in range(n):
        if pos == posList[i]:
            return True
    return False

cdef bint playerUsed(int playerId,
                     list usedPlayers):
    cdef int i, n = len(usedPlayers)
    for i in range(n):
        if playerId == usedPlayers[i]:
            return True
    return False

cpdef double returnLineupValues(object positions,
                             object roster,
                             object replacement):
    playersUsed = []
    cdef double replaceMean = 120
    cdef int i
    lineupScore = 0
    for i in range(len(positions)):
        randMean = replacement[positions[i]['replace']]['replaceMean']
        randDistr = replacement[positions[i]['replace']]['replaceDistr']

        rosIndex = [returnPlayer(x['playerId'],
                   x['predictionValue'],
                   x['playProb'],
                   x['randNum'],
                   x['playerPosition'],
                   randMean,
                   positions[i]['allow'],
                   playersUsed) for j, x in 
                      roster['totalRoster'].iterrows()]                                     
        lineupScore += random.choice(randDistr)
    

    return lineupScore
