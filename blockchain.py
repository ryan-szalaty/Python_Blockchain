import functools
from collections import OrderedDict
import json
from hash_util import hash_string_256, hash_block


MINING_REWARD = 10


genesis_block = {
    'previous_hash': '', 
    'index': 0, 
    'transactions': [],
    'proof': 100
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Max'
participants = {'Max'}


def load_data():
    with open('blockchain.txt', 'r') as file:
        file_content = file.readlines()
        global blockchain
        global open_transactions
        blockchain = json.loads(file_content[0][:-1])
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'], 
                'transactions': [OrderedDict([
                    ('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) 
                    for tx in block['transactions']], 
                'proof': block['proof']
            }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain   
        open_transactions = json.loads(file_content[1])
        updated_transactions = []
        for tx in open_transactions:
            updated_transaction = {
                OrderedDict([
                ('sender', tx['sender']), 
                ('recipient', tx['recipient']), 
                ('amount', tx['amount'])])
            }
            updated_transactions.append(updated_transaction)
        open_transactions = updated_transactions



load_data()


def save_data():
    with open('blockchain.txt', 'w') as file:
        file.write(json.dumps(blockchain))
        file.write('\n')
        file.write(json.dumps(open_transactions))




def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_recipient, 0)
    return amount_received - amount_sent


def get_last_blockchain_value():
    """Returns last value of the current blockchain"""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender = owner, amount = 1.0):
    """Append a new value as well as the last blockchain value to the blockchain
    
    Arguments:
        :sender: Sender of the coins.
        :recipient: Recipient of the transaction.
        :amount: The amount that should be added. (default = [1])
    """
    transaction = OrderedDict([
        ('sender', sender), ('recipient', recipient), ('amount', amount)
    ])


    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    else:
        return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    print(hashed_block)

    reward_transaction = OrderedDict([
        ('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)
    ])

    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)

    block = {
        'previous_hash': hashed_block, 
        'index': len(blockchain), 
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True


def get_transaction_value():
    """Returns the input of the user (a new transaction amount) as a float"""
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Enter your transaction amount: '))
    return (tx_recipient, tx_amount)


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
            print('Outputting Block')
            print(block)


def verify_chain():
    """Verify the current blockchain"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index -1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid.')
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True


while waiting_for_input:
    print('Please choose:')
    print('1: Add a new transaction value')
    print('2: Output the blockchain blocks')
    print('3: Mine a new block')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('h: Manipulate blockchain')
    print('q: Finish')
    
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount = amount):
            print('Added transaction')
        else:
            print('Transaction failed')
    elif user_choice == '2':
        print_blockchain_elements()
    elif user_choice == '3':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid.')
        else:
            print('Invalid transaction detected.')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '', 
                'index': 0, 
                'transactions': [{'sender': 'Chris', 'recipient': 'Dave', 'amount': 100.00}]
            }
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Invalid entry. Please try again.')
    if not verify_chain():
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format('Max', get_balance('Max')))
else:
    print('User left!')

print('Done!')