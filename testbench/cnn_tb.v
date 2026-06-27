`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 24.02.2026 22:45:25
// Design Name: 
// Module Name: cnn_resnet_tb
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////
`timescale 1ns / 1ps

module tb();

    // -------------------------------------------------------------------------
    // 1. System Signals
    // -------------------------------------------------------------------------
    reg clk;
    reg rst;
    reg start;
    reg ready;
    
    wire done;
    wire [7:0] result;
    
    // -------------------------------------------------------------------------
    // 2. Interconnect Wires (CNN to BRAMs)
    // -------------------------------------------------------------------------
    // Feature Map 1 (Image Input / Ping-Pong A)
    wire [31:0] if1_addr;
    wire [31:0] if1_din;
    wire [31:0] if1_dout;
    wire        if1_en;
    wire [3:0]  if1_we;

    // Feature Map 2 (Ping-Pong B)
    wire [31:0] if2_addr;
    wire [31:0] if2_din;
    wire [31:0] if2_dout;
    wire        if2_en;
    wire [3:0]  if2_we;

    // Master Weight BRAM (All 5 layers combined)
    wire [31:0] w_addr;
    wire [31:0] w_dout;
    wire        w_en;

    // -------------------------------------------------------------------------
    // 3. Instantiate the CNN Accelerator (Unit Under Test)
    // -------------------------------------------------------------------------
    cnn uut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .done(done),
        .ready(ready),
        .result(result),
        
        // IF1 Connection
        .BRAM_IF1_ADDR(if1_addr), 
        .BRAM_IF1_EN(if1_en), 
        .BRAM_IF1_WE(if1_we), 
        .BRAM_IF1_DIN(if1_din), 
        .BRAM_IF1_DOUT(if1_dout),
        
        // IF2 Connection
        .BRAM_IF2_ADDR(if2_addr), 
        .BRAM_IF2_EN(if2_en), 
        .BRAM_IF2_WE(if2_we), 
        .BRAM_IF2_DIN(if2_din), 
        .BRAM_IF2_DOUT(if2_dout),
        
        // Master Weight Connection
        .BRAM_W_ADDR(w_addr), 
        .BRAM_W_EN(w_en), 
        .BRAM_W_DOUT(w_dout)
    );

    // -------------------------------------------------------------------------
    // 4. Instantiate the 3 Memory Banks (BRAMs)
    // -------------------------------------------------------------------------
    // NOTE: Change the INIT_FILE paths to match where your Python script saved them!

    // BRAM 1: Feature Map 1 (Loads the 32x32 MNIST image.hex)
    bram #(
        .ADDR_WIDTH(12), 
        .INIT_FILE("D:/Project/custom_cnn_build/hex_weights/image.hex") 
    ) bram_if1 (
        .clk(clk), 
        .en(if1_en), 
        .we(if1_we), 
        .addr(if1_addr[11:0]), 
        .din(if1_din), 
        .dout(if1_dout)
    );
    
    // BRAM 2: Feature Map 2 (Starts empty, used for Ping-Pong)
    bram #(
        .ADDR_WIDTH(12), 
        .INIT_FILE("") 
    ) bram_if2 (
        .clk(clk), 
        .en(if2_en), 
        .we(if2_we), 
        .addr(if2_addr[11:0]), 
        .din(if2_din), 
        .dout(if2_dout)
    );

    // BRAM 3: Master Weights (Loads the massive w_master.hex file)
    // ADDR_WIDTH is bumped to 18 to safely hold up to 262,144 bytes of weight data

// Update this line in your tb.v
    bram #(.ADDR_WIDTH(18), .INIT_FILE("w_master.hex")) bram_w_master (
    .clk(clk), .en(w_en), .we(4'b0000), .addr(w_addr[17:0]), .din(32'd0), .dout(w_dout)
    );
    // -------------------------------------------------------------------------
    // 5. Simulation Clock & Control Sequence
    // -------------------------------------------------------------------------
    
    // 100 MHz Clock Generation (10ns period)
    always #5 clk = ~clk; 

    initial begin
        // Initialize signals
        clk = 0;
        rst = 1;      // Assert strictly synchronous reset
        start = 0;
        ready = 1;

        // Hold reset for a few clock cycles to flush all pipeline registers
        #20;
        rst = 0;
        #20;

        $display("=======================================================");
        $display("Time: %0t | Starting 3-BRAM Synchronous MNIST Inference", $time);
        $display("=======================================================");
        
        // Trigger the CNN FSM
        start = 1;
        #10;
        start = 0;

        // Wait for the FSM to assert the 'done' signal
        wait(done == 1);
        
        $display("=======================================================");
        $display("Time: %0t | Inference Complete!", $time);
        $display("FINAL NETWORK PREDICTION (ArgMax Index): %d", result);
        $display("=======================================================");
        
        #50;
        $finish;
    end
endmodule
 
