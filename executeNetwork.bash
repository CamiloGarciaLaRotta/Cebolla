#!/bin/bash

#input 
#	$1: The number of path nodes: MUST BE THE SAME AS THE INTITIALIZE SCRIPT
#	$2: The CS path to host the client (i.e. cs-6.cs.mcgill.ca) 
#	$3: Port # for regular data communication
#	$4: Port used for pubkey
#	$5: Port for dumydest and client

x=1
while [ $x -le $1 ]
   do
        tmux send-keys -t ssh$x "cd Cebolla; python router/onion_router.py $3 $4 -v" Enter;	
	x=$(($x + 1))
  done
      
tmux send-keys -t directoryNode "cd Cebolla; python directory/onion_directory.py 10 $3 $4 -v" Enter;\
tmux send-keys -t dummyDest "cd Cebolla; python destination/dummy_dest.py $5 -v" Enter;\
sleep 2
tmux send-keys -t client "cd Cebolla; python client/onion_client.py $2 $3 -d $5" Enter ;\
	
