#!/usr/bin/env bash

helpstring="
deploy_directory.sh:
 ( !!! NOTE: must push to github first !!! )
 1. deploy the onion routing directory node to a mcgill cs machine
 2. checkout a git branch of choice and git pull most recent version
 3. run a the python file to start up the sever to listen on chosen port

usage: deploy_directory -u <user> -b <branch> -p <port> -x <execpyfile>
 @param user: the username to be used to login to the remote host
 @param branch: the branch to checkout on github
 @param execpyfile: the name of the python3 file to run the server
 @param port: the port number for the directory node to listen on
"

# ARGUMENT PARSING

user="" # username on remote host
dirCebolla="" # the path to the root of the Cebolla directory
branch= # the git branch to checkout on remote host
port="" # the port to configure the server to listen on
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

# ILLEGAL ARGUMENT CHECKS

if  # need 3 (flag,arg) pairs
    [ "$#" -ne "8" ] ||
    # no empty args
    [ -z "$user" ]   || [ -z "$dirCebolla" ] || [ -z "$branch" ] || [ -z "$port" ]
then
    echo $helpstring
    exit 1
fi

# DO THE THINGS

ssh "$user"@cs-1.cs.mcgill.ca \
  "cd $dirCebolla; git checkout $branch; git pull origin $branch; python3 directory/directory.py $port"
