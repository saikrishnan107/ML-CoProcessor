# Machine Learning Co-Processor for Edge Inference Applications

An FPGA-based Machine Learning Co-Processor designed for low-latency, energy-efficient edge inference using the **PYNQ-Z2 (Xilinx Zynq-7000)** platform.

## Overview

This project presents a hardware-software co-design approach for accelerating Convolutional Neural Network (CNN) inference on edge devices. The ARM Processing System (PS) manages high-level control and preprocessing, while the FPGA Programmable Logic (PL) executes compute-intensive operations such as convolution and matrix multiplication.

The accelerator is based on the **LeNet-5** architecture and uses **fixed-point quantization (Q1.7)** to reduce hardware resource usage while maintaining high inference accuracy.

---

## Features

- FPGA-based CNN accelerator
- Hardware-software co-design
- Instruction-driven architecture
- Parallel Processing Element (PE) array
- BRAM-based memory hierarchy
- FSM-controlled execution
- AXI communication between PS and PL
- Fixed-point (Q1.7) quantization
- Low-latency edge inference

---

## Hardware Platform

| Component | Specification |
|-----------|---------------|
| FPGA Board | PYNQ-Z2 |
| SoC | Xilinx Zynq-7000 XC7Z020 |
| Processor | Dual-core ARM Cortex-A9 |
| FPGA Logic | Programmable Logic (PL) |
| Development Tool | Vivado 2020.1 |
| HDL | Verilog |

---

## System Architecture

The proposed architecture consists of:

- ARM Processing System (PS)
  - Image preprocessing
  - Instruction generation
  - Result interpretation
- FPGA Programmable Logic (PL)
  - CNN accelerator
  - Processing Element array
  - BRAM memory hierarchy
  - FSM controller
  - AXI interface

The ARM processor transfers input data and control instructions through the AXI interface, while the FPGA performs CNN inference and returns the classification results.

---

## LeNet-5 Network

| Layer | Configuration |
|--------|---------------|
| Input | 32×32 Grayscale |
| Conv1 | 6 × 5×5 + ReLU |
| MaxPool | 2×2 |
| Conv2 | 16 × 5×5 + ReLU |
| MaxPool | 2×2 |
| Conv3 | 120 × 5×5 + ReLU |
| FC1 | 84 neurons |
| FC2 | 47 output classes |

---

## Memory Architecture

The accelerator uses an optimized on-chip BRAM hierarchy.

- 5 BRAM blocks for CNN weights
- 2 BRAM blocks for feature maps
- Ping-pong buffering
- Local feature reuse
- Reduced external memory access

---

## Processing Pipeline

```
Input Image
      │
      ▼
 ARM Cortex-A9
      │
 AXI Interface
      │
      ▼
 FPGA Accelerator
      │
 ├── Convolution
 ├── ReLU
 ├── Pooling
 ├── Fully Connected
 └── Quantization
      │
      ▼
 Output Classification
```

---

## Design Modules

- Top Module
- Processing Element (PE)
- CNN Compute Engine
- FSM Controller
- AXI Interface
- BRAM Controller
- Quantizer
- ReLU
- Convolution Engine

---

## Performance

| Metric | Software | FPGA |
|--------|----------:|-----:|
| Accuracy | 85.8% | 85.6% |
| Average Inference Time | 80.86 ms | 0.50 ms |
| Throughput | 12 FPS | 1991 FPS |
| Speedup | — | ~165× |

The hardware implementation achieves approximately **165× acceleration** over CPU execution with only **0.2% accuracy loss**.

---

## FPGA Resource Utilization

| Resource | Used | Available |
|----------|-----:|----------:|
| LUT | 38,690 | 53,200 |
| LUTRAM | 1,883 | 17,400 |
| Flip-Flops | 43,396 | 106,400 |
| BRAM | 30 | 140 |
| DSP | 200 | 220 |

---

## Key Optimizations

- Parallel Processing Elements
- DSP-based MAC operations
- On-chip BRAM storage
- Ping-pong buffering
- Fixed-point arithmetic (Q.17)
- Instruction-driven execution
- Optimized memory hierarchy

## Repository Structure

```
Machine-Learning-CoProcessor/
│
├── rtl/
│   ├── bram.v
│   ├── pe.v
│   └── cnn.v
│
├── wrapper module/
│   └── custom_cnn_build.xpr
│
├── testbench/
│   └──cnn_tb.v
│
├── python/
│   ├── server.py
│   └── main.py
│
└── README.md
```

---

## Applications

- Edge AI
- Smart Surveillance
- Robotics
- Industrial Automation
- Embedded Vision
- IoT Devices
- Medical Diagnostics

---

## Authors

- Sai Krishnan S.
- Srikanth M.
- Srimath Sukumar


---

## License

This project was developed for academic and research purposes.
