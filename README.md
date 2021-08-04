# UoM Pacman Contest Project

This Wiki can be used as external documentation to the project.
- [1. Home](#home)
- [2. Pacman contest description](#Pacman Contest Description)
- [3. Approaches](#3. Approaches)
    - 3.1 Approximate Q-learning
    - 3.2 A star
- [4. Comparison tables](#4. Comparison tables)




# Youtube presentation

https://youtu.be/YkFUq0y_gEs

<figure class="video_container">
  <iframe src="https://www.youtube.com/embed/enMumwvLAug" frameborder="0" allowfullscreen="true"> </iframe>
</figure>

## Team Members

* Team name: Project
* Kaixin Chen - [kaixchen@student.unimelb.edu.au](mailto:kaixchen@student.unimelb.edu.au) - 1103908
* Siyu Bian - [siyub@student.unimelb.edu.au](mailto:siyub@student.unimelb.edu.au) - 984002
* Weilun Chen - [weilun.chen@student.unimelb.edu.au](mailto:weilun.chen@student.unimelb.edu.au) - 960043

# Pacman Contest Description

The purpose of this project is to implement a Pac Man Autonomous Agent that can play and compete in a tournament. There are two agents implemented in the project: the offensive agent and the defensive agent. The general strategy of the offensive agent is made by a hard-coded decision tree. There are three q-learning models in the offensive agent, and each q-learning is used for the particular subtask made by the decision tree. While the task of the defensive is simple. The only thing it needs to do is preventing ghosts eating dots.

Seven candidate techniques can be chosen to implement our agents. The model trained by Model-Based MDP, such as Policy Iteration and Value Iteration, could only be applied to the training map. In contrast, the model trained by Model-Free MDP could be applied to all maps. Because there are many different maps contained in this project, Model-Free MDP could be a better choice. We tried Monte-Carlo Tree Search, but it is hard to train a good model during each tournament because of the limited time between steps. Therefore, approximate Q-learning is then used to implement the offensive agent. A star algorithm, one of the Heuristic Search Algorithms, is suitable for small tasks. Finding the optimal strategy for the offensive agent using A star is infeasible duo to large search space with multi-tasking (eatDots, run, deposit), but it is a good choice to apply it to implement the defensive agent. Compared with other techniques, the search space A star is relatively small (only chase invaders), and a better result can be gained in a shorter time without training. Based on the analysis above, we finally decided to apply approximate Q-learning and A star algorithm to implement our agents.


# 3. Approaches

## 3.1 Approximate Q-learning
----

There are five actions in most path planning problems: North, South, West, East, and Stop. Approximate Q-learning calculates the w×f of each action. The action with the maximum w×f value will be chosen as the next step.

The offensive agent is implemented using approximate Q-learning. Before each action is taken, the current game state is generalised as a list of features. The game states which contain the same features are seen as in the same scenario. Approximate Q-learning could learn a general strategy from the same features used for one particular scenario. In tournaments, our offensive always starts eating the nearest dots. When pursued by ghosts, the offensive chooses to run away. It tends to go in the direction of the capsule as well as eating the dots along the way, and avoids running into corners, which is realised by a defined method. However, after eating the capsule, this agent will continue eating dots instead of pursuing scared ghosts, because pursuing them may waste time in most scenarios. Some conditions of going home are also set manually. After carrying a certain number of dots, the offensive tends to go home and put them down before continuing eating dots. This could avoid losing a large number of dots when our offensive agent dies.

----
## 3.2 A star
----

In this project, A star algorithm is applied to implement the defensive agent. In general, the A star algorithm always chooses the optimal path between the starting point and the goal point. It uses manhattan distance between these two points as a heuristic function. This agent offers higher weights to promote the incentive to chase the enemy Pacman with more dots. After one of them eating the capsule, our defensive agent will still follow it keeping one step away.


----
## 3.3 feature selection
----
There are several features extracted from game to generalize different scenarios.

* 'numCarry': how many dots have been eaten
* 'distanceToBorder': distance to the closest border for depositing foods
* 'distanceToFood': get closer to food
* '#Capsule': eating capsule when needed
* 'reverse': reverse penalty
* 'stop': stop penalty 
* 'closerToGhost': penalty when the ghost is in distance of 2
* 'distanceToCapsule': distance to the closest capsule
* 'distanceToCorner': distance to closest corner,
* 'ghost-one-step-away': the ghost is one step away,
* 'bias': general bias

only relevant features will be considered in the subtask.
For example, if the agent wants to eat food, it only considers:
* how many dots do I carry (numCarry)
* How far is the closest dot (distanceToFood)
* did I stopped (stop)
* should I reverse for dots in another area (reverse)


# 4. Comparison tables

## 4.1 Demo
----

Three different maps are selected to analyse the performance of our agents. Every map contains 30 dots in each team.

### map_RANDOM4854

#### Competition results: 11 points

| | eat | deposit | defence | loss |
| ------ | ------ | ------ | ------ | ------ |
| Offensive vs. staff_team_top | 22 | 11 | \ | \ |
| Defensive vs. staff_team_top | \ | \ | 0 | 0 |

#### Approximate Q-learning
![demo_4854](uploads/028b614a2ae71a8dbba983007dc7a0f7/demo_4854.gif)

Although the offensive ate 22 dots, our team only wins by 11 points. The main reason is that the offensive contains 11 dots but was cornered by a ghost. The ghost swings with our agent instead of killing it. This wasted a lot of time, resulting in that our offensive not only could not deposit dots in our home but also could not eat more dots. This situation could happen on many maps which contain many corners. \
The decision tree may need improvement to encourage the offensive agent to return home when it's carrying lots of dots.

----
### map_RANDOM6992

#### Competition results: 21 points

| | eat | deposit | defence | loss |
| ------ | ------ | ------ | ------ | ------ |
| Offensive vs. staff_team_top | 25 | 25 | \ | \ |
| Defensive vs. staff_team_top | \ | \ | 0 | 4 |

#### Approximate Q-learning
![demo_6992](uploads/c4b38a2ba87c1e9b058da3261d0f21c4/demo_6992.gif)

Our agents perform well on this kind of map which contains many straight walls and most dots are around these walls, because of the “one step away” feature mentioned above. The offensive could get out of the swing situation with the defensive ghost around a wall and then keep eating dots. Also, it chooses not to go into the corner even there are dots there

#### A star
![demo_6992_2](uploads/d4890cac7032a95cc1db2b148a557704/demo_6992_2.gif)

The defensive agent simply finds the shortest path to chase the invader with most dots. Despite its simplicity, it is quite efficient in pre-competition. Most agents in the competition can be caught in some corners. However, it has difficulty catching agents like our offensive agent which can detect corners and takes the 'one-step-away' feature into consideration. However, it is possible to prevent them from depositing dots by understanding the intention of the agent. Instead of closely chasing them, the offensive agent can wander around the mandatory path to home.


----
### map_RANDOM9706

#### Competition results: 11 points

| | eat | deposit | defence | loss |
| ------ | ------ | ------ | ------ | ------ |
| Offensive vs. staff_team_top | 11 | 11 | \ | \ |
| Defensive vs. staff_team_top | \ | \ | 6 | 0 |

#### Approximate Q-learning
![9706](uploads/92d1e19d87cf5b16a1efa812fa7d7cef/9706.gif)

On this map, two entrances are far away. One challenge of approximate Q-learning noted above is that it is impossible for it to learn detour in limited time. When the offensive swings with ghosts around one entrance, it could not realise that there is another entrance. If this happens at the beginning of a tournament, our team has little hope of winning. As far as we know, there are no features that can model an alternative path to the goal.

#### A star
![demo_9706_2](uploads/f986c1fb79a7d2563b5abdf1f10297b9/demo_9706_2.gif)

As discussed above, most offensive agents can be captured by chasing the shortest path to the enemy.

----
## 4.2 Conclusion
----

Offensive Agent: \
Pros: 
* agent has learned a sophisticated way to detect good path to run away
* agent has learned how to use a capsule to maximize the time of eating food 

Cons:
* strategies made by decision tree need further improved
* agent has no clue to change an alternative path while the path is blocked by enemy agents

Defensive Agent: \
Pros: 
* A* requires little computing power because the job is divided into small tasks
* effective to handle the majority of enemy offensive agents 

Cons:
* not good at capturing advanced enemy invaders
