#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"


#       DOCUMENTATION
################################

read -r -d '' helpstring << DOC
deploy_directory.sh usage:

deploy_directory -u <user> -d <dirCebolla> [-b <branch>] [-p <port> -o <okrPort>]

 user         login username on remote host
 dirCebolla   path to Cebolla directory on remote host

 [branch]     if given, deploy version from github branch, else deploy local version

 [port]       port for directory node to listen on
 [okrPort]    port for onion routers to listen on for key requests
              if both port and okrPort given, run after deploy. else just deploy

What it does:
 1. login to cs-1.cs.mcgill.ca
 2. cd to Cebolla directory
 3. if branchname arg given, checkout and pull branch. else, scp local copy
 4. if port and okrPort given run directory.py with params port and okrPort
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
dirCebolla="" # the path to the root of the Cebolla directory
branch=       # the git branch to checkout on remote host
port=""       # the port to configure the server to listen on
okrPort=""    # onion routers respond to pubkey requests on this port
while getopts "u:d:b:p:o:" opt
do
    case "$opt" in
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
        o)
            okrPort="$OPTARG"
            ;;
    esac
done



#   ILLEGAL ARGUMENT CHECKS
################################

if  # didn't pass required args correctly
    [ -z "$user" ] || [ -z "$dirCebolla" ] ||
    # didn't pass optional args correctly [ -z "$port" ] xor [ -z "$okrPort" ]
    [ -z "$port" ] && [ -n "$okrPort" ] || [ -n "$port" ] && [ -z "$okrPort" ]
then
    echo -e "$helpstring"
    exit 1
fi


#     UPDATE AND RUN DIRECTORY.PY ON THE REMOTE
####################################################


dirNodeCmd=""
if [ -n "$port" ] && [ -n "$okrPort" ]
then
    dirNodeCmd="nohup python3 directory/onion_directory.py 50 $port $okrPort > /dev/null 2>&1 &"
fi

servername="cs-1.cs.mcgill.ca"

if [ -z "$branch" ]
then # use local version
    scp "onion_directory.py" "$user"@"$servername":"$dirCebolla/directory/onion_directory.py"
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		$dirNodeCmd
		exit
		DOC
else # use version on github branch
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
		$dirNodeCmd
		exit
		DOC
fi
