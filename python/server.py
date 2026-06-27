"""
ResNet-18 (83.33 MHz) FPGA Accelerator Server
Architecture: 3-BRAM Ping-Pong Buffer (IF1, IF2, W_MASTER)
"""
import socket
import tqdm
import os
import numpy as np
import cv2
import time
from pynq import Overlay
from pynq import MMIO

# MNIST Classes
LABELS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def extract_data():

    time.sleep(0.5) 
    
    img = cv2.imread("./image.jpg")
    if img is None:
        print("[-] Error: Could not read image.jpg")
        return
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Resize to 28x28 and invert colors (MNIST format)
    resize_img = cv2.resize(gray, (28, 28))
    dst = 255 - resize_img
    
    # Pad to 32x32 so the hardware Address Generator sweeps correctly
    arr_2d = np.pad(array=dst, pad_width=((2, 2), (2, 2)), mode='constant', constant_values=0)
    arr_2d = np.reshape(arr_2d, (1024, 1)) 
    np.savetxt("./temp.hex", arr_2d, delimiter="", fmt='%s')
    
    # Read back and format into 32-bit (4-byte) hex words for BRAM
    list_vals = []
    with open("./temp.hex", "r") as f:
        for j in f:
            list_vals.append(int(j))
            
    l_i_hex1 = ['{:02x}'.format(l) for l in list_vals]
    arr_2d = np.reshape(l_i_hex1, (256, 4))
    np.savetxt("./image.hex", arr_2d, delimiter="", fmt='%s')
    print("[+] Image pre-processing and formatting complete.")
    
def pynq_setup():
    """Configures the FPGA fabric and loads the unified Master Weights."""
    global zynq_sys, cdma, gpio_start, gpio_done, gpio_result
    
    print("[*] Loading Bitstream...")
    # UPDATE THIS to match your exact bitstream name
    design = Overlay("./resnet18_83mhz.bit") 
    
    # Extract physical addresses from the Vivado block design dictionary
    cdma_address = design.ip_dict['axi_cdma_0']['phys_addr']
    axi_gpio_address0 = design.ip_dict['axi_gpio_0']['phys_addr'] # Start
    axi_gpio_address1 = design.ip_dict['axi_gpio_1']['phys_addr'] # Done
    axi_gpio_address2 = design.ip_dict['axi_gpio_2']['phys_addr'] # Result

    # Initialize Memory-Mapped I/O (MMIO) interfaces
    # Base Zynq RAM allocated for CDMA staging
    zynq_sys    = MMIO(zynq_addr, 0x200000) # 2MB staging area
    cdma        = MMIO(cdma_address, 0xC000)
    gpio_start  = MMIO(axi_gpio_address0, 8)
    gpio_done   = MMIO(axi_gpio_address1, 8)
    gpio_result = MMIO(axi_gpio_address2, 8)
    
    # Ensure start signal is LOW
    gpio_start.write(0x0, 0)

    print('[*] Loading ResNet-18 Master Weights to Hardware BRAM...')
    w_offset = 0x0

    # Load the unified 1.2MB w_master.hex file
    try:
        with open("w_master.hex", "r") as f_in:
            for line in f_in:
                if not line.strip():
                    break
                zynq_sys.write(w_offset, int('0x'+line, 16))      
                w_offset += 4

        # Trigger CDMA: Zynq RAM -> BRAM W_MASTER (0xC4000000)
        cdma.write(0x00, 0x04) # Clear errors/start
        cdma.write(0x18, zynq_addr) # Source Address
        cdma.write(0x20, w_addr) # Destination Address
        cdma.write(0x28, w_offset) # Transfer size in bytes
        print(f"[+] Master Weights loaded successfully! ({w_offset} bytes transferred)")
        
    except FileNotFoundError:
        print("[-] ERROR: 'w_master.hex' not found! Make sure it is in the same directory.")
        exit(1)

def load_if():
    """Loads the pre-processed image into the IF1 BRAM."""
    bram0_offset = 0x0
    with open("image.hex", "r") as f_in:
        for line in f_in:
            if not line.strip():
                break
            zynq_sys.write(bram0_offset, int('0x'+line, 16))      
            bram0_offset += 4

    # Trigger CDMA: Zynq RAM -> BRAM IF1 (0xC0000000)
    cdma.write(0x00, 0x04)
    cdma.write(0x18, zynq_addr)
    cdma.write(0x20, if1_addr)
    cdma.write(0x28, 0x400) # 1024 bytes (256 words)
    print("[+] Feature Map (image.hex) transferred to IF1.")
    
def main():
    """Triggers the hardware FSM and reads the ping-pong result."""
    print("[*] Starting Hardware Inference...")
    
    start_time = time.perf_counter() # High-precision timer
    
    # Pulse 'start' GPIO to wake up cnn.v
    gpio_start.write(0, 1) 
    gpio_start.write(0, 0)
    
    # Poll 'done' GPIO until the FSM finishes all layers
    while gpio_done.read() == 0:
        pass
        
    # Read classification from the AXI-Lite result register
    softmax_int = gpio_result.read()
    
    end_time = time.perf_counter()
    
    print(f"--- Software Inference Time: {(end_time - start_time):.6f} seconds ---")
    
    try:
        print(f">>> PREDICTED DIGIT: {LABELS[softmax_int]} <<<")
    except IndexError:
        print(f"[-] Error: Hardware returned out-of-bounds value: {softmax_int}")
        
    print('\n===================================\n[*] Ready for next image!')

def sckt():
    """Listens for an incoming image over TCP socket."""
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5001
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"
    
    s = socket.socket()
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(1)
    print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")
    
    client_socket, address = s.accept() 
    print(f"[+] {address} connected.")

    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))

    client_socket.close()
    s.close()
    
if __name__ == "__main__":
    # --- System Memory Map ---
    # Safe DDR space for PS-PL staging to avoid crashing the PYNQ Linux kernel
    zynq_addr  = 0x10000000 
    
    # BRAM Controller Addresses from Vivado Address Editor
    if1_addr   = 0xC0000000 # axi_bram_ctrl_0 (IF1 Input/Even Layers)
    if2_addr   = 0xC2000000 # axi_bram_ctrl_1 (IF2 Ping-Pong Buffer)
    w_addr     = 0xC4000000 # axi_bram_ctrl_2 (Unified W_MASTER)
    
    # 1. Initialize Overlay and load weights once
    pynq_setup()
    
    # 2. Wait in an infinite loop for incoming images to process
    while True:
        sckt()
        extract_data()
        load_if()
        main()