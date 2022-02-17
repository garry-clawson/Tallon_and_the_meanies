#!/bin/bash

# NOTES:
# Bash script that runs an program for x amount of times and appends all printouts in the program to a myscript.txt file
# This .txt can then be used to help get average scores etc tio gauge if the AI q_learnging process is better worse than original tallon.py provided
# To run the file go to folder where the game.py is and type'./testing.sh' into the terminal

for ((i=1; i<=50; i++))
do
    python3 game.py >> 50_results_10by10_1m_1i_3p_3b_original.txt
done