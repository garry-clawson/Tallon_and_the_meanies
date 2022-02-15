#!/bin/bash

for ((i=1; i<=50; i++))
do
    python3 game.py >> 50_results_10by10_1m_3p_3b.txt
done