import requests
import json

from .utils import (two_step_dominance,
                    power_points, )
from .team import Team
from .settings import Settings
from .matchup import Matchup
from .player import Player
from .exception import (PrivateLeagueException,
                        InvalidLeagueException,
                        UnknownLeagueException, )

from .boxCodes import (lineupSlots,
                       nflTeams,
                       nflTeamsAbbrev,
                       playerPos,
                       healthStatus)



class League(object):
    '''Creates a League instance for Public ESPN league'''
    def __init__(self, league_id, year, espn_s2=None, swid=None):

        self.league_id = league_id
        self.year = year
        self.ENDPOINT = "http://fantasy.espn.com/apis/v3/games/ffl/seasons/%d/segments/0/leagues/%d"
        self.teams = []
        self.espn_s2 = espn_s2
        self.swid = swid
        self._fetch_league()
        self._fetch_players()
        self._fetch_teams()

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self):
        
        params = {
           'view':'mTeam'
        }

        cookies = None
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }
        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        ##r = requests.get('%sleagueSettings' % (self.ENDPOINT, ), params=params, cookies=cookies)

        self.status = r.status_code
        
        data = r.json()
        self.teams = {}
        memberData = data['members']
        for team in data['members']:
            teamData = list(filter(lambda d: team['id'] in d['owners'] ,
                                   data['teams']))
            self.teams[team['id']] = {
                    'teamName' : ('Billy' if team['firstName'] == 'Bill' else team['firstName']) + ' ' + team['lastName'],
                    'teamKey' : team['id'],
                    'teamId' : teamData[0]['id'],
                    'nickName' : teamData[0]['location'] + ' ' + teamData[0]['nickname'],
                    'waiverRank' : teamData[0]['waiverRank'],
                    'budgetSpent' : teamData[0]['transactionCounter']['acquisitionBudgetSpent'],
                    'trades' : teamData[0]['transactionCounter']['trades'],
                    'acquisitions' : teamData[0]['transactionCounter']['matchupAcquisitionTotals']
                }

            self.teams[teamData[0]['id']] = {
                    'teamName' : ('Billy' if team['firstName'] == 'Bill' else team['firstName']) + ' ' + team['lastName'],
                    'teamKey' : team['id'],
                    'teamId' : teamData[0]['id'],
                    'nickName' : teamData[0]['location'] + ' ' + teamData[0]['nickname'],
                    'waiverRank' : teamData[0]['waiverRank'],
                    'budgetSpent' : teamData[0]['transactionCounter']['acquisitionBudgetSpent'],
                    'trades' : teamData[0]['transactionCounter']['trades'],
                    'acquisitions' : teamData[0]['transactionCounter']['matchupAcquisitionTotals']
                }
            self.teams[99] = {
                'teamId' : 99,
                'teamName' : 'Bye'
                }



    def _fetch_players(self):
        params = {
            'view':'players_wl'
            }
        playerEndpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/%d/players'
        filters = {"filterActive":{"value":True}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        r = requests.get(playerEndpoint % (self.year), params = params, headers=headers)

        self.players = {}

        for player in r.json():
            self.players[player['id']] = {
                'playerId' : player['id'],
                'player' : player['fullName'].replace("'","_"),
                'position' : player['defaultPositionId'],
                'team' : player['proTeamId'],
                'slots' : player['eligibleSlots']
                }

    def _fetch_teams(self):
        params = {
            'view':'proTeamSchedules'
            }

        teamEndpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/%d/'


        r = requests.get(teamEndpoint % (self.year), params = params)
        teamData = r.json()['settings']['proTeams']
        self.nflTeams = {}
        for team in teamData:
            if 'proGamesByScoringPeriod' in team:
                sched = team['proGamesByScoringPeriod']
            else:
                sched = []
            self.nflTeams[team['id']] = {
                    'id' : team['id'],
                    'abbrev' : team['abbrev'],
                    'games' : sched,
                    'byeWeek' : team['byeWeek']
                }
            self.nflTeams[team['abbrev']] = {
                    'id' : team['id'],
                    'abbrev' : team['abbrev'],
                    'games' : sched,
                    'byeWeek' : team['byeWeek']
                }
        

        


    def transactions(self):
        params = {
            'view' : 'kona_playercard'
            }


        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        
        trans = r.json()['players']

        transList = []
        for player in trans[:50]:
            playerInfo = player['player']
            playerName = playerInfo['fullName']
            playerTeam = playerInfo['proTeamId']
            playerId = playerInfo['id']
            for tran in player['transactions']:
                tranData = {
                        'player' : playerName,
                        'playerId' : playerId,
                        'playerTeam' : playerTeam,
                        'bidAmount' : tran['bidAmount'],
                        'tranPeriod' : tran['scoringPeriodId'],
                        'tranStatus' : tran['status'],
                        'transubOrder' : tran['subOrder'],
                        'tranType' : tran['type'],
                        'leageTeam' : self.teams[tran['teamId']]['teamName'],
                        'tranParts' : []
                    }
                for item in tran['items']:
                    tranData['tranParts'].append({
                        'fromTeam' : 'None' if item['fromTeamId']==0 else self.teams[item['fromTeamId']]['teamName'],
                        'toTeam' : 'None' if item['toTeamId']==0 else self.teams[item['toTeamId']]['teamName'],
                        'pickNumber' : item['overallPickNumber'],
                        'playerId' : item['playerId'],
                        'player' : self.players[item['playerId']]['player'],
                        'position' : self.players[item['playerId']]['position'],
                        'team' : self.players[item['playerId']]['team'],
                        'type' : item['type']
                        })
                transList.append(tranData)

        


    def boxscore(self,week,team):
        params = {
            'view':'mBoxscore',
            'leagueId': self.league_id,
            'seasonId': self.year,
            'scoringPeriodId': week,
            'matchupPeriodId': week,
            'forTeamId' : team
        }
        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        data = r.json()
        if self.status == 401:
            raise PrivateLeagueException(data['error'][0]['message'])

        elif self.status == 404:
            raise InvalidLeagueException(data['error'][0]['message'])

        elif self.status != 200:
            raise UnknownLeagueException('Unknown %s Error' % self.status)

        boxscoreData = data['schedule']
        def checkAwayKey(obj):
            if 'away' in list(obj.keys()):
                return obj['away']['teamId']
            else:
                return 99
        boxscoreData = list(filter(lambda d: (d['matchupPeriodId'] == week and
                                     (d['home']['teamId'] == team or
                                      checkAwayKey(d) == team
                                      )), boxscoreData))

        if boxscoreData[0]['home']['teamId'] == team:
            d = 'home'
            e = 'away'
        else:
            d = 'away'
            e = 'home'
        teamData = boxscoreData[0][d]
        if checkAwayKey(boxscoreData[0]) == 99:
            oppTeam = {'teamId' : 99, 'totalPoints' : 0}
        else:
            oppTeam = boxscoreData[0][e]
        players = teamData['rosterForCurrentScoringPeriod']['entries']
        playerList = []
        for player in players:
            if 'player' in player['playerPoolEntry']:
                playerInfo = player['playerPoolEntry']['player']
                
                if 'appliedStatTotal' not in player['playerPoolEntry']:
                    playerPoints = 0
                else:
                    playerPoints = player['playerPoolEntry']['appliedStatTotal']
                playerData = {'playerName' : playerInfo['fullName'],
                              'playerId' : playerInfo['id'],
                              'playerTeam' : nflTeams[playerInfo['proTeamId']],
                              'slot' : lineupSlots[player['lineupSlotId']],
                              'healthStatus' : 'empty',
                              'stats' : playerInfo['stats'],
                              'playerPos' : playerPos[playerInfo['defaultPositionId']],
                              'Points' : playerPoints
                              }
            else:
                playerData = {'playerName' : 'empty',
                              'playerId' : 'empty',
                              'playerTeam' : 'empty',
                              'slot' : lineupSlots[player['lineupSlotId']],
                              'healthStatus' : 'empty',
                              'stats': 'empty',
                              'playerPos' : 'empty',
                              'Points' : 0}
            playerList.append(playerData)
        result = {'teamId' : teamData['teamId'],
                  'season' : self.year,
                  'week' : week,
                  'teamName' : self.teams[team]['teamName'],
                  'teamPoints' : teamData['rosterForCurrentScoringPeriod']['appliedStatTotal'],
                  'opponentId' : oppTeam['teamId'],
                  'opponentName' : self.teams[oppTeam['teamId']]['teamName'],
                  'opponentPoints' : 0,
                  'playerList' : playerList}

        return result

    def matchup(self,week,team):
        params = {
            'view':'mBoxscore',
            'leagueId': self.league_id,
            'seasonId': self.year,
            'scoringPeriodId': week,
            'matchupPeriodId': week,
            'forTeamId' : team
        }
        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        data = r.json()
        if self.status == 401:
            raise PrivateLeagueException(data['error'][0]['message'])

        elif self.status == 404:
            raise InvalidLeagueException(data['error'][0]['message'])

        elif self.status != 200:
            raise UnknownLeagueException('Unknown %s Error' % self.status)

        boxscoreData = data['schedule']
        def checkAwayKey(obj):
            if 'away' in list(obj.keys()):
                return obj['away']['teamId']
            else:
                return 99
        boxscoreData = list(filter(lambda d: (d['matchupPeriodId'] == week and
                                     (d['home']['teamId'] == team or
                                      checkAwayKey(d) == team
                                      )), boxscoreData))

        if boxscoreData[0]['home']['teamId'] == team:
            d = 'home'
            e = 'away'
        else:
            d = 'away'
            e = 'home'
        teamData = boxscoreData[0][d]
        if checkAwayKey(boxscoreData[0]) == 99:
            return 99
        else:
            return boxscoreData[0][e]['teamId']


    def freeAgents(self, week=None):

        params = {
            'scoringPeriodId':week,
            'view':'kona_player_info'
        }

    def draftData(self):
        params = {
            'view':'mDraftDetail'
        }

        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        
        data = r.json()
        draftData = data['draftDetail']['picks']


        draftPicks = []
        for pick in draftData:
            playerData = self.players[pick['playerId']]

            
            pickData = {
                'round' : pick['roundId'],
                'pick' : pick['overallPickNumber'],
                'teamId' : self.teams[pick['teamId']]['teamName'],
                'playerId' : pick['playerId'],
                'playerName' : playerData['player'],
                'nflTeam' : self.nflTeams[playerData['team']]['abbrev'],
                'playerPosition' : playerPos[playerData['position']]

                }

            draftPicks.append(pickData)
        return draftPicks

    def currentRosters(self):
        params = {
            'view':'mRoster'
        }

        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies = self.cookies, params = params)

        data = r.json()

        rosters = []

        teams = data['teams']

        for team in teams:
            teamId = team['id']
            for player in team['roster']['entries']:
                playerData = player['playerPoolEntry']['player']
                rosters.append({'teamId' : teamId,
                                'playerESPNId' : player['playerId'],
                                'playerName' : playerData['fullName'],
                                'playerPosition' : playerPos[playerData['defaultPositionId']],
                                'playerTeam' : nflTeams[playerData['proTeamId']],
                                'playerSlot' : lineupSlots[player['lineupSlotId']]
                                })
        return rosters
