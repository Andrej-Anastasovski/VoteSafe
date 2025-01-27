from flask import Flask, render_template, request, redirect, url_for, flash
from src.blockchain import Blockchain
from src.vote_encryption import encrypt_vote, decrypt_vote
import hashlib

app = Flask(__name__)
app.secret_key = "secret_key"  # For flash messages and session management

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        if len(voter_id) == 10 and voter_id.isdigit():
            if not blockchain.check_duplicate_voter(voter_id):
                return redirect(url_for('vote', voter_id=voter_id))
            else:
                flash("This voter ID has already voted.")
                return redirect(url_for('register'))
        else:
            flash("Invalid voter ID. It must be a 10-digit number.")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/vote/<voter_id>', methods=['GET', 'POST'])
def vote(voter_id):
    if request.method == 'POST':
        president = request.form['president']
        party = request.form['party']

        encrypted_vote = encrypt_vote(president, party)
        blockchain.add_vote(voter_id, encrypted_vote)
        return render_template('success.html')
    return render_template('vote.html', voter_id=voter_id)

@app.route('/results')
def results():
    # Get all blocks from chain
    blocks = blockchain.chain
    
    # Process each block with full data
    processed_blocks = [{

        'index': block['index'],
        'timestamp': block['timestamp'],
        'votes': [{
            'voter_id': vote['voter_id'],  # Hashed voter ID
            'encrypted_president': vote['president'],
            'encrypted_party': vote['party'],
            'decrypted_president': decrypt_vote(vote['president']),
            'decrypted_party': decrypt_vote(vote['party']),
            'timestamp': vote['timestamp']
        } for vote in block['votes']],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    } for block in blocks]
    
    return render_template('results.html', blocks=processed_blocks)

@app.route('/aggresults')
def aggresults():
    blocks = blockchain.chain
    total_voters = 6797698
    total_votes = 0
    
    # Initialize vote counters
    president_votes = {"President1": 0, "President2": 0, "President3": 0, "President4": 0}
    party_votes = {"Party1": 0, "Party2": 0, "Party3": 0, "Party4": 0}
    
    # Count votes
    for block in blocks:
        for vote in block['votes']:
            total_votes += 1
            president_votes[decrypt_vote(vote['president'])] += 1
            party_votes[decrypt_vote(vote['party'])] += 1
    
    # Sort results
    sorted_presidents = sorted(president_votes.items(), key=lambda x: x[1], reverse=True)
    sorted_parties = sorted(party_votes.items(), key=lambda x: x[1], reverse=True)
    turnout = (total_votes / total_voters) * 100
    
    return render_template('graphresult.html',
                         total_voters=total_voters,
                         total_votes=total_votes,
                         turnout=turnout,
                         sorted_presidents=sorted_presidents,
                         sorted_parties=sorted_parties)

if __name__ == '__main__':
    app.run(debug=True)
