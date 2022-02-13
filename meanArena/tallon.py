# ----------------- Start Student Details -----------------------------

# Name:     Garry Clawson
# ID:       18685030
# Date:     29th Jan 2022
# Module:   CMP9132M
# Title:    AAI Assignment 2
# Version:  0.1.0

# ----------------- End Student Details -----------------------------
#
# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the next move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22


# GC imports
from glob import glob
from pickle import NONE
from re import X
import numpy as np
import string

# Original imports
import world
import random
import utils
from utils import Directions

# ================= GC global variables ========================

rewards = [NONE]
q_values = [NONE]
environment_rows = 0
environment_columns = 0

#define q_learning training parameters
epsilon = 0.9 #the percentage of time when we should take the best action (instead of a random action)
discount_factor = 0.9 #discount factor for future rewards
learning_rate = 0.9 #the rate at which the AI agent should learn


# ================ GC end global variables ====================



# -------------------- define actions -------------------------
#numeric action codes: 0 = up, 1 = right, 2 = down, 3 = left
actions = ['up', 'right', 'down', 'left']


def gridWorld(self):

    global rewards, q_values, environment_columns, environment_rows

    # ------------------ define the shape of the environment (i.e., its states) -------------------------
    environment_rows = self.gameWorld.maxX + 1# direction of a row is > top to bottom
    environment_columns = self.gameWorld.maxY + 1# direction of a colum is > left to right

    #Create a 3D numpy array to hold the current Q-values for each state and action pair: Q(s, a) 
    #The array contains 11 rows and 11 columns (to match the shape of the environment), as well as a third "action" dimension.
    #The "action" dimension consists of 4 layers that will allow us to keep track of the Q-values for each possible action in
    #each state (see next cell for a description of possible actions). 
    #The value of each (state, action) pair is initialized to 0.
    q_values = np.zeros((environment_rows, environment_columns, 4))


    # -------------------- Create a 2D numpy array to hold the rewards for each state -------------------------
    #The array contains 10 rows and 10 columns (to match the shape of the environment), and each value is initialized to -100.
    rewards = np.full((environment_rows, environment_columns), -1.)

    #rewards[0, 5] = 100. #set the reward for the packaging area (i.e., the goal) to 100

    #define aisle locations (i.e., white squares) for rows 1 through 9
    aisles = {} #store locations in a dictionary

    # GC Create blank posistions for the grid to initialsie
    # we will fill them up by getting the states of the meanies/tollen/pist and bonusses

    aisles[0] = []
    aisles[1] = []
    aisles[2] = []
    aisles[3] = []
    aisles[4] = []
    aisles[5] = []
    aisles[6] = []
    aisles[7] = []
    aisles[8] = []
    aisles[9] = []
    
    # define the states of the arena so we can add the objects to the grid for the q-values
    getMeanieStates(self, aisles)
    getTallonState(self, rewards)
    getPitsStates(self, aisles)
    getBonusStates(self, rewards)
    
    #set the rewards for all aisle locations (i.e., all non pit or meanie positions)
    for row_index in range(0, 10):
        for column_index in aisles[row_index]:
            rewards[row_index, column_index] = -100.

    #print rewards matrix in terminal so we can see where the meanies and pits etc are for our q_learning
    for row in rewards:
        format_string = "{:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}  {:>6}"
        print(format_string.format(*row))
        #print(row)



#GC Get tellon state/postion and add this to the aisles grid
def getTallonState(self, rewards):
    #print("Tallon state:")
    #self.gameWorld.getTallonLocation().print()
    #print(self.gameWorld.getTallonLocation().x)
    #print(self.gameWorld.getTallonLocation().y)
    x = self.gameWorld.getTallonLocation().x
    y = self.gameWorld.getTallonLocation().y
    rewards[y, x] = 0.
    #aisles[y].append(x)

#GC Get meenie state/position and add this to the aisles grid
def getMeanieStates(self, aisles):
    #print("Meanies state:")
    for i in range(len(self.gameWorld.getMeanieLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getMeanieLocation()[i].x
        y = self.gameWorld.getMeanieLocation()[i].y
        aisles[y].append(x)

#GC Get pit state/position and add this to the aisles grid
def getPitsStates(self, aisles):
    #print("Pit state:")
    for i in range(len(self.gameWorld.getPitsLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getPitsLocation()[i].x
        y = self.gameWorld.getPitsLocation()[i].y
        aisles[y].append(x)

#GC Get bonus state/position and add this to the aisles grid
def getBonusStates(self, rewards):
    #print("Bonus state:")
    for i in range(len(self.gameWorld.getBonusLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getBonusLocation()[i].x
        y = self.gameWorld.getBonusLocation()[i].y
        rewards[y, x] = 99.

# GC Get current state of arena so we can add the objects to the grid for the q-values
# Credit to S. Parsons >> below was taken from utils.py

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

    #print("Clock:")
    #print(self.gameWorld.getClock())

    #print("Score:")
    #print(self.gameWorld.getScore())

    print("")



#define a function that will choose a random, non-terminal starting location
def get_starting_location():
  #get a random row and column index
  current_row_index = np.random.randint(environment_rows)
  current_column_index = np.random.randint(environment_columns)
  #continue choosing random row and column indexes until a non-terminal state is identified
  #(i.e., until the chosen state is a 'white square').
  while is_terminal_state(current_row_index, current_column_index):
    current_row_index = np.random.randint(environment_rows)
    current_column_index = np.random.randint(environment_columns)
  return current_row_index, current_column_index

# ----------------- define a function that determines if the specified location is a terminal state -------------------------
def is_terminal_state(current_row_index, current_column_index):
  #if the reward for this location is -1, then it is not a terminal state (i.e., it is a 'white square')
  if rewards[current_row_index, current_column_index] == -1.:
    return False
  else:
    return True


#define an epsilon greedy algorithm that will choose which action to take next (i.e., where to move next)
def get_next_action(current_row_index, current_column_index, epsilon):
  #if a randomly chosen value between 0 and 1 is less than epsilon, 
  #then choose the most promising value from the Q-table for this state.
  if np.random.random() < epsilon:
    return np.argmax(q_values[current_row_index, current_column_index])
  else: #choose a random action
    return np.random.randint(4)


#define a function that will get the next location based on the chosen action
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


#Define a function that will get the shortest path between any location within the warehouse that 
#the robot is allowed to travel and the item packaging location.
def get_shortest_path(start_row_index, start_column_index):
  #return immediately if this is an invalid starting location
  if is_terminal_state(start_row_index, start_column_index):
    print("TERMINAL STATE")
    return []
  else: #if this is a 'legal' starting location
    current_row_index, current_column_index = start_row_index, start_column_index
    shortest_path = []
    shortest_path.append([current_row_index, current_column_index])
    #continue moving along the path until we reach the goal (i.e., the item packaging location)
    while not is_terminal_state(current_row_index, current_column_index):
      #get the best action to take
      action_index = get_next_action(current_row_index, current_column_index, 1.)
      #move to the next location on the path, and add the new location to the list
      current_row_index, current_column_index = get_next_location(current_row_index, current_column_index, action_index)
      shortest_path.append([current_row_index, current_column_index])
    return shortest_path #note returns y then x i.e., row then column - up/down then left/right


# ---------------------- train the AI agent -------------------------
def q_learning(self):

    #run through 1000 training episodes
    for episode in range(1000):
    #get the starting location for this episode
        row_index, column_index = get_starting_location()
        #continue taking actions (i.e., moving) until we reach a terminal state
        #(i.e., until we reach the item packaging area or crash into an item storage location)
        while not is_terminal_state(row_index, column_index):
            #choose which action to take (i.e., where to move next)
            action_index = get_next_action(row_index, column_index, epsilon)
 
            #perform the chosen action, and transition to the next state (i.e., move to the next location)
            old_row_index, old_column_index = row_index, column_index #store the old row and column indexes
            row_index, column_index = get_next_location(row_index, column_index, action_index)
            
            #receive the reward for moving to the new state, and calculate the temporal difference
            reward = rewards[row_index, column_index]
            old_q_value = q_values[old_row_index, old_column_index, action_index]
            temporal_difference = reward + (discount_factor * np.max(q_values[row_index, column_index])) - old_q_value

            #update the Q-value for the previous state and action pair
            new_q_value = old_q_value + (learning_rate * temporal_difference)
            q_values[old_row_index, old_column_index, action_index] = new_q_value

    print('Training complete!')


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

        # if there are still bonuses, move towards the next one. << GC  one position in the grid at a time
        if len(allBonuses) > 0:
            nextBonus = allBonuses[0] 
            myPosition = self.gameWorld.getTallonLocation()

        # if there are still bonuses, move towards the next one. << GC does this include the 0.95 probablity aspect?
        if len(allBonuses) > 0:

            #GC print game state
            print("GAME STATE:")
            printGameState(self)

            

            nextBonus = allBonuses[0]

            #define a function that will choose a random, non-terminal starting location
            myPosition = self.gameWorld.getTallonLocation()
            
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
            #print(get_shortest_path(self.gameWorld.getTallonLocation().x, self.gameWorld.getTallonLocation().y)) 
            print(get_shortest_path(0, 0)) 




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

        

        # if there are no more bonuses, Tallon doesn't move
        # GC The bonuses are made up of an array list - check how this builds up?

