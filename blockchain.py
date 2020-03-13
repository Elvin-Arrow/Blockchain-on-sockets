import datetime
import hashlib
import block

class Blockchain:

    diff = 20
    maxNonce = 2**32
    target = 2 ** (256-diff)

    block = block.Block("Genesis")
    dummy = head = block

    def __init__(self):
        self.blocks = []
        self.blocks.append(self.block)

    def addBlock(self, block):
        self.blocks.append(block)

    def setBlock(self, block):
        self.block = block

    def add(self, block):

        block.previous_hash = self.block.hash()
        block.blockNo = self.block.blockNo + 1

        self.block.next = block
        self.block = self.block.next
        self.block = block
        self.addBlock(block)

    def mine(self, block):
        for n in range(self.maxNonce):
            if int(block.hash(), 16) <= self.target:
                self.add(block)
                print(block)
                break
            else:
                block.nonce += 1

    def isValidBlock(self, block):
        if block.blockNo < self.block.blockNo:
            return False
        else:
            return True

    def lastBlock(self):
        return self.blocks[-1]

    def details(self):
        candidate1 = 0
        candidate2 = 0
        for block in self.blocks:
            if block.data == '0':
                candidate1 = candidate1 + 1
            elif block.data == '1':
                candidate2 = candidate2 + 1

        # detail = ("================== Votes ==================\nCandidate 1: %d\nCandidate 2: %d", candidate1, candidate2)

        return [candidate1, candidate2]

    @classmethod
    def updateDetails(cls, voteCount, vote):
        candidate1 = 0
        candidate2 = 0
        try:
            if vote == 0:
                voteCount[0] = voteCount[0] + 1
            elif vote == 1:
                voteCount[1] = voteCount[1] + 1
            return voteCount
        except:
            if vote == 0:
                candidate1 = 1
            elif vote == 1:
                candidate2 = 1
            return [candidate1, candidate2] 
        

    @classmethod
    def getDetails(cls, details):
        candidate1 = details[0]
        candidate2 = details[1]

        detail = ("================== Votes ==================\nCandidate 1: " + str(candidate1) + "\nCandidate 2: " + str(candidate2))

        return detail
