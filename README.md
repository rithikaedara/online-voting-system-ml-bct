# Online Voting System using ML and Blockchain

A secure online voting system developed as an academic project, combining *Machine Learning* for voter verification (face recognition) and *Blockchain* to ensure vote integrity. The goal is to build a transparent and tamper-proof voting process suitable for educational or prototype environments.

## Features

- Voter authentication using *face recognition* (Dlib, OpenCV)
- *Blockchain-based ledger* to store and verify each vote
- Separate portals for *admin* and *voters*
- Simple web interface using *Django*

## Technologies Used

- Python
- Django
- OpenCV
- Dlib (Face recognition)
- MySQL
- Ganache & Solidity (for Blockchain simulation)
- HTML/CSS

## Project Modules

- adminapp/ – Admin login, candidate management, result view
- userapp/ – Voter login, face verification, voting
- ganachefaceproject/ – Machine learning models and blockchain integration
- media/, assets/, Project Images/ – Static files and documentation
