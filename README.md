# P2P Secure Chat: Progressive Implementation with DH & AES

A progressive implementation of P2P chat systems, evolving from basic socket programming to secure communication with Diffie-Hellman key exchange and AES encryption, featuring practical network analysis and security implementations.

## Project Features
- Foundational network programming concepts
- Real-time P2P chat functionality
- Advanced security implementations:
  - Diffie-Hellman key exchange
  - AES-256 encryption
  - Secure message handling
- Complete with network analysis and security demonstrations

## Project Highlights
- Implementation of basic to advanced networking concepts
- Progressive enhancement of security features
- Real-world application of cryptographic protocols
- Practical demonstration of P2P architecture
- Network traffic analysis and monitoring

## Tasks Overview

### 1. Client-Server Calculator
A socket-based calculator implementation supporting basic arithmetic operations with left-to-right evaluation.
- Supports operations: +, -, *, /, %
- Server handles expression evaluation
- Client provides user interface for input

### 2. P2P Chat System
A basic chat system with central server for user registration and P2P messaging capabilities.
- Central server for user management
- P2P direct messaging
- Real-time chat using threading
- User discovery functionality

### 3. Secure Chat with Diffie-Hellman
Enhanced P2P chat system implementing Diffie-Hellman key exchange for secure communication.
- Secure key exchange using Diffie-Hellman algorithm
- Central server for user registration
- P2P encrypted messaging
- Network traffic analysis using Wireshark

### 4. AES Encrypted Chat System
Advanced secure chat implementation using AES encryption for message confidentiality.
- AES encryption in CBC mode
- Diffie-Hellman key exchange
- Secure P2P communication
- Wireshark packet analysis

## Getting Started

### Prerequisites
- Python 3.x
- Basic understanding of networking concepts
- Wireshark (for packet analysis)

### Running the Applications

Each task contains two main components:
1. Server (`server.py`)
2. Client (`client.py`)

#### General Setup Steps:
1. Navigate to the specific task directory
2. Start the server first:
   ```bash
   python server.py
   ```
3. Start the client in a new terminal:
   ```bash
   python client.py
   ```

Refer to individual task directories for specific instructions and port configurations.

## Detailed Implementation

### calculator-service/
The foundational client-server implementation demonstrating:
- Socket programming basics
- Server-side expression parsing and evaluation
- Client-side input handling and response processing
- Support for complex arithmetic expressions
- Error handling and input validation
- **Port**: 10001

### basic-p2p-chat/
Introduction to P2P architecture with features:
- Centralized user registration system
- Direct P2P messaging capabilities
- Multi-threaded message handling
- Real-time user discovery
- Connection state management
- **Port**: 10000

### secure-dh-chat/
Enhanced P2P system with Diffie-Hellman key exchange:
- Secure key establishment protocol
- Mathematical implementation of DH algorithm
- Protection against man-in-the-middle attacks
- Session key generation
- Network traffic analysis
- **Port**: 10000
- **Includes**: Wireshark capture files for analysis

### encrypted-aes-chat/
Advanced secure messaging system implementing:
- AES-CBC mode encryption
- Secure key exchange using DH
- Message confidentiality and integrity
- Encrypted P2P communication
- Detailed packet analysis
- **Port**: 10001
- **Includes**: Wireshark capture files and encryption analysis

## Technical Details

### Security Features
- **Diffie-Hellman Key Exchange**
  - Prime number generation
  - Public/private key pairs
  - Shared secret computation
  
- **AES Encryption**
  - CBC mode implementation
  - Key size: 256 bits
  - IV handling
  - Message padding

### Network Architecture
- **Server Components**
  - User registration handling
  - Active user management
  - Connection brokering
  
- **Client Components**
  - P2P connection establishment
  - Message encryption/decryption
  - Multi-threaded operations

### Error Handling
- Connection failures
- Invalid user inputs
- Encryption/decryption errors
- Network timeouts
- Graceful disconnection

## Repository Structure
```
.
├── calculator-service/     # Basic Socket Programming
├── basic-p2p-chat/        # P2P Chat Implementation
├── secure-dh-chat/        # DH Key Exchange System
│   └── Task3.pcap         # Wireshark Capture File
└── encrypted-aes-chat/    # AES Encrypted Chat
    └── Task4.pcap         # Wireshark Capture File
```

## Installation and Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/p2p-secure-chat.git

# Navigate to project directory
cd p2p-secure-chat

# Install required Python packages (if any)
pip install -r requirements.txt
```

## Authors
- Sushant Joshi (CS24MTECH14017)
- Kshitij Sonje (CS24MTECH11025)