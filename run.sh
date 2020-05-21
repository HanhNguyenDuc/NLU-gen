#!/bin/bash
bin=/root/anaconda3/envs/pipenv/bin

nohup $bin/python gen_data.py > gen_data.log &
pid_action=$(echo $!)
echo $pid_action > pid.pid
