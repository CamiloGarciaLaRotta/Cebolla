#!/usr/bin/env bash

# go to the directory where THIS FILE is
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$THIS_DIR"



#       DOCUMENTATION
################################

read -r -d '' helpstring << DOC
shutdown_dummy_dests.sh usage:

shutdown_dummy_dests.sh -u <user> -p <port>
 @param  user         the username to be used to login to the remote host
 @param  port         the port number for the onion router node to listen on

What it does:
 1. login to cs-2.cs.mcgill.ca
 2. find and kill the running dummy_dest.py on the specified port
DOC



#      ARGUMENT PARSING
################################

user=""       # username on remote host
port=""       # the port to configure the server to listen on
while getopts "m:u:p:" opt
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

if  # not passed 6 cli tokens
    [ "$#" -ne "4" ] ||
    # didn't pass args correctly
    [ -z "$user" ] || [ -z "$port" ] ||
then
    echo -e "$helpstring"
    exit 1
fi



#     KILL RUNNING dummy_dest.py ON THE REMOTE
####################################################

servername="cs-2.cs.mcgill.ca"
echo "killing dummy_dest.py $port on $servername"
ssh -t "$user"@"$servername" > /dev/null 2>&1 'bash -s' <<-DOC
	pid=\$(ps aux | grep "dummy_dest.py $port" | grep -v 'grep' | awk '{print \$2}')
	if [ -n "\$pid" ]; then kill "\$pid"; fi
	exit
	DOC
