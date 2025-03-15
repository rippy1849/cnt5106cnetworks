import socket
import os
import time

CHUNK_SIZE = 64 * 1024  # 64KB per chunk

def send_file(peer_ip, peer_port):
    file_path = input("Enter the full path of the file you want to send: ")

    if not os.path.isfile(file_path):
        print("Error: The file does not exist.")
        return

    # Read file into chunks
    with open(file_path, 'rb') as file:
        chunks = []
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_ip, peer_port))
            print(f"Connected to peer at {peer_ip}:{peer_port}")

            # Send number of chunks and wait for acknowledgment
            s.sendall(str(len(chunks)).encode('utf-8'))
            ack = s.recv(1024).decode('utf-8')
            if ack != "READY":
                print("Receiver not ready. Aborting transfer.")
                return

            # Send file chunks with progress output
            for i, chunk in enumerate(chunks):
                s.sendall(chunk)
                print(f"Sent chunk {i+1}/{len(chunks)} of size {len(chunk)} bytes")  # ✅ Display progress
                ack = s.recv(1024).decode('utf-8')
                if ack != "RECEIVED":
                    print("Error: Receiver did not confirm chunk. Aborting.")
                    return
            print("File sent successfully!")
    except ConnectionResetError:
        print("Error: Connection lost. The receiver might have disconnected.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def receive_file(local_ip, local_port):
    save_as = input("Enter the name you want to save the received file as: ")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((local_ip, local_port))
            s.listen(1)
            print(f"Listening for incoming connections on {local_ip}:{local_port}")

            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")

                # Receive number of chunks and send acknowledgment
                num_chunks = int(conn.recv(1024).decode('utf-8'))
                print(f"Expecting {num_chunks} chunks...")
                conn.sendall(b"READY")

                # Receive file chunks with progress output
                with open(save_as, 'wb') as file:
                    for i in range(num_chunks):
                        chunk = conn.recv(CHUNK_SIZE)
                        if not chunk:
                            break
                        file.write(chunk)
                        print(f"Received chunk {i+1}/{num_chunks} of size {len(chunk)} bytes")  # ✅ Display progress
                        conn.sendall(b"RECEIVED")

                print(f"File received and saved as {save_as}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    role = input("Do you want to (s)end or (r)eceive a file? (s/r): ").lower()

    PEER_IP = '127.0.0.1'
    PEER_PORT = 5001

    if role == 's':
        send_file(PEER_IP, PEER_PORT)
    elif role == 'r':
        receive_file(PEER_IP, PEER_PORT)
    else:
        print("Invalid option. Please choose 's' for send or 'r' for receive.")

if __name__ == "__main__":
    main()
