import hashlib
import json
from time import time

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.curTransactions = []

        # Create the genesis block with no previous block
        self.newBlock(prevHash = 1, proof = 100)

        def newBlock(self, proof, prevHash = None):
            """
            Creates a new block and adds it to the blockchain

            Args:
                proof (int): Proof of work given by algo
                prevHash (str, optional): Hash of previous block. Defaults to None.
            """
            
            block = {
                "index": len(self.chain) + 1,
                "timestamp": time(),
                "transactions": self.curTransactions,
                "proof": proof,
                "prevHash": prevHash or self.hash(self.chain[-1],)
            }

            # Reset current transactions
            self.curTransactions = []

            self.chain.append(block)
            return block

        def newTransaction(self, sender, recipient, amount):
            """
            Adds new transaction to list of current transactions to be mined in next Block

            Args:
                sender (str): Address of the Sender
                recipient (str): Address of the Recipient
                amount (int): Amount of transaction
            """
            
            self.curTransactions.append(
                {"sender": sender,
                "recipient": recipient,
                "amount": amount,}
            )

            return self.lastBlock("index") + 1

        @property
        def lastBlock(self):
            return self.chain[-1]

        @staticmethod
        def hash(block):
            """
            Creates a SHA-256 hash for a block

            Args:
                block (dict): Block
            """

            # The dictionary representing block must be ordered, or we'll have inconsistent hashing
            blockStr = json.dumps(block, sort_keys=True).encode()
            return hashlib.sha256(blockStr).hexdigest()

        


