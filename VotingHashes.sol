// VotingHashes.sol
pragma solidity ^0.8.0;

contract VotingHashes {
    event HashStored(bytes32 indexed hashValue);

    function storeHash(bytes32 hashValue) public {
        emit HashStored(hashValue);
    }
}
