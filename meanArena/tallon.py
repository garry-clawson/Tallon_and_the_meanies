# ================ Student Details ======================= 
#
# Name:     Garry Clawson
# ID:       18685030
# Date:     14th Jan 2022
# Module:   CMP9132M
# Title:    AAI Assignment 2
# Version:  0.1.0
# Notes:    This program implements the q_learning AI system with epsilon greedy algorithm to choose next action and encourage exploration
# Credits:  Credits are noted throughout the code
#
# Areas to improve: 0) Note: Very very occasionally (found through the testing I did), the program will hang. If this happens 
#                   please just retart the game. I have not been able to track this down as it happens so rarely. 
# 
#                   1) A meanie state supercedes other states as they move through the gridworld. Therefdore can step and 'hide' on a bonus (say the last bonus) or pit
#                   then the q_learning does not see any further bonuses and hangs. But the main makeMove() function still sees the bonus so never transitions to
#                   creating a new bonus. The Tallon just does not know where to go ang hangs. This could be resolved if we always add a randomBonus in
#                   if we only have 1 actual bonus left (arena world view). It would just mean that we only have 50% chance tof trying to get that last bonus
#
#                   2) Because we us the current state to learn a new path to the bonus while avoiding all obsticles we do not properly account for the next state
#                   of a meanie. There is some test script for adding a buffer around the nearest grid position to Tallon if the meanie is 2 grid places away. 
#                   This results in the grid having fewer options to create a path and with a small grid paths are sometimes not available.
#
#                   3) It would be good to identify the density of the grid in someway so that we can switch from 'get bobnus' mode to survival mode
#                   depending on the value of the remaining rewards, how far away they are (value of shortest path in steps) Vs steps we think we can get if we just kept moving.
#
#                   4) Because of the way the game is organised in game.py, we update Tallon, then the meanie, then we add a meanie, then we update the display. 
#                   Because the gridWorld takes the current state straight after Tallon move (i.e. call makeMOve()), we are always one step behind the when we look at
#                   the gridWorld in the terminal and the actual arena map displayed. However, that also impacts the game play of the q_learning and getting the shortest path. 
#
#                   5) Add some functionality when it sees an edge of the gridWorld to not get boxed in (i.e. add some priority to moving EAST moving towards a WEST wall)
#
#                   6) If Tallon is boxed in by meanies (say 3 of them against a wall/edge), then because we cannot create a shortest path the program will hang. 
#                   A resolution to this would be to just randomly move and die. But I kind of like the fact that in this scenario Tallon will never die. Like a checkmate
#                   but the player refusing to resign their king. The time just keeps going. Even though we don't accrue points, Tallon in this state, is alive and like 
#                   Schrödinger's cat, somehow 'surviving'. so yes, I am stetching here the assignment objectives, but just for fun!!
#
#                   7) .... lot of others but the above would help a lot.
#     
              
# ================ Tallon.py details ======================= 
#
# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

# ================= imports ========================

# Imports
from glob import glob
from pickle import NONE
from re import X
from sre_parse import State
import numpy as np
import string

# Original imports
import world
import random
import utils
from utils import Directions, State


# ================ Global variables and parameters ====================

# Define the global variables
rewards = [NONE]
q_values = [NONE]
environment_rows = 0
environment_columns = 0

# Define q_learning training parameters
epsilon = 0.9 #the percentage of time when we should take the best action (instead of a random action)
discount_factor = 0.9 #discount factor for future rewards
learning_rate = 0.9 #the rate at which the AI agent should lear
actions = ['up', 'right', 'down', 'left'] #numeric action codes: 0 = up, 1 = right, 2 = down, 3 = left

# ================ Required helper functions for q_learning ====================

# Define the gridWorld that the q_learning will use replicate the arena and then to iterate through at each interval
def gridWorld(self):

    global rewards, q_values, environment_columns, environment_rows

    # define the shape and size of the environment (i.e., its states) 
    environment_rows = self.gameWorld.maxY + 1 # direction of a row is > top to bottom
    environment_columns = self.gameWorld.maxX + 1 # direction of a colum is > left to right

    # Create a 3D numpy array to hold the current q_values for each state and action pair: Q(s, a) 
    # The array is of variable size set by utils.py (to match the shape of the environment), and a third "action" dimension.
    # The "action" dimension consists of 4 layers that will allow us to keep track of the q_values for each possible action in each state
    # The value of each (state, action) pair is initialized to 0.
    q_values = np.zeros((environment_rows, environment_columns, 4))

    # Create a 2D numpy array to hold the rewards for each state. The rewards include all meanies, pits and bonuses
    # Each value is initialized to reward of -1.  
    rewards = np.full((environment_rows, environment_columns), -1.)

    # Define locations (i.e., places that the agent can traverse]) for rows and columns of grid in dictionary
    grid_rows = {} #store locations in a dictionary
    # Creates the grid to the size of the number of rows (Note: assumes square arena). This is where we will update our states to
    for i in range(environment_rows):
      grid_rows[i] = []
    
    # Use the states of the arena to define the states of the grid
    getMeanieStates(self, grid_rows)
    getTallonState(self, rewards)
    getPitsStates(self, grid_rows)
    getBonusStates(self, rewards)
    
    # If there are no more bonuses then place a random bonus in the grid - this will keep Tollen moving around after all bonuses are collected
    if 99 not in rewards: 
      #print('New Random Bonus added to gridWorld')
      getRandomBonusState(rewards) #Do this twice so there is something on the grid (the more meanies the more chance this is covered)
      getRandomBonusState(rewards)
    
    #set the rewards for all grid locations at a reward value of -100 (i.e., all pit or meanie positions)
    for row_index in range(environment_rows):
        for column_index in grid_rows[row_index]:
            rewards[row_index, column_index] = -100.

    #print rewards matrix in terminal so we can see where the meanies and pits etc are for our q_learning
    for row in rewards:
        format_string = "{:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}" #just used for easy terminal spacing
        print(format_string.format(*row))

# Get Tallon state and add this to the grid
def getTallonState(self, rewards):
    #print("Tallon state:")
    #self.gameWorld.getTallonLocation().print()
    #print(self.gameWorld.getTallonLocation().x)
    #print(self.gameWorld.getTallonLocation().y)
    x = self.gameWorld.getTallonLocation().x
    y = self.gameWorld.getTallonLocation().y
    rewards[y, x] = -1. #0.

#GC Get meanie state and this to the grid
def getMeanieStates(self, grid_rows):
    #print("Meanies state:")
    for i in range(len(self.gameWorld.getMeanieLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getMeanieLocation()[i].x
        y = self.gameWorld.getMeanieLocation()[i].y
        grid_rows[y].append(x)

        
        # The q_learning will only plot a path avoiding obsticles (i.e. rewards of -100) using the current available view
        # This does not allow for future views or possible positions when moving - 1 x state transition at a time
        # A possible way to resolve is by adding a buffer to the meanies size of 1 x extra grid position around the meanie
        # This reduces the size of the board that can be played and also the available shortest path to a bonus
        #
        # check to see if any position iof a meanie is adjacent to Tallon. if so then mark it as cannot be traversed i.e. -100
        #
        #     0 0 0
        #  T  0 x 0
        #     0 0 0
        #
        # change area that the q_learning process sees as no-go areas (i.e., very low reward -100):
        #
        #     0 0 0               0 0 0 
        #  T  x x 0     or        x x 0
        #     0 0 0           T   x 0 0
        #
        # Another option could also be to give the meanies a really bad reward (say -500), so really promote avoiding them
        '''
        # check directly adjacent areas the meanies could move into >> protect 1 x move ahead but reduces potential paths on the grid
        if x == self.gameWorld.getTallonLocation().x + 2: #i.e. the meanie position is 2 to the EAST (right) of Tallon
            grid_rows[y].append(x + 1)
            print("enemy close - east")
        if x == self.gameWorld.getTallonLocation().x - 2: #i.e. the meanie position is 2 to the WEST (left) of Tallon
            grid_rows[y].append(x - 1)
            print("enemy close - west")
        if y == self.gameWorld.getTallonLocation().y + 2: #i.e. the meanie position is 2 to the NORTH (top) of Tallon
            grid_rows[y + 1].append(x)
            print("enemy close - north")
        if y == self.gameWorld.getTallonLocation().y - 2: #i.e. the meanie position is 2 to the SOUTH (bottom) of Tallon
            grid_rows[y - 1].append(x)
            print("enemy close - south")
        '''

        x = self.gameWorld.getMeanieLocation()[i].x
        y = self.gameWorld.getMeanieLocation()[i].y

        # check diagonal of meanie for areas they could move into - add these to the grid of places to avoid (i.e. low reward of -100)
        # Note: the grid has origin points of 0,0 in the top left (which is why to get to the NE requires a move of -Y and +X)
        if x == self.gameWorld.getTallonLocation().x + 1 and y == self.gameWorld.getTallonLocation().y - 1: #i.e. the meanie position is 1 to the NORTH EAST of Tallon
            grid_rows[y + 1].append(x - 1) # These points are different as the x,y axis is switched in the gridWorld Vs Tallon's world (y,x Vs x,y respectivley)
            #print("enemy close - NE")
        if x == self.gameWorld.getTallonLocation().x - 1 and y == self.gameWorld.getTallonLocation().y - 1: #i.e. the meanie position is 1 to the NORTH WEST of Tallon
            grid_rows[y - 1].append(x - 1)
            #print("enemy close - NW")
        if x == self.gameWorld.getTallonLocation().x + 1 and y == self.gameWorld.getTallonLocation().y + 1: #i.e. the meanie position is 1 to the SOUTH EAST of Tallon
            grid_rows[y + 1].append(x + 1)
            #print("enemy close - SE")
        if x == self.gameWorld.getTallonLocation().x - 1 and y == self.gameWorld.getTallonLocation().y + 1: #i.e. the meanie position is 1 to the SOUTH WEST of Tallon
            grid_rows[y - 1].append(x + 1)
            #print("enemy close - SW")
        

# Get pit state and add this to the grid
def getPitsStates(self, grid_rows):
    #print("Pit state:")
    for i in range(len(self.gameWorld.getPitsLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getPitsLocation()[i].x
        y = self.gameWorld.getPitsLocation()[i].y
        grid_rows[y].append(x)

#Get bonus state and add this to the grid
def getBonusStates(self, rewards):
    #print("Bonus state:")
    for i in range(len(self.gameWorld.getBonusLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getBonusLocation()[i].x
        y = self.gameWorld.getBonusLocation()[i].y
        rewards[y, x] = 99. # A bonus is worth 99 (99 is also an easy number to see on the terminal grid!) so that it is rewarded for traversing to it
      
# Define a function that will choose a random, non-terminal point for a bonus if no further bonuses are available
def getRandomBonusState(rewards):
    #get a random row and column index
    current_row_index = np.random.randint(environment_rows)
    current_column_index = np.random.randint(environment_columns)
    # apply new reward somewhere in grid (I should check if its a terminal state but the aim here is to keep moving)
    while is_terminal_state(current_row_index, current_column_index):
      current_row_index = np.random.randint(environment_rows)
      current_column_index = np.random.randint(environment_columns)
    rewards[current_column_index, current_row_index] = 99.

# Helper function to get the states of the arena and print them to the terminal for trouble shooting
# CREDIT >> Credit to S. Parsons. Below was taken from utils.py
def printGameState(self):
    print("Meanies:")
    for i in range(len(self.gameWorld.getMeanieLocation())):
        self.gameWorld.getMeanieLocation()[i].print()
        
    print("Tallon:")
    self.gameWorld.getTallonLocation().print()

    print("Bonuses:")
    for i in range(len(self.gameWorld.getBonusLocation())):
        self.gameWorld.getBonusLocation()[i].print()

    print("Pits:")
    for i in range(len(self.gameWorld.getPitsLocation())):
        self.gameWorld.getPitsLocation()[i].print()

    print("Clock:")
    print(self.gameWorld.getClock())

    print("Score:")
    print(self.gameWorld.getScore())

    print("")


# Define a function that will choose a random, non-terminal starting location for each q_learbing iteration
def get_starting_location():
  #get a random row and column index
  current_row_index = np.random.randint(environment_rows)
  current_column_index = np.random.randint(environment_columns)
  #continue choosing random row and column indexes until a non-terminal state is identified
  #(i.e., until the chosen state is a of value -1 (any other value such as -100, indicates it is a meanie or pit)).
  while is_terminal_state(current_row_index, current_column_index):
    current_row_index = np.random.randint(environment_rows)
    current_column_index = np.random.randint(environment_columns)
  return current_row_index, current_column_index


# Define a function that determines if the specified location is a terminal state (i.e. has a reward of -100 and is a meanie etc)
def is_terminal_state(current_row_index, current_column_index):
  #if the reward for this location is -1, then it is not a terminal state (i.e., it is an available space to traverse)
  if rewards[current_row_index, current_column_index] == -1.:
    return False
  #elif rewards[current_row_index, current_column_index] == 0.: # 0 is the state of Tallon. We only use this so we can see Tallon on the grid
  #  return False
  else:
    return True


# Define an epsilon greedy algorithm that will choose which action to take next (i.e., where to move next in N/S/E/W)
def get_next_action(current_row_index, current_column_index, epsilon):
  # if a randomly chosen value between 0 and 1 is less than epsilon, 
  # then choose the most promising value from the q_table for this state. Epsilon is set at 0.9.
  if np.random.random() < epsilon:
    return np.argmax(q_values[current_row_index, current_column_index])
  else: # choose a random action. This promotes exploration. 
    return np.random.randint(4)


# Define a function that will get the next location based on the chosen action of N/S/E/W
def get_next_location(current_row_index, current_column_index, action_index):
  new_row_index = current_row_index
  new_column_index = current_column_index
  if actions[action_index] == 'up' and current_row_index > 0:
    new_row_index -= 1
  elif actions[action_index] == 'right' and current_column_index < environment_columns - 1:
    new_column_index += 1
  elif actions[action_index] == 'down' and current_row_index < environment_rows - 1:
    new_row_index += 1
  elif actions[action_index] == 'left' and current_column_index > 0:
    new_column_index -= 1
  return new_row_index, new_column_index


# Define a function that will get the shortest path between any location within the grid that 
# Tallon is allowed to travel and the next bonus location.
def get_shortest_path(start_row_index, start_column_index):
  # Return empty array if this is an invalid starting location
  if is_terminal_state(start_row_index, start_column_index):
    #print("TERMINAL STATE")
    return []
  else: # If this is an available starting location
    current_row_index, current_column_index = start_row_index, start_column_index
    shortest_path = []
    shortest_path.append([current_row_index, current_column_index])
    # Continue moving along the path until we reach the bonus
    while not is_terminal_state(current_row_index, current_column_index):
      # Retrieve the best next action to take
      action_index = get_next_action(current_row_index, current_column_index, 1.)
      # Move to the next location on the path and append the new location to the list
      current_row_index, current_column_index = get_next_location(current_row_index, current_column_index, action_index)
      shortest_path.append([current_row_index, current_column_index])
    return shortest_path 


# Define a function that will train the AI agent
# INSPIRED BY >>  https://www.geeksforgeeks.org/q-learning-in-python/ 
#                 & https://www.learndatasci.com/tutorials/reinforcement-q-learning-scratch-python-openai-gym/
#                 & https://www.analyticsvidhya.com/blog/2021/04/q-learning-algorithm-with-step-by-step-implementation-using-python/
#                 & https://towardsdatascience.com/q-learning-algorithm-from-explanation-to-implementation-cdbeda2ea187

def q_learning(self):

    # Run through 1000 training iterations - taken from trail and error when reveiwing convergence
    for episode in range(1000):
    # Fetch the starting location for this iteration
        row_index, column_index = get_starting_location()
        # continue taking actions (i.e., traversing the grid) until we reach a terminal state
        # (i.e. until we reach the bonus or crash into an meanie or pit)
        while not is_terminal_state(row_index, column_index):
            # Get next action to take (i.e. where to move next)
            action_index = get_next_action(row_index, column_index, epsilon)
 
            # Complete the chosen action, and transition to the next state (i.e. move to the next location)
            old_row_index, old_column_index = row_index, column_index #store the old row and column indexes
            row_index, column_index = get_next_location(row_index, column_index, action_index)
            
            # Receive the reward for moving to the new state and calculate the temporal difference (TD)
            reward = rewards[row_index, column_index]
            old_q_value = q_values[old_row_index, old_column_index, action_index]
            temporal_difference = reward + (discount_factor * np.max(q_values[row_index, column_index])) - old_q_value

            # Update the q_value for the previous state and action pair
            new_q_value = old_q_value + (learning_rate * temporal_difference)
            q_values[old_row_index, old_column_index, action_index] = new_q_value

            # Print the converging results for the updated q_value
            # this will be used for analysing convergence times (i.e. is 1000 iterations enough)
            #for row in q_values:
            #    print(row)


# ================ main tallon class ====================

# Define the Talon class as per requirements to run the program from a vanilla project using just a tallon.py file
class Tallon():

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can query the state of the world
        self.gameWorld = arena

        # Define what moves are possible to Tallon
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
    def makeMove(self):

        # Get the location of the Bonuses.
        allBonuses = self.gameWorld.getBonusLocation()

        # Main game program which calls the functional requirements for the q_learning AI
        # if there are still bonuses move towards the next one. Else, create a new bonus in the q_learning grid so the game keeps playing
        if len(allBonuses) > 1:

            # Print start of game state header and also game state so we know were all the grid participants are
            print(" ---- GAME STATE: ----")
            #printGameState(self)

            # Call gridWorld function so we can create the state of the arena for the q_learnign process
            gridWorld(self)

            # Take the created state of the gridWorld and apply q_learning over 1000 iterations
            # returns the shortest path to the reward which avoids all meanies and pits etc (everything with -100 negative reward)
            # the first value fo this will be used to move the tallon to its next position
            # we should see that the path stays the same when the tallen moves unless blocked, then a new path will provail
            q_learning(self)

            # Prints the shortest path after the q_learnign process
            # Returns the shortest path to the reward which avoids all meanies and pits in that current state (i.e. everything with -100 reward)
            getShortestPath = get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)
            print("Shortest Path to next Bonus (row, column): ", get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)) 

            if getShortestPath == []:
              #print("There is no shortest path - game lost")
              return State.LOST
            else:
              # Define the variables to hold the first [0] and second [1[] path positions from the geSthortestPath function
              currentPosition = getShortestPath[0]
              nextPosition = getShortestPath[1]

              # As we know the meanies (dynamic) and pits (static) positions we will plan a trajectory that avoids them using the shortest path
              # We do this by comparing the current and next position on the grid and moving in the required direction to avoid all obsticles but also moves us closer to the bonus
              # INSPIRED BY >> S. Parsons makeMove() code from original tallon.py project file
              if nextPosition[1] > currentPosition[1]: #i.e. the next position is further to the EAST than current
                  return Directions.EAST 
              if nextPosition[1] < currentPosition[1]: #i.e. the next position is further to the WEST than current
                  return Directions.WEST
              if nextPosition[0] < currentPosition[0]: #i.e. the next position is further to the NORTH than current
                  return Directions.NORTH
              if nextPosition[0] > currentPosition[0]: #i.e. the next position is further to the SOUTH than current
                  return Directions.SOUTH
       
        # If no bonusses are left then randomly create one to provide somewhere for the q_learning process to target so Tallon can move
        # Resuse the above code functions to enable the movements (yep, should follow the DRY principle here)
        # This will now continue trying the build up clock points until Tallon is either captured or falls into a pit (somehow)
        else: 
          print("\n ---- NO LOOT LEFT SO JUST AVOID MEANIES & PITS: ----")
          #printGameState(self)
          gridWorld(self)
          q_learning(self)

          getShortestPath = get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)
          print("Shortest path (row, column): ", get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)) 

          if getShortestPath == []:
            #print("There is no shortest path - game lost")
            return State.LOST
          else:
            currentPosition = getShortestPath[0]
            nextPosition = getShortestPath[1]

            if nextPosition[1] > currentPosition[1]: #i.e. the next position is further to the EAST than current
                return Directions.EAST 
            if nextPosition[1] < currentPosition[1]: #i.e. the next position is further to the WEST than current
                return Directions.WEST
            if nextPosition[0] < currentPosition[0]: #i.e. the next position is further to the NORTH than current
                return Directions.NORTH
            if nextPosition[0] > currentPosition[0]: #i.e. the next position is further to the SOUTH than current
                return Directions.SOUTH
            
