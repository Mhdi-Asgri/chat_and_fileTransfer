import socket
import threading


def send_file(client_socket, buffer_size=1024):
    filename = input("Please enter the name of the file you want to send: ")
    try:
        client_socket.sendall(filename.encode())
        response = client_socket.recv(buffer_size)
        if response.decode() == 'OK':
            with open(filename, 'rb') as f:
                while True:
                    data = f.read(buffer_size)
                    if not data:
                        break
                    client_socket.sendall(data)
            client_socket.sendall(b'EOF')
            print("File sent successfully")
        else:
            print("Server did not acknowledge the filename.")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def receive_file(client_socket, buffer_size=1024):
    client_socket.settimeout(30.0)  # Set timeout of 30 seconds for socket operations
    try:
        # Receive filename from client
        filename_bytes = client_socket.recv(buffer_size)
        filename = "received_" + filename_bytes.decode()
        print(f"Receiving file: {filename}")

        # Acknowledge receipt of filename (optional)
        client_socket.sendall(b'OK')

        # Open file to write received data
        with open(filename, 'wb') as f:
            while True:
                try:
                    data = client_socket.recv(buffer_size)
                    if not data:
                        break
                    # Check if the received data contains the EOF marker
                    if b'EOF' in data:
                        f.write(data)
                        break
                    f.write(data)
                except socket.timeout:
                    print("Socket timed out. Stopping file reception.")
                    break
        
        print(f"File '{filename}' received successfully")
        
    except Exception as e:
        print(f"An error occurred: {e}")


def receive_messages(client_socket, buffer_size=1024):
    while True:
        try:
            rec_msg = client_socket.recv(buffer_size)
            if not rec_msg:
                print("Connection closed by the server.")
                break
            print("\rclient ->", rec_msg.decode(), "\nYou -> ", end="")
        except Exception as e:
            print(f"An error occurred receiving message: {e}")
            break

def send_messages(client_socket):
    while True:
        try:
            msg = input("You -> ")
            if msg.lower() == 'exit':  # Optional: Exit condition
                print("Exiting chat.")
                client_socket.close()
                break
            client_socket.sendall(msg.encode())
        except Exception as e:
            print(f"An error occurred sending message: {e}")
            break

def chat(client_socket, buffer_size=1024):
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, buffer_size))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()



if __name__ == "__main__":
    host='127.0.0.1'
    port=65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}...")
        
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        while True:
            print("q: for quite")
            print("h: for help")
            print("s: for sending file")
            print("r: for receiving file")
            print("c: for chat")
            cmnd = input("Enter your choice: ").strip()

            if cmnd == "s":
                send_file(client_socket)
            elif cmnd == "h":
                continue  # Display help again
            elif cmnd == "q":
                break
            elif cmnd == "r":
                receive_file(client_socket)
            elif cmnd == "c":
                chat(client_socket)
            else:
                print("Invalid command. Please try again.")
                continue
            # After each command, optionally prompt for another action
            more = input("Do you want to perform another action? (yes/no): ").strip().lower()
            if more != "yes":
                break  # Exit loop if not continuing
        client_socket.close()
