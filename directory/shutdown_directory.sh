#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"



#       DOCUMENTATION
################################

read -r -d '' helpstring << DOC
shutdown_directory.sh usage:

shutdown_directory.sh -u <user> -p <port>
 @param  user         the username to be used to login to the remote host
 @param  port         the port on which the running directory node is listening

What it does:
login to cs-1.cs.mcgill.ca and kill the directory.py running on the port specified
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
port=""       # the port to configure the server to listen on
while getopts "u:p:" opt
do
    case "$opt" in
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

if  # not passed 4 cli tokens
    [ "$#" -ne "4" ] ||
    # didn't pass args correctly
    [ -z "$user" ] || [ -z "$port" ]
then
    echo -e "$helpstring"
    exit 1
fi



#     UPDATE AND RUN DIRECTORY.PY ON THE REMOTE
####################################################

servername="cs-1.cs.mcgill.ca"
echo "killing directory.py on $port on $servername"
ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<- DOC
	pid=\$(ps aux | grep "directory.py 50 $port" | grep -v 'grep' | awk '{print \$2}')
	if [ -n "\$pid" ]; then kill "\$pid"; fi
	exit
	DOC
