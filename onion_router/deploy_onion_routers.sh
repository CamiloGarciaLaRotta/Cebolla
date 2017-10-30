#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"



#       DOCUMENTATION
################################

read -r -d '' helpstring <<DOC
deploy_directory.sh usage:

deploy_directory -u <user> -d <dirCebolla> [-b <branch>] -p <port>
 @param  user         the username to be used to login to the remote host
 @param  maxNodes     the number of onion router nodes to set up. 1 <= maxNodes <= 50
 @param  dirCebolla   the path to the dirCebolla directory
 @option branch       if given, the github branch version to use, else use local version
 @param  port         the port number for the onion router node to listen on

What it does:
for i in [1 ... maxNodes]
 1. login to a mcgill machine (specifically lab2-i.cs.mcgill.ca)
 2. cd to Cebolla directory
 3. if branchname arg, checkout and pull branch. else, scp local copy
 4. run onion_router.py to start up the onion_router node server
endfor

*note that ^C will go to the next iteration of the loop
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
maxNodes=""   # the number of onion router nodes to set up
dirCebolla="" # the path to the root of the Cebolla directory
branch=       # the git branch to checkout on remote host
port=""       # the port to configure the server to listen on
while getopts "m:u:d:b:p:" opt
do
    case "$opt" in
        m)
            maxNodes="$OPTARG"
            ;;
        u)
            user="$OPTARG"
            ;;
        d)
            dirCebolla="$OPTARG"
            ;;
        b)
            branch="$OPTARG"
            ;;
        p)
            port="$OPTARG"
            ;;
    esac
done



#   ILLEGAL ARGUMENT CHECKS
################################

if  # dont have 6 or 8 args
    [ "$#" -ne "10" ] && [ "$#" -ne "8" ] ||
    # didn't pass args correctly
    [ -z "$maxNodes" ] || [ -z "$user" ] || [ -z "$dirCebolla" ] || [ -z "$port" ] ||
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
    if [ -z "$branch" ]
    then # use local version
        echo "sending local onion_router.py to $servername to run on port $port"
        scp  "onion_router.py" "$user"@"$servername":"$dirCebolla/onion_router/onion_router.py"
        ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
			cd $dirCebolla
			nohup python3 onion_router/onion_router.py $port > /dev/null 2>&1 &
			exit
			DOC
    else # use version on github branch
        ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
			cd $dirCebolla
			git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
			nohup python3 onion_router/onion_router.py $port > /dev/null 2>&1 &
			exit
			DOC
    fi
done
