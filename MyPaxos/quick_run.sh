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

# ./client.sh 1 ../paxos.conf <<<"123"&
# ./client.sh 2 ../paxos.conf <<<"456"&

./client.sh 1 ../paxos.conf <<<"111 
 222
 333" &

 ./client.sh 2 ../paxos.conf <<<"666 
 777
 888" &

sleep 10

$KILLCMD
wait
