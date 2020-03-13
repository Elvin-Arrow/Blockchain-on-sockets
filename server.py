import socket
import time
import queue
import threading
import chain
import block
import blockchain
import pickle
from _thread import *


# Constants
HOST = socket.gethostbyname('DESKTOP-QQB5RUH')
NODEHOST = socket.gethostbyname('DESKTOP-QQB5RUH')
# HOST = '127.0.0.1' 
# NODEHOST = '127.0.0.1'
PORT = 12000
NODEPORT = 12500
NUMBER_OF_THREADS = 4

# Global Variables
serverSocket = None
nodeServerSocket = None
voteDetails = None
_chain = None
stopMining = False
votesUpdated = False
blocks = []
callCount = 0
clientConnections = []
clientAddresses = []
votersList = []
queue = queue.Queue()
a_lock = allocate_lock()

# Working area
# ------------------------------Thread 1 -----------------------------
# Create a socket
def createSocket():
    global serverSocket

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket
def bindSocket():
    global serverSocket

    # Bind takes a tuple!
    serverSocket.bind((HOST, PORT))

    # Listen to te socket
    serverSocket.listen(5)

# Accept connetion
def acceptConnection():
    global serverSocket
    global clientConnections
    global clientAddresses
    global votersList
    global stopMining
    global a_lock

    # Flush all previous connections
    for connection in clientConnections:
        connection.close()

    del clientConnections[:]
    del clientAddresses[:]

    while True:
        try:
            clientConnection, clientAddress = serverSocket.accept()

            clientConnections.append(clientConnection)
            clientAddresses.append(clientAddress)
            votersList.append(False)

            print(clientAddress[0] + " just connected")

            # Tell the client to vote
            data = pickle.dumps("vote")
            clientConnection.sendall(data)

            start_new_thread(listenToTheClients, (clientConnection, clientAddress))

            # Set the minig flag
            a_lock.acquire(0)
            stopMining = False
            a_lock.release()
        except Exception as e:
            print("Error in accepting connections" + str(e))

# Serve the connection
# ------------------------------Thread 2 -----------------------------
def configure():
    global serverSocket
    global stopMining

    while True:
        # Get command
        # command = input("Key in the candidate details\n")

        stopMining = False


        for conn in clientConnections:
            data = pickle.dumps(command)
            conn.sendall(data)




        else:
            print("Error no such command...")

# ------------------------------Thread 3 -----------------------------
def pingClients():
    global clientConnections
    global clientAddresses

    while True:
        try:
            # Loop through all the clients and check the active ones
            for i, connection in enumerate(clientConnections):
                try:
                    # Ping client
                    msg = '@'
                    data = pickle.dumps(msg)
                    connection.send(data)
                except:
                    # Delete the client from the list
                    print(str(clientAddresses[i][0]) + " disconnected")
                    del clientConnections[i]
                    del clientAddresses[i]
                    del votersList[i]
                    continue
        except:
            break
        time.sleep(5)
        
# ------------------------------Thread 4 -----------------------------
def listenToTheClients(clientConnection, clientAddress):
    global _chain
    global blocks
    global voteDetails
    global votersList

    while True:
        # Listen to the client's request
        data = clientConnection.recv(1024)
        candidate = data.decode()
        print("Client voted for candidated: " + candidate)

        # Mark the client as voted
        client = lookUpClient(clientConnection)
        votersList[client] = True

        # Update vote count locally
        votes = blockchain.Blockchain.updateDetails(voteDetails, candidate)

        # Initialize chain
        # _chain = chain.Chain(lastBlock)

        # Get the last block
        lastBlock = _chain.getBlock()

        # Initialize block 
        newblock = block.Block(candidate)
        newblock.updateBlock(lastBlock)
        blocks.append(newblock)
        print("Sending this to server")
        print(newblock)

        # Intimate the node server that a block is available for mining
        data = pickle.dumps(newblock)
        nodeServerSocket.sendall(data)

        # # Send vote details to all clients
        # data = pickle.dumps(blockchain.Blockchain.getDetails(votes))
        # clientConnection.sendall(data)


# ------------------------------Thread 6 -----------------------------
# def listenToNodeServer():
#     global stopMining
#     global nodeServerSocket
#     time.sleep(1)
#     while True:
#         data = nodeServerSocket.recv(1024)
#         block = pickle.loads(data)

#         if "MINED" not in block:
#             start_new_thread(mineBlock, (block,))
#         else:
#             stopMining = True
        
# ------------------------------Thread 5 -----------------------------
'''
'''
def connectToNodeServer():
    global nodeServerSocket
    global callCount
    global stopMining
    global voteDetails
    global _chain
    global a_lock

    # Create the socket
    nodeServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect via the socket
    try:
        nodeServerSocket.connect((NODEHOST, NODEPORT))
    except:
        print("Unable to connect to the blockchain service")
        print("Trying again...")
        callCount = callCount + 1
        if callCount > 2:
            return
        else:
            connectToNodeServer()
    
    # Get the last block
    data = nodeServerSocket.recv(1024)
    lastBlock = pickle.loads(data)

    if _chain == None:
        _chain = chain.Chain(lastBlock)
    else:
        _chain.setBlock(block)

    # Get the vote count
    data = nodeServerSocket.recv(1024)
    voteDetails = pickle.loads(data)

    while True:
        data = nodeServerSocket.recv(1024)
        msg = pickle.loads(data)

        if isinstance(msg, block.Block):
            if stopMining:
                stopMining = False
            start_new_thread(mineBlock, (msg,))
            # else:
            #     print("Server sent this: \n")
            #     print(msg)

            #     if _chain == None:
            #         _chain = chain.Chain(msg)
            #     else:
            #         _chain.setBlock(msg)
        elif isinstance(msg, list):
                voteDetails = msg

                # Broadcast the vote count to all connected clients
                broadCastVoteCount()
        # Another server on the blockchain network has mined the block
        else:
            a_lock.acquire(0)
            stopMining = True
            a_lock.release()

            data = nodeServerSocket.recv(1024)
            msg = pickle.loads(data)
            if _chain == None:
                _chain = chain.Chain(msg)
            else:
                _chain.setBlock(msg)

# ------------------------------Thread 7 -----------------------------
def mineBlock(block):
    global _chain
    global stopMining
    diff = 20
    maxNonce = 2**32
    target = 2 ** (256-diff)

    while not stopMining:
        for n in range(maxNonce):
            if stopMining:
                print("Minig halted")
                return
 
            if int(block.hash(), 16) <= target:
                if _chain == None:
                    _chain = chain.Chain(block)
                previousBlock = _chain.getBlock()
                
                block.previous_hash = previousBlock.hash()
                block.blockNo = previousBlock.blockNo + 1

                _chain.add(block)
                print(block)
                msg = "MINED"
                data = pickle.dumps(msg)
                nodeServerSocket.sendall(data)

                data = pickle.dumps(_chain)
                nodeServerSocket.sendall(data)
                return
            else:
                block.nonce += 1
    
    data = pickle.dumps(_chain)
    nodeServerSocket.sendall(data)

def lookUpClient(client):
    global clientConnections

    for i, conn in enumerate(clientConnections):
        if conn == client:
            return i

def broadCastVoteCount():
    global voteDetails
    global clientConnections
    global votersList

    # Package the data for sending 
    votes = blockchain.Blockchain.getDetails(voteDetails)
    data = pickle.dumps(votes)

    for i, conn in enumerate(clientConnections):
        # Send the vote count to the clients who have already voted
        if votersList[i]:
            conn.sendall(data)

# create jobs
def create_jobs():
    global queue

    for i in range(1, NUMBER_OF_THREADS + 1):
        queue.put(i)

    queue.join() # Halt the main thread

def create_threads():

    for i in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=work)
        thread.daemon = True # make it a background process
        thread.start()

def work():
    global queue

    while True:
        job = queue.get()
        if job == 1:
            createSocket()
            bindSocket()
            acceptConnection()
        # elif job == 2:
        #     configure()
        elif job == 3:
            pingClients()
        elif job == 4:
            connectToNodeServer()
        # elif job == 5:
        #     listenToTheClients()
        # elif job == 5:
        #     listenToNodeServer()

create_threads()
create_jobs()
