# blockchain_utils.py
import hashlib
from web3 import Web3
from django.conf import settings

web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))

# Load contract ABI
abi = [
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "hashValue",
                "type": "bytes32"
            }
        ],
        "name": "storeHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
contract = web3.eth.contract(address=settings.CONTRACT_ADDRESS, abi=abi)

def store_hash_on_blockchain(data):
    # Compute the SHA-256 hash of the data
    hash_value = hashlib.sha256(data.encode()).hexdigest()
    
    # Convert the hash to bytes32 format
    hash_bytes32 = bytes.fromhex(hash_value)
    if len(hash_bytes32) != 32:
        raise ValueError("Hash must be 32 bytes long")
    
    nonce = web3.eth.get_transaction_count(settings.GANACHE_ACCOUNT_ADDRESS)
    
    # Build the transaction
    transaction = contract.functions.storeHash(hash_bytes32).build_transaction({
        'from': settings.GANACHE_ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 2000000,
        'maxFeePerGas': web3.to_wei('50', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei')
    })
    
    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=settings.GANACHE_PRIVATE_KEY)
    
    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) 
    
    # Wait for the transaction receipt
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return receipt
