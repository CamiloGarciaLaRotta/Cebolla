CEBOLLA OPERATING GUIDE
=======================

This page will describe how the Cebolla Onion Routing implementation can be tested.

Installation
------------
Cebolla may be installed on a Unix-like system with git installed. For the
purposes of this project, the servers must all run on McGill machines, which
have git installed and configured. Furthermore, the PyCrypto Python library is
a dependency of Cebolla, however the McGill machines have this installed as
well. To install Cebolla, run the following command: `git clone
https://github.com/CamiloGarciaLaRotta/Cebolla.git`.

Components
----------
### Onion Router
* An onion router is a server that is responsible for passing along *onion* messages, peeling off their layers of encryption, and encrypting reponse messages
* Any message sent through an onion network passes through three onion routers before being sent to the destination
* For the purposes of this project, onion routers should be run on a McGill machine with a domain like `lab2-x.cs.mcgill.ca`

### Directory Node
* The directory node is a server that the client contacts first.
* The directory node knows the public keys of all onion routers and their domain names.
* The directory node calculates a path of onion routers for the client.
* For the purposes of this project, the directory node should run on `cs-1.cs.mcgill.ca`.

### Onion Client
* The onion client is a command line interface that handles virtual circuit establishments, onion message creation, and response message decryption for a user that wishes to communicate through the onion network.

### Dummy Destination
* The so-called Dummy Destination is a server set up to accept very
simple request messages and respond with equally-simple responses. The Dummy
Destination accepts virtually any request message and responds with the
capitalized version.

Simulating the Onion Network
---------------------------
### Step 1 - Launch Onion Routers
1. Log in to several `lab2-x.cs.mcgill.ca` machines with Cebolla installed and
   navigate to the Cebolla directory.
2. Launch onion routers. If no onion routers are listening on any of the
   `lab2-x.cs.mcgill.ca` machines, the directory node will shut down
   immediately. To launch an onion router, run `python router/onion_router.py
   LISTEN_PORT KEY_PORT [-v]`, where `LISTEN_PORT` is the port that should
   listen for new connections, `KEY_PORT` is the port to communicate public
   keys with the directory node on, and specifying `-v` enables verbose mode,
   which shows lots of debugging output.

### Step 2 - Launch Directory Node
3. Log in to `cs-1.cs.mcgill.ca` and have Cebolla installed. Navigate to the Cebolla directory.
4. Launch the directory node with the following command: `python
   directory/onion_directory.py MAX_NODES LISTEN_PORT KEY_PORT [-v]`, where
   `MAX_NODES` is the largest value of `x` such that `lab2-x.cs.mcgill.ca` has an
   onion router running, and `LISTEN_PORT` and `KEY_PORT` serve the same
   purpose as in the onion router command. Upon running this command, the
   listening onion routers that were found should be displayed.

### Step 3 (Optional) - Launch the Dummy Destination
5. Log in to a McGill machine with Cebolla installed. Navigate to the Cebolla directory.
6. Run the following command: `python destination LISTEN_PORT [-v]`, following
   the same parameter conventions as the other servers described.

NOTE: this step is not necessary. Theoretically, any destination can be used,
	though more sophisticated request messages may need to be constructed on
	the client.

### Step 4 - Launch a Client
7. Log in to a McGill machine with Cebolla installed. Navigate to the Cebolla directory.
8. Run the following command: `python client/onion_client.py DESTINATION
   LISTEN_PORT [-d DESTINATION_PORT] [-v]`, where `DESTINATION` is the domain
   name of the destination, `LISTEN_PORT` is the port that onion routers are
   listening on, and `DESTINATION_PORT` specifies the port that the destination
   is listening on. This value defaults to 80 when not specified.
9. Now, a prompt should appear, and messages may be entered. Type a message and
   press RETURN to send the message. A response should follow shortly after,
   and more messages may be sent.
