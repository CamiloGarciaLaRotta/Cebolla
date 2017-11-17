#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"


#       DOCUMENTATION
################################

read -r -d '' helpstring << DOC
deploy_all.sh usage:

deploy_all.sh -m maxNodes -u user -d dirCebolla [-b branch] [-p port -o okrPort]

 maxNodes     the number of nodes to setup in the onion network
 user         login username on remote host
 dirCebolla   path to Cebolla directory on remote host

 [branch]     if given, deploy version from github branch, else deploy local version

 [port]       port for directory node to listen on
 [okrPort]    port for onion routers to listen on for key requests
              if both port and okrPort given, run after deploy. else just deploy

What it does:
TODO TODO TODO
DOC



#      ARGUMENT PARSING
################################

maxNodes=""   # the number of onion router nodes to set up
user=""       # username on remote host
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
        o)
            okrPort="$OPTARG"
            ;;
    esac
done



#   ILLEGAL ARGUMENT CHECKS
################################

if  # didn't pass optional args correctly [ -z "$port" ] xor [ -z "$okrPort" ]
    [ -z "$port" ] && [ -n "$okrPort" ] || [ -n "$port" ] && [ -z "$okrPort" ] ||
    # didn't pass required args correctly
    [ -z "$maxNodes" ] || [ -z "$user" ] || [ -z "$dirCebolla" ]
then
    echo -e "$helpstring"
    exit 1
fi

maxNodes="-m $maxNodes"
user="-u $user"
dirCebolla="-d $dirCebolla"

if [ -n "$port" ] && [ -n "$okrPort" ]
then
    port="-p $port"
    okrPort="-o $okrPort"
fi

if [ -n "$branch" ]
then
    branch="-b $branch"
fi


#   DEPLOY THE ENTIRE PROJECT
./../destination/deploy_dummy_dest.sh "$user" "$dirCebolla" "$branch" "$port"
./../router/deploy_onion_routers.sh "$maxNodes" "$user" "$dirCebolla" "$branch" "$port" "$okrPort"
./../directory/deploy_directory.sh "$user" "$directory" "$branch" "$port" "$okrPort"
./../client/deploy_client.sh "$user" "$dirCebolla" "$branch"

# now you can log in to cs-10 (the originator) and run it.  The whole onion network should
# have been deployed (assuming you passed the port and okrPort arguments)
