# Autonomous Security Robot Platform

Autonomous security robot with real-time SLAM mapping, web dashboard control, interactive expressions, and obstacle avoidance.
Built on Raspberry Pi 4 + ROS2 Humble + STM32F103 + ESP32.

## Project Overview

* Motor Controller: STM32F103C8T6 (Blue Pill)
* Main Computer: Raspberry Pi 4 Model B (4GB) running Ubuntu Server 22.04 LTS + ROS2 Humble
* Interactive Display: ESP32 driving 2x GC9A01 Round LCDs (Robot Eyes)
* LiDAR: RPLidar A1M8 (sllidar_ros2 + slam_toolbox)
* IMU: MPU6050 GY-521
* Camera: IMX219 (Raspberry Pi Camera v2)
* Web Dashboard: rosbridge + vanilla JS

## System Architecture
```text
┌─────────────────────────────────────────────────────┐
│                Raspberry Pi 4                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  slam_   │  │rosbridge │  │   cam_stream.py  │   │
│  │ toolbox  │  │  :9090   │  │   (MJPEG :8080)  │   │
│  └────┬─────┘  └────┬─────┘  └──────────────────┘   │
│       │ /map        │ WebSocket                     │
│  ┌────┴──────────────────────────────────────┐      │
│  │         ROS2 Humble (CycloneDDS)          │      │
│  │  /scan_filtered  /imu/data  /cmd_vel      │      │
│  └──┬─────────────┬──────────────────────────┘      │
│     │             │                                 │
│  ┌──┴──────┐  ┌───┴─────────┐                       │
│  │RPLidar  │  │  MPU6050    │  uart_bridge.py       │
│  │ A1M8    │  │  GY-521     │  GPIO UART -> STM32   │
│  └─────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────┘
            ↕ WebSocket ws://pi-ip:9090
┌─────────────────────────────────────────────────────┐
│               Web Browser (any device)              │
│  ┌────────────────────────────────────────────────┐ │
│  │  SLAM Map · Camera Feed · Joystick · D-pad     │ │
│  │          web/index.html (served by Pi)         │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
            ↕ UART (115200 baud, GPIO14/15)
┌─────────────────────────────────────────────────────┐
│                STM32F103C8T6                        │
│  Motor PWM · HC-SR04 Ultrasonic · AUTO navigation   │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│                ESP32 (Expression Module)            │
│  SPI Bus -> 2x GC9A01 Round LCDs (Interactive Eyes) │
└─────────────────────────────────────────────────────┘
```
## Repository Structure

* /docs: Setup guides, wiring diagrams, and motor shield datasheets.
* /hardware: 3D printed mechanical parts and KiCAD PCB schematics.
* /stm32: Low-level STM32 firmware for motor control and obstacle avoidance.
* /esp32: Firmware for LCD eyes rendering and animation control.
* /raspberry_pi: ROS2 workspace containing custom nodes for IMU processing and UART bridging.
* /web: Web dashboard interface and MJPEG camera streaming script.

## Hardware Integration & Wiring

ESP32 to GC9A01 Round LCDs (SPI)
* MOSI / SCLK: Shared SPI data and clock lines for both screens.
* CS1 / CS2: Independent Chip Select pins to control Left and Right eyes.
* DC / RST: Data/Command and Reset pins.

STM32 to Motor Driver (L298N / TB6612)
* PA0 (ENA) / PA1 (ENB): Motor PWM
* PA2 / PA3: Left motor direction
* PA4 / PA5: Right motor direction

Pi 4 to STM32 (UART)
* GPIO14 (TX, pin 8) -> RX (PA10 / Serial1)
* GPIO15 (RX, pin 10) -> TX (PA9 / Serial1)

Please refer to the /docs directory for complete wiring diagrams and system setup instructions.

## Quick Start

1. Clone the repository:
   git clone https://github.com/Cmplex7/Autonomous-Security-Robot.git

2. Flash STM32 Firmware: Open `stm32/robot_final.ino` in Arduino IDE with the STM32duino board package. Upload via Serial or ST-Link at 115200 baud.

3. Flash ESP32 Firmware: Upload the GC9A01 display code to the ESP32 module to initialize the screen animations.

4. Set Up Raspberry Pi 4: Follow the detailed setup guide in the `docs/` folder to install Ubuntu Server 22.04 LTS and ROS2 Humble.

5. Launch Workspace: Compile the ROS2 packages using `colcon build` and launch the bringup scripts.

## STM32 UART Command Protocol

Commands are sent as ASCII strings terminated with \n at 115200 baud:
* ON / BACK / LEFT / RIGHT: Basic directional movement
* UP_LEFT / UP_RIGHT / DOWN_LEFT / DOWN_RIGHT: Arced movement
* AUTO: Enable onboard ultrasonic obstacle avoidance
* OFF / MANUAL: Stop and exit AUTO mode

## Author
ThanhDat (CmpleX7)
