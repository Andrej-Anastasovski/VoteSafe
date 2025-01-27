import hashlib
import json
import datetime
from .blockchain_storage import BlockchainStorage

class Blockchain:
    def __init__(self):
        self.chain = []  # Initialize chain first
        self.current_votes = []
        self.storage = BlockchainStorage()
        loaded_chain = self.storage.load_blockchain()
        
        if loaded_chain:
            self.chain = loaded_chain
        else:
            genesis = self.create_genesis_block()
            self.chain = [genesis]
            self.storage.save_blockchain(self.chain)

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.current_votes = []
        self.chain.append(block)
        return block

    def create_genesis_block(self):
        return self.create_block(proof=1, previous_hash='0')

    def add_vote(self, voter_id, encrypted_vote):
        # Hash the voter ID using SHA-256
        hashed_voter_id = hashlib.sha256(voter_id.encode()).hexdigest()
        
        # Add the vote to the current votes
        self.current_votes.append({
            'voter_id': hashed_voter_id,  # Store hashed ID instead of plain ID
            'president': encrypted_vote[0],
            'party': encrypted_vote[1],
            'timestamp': str(datetime.datetime.now())
        })
        
        # Create a new block and add it to the blockchain
        block = self.create_block(proof=100, previous_hash=self.hash(self.chain[-1]))
        
        # Save the updated blockchain to a file
        self.storage.save_blockchain(self.chain)
        
        return block


    def check_duplicate_voter(self, voter_id):
        hashed_voter_id = hashlib.sha256(voter_id.encode()).hexdigest()
        for block in self.chain:
            for vote in block['votes']:
                if vote['voter_id'] == hashed_voter_id:
                    return True
        return False

    def get_votes(self):
        all_votes = []
        for block in self.chain:
            all_votes.extend(block['votes'])
        return all_votes

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
