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


from captureAgents import CaptureAgent
import random, time
import util
from game import Directions, Actions
import game
import os
import pickle

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent', numTraining=1000):
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
  print(numTraining)
  return [eval(first)(firstIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
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
    print("start registeration")
    self.epsilon = 0.0
    self.gamma = 0.9
    self.alpha = 0.9


    self.eatDots = util.Counter()
    self.run = util.Counter()
    self.deposit = util.Counter()

    self.numFood = len(self.getFood(gameState).asList())
    self.gridSize = gameState.data.layout.width * gameState.data.layout.height
    

    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''

    self.command = 'eatDots'
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

    if os.path.exists('eatDots'):
        print("restore weights")
        with open('eatDots', 'rb') as handle:
          self.eatDots = pickle.loads(handle.read())
        with open('run', 'rb') as handle:
          self.run = pickle.loads(handle.read())
        with open('deposit', 'rb') as handle:
          self.deposit = pickle.loads(handle.read())
                  
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


  def getWeights(self):
    if self.command == 'eatDots':
        return self.eatDots
    if self.command == 'run':
        return self.run
    if self.command == 'deposit':
        return self.deposit

  def getQValue(self, state, action):
    w = self.getWeights()
    f = self.getFeatures(state, action)
#    for key in f.keys():
#      w[key] = self.getWeights()[key]
    return w * f

  def update(self, state, action, nextState, reward):
    """
     Should update your weights based on transition
    """
    nextAction = self.computeActionFromQValues(nextState)
    expectedReward = reward + self.gamma*self.getQValue(nextState, nextAction)
    qValue = self.getQValue(state, action)
    f = self.getFeatures(state, action)
    for key in f.keys():
      self.getWeights()[key] += self.alpha*(expectedReward-qValue)*f[key]

  def computeActionFromQValues(self, state):
    legalActions = state.getLegalActions(self.index)
    value = util.Counter()
    for action in legalActions:
        value[action] = self.getQValue(state, action)
#    print(value)
    return value.argMax()

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

    '''
    You should change this in your own agent.
    '''
    foodList = self.getFood(gameState).asList()
    successor = gameState.getAgentState(self.index)
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

    action = None
    if util.flipCoin(self.epsilon):
        action = random.choice(actions)
    else:
        action = self.computeActionFromQValues(gameState)

    '''
    select the next action a' to s' and update Q(s, a)
    '''
    successor = self.getSuccessor(gameState, action)
#    if prevState != None:
    reward = 0
    '''
      reward shaping
      '''
    numCarry = successor.getAgentState(self.index).numCarrying \
        - gameState.getAgentState(self.index).numCarrying
    numReturn = successor.getAgentState(self.index).numReturned \
        - gameState.getAgentState(self.index).numReturned
    reward = reward + numCarry + numReturn*2
    if action == Directions.STOP:
        reward = reward-1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev:
        reward = reward-1
    if len(foodList) > 0:
      dists = [self.getMazeDistance(myPos, food) for food in foodList]
      minDistance = min(dists)
      reward = reward - minDistance / self.gridSize
    if self.command == 'deposit':
      distanceToBorder = min([self.getMazeDistance(myPos, self.border[i]) 
                                                 for i in range(len(self.border))])
      reward = reward - distanceToBorder / self.gridSize
    if self.command == 'run':
        reward = reward - len(self.getCapsules(successor))*2

#    print("reward: ", reward)
#    print("before: ", self.getWeights())
    self.update(gameState, action, successor, reward)
#    print("after: ", self.getWeights())
#    self.prevAction = action
#    if self.prevAction == None:
#        self.prevAction == Directions.STOP
    return action

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
        
        '''
        team = self.getTeam(state)
        teammateIndex = [i for i in team if i != self.index][0]
        teammateState = successor.getAgentState(teammateIndex)
        teammatePos = teammateState.getPosition()
        '''
        if self.command == 'run':
            features['numCarry'] = successor.getAgentState(self.index).numCarrying / self.numFood
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
                    features['distanceToCapsule'] = min(distanceToCapsules) / self.gridSize
                    features['#Capsule'] = len(distanceToCapsules)
        elif self.command == 'deposit':
            features['distanceToHome'] = min(distsToHome) / self.gridSize
            # TODO
            if len(ghosts) > 0:
                dangerousDist = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts if a.scaredTimer < 6]
                if len(dangerousDist) > 0:
                    if min(dangerousDist) == 2:
                        features['closerToGhost'] = min(dangerousDist)
                    if min(dangerousDist) < 2:
                        features['bias'] = 1
                        features['ghostDistance'] = min(dangerousDist)
                    if len(distanceToCapsules) > 0:
                        features['distanceToCapsule'] = min(distanceToCapsules) / self.gridSize
                    
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
      features['numCarry'] = successor.getAgentState(self.index).numCarrying/self.numFood#self.getScore(successor)
      #features['successorScore'] = self.getScore(successor)
      # Compute distance to the nearest food
    
      if len(foodList) > 0: # This should always be True,  but better safe than sorry
        myPos = successor.getAgentState(self.index).getPosition()
        minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
        features['distanceToFood'] = minDistance/self.gridSize
        return features

  def final(self, gameState):
    self.observationHistory = []
    with open('eatDots', 'wb') as handle:
      pickle.dump(self.eatDots, handle)
    with open('run', 'wb') as handle:
      pickle.dump(self.run, handle)
    with open('deposit', 'wb') as handle:
      pickle.dump(self.deposit, handle)
