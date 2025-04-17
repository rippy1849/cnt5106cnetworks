# CNT5106cnetworks

Team 9: Andrew Rippy,
        Sri Vaishnavi Borusu

# Peer-to-Peer File Sharing System 

## Overview

This project implements a BitTorrent-like peer-to-peer (P2P) file sharing system using Java. Each peer in the system is capable of reading configuration files, establishing connections with other peers, exchanging file pieces, and gracefully exiting once all peers have the complete file. The system follows a structured protocol to handle peer coordination, message exchange, and file distribution.

---

## Configuration Files

### 1. `Common.cfg`

Defines the global configuration parameters for all peers:

- **NumberOfPreferredNeighbors**: `k` – The number of preferred neighbors each peer unchokes every round.
- **UnchokingInterval**: `p` – Time interval (in seconds) to change the set of preferred neighbors.
- **OptimisticUnchokingInterval**: `m` – Time interval (in seconds) to optimistically unchoke a random neighbor.
- **FileName**: The name of the file being shared.
- **FileSize**: The size of the file in bytes.
- **PieceSize**: The size of each piece in bytes.

### 2. `PeerInfo.cfg`

Defines peer-specific parameters:

- **PeerID**: A unique identifier for the peer.
- **Hostname**: IP address or hostname of the peer.
- **Port**: Listening port for incoming TCP connections.
- **HasFile**: `1` if the peer has the complete file initially, `0` otherwise.

---

## Process Initialization

Each peer, when launched, performs the following steps:

- Parses both `Common.cfg` and `PeerInfo.cfg` to initialize relevant variables and state.
- Starts a server socket to accept incoming connections from peers with higher PeerIDs.
- Initiates TCP connections to all peers listed before it in the configuration.

---

## Protocol and Message Exchange

### 1. Handshake Phase

When a connection is established between two peers, a **handshake message** is immediately sent by both peers. This is used for initial peer validation.

### 2. Bitfield Exchange

After the handshake, each peer sends a **bitfield message** representing the pieces of the file it currently possesses.

### 3. Interest Management

Each peer evaluates the bitfield of its connected neighbors:

- Sends an **interested** message if the neighbor has pieces it needs.
- Sends a **not interested** message otherwise.

### 4. Choking and Unchoking

- Every `p` seconds, a peer selects `k` preferred neighbors (based on download rate) to unchoke. All other peers are choked.
- Every `m` seconds, an **optimistically unchoked** neighbor is randomly selected from among the interested, choked peers.

---

## File Piece Exchange

### Message Types Involved:

- **Request**: Sent to request a specific piece.
- **Piece**: Contains the actual piece data in response to a request.
- **Have**: Notifies neighbors that a new piece has been obtained.
- **Interested** / **Not Interested**: Re-evaluated as bitfields change after receiving `have`.

Each peer maintains:

- A bitfield representing its own file state.
- A bitfield for each connected peer.
- A queue of pending requests.
- A log of pieces already received.

---

## File Completion and Termination

- Once a peer has downloaded all pieces, it checks whether all other peers also have the full file.
- If true for all peers, the process gracefully shuts down, closing all connections and threads.
- Proper logging and cleanup ensure no dangling processes.

---

## Logging (Optional but Recommended)

Peers may maintain a log of all events for debugging and evaluation:

- Connection establishment
- Message exchange
- Piece download
- Choke/Unchoke events
- File completion

---

## Technical Challenges & Considerations

- **Thread safety**: Concurrent socket communication and state updates require synchronization.
- **Fairness in peer selection**: Correctly implementing selection of preferred and optimistic unchoking neighbors.
- **Efficient data transfer**: Managing buffer sizes and avoiding redundant piece transfers.
- **Graceful termination**: Ensuring all threads and sockets close without data loss or deadlocks.
- **Scalability**: Code structure supports the addition of more peers without manual changes.

---

## Conclusion

This system simulates the core principles of a distributed file-sharing protocol with dynamic peer management, robust messaging, and efficient piece distribution. It ensures that all peers eventually receive the complete file while maintaining proper communication and termination protocols.
