# UoM COMP90054 Contest Project

This Wiki can be used as external documentation to the project.
- [1. Home](/home)
- [2. Design decision made](/2_design_decision_made)
- [3. Approaches](/3_approaches)
    - 3.1 Approximate Q-learning
    - 3.2 A star
- [4. Challenges](/4_challenges)
    - 4.1 Approximate Q-learning
    - 4.2 Improvement
- [5. Possible improvements](/5_possible_improvements)
- [6. Comparison tables](/6_comparison_tables)

[Next Page ](/2_design_decision_made)



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

# 2. Design decision made

The purpose of this project is to implement a Pac Man Autonomous Agent that can play and compete in a tournament. There are two agents implemented in the project: the offensive agent and the defensive agent. The general strategy of the offensive agent is made by a hard-coded decision tree. There are three q-learning models in the offensive agent, and each q-learning is used for the particular subtask made by the decision tree. While the task of the defensive is simple. The only thing it needs to do is preventing ghosts eating dots.

Seven candidate techniques can be chosen to implement our agents. The model trained by Model-Based MDP, such as Policy Iteration and Value Iteration, could only be applied to the training map. In contrast, the model trained by Model-Free MDP could be applied to all maps. Because there are many different maps contained in this project, Model-Free MDP could be a better choice. We tried Monte-Carlo Tree Search, but it is hard to train a good model during each tournament because of the limited time between steps. Therefore, approximate Q-learning is then used to implement the offensive agent. A star algorithm, one of the Heuristic Search Algorithms, is suitable for small tasks. Finding the optimal strategy for the offensive agent using A star is infeasible duo to large search space with multi-tasking (eatDots, run, deposit), but it is a good choice to apply it to implement the defensive agent. Compared with other techniques, the search space A star is relatively small (only chase invaders), and a better result can be gained in a shorter time without training. Based on the analysis above, we finally decided to apply approximate Q-learning and A star algorithm to implement our agents.



[Previous Page](/home) | [Next Page](/3_approaches)
