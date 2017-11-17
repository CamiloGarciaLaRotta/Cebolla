#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"



#       DOCUMENTATION
################################

read -r -d '' helpstring <<DOC
deploy_onion_routers.sh usage:

deploy_onion_routers.sh -m maxNodes -u <user> -d <dirCebolla> [-b <branch>] [-p <port> -o <okrPort>]

 @param  maxNodes     the number of onion router nodes to set up. 1 <= maxNodes <= 50
 @param  user         the username to be used to login to the remote host
 @param  dirCebolla   the path to the dirCebolla directory on the remote host

 @option branch       if given, the github branch version to deploy, else deploy local version

 @option port         port for onion routers to listen for new connections
 @option okrPort      port for onion routers to listen on for public key requests
                      if both port and okrPort are given, run after deploy. else just deploy

What it does:
for i in [1 ... maxNodes]
 1. login to lab2-i.cs.mcgill.ca
 2. cd to Cebolla directory
 3. if branchname arg given, checkout and pull branch. else, scp local copy
 4. if port and okrPort given, run onion_router.py with params port and okrPort
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
okrPort=""    # onion routers respond to pubkey requests on this port
while getopts "m:u:d:b:p:o:" opt
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
        o)  okrPort="$OPTARG"
            ;;
    esac
done



#   ILLEGAL ARGUMENT CHECKS
################################

if  # didn't pass args correctly
    [ -z "$maxNodes" ] || [ -z "$user" ] || [ -z "$dirCebolla" ] ||
    # maxNodes out of range
    [ "$maxNodes" -lt "1" ] || [ "$maxNodes" -gt "50" ] ||
    # port or okrPort given but not both
    [ -n "$port" ] && [ -z "$okrPort" ] || [ -n "$okrPort" ] && [ -z "$port" ]
then
    echo -e "$helpstring"
    exit 1
fi



#     UPDATE AND RUN onion_router.py ON THE REMOTE
####################################################

trap 'continue' SIGINT # ^C goes to next iteration of loop below

routerNodeCmd=""
if [ -n "$port" ] && [ -n "$okrPort" ]
then
    routerNodeCmd="nohup python3 onion_router/onion_router.py $port $okrPort > /dev/null 2>&1 &"
fi

for i in $(seq 1 "$maxNodes")
do
    servername="lab2-$i.cs.mcgill.ca"
    if [ -z "$branch" ]
    then # use local version
        echo "sending local onion_router.py to $servername to run on port $port"
        scp  "onion_router.py" "$user"@"$servername":"$dirCebolla/onion_router/onion_router.py"
        ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
			cd $dirCebolla
			$routerNodeCmd
			exit
			DOC
    else # use version on github branch
        ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
			cd $dirCebolla
			git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
			$routerNodeCmd
			exit
			DOC
    fi
done
