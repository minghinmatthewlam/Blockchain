import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

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

        Returns:
            dict: New block
        """
        
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.curTransactions,
            "proof": proof,
            "prevHash": prevHash or self.hash(self.chain[-1]),
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

        Returns:
            int: Index of the block that will hold this transaction
        """
        
        self.curTransactions.append(
            {"sender": sender,
            "recipient": recipient,
            "amount": amount,}
        )

        return self.lastBlock["index"] + 1

    @property
    def lastBlock(self):
        """
        Returns the last block of the chain

        Returns:
            dict: Last block
        """
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash for a block

        Args:
            block (dict): Block

        Returns:
            str: hash of the block
        """

        # The dictionary representing block must be ordered, or we'll have inconsistent hashing
        blockStr = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockStr).hexdigest()

    def proofWork(self, lastProof):
        """
        Proof of work Algorithm:
            - Find a numper p' such that hash(pp') contains 4 leading 0's, where p is previous p' (proof of prevBlock)
            - p is the previous proof, and p' is the new proof

        Args:
            lastProof (int): Last proof (proof of prevBlock)

        Returns:
            int: New proof
        """

        proof = 0
        while self.validProof(lastProof, proof) is False:
            proof += 1

        return proof

    def validProof(self, lastProof, proof):
        """
        Validates the proof: Does hash(lastProof, proof) have 4 leading 0's?

        Args:
            lastProof (int): last proof
            proof (int): current proof

        Returns:
            bool: Whether the pass proof is valid with prevProof
        """

        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4] == "0000"
    
# Instantiate our node
app = Flask(__name__)

# Generate a global unique addr for node
nodeIdentity = str(uuid4()).replace('-', '')

# Create Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Run proof of work algo for next proof
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock["proof"]
    proof = blockchain.proofWork(lastProof)
    
    # Reward miner a coin, mark sender as 0
    blockchain.newTransaction(
        sender = "0",
        recipient = nodeIdentity,
        amount = 1,
    )
    
    # Create the new block and add it to the end of blockchain
    prevHash = blockchain.hash(lastBlock)
    newBlock = blockchain.newBlock(proof, prevHash)
    
    response = {
        'message': 'New Block Forged',
        'index': newBlock["index"],
        'transactions': newBlock["transactions"],
        'proof': newBlock["proof"],
        'prevHash': newBlock["prevHash"],
    }
    
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def newTransaction():
    values = request.get_json() 
    
    # Check values has the correct fields for POST
    required = ["sender", "recipient", "amount"]
    if not all(x in values for x in required):
        return "Missing values for POST", 400
    
    # We have all required fields, create the transaction
    index = blockchain.newTransaction(values["sender"], values["recipient"], values["amount"])

    response = {
        "message": f"Transaction will be added to Block {index}"
    }
    return jsonify(response), 201
    
@app.route('/chain', methods=['GET'])
def fullChain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
