# Tallon and the Meanies

The aim of this project was to implement some sort of AI technique to escape and evade the meanies while avoiding pits and collecting bonuses. 

I deceived to try my hand at Q-Learning and the Epsilon Greedy Algorithm. More can be read about these here:

- https://www.geeksforgeeks.org/q-learning-in-python/ 
- https://www.learndatasci.com/tutorials/reinforcement-q-learning-scratch-python-openai-gym/
- https://www.analyticsvidhya.com/blog/2021/04/q-learning-algorithm-with-step-by-step-implementation-using-python/
- https://towardsdatascience.com/q-learning-algorithm-from-explanation-to-implementation-cdbeda2ea187
- https://www.youtube.com/watch?v=iKdlKYG78j4

## Areas to Improve

0) Note: Very very occasionally (found through the testing I did), on my machine the program hangs for no obvious reason. If this happens 
please just retart the game. I have not been able to track this down as it happens so rarely. 

1) A meanie state supercedes other states as they move through the gridworld. Therefdore can step and 'hide' on a bonus (say the last bonus) or pit
then the q_learning does not see any further bonuses and hangs. But the main makeMove() function still sees the bonus so never transitions to
creating a new bonus. The Tallon just does not know where to go ang hangs. This could be resolved if we always add a randomBonus in
if we only have 1 actual bonus left (arena world view). It would just mean that we only have 50% chance tof trying to get that last bonus

2) Because we us the current state to learn a new path to the bonus while avoiding all obsticles we do not properly account for the next state
of a meanie. There is some test script for adding a buffer around the nearest grid position to Tallon if the meanie is 2 grid places away. 
This results in the grid having fewer options to create a path and with a small grid paths are sometimes not available.

3) It would be good to identify the density of the grid in someway so that we can switch from 'get bobnus' mode to survival mode
depending on the value of the remaining rewards, how far away they are (value of shortest path in steps) Vs steps we think we can get if we just kept moving.

4) Because of the way the game is organised in game.py, we update Tallon, then the meanie, then we add a meanie, then we update the display. 
Because the gridWorld takes the current state straight after Tallon move (i.e. call makeMOve()), we are always one step behind the when we look at
the gridWorld in the terminal and the actual arena map displayed. However, that also impacts the game play of the q_learning and getting the shortest path. 

5) Add some functionality when it sees an edge of the gridWorld to not get boxed in (i.e. add some priority to moving EAST moving towards a WEST wall)

6) If Tallon is boxed in by meanies (say 3 of them against a wall/edge), then because we cannot create a shortest path the program will hang. 
A resolution to this would be to just randomly move and die. But I kind of like the fact that in this scenario Tallon will never die. Like a checkmate
but the player refusing to resign their king. The time just keeps going. Even though we don't accrue points, Tallon in this state, is alive and like 
Schrödinger's cat, somehow 'surviving'. so yes, I am stetching here the assignment objectives, but just for fun!!

7) .... lot of others but the above would help a lot.
    

## Videos of Attempts

### Scoring 40 points

https://user-images.githubusercontent.com/44243266/153961130-d83f82ba-c9f0-4fba-86b2-bf451626126b.mov

### Evading the Meanies once all bonuses have been collected

https://user-images.githubusercontent.com/44243266/153962153-b9340ad9-30e7-4fd3-a935-06a1b38b0755.mov

### Meanies covering the last bonus so my Q-Learning has no where to plot a path to :(

https://user-images.githubusercontent.com/44243266/153961155-b2e360e8-b772-4cce-99ed-555d6f498bd3.mov




