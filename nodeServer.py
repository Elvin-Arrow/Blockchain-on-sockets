import socket
import time
import queue
import threading
from _thread import *
import blockchain
import block
import pickle
import chain


# Constants
# HOST = '127.0.0.1' 
# HOST = '192.168.100.18'
HOST = socket.gethostbyname('DESKTOP-QQB5RUH')
PORT = 12500
NUMBER_OF_THREADS = 1

# Global Variables
nodeSocket = None
clientConnections = []
clientAddresses = []
queue = queue.Queue()

# Initialize blockchain
_blockchain = blockchain.Blockchain()

def serveBlockChain():
    global nodeSocket
    global clientConnections
    global clientAddresses

    # Create a socket
    nodeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket
    nodeSocket.bind((HOST, PORT))

    nodeSocket.listen(5)
    print("Listening to port " + str(PORT))

    while(True):
        try:
            clientConnection, clientAddress = nodeSocket.accept()

            clientConnections.append(clientConnection)
            clientAddresses.append(clientAddress)
            print(str(clientAddress[0]) + " just connected")

            # Send in the block to the client that just connected
            _block = _blockchain.lastBlock()
            data = pickle.dumps(_block)
            clientConnection.sendall(data)

            # Send the vote count
            data = pickle.dumps(_blockchain.details())
            clientConnection.sendall(data)

            start_new_thread(notifier, (clientConnection, clientAddress))

        except Exception as e:
            print("Error in accepting connections" + e)

'''
Function to receive blocks and set the mine status
'''
def notifier(clientConnection, clientAddress):
    global _blockchain

    while True:
        data = clientConnection.recv(1024)
        msg = pickle.loads(data)
        print(msg)

        # The new vote block
        if isinstance(msg, block.Block):
            for conn in clientConnections:
                conn.sendall(data)
        # The mined block to be added to the block chain
        elif isinstance(msg, chain.Chain):
            newBlock = msg.getBlock()
            if _blockchain.isValidBlock(newBlock):
                _blockchain.add(newBlock)
                print("Node added successfully")

                # Send the latest block to all clients
                _block = _blockchain.lastBlock()
                data = pickle.dumps(_block)
                
                for conn in clientConnections:
                    conn.sendall(data)

                print("Send the updated vote count")
                # Sending the updated vote count
                voteCount = _blockchain.details()
                print(voteCount)
                data = pickle.dumps(voteCount)
                
                for conn in clientConnections:
                    conn.sendall(data)

        # Some client has successfully mined a block
        elif "MINED" in msg:
            print("Block mined successfully")
            msg = "MINED"
            data = pickle.dumps(msg)
            for conn in clientConnections:
                conn.sendall(data)
            
        # else:
        #     chain = msg
        #     newBlock = chain.getBlock()
        #     blockchain.add(newBlock)
        

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
            serveBlockChain()
        # elif job == 2:
        #     notifier()
        # elif job == 3:
        #     pingClients()
        # elif job == 4:
        #     connectToNodeServer()

create_threads()
create_jobs()
