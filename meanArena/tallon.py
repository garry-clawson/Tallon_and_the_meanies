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
from re import X
import numpy as np

# Original imports
import world
import random
import utils
from utils import Directions

# ================= GC global variables ========================

def gridWorld(self):

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
    rewards = np.full((environment_rows, environment_columns), -100.)

    rewards[0, 5] = 100. #set the reward for the packaging area (i.e., the goal) to 100

    #define aisle locations (i.e., white squares) for rows 1 through 9
    aisles = {} #store locations in a dictionary

    #getMeanieStates(self, aisles)

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
    
    
    # update the states of the arena so we can add the objects to the grid for the q-values
    #getTallonState(self, aisles)
    getMeanieStates(self, aisles)
    
    
    #set the rewards for all aisle locations (i.e., white squares)
    for row_index in range(0, 10):
        for column_index in aisles[row_index]:
            rewards[row_index, column_index] = -1.
    

    #print rewards matrix
    for row in rewards:
        print(row)



# ================ GC end global variables ====================

#GC Get tellon state/postion and add this to the aisles grid
def getTallonState(self, aisles):
    #print("Tallon state:")
    #self.gameWorld.getTallonLocation().print()
    #print(self.gameWorld.getTallonLocation().x)
    #print(self.gameWorld.getTallonLocation().y)
    x = self.gameWorld.getTallonLocation().x
    y = self.gameWorld.getTallonLocation().y
    aisles[y].append(x)

#GC Get meenie state/position and add this to the aisles grid
def getMeanieStates(self, aisles):
    #print("Meanies state:")
    for i in range(len(self.gameWorld.getMeanieLocation())):
        #print(self.gameWorld.getMeanieLocation()[i].x)
        #print(self.gameWorld.getMeanieLocation()[i].y)
        x = self.gameWorld.getMeanieLocation()[i].x
        y = self.gameWorld.getMeanieLocation()[i].y
        aisles[y].append(x)


#GC Get current state of arena so we can add the objects to the grid for the q-values
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
            myPosition = self.gameWorld.getTallonLocation()
            

            # GC how to print an object https://www.delftstack.com/howto/python/print-object-python/ 
            #myPosition.print()


            # GC create gridworld for q_learning process to identify next move E/W/N/S
            gridWorld(self)





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

