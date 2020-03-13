import socket
import os
import subprocess
import pickle

# Constants
HOST = socket.gethostbyname('DESKTOP-QQB5RUH')
# HOST = '127.0.0.1'
PORT = 12000

# Working area

# Create a socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect via the socket
clientSocket.connect((HOST, PORT))
print("Connection with the server established")

# Begin sending and recieving data
while True:
    # Receive the command from the server
    command = clientSocket.recv(1024)

    # Decode the command
    command = pickle.loads(command)

    # Skip the ping
    if "@" in command:
        continue
    elif "=" in command:
        print(command)
    elif "vote" in command:
        # Display the candidates
        print("================================ Candidates ================================\n0: Candidate 1\n1: Candidate 2\nEnter the candidate index to cast your vote")

        candidate = input("Your vote: ")

        data = candidate.encode()

        clientSocket.sendall(data)

        print("Fetching results...")
    else:
        print(command)
    

    

