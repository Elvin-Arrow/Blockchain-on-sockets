import datetime
import hashlib

class Chain:

    def __init__(self, block):
        self.block = block

    def add(self, block):

        block.previous_hash = self.block.hash()
        block.blockNo = self.block.blockNo + 1

        self.block.next = block
        self.block = self.block.next
        self.blocks = block

    def getBlock(self):
        return self.block

    def setBlock(self, block):
        self.block = block

    def updateBlock(self, block):
        block.blockNo = self.block.blockNo + 1
        return block

    def __str__(self):
        return "Chain Object"