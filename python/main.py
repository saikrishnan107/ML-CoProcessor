import socket
import tqdm
import os
import sys

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4 # 4KB

# --- UPDATE THIS TO YOUR PYNQ IP ---
HOST = "192.168.2.1" 
PORT = 5001
def send_image(filepath):
    # Check if file exists
    if not os.path.isfile(filepath):
        print(f"[-] Error: File '{filepath}' not found.")
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    # Initialize Socket
    s = socket.socket()
    print(f"[+] Connecting to {HOST}:{PORT}...")
    
    try:
        s.connect((HOST, PORT))
        print("[+] Connected to FPGA Server.")
    except Exception as e:
        print(f"[-] Connection failed. Is server.py running on the PYNQ? Error: {e}")
        return

    # 1. Send file metadata (Name and Size)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # 2. Send the actual image bytes
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))
            
    s.close()
    print("\n[+] Image successfully uploaded to the ResNet-18 pipeline.")

if __name__ == "__main__":
    # Ensure the user provided an image path
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_image.jpg>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    send_image(image_path)