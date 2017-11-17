#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"


#       DOCUMENTATION
################################

read -r -d '' helpstring << DOC
deploy_client.sh usage:

deploy_client.sh -u <user> -d <dirCebolla> [-b <branch>]

 user         login username on remote host
 dirCebolla   path to Cebolla directory on remote host

 [branch]     if given, deploy version from github branch, else deploy local version

What it does:
 1. login to cs-10.cs.mcgill.ca
 2. cd to Cebolla directory
 3. if branchname arg given, checkout and pull branch. else, scp local copy
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
dirCebolla="" # the path to the root of the Cebolla directory
branch=       # the git branch to checkout on remote host
while getopts "u:d:b:" opt
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


#     UPDATE AND RUN DIRECTORY.PY ON THE REMOTE
####################################################


servername="cs-10.cs.mcgill.ca"

if [ -z "$branch" ]
then # use local version
    scp "onion_client.py" "$user"@"$servername":"$dirCebolla/client/onion_client.py"
else # use version on github branch
    ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
		cd $dirCebolla
		git fetch origin; git checkout $branch; git reset --hard; git pull origin $branch
		exit
		DOC
fi
