from socket import *
import datetime
serverName = 'cs-2.cs.mcgill.ca'
serverPort = 5555
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = raw_input('Input lowercase sentence:')
Start = datetime.datetime.now().time()
print Start
clientSocket.send(sentence)
modifiedSentence = clientSocket.recv(1024)
End = datetime.datetime.now().time()
print 'From Server:', modifiedSentence
print End
clientSocket.close()
