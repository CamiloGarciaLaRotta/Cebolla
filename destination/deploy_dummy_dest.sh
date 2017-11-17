#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"


#       DOCUMENTATION
################################

read -r -d '' helpstring <<DOC
deploy_dummy_dest.sh usage:

deploy_dummy_dest.sh -u <user> -d <dirCebolla> [-b <branch>] [-p <port>]

 @param  user         the username to be used to login to the remote host
 @param  dirCebolla   the path to the dirCebolla directory on the remote host

 @option branch       if given, the github branch version to deploy, else deploy local version

 @option port         if given, port to listen on while running.  else, deploy without running

What it does:
 1. login to cs-2.cs.mcgill.ca
 2. cd to Cebolla directory
 3. if branchname arg given, checkout and pull branch. else, scp local copy
 4. if port given, run dummy_dest.py on the specified port
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

if  # didn't pass required args correctly
    [ -z "$user" ] || [ -z "$dirCebolla" ]
then
    echo -e "$helpstring"
    exit 1
fi



#     UPDATE AND RUN dummy_dest.py ON THE REMOTE
####################################################

dummyDestCmd=""
if [ -n "$port" ]
then
    dummyDestCmd="nohup python3 destination/dummy_dest.py $port > /dev/null 2>&1 &"
fi

servername="cs-2.cs.mcgill.ca"

if [ -z "$branch" ]
then # use local version
    scp  "dummy_dest.py" "$user"@"$servername":"$dirCebolla/destination/dummy_dest.py"
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		$dummyDestCmd
		exit
		DOC
else # use version on github branch
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
		$dummyDestCmd
		exit
		DOC
fi
