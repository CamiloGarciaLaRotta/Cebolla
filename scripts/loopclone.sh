#!/usr/bin/env bash



#    DOCUMENTATION
##################################################

read -r -d '' helpstring <<'EOF'
loopclone.sh usage:

loopclone.sh -u <user> -m <maxNodes> -d <dirCebolla>
 @param user         the username to be used to login to the remote host
 @param maxNodes     the number of onion routing nodes in the network
 @param dirCebolla   the path to the dirCebolla directory

What it does:
for i in [1 ... maxNodes]
 1. login to a mcgill machine (specifically lab2-i.cs.mcgill.ca)
 2. git clone Cebolla to dirCebolla
endfor

Inside the loop, the SIGSTP signal (^Z) goes to next iteration of loop
EOF



#    CLI ARGUMENT PARSING
##################################################

user=""       # username on remote host
maxNodes=""   # the number of onion router nodes to set up
dirCebolla="" # the path to the root of the Cebolla directory
while getopts "m:u:d:" opt
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
    esac
done



#    VERIFY CORRECT ARGS
##################################################

if # any arguments missing
   [ -z "$maxNodes" ] || [ -z "$user" ] || [ -z "$dirCebolla" ] ||
   # maxNodes out of range
   [ "$maxNodes" -lt 1 ] || [ "$maxNodes" -gt 50 ]
then
    echo "$helpstring"
fi



#     CLONE CEBOLLA REPO INTO DIRCEBOLLA FOR EACH SERVER
##############################################################

trap 'continue' SIGSTP # ^Z goes to next iteration

for i in $(seq 1 "$maxNodes")
do
    servername="lab2-$i.cs.mcgill.ca"; echo "$servername"
    # use version on github branch
    ssh "$user"@"$servername" \
        "git clone https://github.com/CamiloGarciaLaRotta/Cebolla/ $dirCebolla;"
done
