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
 @param  dirCebolla   the path to the dirCebolla directory
 @option branch       if given, the github branch version to use, else use local version
 @param  port         the port number for the directory node to listen on

What it does:
 1. login to a mcgill machine (specifically cs-1.cs.mcgill.ca)
 2. cd to Cebolla directory
 3. if branchname arg, checkout and pull branch. else, scp local copy
 4. run directory.py to start up the directory node server
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
dirCebolla="" # the path to the root of the Cebolla directory
branch=       # the git branch to checkout on remote host
port=""       # the port to configure the server to listen on
while getopts "u:d:b:p:" opt
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
    esac
done



#   ILLEGAL ARGUMENT CHECKS
################################

if  # dont have 6 or 8 args
    [ "$#" -ne "8" ] && [ "$#" -ne "6" ] ||
    # didn't pass args correctly
    [ -z "$user" ] || [ -z "$dirCebolla" ] || [ -z "$port" ]
    # port out of range
    [ "$port" -lt "5551"] || [ "$port" -gt "5557" ] # 7 group members, 7 ports
then
    echo -e "$helpstring"
    exit 1
fi



#     UPDATE AND RUN DIRECTORY.PY ON THE REMOTE
####################################################

servername="cs-1.cs.mcgill.ca"
if [ -z "$branch" ]
then # use local version
    scp "directory.py" "$user"@"$servername":"$dirCebolla/directory/directory.py"
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		nohup python3 directory/directory.py 50 $port > /dev/null 2>&1 &
		exit
		DOC
else # use version on github branch
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
        cd $dirCebolla
		git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
		nohup python3 directory/directory.py 50 $port > /dev/null 2>&1 &
		exit
		DOC
fi
