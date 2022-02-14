# ----------------- Start Student Details -----------------------------

# Name:     Garry Clawson
# ID:       18685030
# Date:     14th Jan 2022
# Module:   CMP9132M
# Title:    AAI Assignment 2
# Version:  0.1.0
# Notes:    This program implements the q_learning AI system with epsilon greedy algorithm to choose next action and encourage exploration
# Credits:  Credits are noted throughout the code
#           
# ----------------- End Student Details -----------------------------

# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

# ================= imports ========================

# imports
from glob import glob
from pickle import NONE
from re import X
import numpy as np
import string

# original imports
import world
import random
import utils
from utils import Directions


# ================ Global variables and parameters ====================

rewards = [NONE]
q_values = [NONE]
environment_rows = 0
environment_columns = 0

# define q_learning training parameters
epsilon = 0.9 #the percentage of time when we should take the best action (instead of a random action)
discount_factor = 0.9 #discount factor for future rewards
learning_rate = 0.9 #the rate at which the AI agent should lear
actions = ['up', 'right', 'down', 'left'] #numeric action codes: 0 = up, 1 = right, 2 = down, 3 = left

# ================ Required helper functions for q_learning ====================

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
    aisles_rows = {} #store locations in a dictionary

    # Initialise the dictionary so we can later add states (i.e.m of meanies, pits etc)    
    aisles_rows[0] = []
    aisles_rows[1] = []
    aisles_rows[2] = []
    aisles_rows[3] = []
    aisles_rows[4] = []
    aisles_rows[5] = []
    aisles_rows[6] = []
    aisles_rows[7] = []
    aisles_rows[8] = []
    aisles_rows[9] = []
    
    
    # Use the states of the arena to define the states of the grid
    getMeanieStates(self, aisles_rows)
    getTallonState(self, rewards)
    getPitsStates(self, aisles_rows)
    getBonusStates(self, rewards)
    
    # If there are no more bonuses then place a random bonus in the grid - this will keep Tollen moving around after all bonuses are collected
    if 99 not in rewards: 
      print('random bonus added')
      getRandomBonusState(rewards)
    
    #set the rewards for all grid locations at a reward value of -100 (i.e., all pit or meanie positions)
    for row_index in range(0, 10):
        for column_index in aisles_rows[row_index]:
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
    rewards[y, x] = 0. 

#GC Get meanie state and this to the grid
def getMeanieStates(self, aisles_rows):
    #print("Meanies state:")
    for i in range(len(self.gameWorld.getMeanieLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getMeanieLocation()[i].x
        y = self.gameWorld.getMeanieLocation()[i].y
        aisles_rows[y].append(x)

        '''
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
        
        # check directly adjacent areas the meanies could move into >> protect 1 x move ahead but reduces potential paths on the grid
        if x == self.gameWorld.getTallonLocation().x + 2: #i.e. the meanie position is 2 to the EAST than Tallon
            aisles_rows[y].append(x + 1)
            print("enemy close - east")
        if x == self.gameWorld.getTallonLocation().x - 2: #i.e. the meanie position is 2 to the WEST than Tallon
            aisles_rows[y].append(x - 1)
            print("enemy close - west")
        if y == self.gameWorld.getTallonLocation().y + 2: #i.e. the meanie position is 2 to the NORTH than Tallon
            aisles_rows[y + 1].append(x)
            print("enemy close - north")
        if y == self.gameWorld.getTallonLocation().y - 2: #i.e. the meanie position is 2 to the SOUTH than Tallon
            aisles_rows[y - 1].append(x)
            print("enemy close - south")

        # check diagonal of enemy for areas they could move into - add these ot the grid
        if x == self.gameWorld.getTallonLocation().x + 1 and y == self.gameWorld.getTallonLocation().y + 1: #i.e. the meanie position is 1 to the NORTH EAST than tallon
            aisles_rows[y + 1].append(x + 1)
            print("enemy close - NE")
        if x == self.gameWorld.getTallonLocation().x - 1 and y == self.gameWorld.getTallonLocation().y + 1: #i.e. the meanie position is 1 to the NORTH WEST than tallon
            aisles_rows[y + 1].append(x - 1)
            print("enemy close - NW")
        if x == self.gameWorld.getTallonLocation().x + 1 and y == self.gameWorld.getTallonLocation().y - 1: #i.e. the meanie position is 1 to the SOUTH EAST than tallon
            aisles_rows[y - 1].append(x + 1)
            print("enemy close - SE")
        if x == self.gameWorld.getTallonLocation().x - 1 and y == self.gameWorld.getTallonLocation().y - 1: #i.e. the meanie position is 1 to the SOUTH WEST than tallon
            aisles_rows[y - 1].append(x - 1)
            print("enemy close - SW")
        '''



# Get pit state and add this to the grid
def getPitsStates(self, aisles_rows):
    #print("Pit state:")
    for i in range(len(self.gameWorld.getPitsLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getPitsLocation()[i].x
        y = self.gameWorld.getPitsLocation()[i].y
        aisles_rows[y].append(x)

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
  elif rewards[current_row_index, current_column_index] == 0.: # 0 is the state of Tallon. We only use this so we can see Tallon on the grid
    return False
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
    print("TERMINAL STATE")
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
# INSPIRED BY >> 
def q_learning(self):

    # Run through 1000 training iterations - taken form trail and error of convergence
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

            #print the coberging results for the updated q_value
            #this will be used for analysing convergence times (i.e. is 1000 iterations enough)
            #for row in q_values:
            #    print(row)

    print('Training complete!')


# Define the Talon class as per requirements ot run the program from a vanilla project using just a tallon.py file
class Tallon():

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. << GC this is key
        # It ignores Meanies  >> GC we need to upade this to caputure thoise probabalistic pit action
        # and pits.
        # 
        # Get the location of the Bonuses.

        # ------ GC NOTES ----------------
        #
        # Process: Think bellman equation, value iteration, stragty and policies, q-learning
        # Find the current states of the grid
        # then calculate the stae values and probablities
        # move acoording to what the baddies can do if they are near you
        # if you have found all the bonuesses then keep moving away
        # focuis on the whole stae first
        #
        # ----- GC END NOTES --------------

        allBonuses = self.gameWorld.getBonusLocation()

        # if there are still bonuses, move towards the next one. << GC does this include the 0.95 probablity aspect?
        if len(allBonuses) > 0:

            #GC print game state
            print(" ---- GAME STATE: ----")
            #printGameState(self)

            # GC how to print an object https://www.delftstack.com/howto/python/print-object-python/ 
            #myPosition.print()


            # GC create gridworld for q_learning process to identify next move E/W/N/S
            gridWorld(self)

            # GC takes the sta eof the gridWorld form above and applies q_learning over 1000 iterations
            # returns the shortest path to the reward which avoids all meanies and pits etc (everything with -100 negative reward)
            # the first value fo this will be used to move the tallon to its next position
            # we should see that the path stays the same when the tallen moves unless blocked, then a new path will provail
            q_learning(self)

            # GC prints shortest path after the q_learnign has completed
            # the shortest path is form tallons current location in the grid
            getShortestPath = get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)
            print("Shortest path (row, column): ", get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)) 

            # TODO create function that compares current position (1st array item) and next move and moves that way using return.Directions.EAST etc

            #print 2nd item in array

            currentPosition = getShortestPath[0]
            #print("current position: ", currentPosition)
            nextPosition = getShortestPath[1]
            #print("next position: ", nextPosition)

            #positions for y and x
            #print("current position y: ", currentPosition[0])
            #print("current position x: ", currentPosition[1])
            #print("next position y: ", nextPosition[0])
            #print("next position x: ", nextPosition[1])

            # GC East is left in the map and should be to avoid an enemy
            # GC tallon is updated through ther world.py file and updatetallon() function from game.py
            # If not at the same x coordinate, reduce the difference
            # The next position is only different by 1 value as it can only move in 1 direction
            # so we check to see which position that is and then move in that direction using directions.EAST etc
            # since were are just using the shortestPath to get out positions these co-ordinates are in y, x (as in numpy array row then column)
            # the Tallons position is in x, y. This is whey when we get the shortest path we specify y then x to get our starting point iin the righty position

            
            # The positions here are defined on the grid with 'further' menaing to the down and right
            # Inspired by S. Parsons move code commented aout below
            if nextPosition[1] > currentPosition[1]: #i.e. the next position is further to the EAST than current
                return Directions.EAST 
            if nextPosition[1] < currentPosition[1]: #i.e. the next position is further to the WEST than current
                return Directions.WEST
            if nextPosition[0] < currentPosition[0]: #i.e. the next position is further to the NORTH than current
                return Directions.NORTH
            if nextPosition[0] > currentPosition[0]: #i.e. the next position is further to the SOUTH than current
                return Directions.SOUTH
            
            



            '''
            # GC East is left in the map and should be to avoid an enemy
            # GC tallon is updated through ther world.py file and updatetallon() function from game.py
            # If not at the same x coordinate, reduce the difference
            if nextBonus.x > myPosition.x:
                return Directions.EAST # GC note that EAST is an enum
            if nextBonus.x < myPosition.x:
                return Directions.WEST
            # If not at the same y coordinate, reduce the difference
            if nextBonus.y < myPosition.y:
                return Directions.NORTH
            if nextBonus.y > myPosition.y:
                return Directions.SOUTH
            '''
        

        # if there are no more bonuses, Tallon doesn't move
        # GC The bonuses are made up of an array list - check how this builds up?

        # If no bonusses are left then randomly create one to act as somewhere to move
        else: 
          print(" ---- NO LOOT SO JUST OVOID MEANIES: ----")
          printGameState(self)
          gridWorld(self)
          q_learning(self)

          getShortestPath = get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)
          print("Shortest path (row, column): ", get_shortest_path(self.gameWorld.getTallonLocation().y, self.gameWorld.getTallonLocation().x)) 

          currentPosition = getShortestPath[0]

          nextPosition = getShortestPath[1]

          # Inspired by S. Parsons move code commented aout below
          if nextPosition[1] > currentPosition[1]: #i.e. the next position is further to the EAST than current
              return Directions.EAST 
          if nextPosition[1] < currentPosition[1]: #i.e. the next position is further to the WEST than current
              return Directions.WEST
          if nextPosition[0] < currentPosition[0]: #i.e. the next position is further to the NORTH than current
              return Directions.NORTH
          if nextPosition[0] > currentPosition[0]: #i.e. the next position is further to the SOUTH than current
              return Directions.SOUTH
            
