#!/usr/bin/env bash


# conf=../paxos.conf
# KILLCMD="pkill -f $conf"

# ./proposer.sh 1 ../paxos.conf &
# ./proposer.sh 2 ../paxos.conf &

# ./acceptor.sh 1 ../paxos.conf &
# ./acceptor.sh 2 ../paxos.conf &
# ./acceptor.sh 3 ../paxos.conf &

# ./learner.sh 1 ../paxos.conf &

# sleep 5
# #Test for phase1-a rejection

# ./client.sh 1 ../paxos.conf <<<"123 
#  224
#  555" &

#  ./client.sh 2 ../paxos.conf <<<"0" &
# # ./client.sh 1 ../paxos.conf <<<"123" &

# sleep 5

# $KILLCMD
# wait


conf=../paxos.conf
KILLCMD="pkill -f $conf"

./proposer.sh 1 ../paxos.conf &
./proposer.sh 2 ../paxos.conf &

./acceptor.sh 1 ../paxos.conf &
./acceptor.sh 2 ../paxos.conf &
./acceptor.sh 3 ../paxos.conf &

./learner.sh 1 ../paxos.conf &

sleep 5
#Test for phase1-a rejection

# ./client.sh 1 ../paxos.conf <<<"1
# 11
# 111
# 1111
# 12
# 11111111"&
# ./client.sh 2 ../paxos.conf <<<"2
# 22
# 222
# 2222
# 21
# 222222"&

./client.sh 1 ../paxos.conf <<<"1
2
3
4
5
6
7
8
9"&

./client.sh 2 ../paxos.conf <<<"11
22
33
44
55
66
77
88
99"&



sleep 70

$KILLCMD
wait
