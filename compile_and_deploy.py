# compile_and_deploy.py
import json
from web3 import Web3
from solcx import compile_standard, install_solc

# Install the Solidity compiler
install_solc('0.8.0')

# Read the Solidity contract
with open('VotingHashes.sol', 'r') as file:
    voting_hashes_sol = file.read()

# Compile the Solidity contract
compiled_sol = compile_standard({
    'language': 'Solidity',
    'sources': {
        'VotingHashes.sol': {
            'content': voting_hashes_sol
        }
    },
    'settings': {
        'outputSelection': {
            '*': {
                '*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap']
            }
        }
    }
}, solc_version='0.8.0')

# Save compiled contract data
with open('compiled_contract.json', 'w') as file:
    json.dump(compiled_sol, file)

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
w3.eth.default_account = w3.eth.accounts[0]

# Get bytecode
bytecode = compiled_sol['contracts']['VotingHashes.sol']['VotingHashes']['evm']['bytecode']['object']

# Get ABI
abi = compiled_sol['contracts']['VotingHashes.sol']['VotingHashes']['abi']

# Deploy the contract
VotingHashes = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = VotingHashes.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Get contract address
contract_address = tx_receipt.contractAddress
print(f'Contract deployed at address: {contract_address}')
