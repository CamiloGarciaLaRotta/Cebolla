#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"



#       DOCUMENTATION
################################

read -r -d '' helpstring <<DOC
deploy_dummy_dest.sh usage:

deploy_dummy_dest.sh -u <user> -d <dirCebolla> [-b <branch>] -p <port>
 @param  user         the username to be used to login to the remote host
 @param  dirCebolla   the path to the dirCebolla directory on the remote host
 @option branch       if given, the github branch version to use, else use local version
 @param  port         the port number for the onion router node to listen on. 5551 <= port <= 5557

What it does:
 1. login to cs-2.cs.mcgill.ca
 2. cd to Cebolla directory
 3. if branchname arg given, checkout and pull branch. else, scp local copy
 4. run dummy_dest.py on the specified port to start up dummy_dest server
endfor
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
dirCebolla="" # the path to the root of the Cebolla directory on remote host
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

if  # dont have 8 or 10 args
    [ "$#" -ne "8" ] && [ "$#" -ne "6" ] ||
    # didn't pass args correctly
    [ -z "$user" ] || [ -z "$dirCebolla" ] || [ -z "$port" ] ||
    # port out of range
    [ "$port" -lt "5551" ] || [ "$port" -gt "5557" ] # 7 group members, 7 ports
then
    echo -e "$helpstring"
    exit 1
fi



#     UPDATE AND RUN dummy_dest.py ON THE REMOTE
####################################################

servername="cs-2.cs.mcgill.ca"
if [ -z "$branch" ]
then # use local version
    echo "sending local dummy_dest.py to $servername to run on port $port"
    scp  "dummy_dest.py" "$user"@"$servername":"$dirCebolla/dummy_dest/dummy_dest.py"
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		nohup python3 dummy_dest/dummy_dest.py $port > /dev/null 2>&1 &
		exit
		DOC
else # use version on github branch
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
		nohup python3 dummy_dest/dummy_dest.py $port > /dev/null 2>&1 &
		exit
		DOC
fi
