#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"



#       DOCUMENTATION
################################

read -r -d '' helpstring << DOC
deploy_directory.sh usage:

deploy_directory -u <user> -d <dirCebolla> [-b <branch>] -p <port>
 @param  user         the username to be used to login to the remote host
 @param  maxNodes     the number of onion router nodes to set up. 1 <= maxNodes <= 50
 @param  port         the port number for the onion router node to listen on

What it does:
for i in [1 ... maxNodes]
 1. login to a mcgill machine (specifically lab2-i.cs.mcgill.ca)
 2. find and kill the running onion_router.py on the specified port
endfor

*note that ^C will go to the next iteration of the loop
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
maxNodes=""   # the number of onion router nodes to set up
port=""       # the port to configure the server to listen on
while getopts "m:u:p:" opt
do
    case "$opt" in
        m)
            maxNodes="$OPTARG"
            ;;
        u)
            user="$OPTARG"
            ;;
        p)
            port="$OPTARG"
            ;;
    esac
done



#   ILLEGAL ARGUMENT CHECKS
################################

if  # not passed 6 cli tokens
    [ "$#" -ne "6" ] ||
    # didn't pass args correctly
    [ -z "$maxNodes" ] || [ -z "$user" ] || [ -z "$port" ] ||
    # maxNodes out of range
    [ "$maxNodes" -lt "1" ] || [ "$maxNodes" -gt "50" ]
then
    echo -e "$helpstring"
    exit 1
fi



#     UPDATE AND RUN DIRECTORY.PY ON THE REMOTE
####################################################

trap 'continue' SIGINT # ^C goes to next iteration of loop below

for i in $(seq 1 "$maxNodes")
do
    servername="lab2-$i.cs.mcgill.ca"
    echo "killing onion_router.py $port on $servername"
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<-DOC
		pid=\$(ps aux | grep "onion_router.py $port" | grep -v 'grep' | awk '{print \$2}')
		if [ -n "\$pid" ]; then kill "\$pid"; fi
		exit
		DOC
done
