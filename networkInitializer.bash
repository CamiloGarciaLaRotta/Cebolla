#!/bin/bash

#input 
#	$1: The number of path nodes: will be propted to sign in
#	$2: The users cs account name
#       $3: The cs path for the destination 
x=0
while [ $x -lt $1 ]
	do
		x=$(($x + 1))
		tmux neww -n ssh$x 
	done

tmux neww -n directoryNode
tmux neww -n dummyDest
tmux neww -n client 

x=1
while [ $x -le $1 ]
   do
        tmux send-keys -t ssh$x "ssh $2@lab2-$x.cs.mcgill.ca" Enter;	
	x=$(($x + 1))
  done
      
tmux send-keys -t directoryNode "ssh $2@cs-1.cs.mcgill.ca" Enter;\
tmux send-keys -t dummyDest "ssh $2@$3" Enter;\
tmux send-keys -t client "ssh $2@cs-3.cs.mcgill.ca" Enter ;\
	
