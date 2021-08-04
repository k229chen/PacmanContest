# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import sys
sys.path.append('teams/Project/')

from captureAgents import CaptureAgent
import random
import time
import util
from game import Directions, Actions, Grid
import game
import pickle
from util import nearestPoint
from distanceCalculator import manhattanDistance
from operator import itemgetter

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='AgentA', second='AgentD'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]
#  return [eval(first)(firstIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """
    
    def registerInitialState(self, gameState):
      self.start = gameState.getAgentPosition(self.index)
      self.restartPos = None
      self.command = ''
      CaptureAgent.registerInitialState(self, gameState)
    
      enemies = [gameState.getAgentState(i) for i in self.getOpponents(successor)]
      ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
      self.ghostStart = ghosts[0]
    
    def chooseAction(self, gameState):
      """
      Picks among the actions with the highest Q(s,a).
      """
      actions = gameState.getLegalActions(self.index)
    
      # You can profile your evaluation time by uncommenting these lines
      # start = time.time()
      values = [self.evaluate(gameState, a) for a in actions]
      # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    
      maxValue = max(values)
      bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    
      foodLeft = len(self.getFood(gameState).asList())
    
      if foodLeft <= 2:
        bestDist = 9999
        for action in actions:
          successor = self.getSuccessor(gameState, action)
          pos2 = successor.getAgentPosition(self.index)
          dist = self.getMazeDistance(self.start,pos2)
          if dist < bestDist:
            bestAction = action
            bestDist = dist
        return bestAction
    
      return random.choice(bestActions)
    
    def getSuccessor(self, gameState, action):
      """
      Finds the next successor which is a grid position (location tuple).
      """
      successor = gameState.generateSuccessor(self.index, action)
      pos = successor.getAgentState(self.index).getPosition()
      if pos != nearestPoint(pos):
        # Only half a grid position was covered
        return successor.generateSuccessor(self.index, action)
      else:
        return successor
    
    def evaluate(self, gameState, action):
      """
      Computes a linear combination of features and feature weights
      """
      features = self.getFeatures(gameState, action)
      weights = self.getWeights(gameState, action)
#      print("eval: ", action, features * weights)
#      print("features: ", features)
#      print("weights: ", weights)
      return features * weights
    
    def getFeatures(self, gameState, action):
      """
      Returns a counter of features for the state
      """
      features = util.Counter()
      successor = self.getSuccessor(gameState, action)
      features['successorScore'] = self.getScore(successor)
      return features
    
    def getWeights(self, gameState, action):
      """
      Normally, weights do not depend on the gamestate.  They can be either
      a counter or a dictionary.
      """
      return {'successorScore': 1.0}

class AgentA(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """
    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        self.restartPos = None
        self.command = ''
        CaptureAgent.registerInitialState(self, gameState)
        self.corners = self.findCorners(gameState)
        self.lastTenMoves = []
        
        #      print("corners:", self.corners)
        if self.red:
            self.middle = int((gameState.data.layout.width - 2) / 2)
        else:
            self.middle = int((gameState.data.layout.width - 2) / 2 + 1)
        
        self.border = []
        for i in range(1, gameState.data.layout.height - 1):
            if not gameState.hasWall(self.middle, i):
                self.border.append((self.middle, i))    
              
    def findCorners(self, state):
        w = state.data.layout.width
        h = state.data.layout.height
        
        red = []
        blue = []
        corners = []
        for i in range(1, w-1):
            for j in range(1, h-1):
                pos = (i, j)
                numWalls = self.countWalls(state, i, j)
                if numWalls >= 3 and not state.hasWall(i, j):
                    corners.append(pos)
        
        forbidden = []
        for corner in corners:
            while corner != None:
                forbidden.append(corner)
                corner = self.expand(state, forbidden, corner)
                
        
        for p in forbidden:
            if state.isRed(p):
                red.append(p)
            else:
                blue.append(p)
#        self.debugDraw(forbidden, [0,1,0])
        if self.red:
            return blue
        else:
            return red
           
              
    def expand(self, state, forbidden, corner):
        x,y = corner
        if not state.hasWall(x-1, y) and self.countWalls(state, x-1, y)>1 \
        and (x-1,y) not in forbidden:
            return (x-1,y)
        if not state.hasWall(x+1, y) and self.countWalls(state, x+1, y)>1 \
        and (x+1,y) not in forbidden:
            return (x+1,y)
        if not state.hasWall(x, y-1) and self.countWalls(state, x, y-1)>1 \
        and (x,y-1) not in forbidden:
            return (x,y-1)
        if not state.hasWall(x, y+1) and self.countWalls(state, x, y+1)>1 \
        and (x,y+1) not in forbidden:
            return (x,y+1)
        return None
    
    def countWalls(self, state, x, y):
        numWalls = 0
        if state.hasWall(x-1, y):
            numWalls = numWalls+1
        if state.hasWall(x+1, y):
            numWalls = numWalls+1
        if state.hasWall(x, y-1):
            numWalls = numWalls+1
        if state.hasWall(x, y+1):
            numWalls = numWalls+1
        return numWalls
            
    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)
    
        # Computes distance to invaders we can see
        foodList = self.getFood(gameState).asList()
        myPos = gameState.getAgentState(self.index).getPosition()
        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        myAgent = gameState.getAgentState(self.index)
        
        
        if len(foodList) < 3:
            self.command = 'deposit'
        else:
            self.command = 'eatDots'
            
        if len(ghosts) > 0:
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts if a.scaredTimer < 6]
          if len(dists) > 0 and min(dists) < 6:
              self.command = 'run'
        
        if len(foodList) > 0:
          dists = [self.getMazeDistance(myPos, food) for food in foodList]
          minDistance = min(dists)
          distanceToBorder = min([self.getMazeDistance(myPos, self.border[i]) 
                                                     for i in range(len(self.border))])
          numCarry = gameState.getAgentState(self.index).numCarrying
          if (float(numCarry)/ (3*distanceToBorder+0.001) > float(1)/minDistance and numCarry > 2) \
          or (12*distanceToBorder > gameState.data.timeleft and numCarry > 2) \
          or len(foodList)< 3 or numCarry > 7:            
            self.command = 'deposit'
        
            
        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    
#        print("bestActions: ", bestActions)
        if len(self.lastTenMoves) == 10:
            self.lastTenMoves.pop()
        self.lastTenMoves.insert(0, myPos)
        return random.choice(bestActions)
    
    
    def getFeatures(self, state, action):
        features = util.Counter()
        
        
        '''
        normal decision making
        '''
        successor = self.getSuccessor(state, action)
        myPos = successor.getAgentState(self.index).getPosition()
        foodList = self.getFood(successor).asList()
        defendingFoodList = self.getFoodYouAreDefending(successor).asList()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
#        features['numGhost'] = len(ghosts)
        distsToHome = [self.getMazeDistance(myPos, self.border[i]) for i in range(len(self.border))]
        distanceToCapsules = [self.getMazeDistance(myPos, cap) for cap in self.getCapsules(successor)]
        if len(foodList) > 0:
            minFoodDists = [self.getMazeDistance(myPos, food) for food in foodList]
        if len(defendingFoodList) > 0:
            minDefendingFoodDists = [self.getMazeDistance(myPos, food) for food in defendingFoodList]
        if len(invaders) > 0:
            invaderDists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        if len(ghosts) > 0:
            ghostDists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        
        
        
        if self.command == 'run':
            features['numCarry'] = successor.getAgentState(self.index).numCarrying
            if len(foodList) > 0:
                features['distanceToFood'] = min(minFoodDists)
            distToCorners = [self.getMazeDistance(myPos, self.corners[i]) for i in range(len(self.corners))]
            if myPos in self.corners:
                features['distanceToCorner'] = 1            
            if len(ghosts) > 0:
                if min(ghostDists) == 2:
                    features['closerToGhost'] = min(ghostDists)
                elif min(ghostDists) < 2:
                    features['bias'] = 1
                    features['ghostDistance'] = min(ghostDists)
                if len(distanceToCapsules) > 0:
                    features['distanceToCapsule'] = min(distanceToCapsules)
                    features['#Capsule'] = len(distanceToCapsules)
        elif self.command == 'deposit':
            features['distanceToHome'] = min(distsToHome)
            if myPos in self.corners:
                features['distanceToCorner'] = 1   
            # TODO
            if len(ghosts) > 0:
                dangerousDist = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts if a.scaredTimer < 6]
                if myPos == self.start:
                    features['dead'] = 1
                if len(dangerousDist) > 0:
                    if min(dangerousDist) == 2:
                        features['closerToGhost'] = min(dangerousDist)
                    if min(dangerousDist) < 2:
                        features['bias'] = 1
                        features['ghostDistance'] = min(dangerousDist)
                    if len(distanceToCapsules) > 0:
                        features['distanceToCapsule'] = min(distanceToCapsules)
                    
        else:
            features = self.eatDotsFeatures(state, action)
            if len(distanceToCapsules) > 0:
                features['#Capsule'] = len(distanceToCapsules)
        
            
        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[state.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1
        
        return features
    
    
    def eatDotsFeatures(self, state, action):
      features = util.Counter()
      successor = self.getSuccessor(state, action)
      foodList = self.getFood(successor).asList()    
      features['numCarry'] = successor.getAgentState(self.index).numCarrying#self.getScore(successor)
      #features['successorScore'] = self.getScore(successor)
      # Compute distance to the nearest food
    
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance
    
      return features
    
    def getWeights(self, gameState, action):
        if self.command == 'eatDots':
          return {'numCarry': 100, 'distanceToFood': -1, '#Capsule':0.1, 'reverse': -20, 'stop':-50}
        if self.command == 'run':
          return {'distanceToFood': -1, 'numCarry':10, '#Capsule':-30000, 'closerToGhost':-0.1, 'distanceToCapsule':-80, 'distanceToCorner':-70, 'ghostDistance': 100, 'stop':-500, 'bias':-1000}
        if self.command == 'deposit':
            return {'distanceToHome':-1, 'closerToGhost':-0.1, 'distanceToCapsule':-0.41, 'ghostDistance': 100, 'bias':-1000, 'dead':-10000, 'distanceToCorner':-70}
    
    



class AgentB(ReflexCaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''


        self.weights = util.Counter()
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''
        
        self.corners = self.findCorners(gameState)
        #      self.debugDraw(self.corners, [1,0,0])

        if self.red:
            self.middle = int((gameState.data.layout.width - 2) / 2)
        else:
            self.middle = int((gameState.data.layout.width - 2) / 2 + 1)
        self.middlePos = (self.middle, int(gameState.data.layout.height/2))
        
        x,y = self.middlePos
        for i in range(int(gameState.data.layout.height/2)):
            pos = (x,y-i)
            if not gameState.hasWall(x, y-i):
#                self.debugDraw(pos, [1,0,0])
                self.nextPos = pos
                break
            pos = (x,y+i)
            if not gameState.hasWall(x, y+i):
#                self.debugDraw(pos, [1,0,0]) 
                self.nextPos = pos
                break
        
        self.border = []
        for i in range(1, gameState.data.layout.height - 1):
            if not gameState.hasWall(self.middle, i):
                self.border.append((self.middle, i))    


    def findCorners(self, state):
        w = state.data.layout.width
        h = state.data.layout.height
        
        red = []
        blue = []
        corners = []
        for i in range(1, w-1):
            for j in range(1, h-1):
                pos = (i, j)
                numWalls = self.countWalls(state, i, j)
                if numWalls >= 3 and not state.hasWall(i, j):
                    corners.append(pos)
        
        forbidden = []
        for corner in corners:
            while corner != None:
                forbidden.append(corner)
                corner = self.expand(state, forbidden, corner)
                
        
        for p in forbidden:
            if state.isRed(p):
                red.append(p)
            else:
                blue.append(p)
#        self.debugDraw(forbidden, [0,1,0])
        if self.red:
            return blue
        else:
            return red
              
    def expand(self, state, forbidden, corner):
        x,y = corner
        if not state.hasWall(x-1, y) and self.countWalls(state, x-1, y)>1 \
        and (x-1,y) not in forbidden:
            return (x-1,y)
        if not state.hasWall(x+1, y) and self.countWalls(state, x+1, y)>1 \
        and (x+1,y) not in forbidden:
            return (x+1,y)
        if not state.hasWall(x, y-1) and self.countWalls(state, x, y-1)>1 \
        and (x,y-1) not in forbidden:
            return (x,y-1)
        if not state.hasWall(x, y+1) and self.countWalls(state, x, y+1)>1 \
        and (x,y+1) not in forbidden:
            return (x,y+1)
        return None
    
    def countWalls(self, state, x, y):
        numWalls = 0
        if state.hasWall(x-1, y):
            numWalls = numWalls+1
        if state.hasWall(x+1, y):
            numWalls = numWalls+1
        if state.hasWall(x, y-1):
            numWalls = numWalls+1
        if state.hasWall(x, y+1):
            numWalls = numWalls+1
        return numWalls



    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)



        values = [self.evaluate(gameState, a) for a in actions]

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        
#        print("bestActions: ", bestActions)
        
        return random.choice(bestActions)

    def getFeatures(self, state, action):
        features = util.Counter()
        
        
        '''
        normal decision making
        '''
        prevState = self.getPreviousObservation()
        
        successor = self.getSuccessor(state, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()
        foodList = self.getFood(successor).asList()
        defendingFoodList = self.getFoodYouAreDefending(successor).asList()
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
#        features['numGhost'] = len(ghosts)
        distsToHome = [self.getMazeDistance(myPos, self.border[i]) for i in range(len(self.border))]
        distanceToCapsules = [self.getMazeDistance(myPos, cap) for cap in self.getCapsulesYouAreDefending(state)]
        if len(foodList) > 0:
            minFoodDists = [self.getMazeDistance(myPos, food) for food in foodList]
        if len(defendingFoodList) > 0:
            minDefendingFoodDists = [self.getMazeDistance(myPos, food) for food in defendingFoodList]
        if len(invaders) > 0:
            invaderDists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
        if len(ghosts) > 0:
            ghostDists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
        '''
        team = self.getTeam(state)
        teammateIndex = [i for i in team if i != self.index][0]
        teammateState = successor.getAgentState(teammateIndex)
        teammatePos = teammateState.getPosition()
        '''
        # Computes whether we're on defense (1) or offense (0)
        myAgent = state.getAgentState(self.index)
        if myState.isPacman:
            features['onDefense'] = 0
        else:
            features['onDefense'] = 1

        # Computes distance to invaders we can see
        features['numInvaders'] = len(invaders)
        if len(ghosts) > 0:
            features['ghostDistance'] = min(ghostDists)
        if len(invaders) > 0:
            if myAgent.scaredTimer == 0 or min(invaderDists)>2:
                features['invaderDistance'] = min(invaderDists)
            else:
                features['invaderDistance'] = -min(invaderDists)
        else:
            if prevState != None:
                prefood = self.getFoodYouAreDefending(prevState).asList()
                eatenfood = list(set(prefood) - set(defendingFoodList))
                
                if len(eatenfood) > 0:
                    cloestPoint = eatenfood[0]
                    minDist = self.getMazeDistance(myPos, cloestPoint)
                    for f in eatenfood:
                        if self.getMazeDistance(myPos, f) < minDist:
                            cloestPoint = f
                            minDist = self.getMazeDistance(myPos, f)
                        
                    self.nextPos = cloestPoint
                features['invaderDistance'] = self.getMazeDistance(myPos, self.nextPos)

            
        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[state.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        return features

    def getWeights(self, state, action):
        return {'invaderDistance':-2, 'ghostDistance':-1, 'numInvaders':-100, 'onDefense':1000}


class AgentC(AgentA):

    
    def getWeights(self, gameState, action):
        if self.command == 'eatDots':
          return {'numCarry': 100, 'distanceToFood': -1, 'distanceToHome': -0.001, 'distanceToTeammate':1, 'reverse': -15, 'stop':-50}
        if self.command == 'run':
          return {'distanceToFood': -1, 'distanceToHome': -1, 'distanceToCapsule':-80, 'distanceToCorner':-100, 'ghostDistance': 100, 'stop':-500, 'bias':-1000}
        if self.command == 'chaseInvader':
          return {'distanceToInvader':-1, 'distanceToDefendingFood':-0.01}
        if self.command == 'deposit':
            return {'distanceToHome':-1}
        

class AgentD(CaptureAgent):

    def registerInitialState(self, gameState):

        CaptureAgent.registerInitialState(self, gameState)

        self.border = []
        self.prePosition = None
        self.chasePath = None
        self.prevCarry = 0

        self.walls = None
        layout = gameState.data.layout
        height = layout.height
        width = layout.width
        half = width // 2
        wall = layout.walls.data

        if self.red:
            self.middle = int((width - 2) / 2)
        else:
            self.middle = int((width - 2) / 2 + 1)

        for i in range(1, gameState.data.layout.height - 1):
            if not gameState.hasWall(self.middle, i):
                self.border.append((self.middle, i))

        '''
        regard bounds as walls
        '''
        for x in (range(half, width) if self.red else range(half)):
            for y in range(height):
                wall[x][y] = True
        self.walls = wall

    def chaseEnemy(self, gameState, target):
        target = tuple(map(int, target))

        myAgent = gameState.getAgentState(self.index)
        myPos = tuple(map(int, myAgent.getPosition()))
        x, y = myPos

        actions = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        actionVectors = [Actions.directionToVector(action) for action in actions]
        actionVectors = [tuple(int(number) for number in vector) for vector in actionVectors]

        dist = self.getMazeDistance(myPos, target)
        path = self.chasePath

        if path is not None:
            move = manhattanDistance(path[0], target)
            if move == 1:
                path = [target] + path
            if move <= 1:
                if len(path) <= dist:
                    a, b = path.pop()
                    self.chasePath = path if path else None
                    act = Actions.vectorToDirection((a - x, b - y))
                    return act

        self.chasePath = None

        '''
        AStarSearch
        '''

        curPath = []
        queue = util.PriorityQueue()
        queue.push((dist, 0, myPos, curPath), 0)

        visited = set()
        while not queue.isEmpty():
            h, curTotal, curPos, curPath = queue.pop()
            if curPos == target:
                break

            visited.add(curPos)
            x, y = curPos
            for vx, vy in actionVectors:
                a = x + vx
                b = y + vy
                nextPos = a, b
                if not self.walls[a][b] and nextPos not in visited:
                    h = self.getMazeDistance(curPos, target)
                    queue.push((h, curTotal + 1, nextPos, curPath + [nextPos]), 0)

        if not curPath:
            return Directions.STOP

        curPath.reverse()
        x, y = myAgent.getPosition()
        a, b = curPath.pop()
        act = Actions.vectorToDirection((a - x, b - y))
        self.chasePath = curPath if curPath else None

        return act

    def scaredDefender(self, gameState, target, width, height):

        rounds = {(2, 0), (0, 2), (-2, 0), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)}

        bounds = self.border
        myAgent = gameState.getAgentState(self.index)
        myPos = myAgent.getPosition()

        tx, ty = target
        surroundings = [(int(tx + cx), int(ty + cy)) for cx, cy in rounds]
        surroundings = [(x, y) for x, y in surroundings if
                        0 <= x < width and 0 <= y < height and not gameState.hasWall(x, y)]
        aim = min(((s, min(self.getMazeDistance(s, b) for b in bounds), self.getMazeDistance(myPos, s)) for s in
                   surroundings), key=itemgetter(1, 2))[0]
        return aim

    def observationFunction(self, gameState):
        return gameState

    def chooseAction(self, gameState):

        enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        layout = gameState.data.layout
        width = layout.width
        height = layout.height

        bounds = self.border
        myAgent = gameState.getAgentState(self.index)
        myPos = myAgent.getPosition()
        target = None
        state = []
        curNum = 0

        prePosition = self.prePosition
        if prePosition is not None:
            if manhattanDistance(myPos, prePosition) > 1:
                self.chasePath = None

        self.prePosition = myPos

        '''
        Chase the pacman with most food
        '''

        for i in enemies:
            enemyState = i
            foodStolen = enemyState.numCarrying
            enemyPos = enemyState.getPosition()

            if foodStolen > curNum:
                curNum = foodStolen
                target = enemyState.getPosition()
            state.append((
                min(((b, (self.getMazeDistance(enemyPos, b), self.getMazeDistance(myPos, b))) for b in bounds),
                    key=itemgetter(1)), enemyPos, enemyState.isPacman))

        if target is not None:
            if myAgent.scaredTimer > 0:
                aim = self.scaredDefender(gameState, target, width, height)
                return self.chaseEnemy(gameState, aim)
            return self.chaseEnemy(gameState, target)

        '''
        Chase closest pacman if no carrying food 
        '''

        curBounds = None
        maxDist = (9999, 9999)
        bestDist = 9999

        for (border, borderDist), enemyPos, pacmanState in state:
            dist = self.getMazeDistance(enemyPos, myPos)
            if pacmanState:
                if dist < bestDist:
                    target = enemyPos
                    bestDist = dist
            else:
                if borderDist < maxDist:
                    curBounds, maxDist = border, borderDist

        if target is not None:
            if myAgent.scaredTimer > 0:
                aim = self.scaredDefender(gameState, target, width, height)
                return self.chaseEnemy(gameState, aim)
            return self.chaseEnemy(gameState, target)

        '''
        Reach border when no invaders 
        '''

        if myAgent.scaredTimer > 0:
            aim = self.scaredDefender(gameState, curBounds, width, height)
            return self.chaseEnemy(gameState, aim)
        return self.chaseEnemy(gameState, curBounds)