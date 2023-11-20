# Arduino

This project contains Arduino sketches and libraries for controlling a power supply, a pump, and includes a test sketch.

## Directory Structure

- `control_power_supply`: Contains the `control_power_supply.ino` sketch.
- `libraries/PowerSupply`: Includes the `PowerSupply` library with `.cpp` and `.h` files.
- `pump`: Contains the `pump.ino` sketch.
- `test`: Includes the `test.ino` sketch for testing purposes.

## Getting Started

### Requirements

- Arduino IDE
- Arduino hardware compatible with the sketches

### Setup Instructions

#### Installing the Arduino IDE

- **Windows/macOS/Linux:** 
  - Download the Arduino IDE from the [Arduino website](https://www.arduino.cc/en/software).
  - For Linux users, you can also search for installation instructions specific to your distribution. For example, search "install arduino on Ubuntu" or "install arduino on Gentoo."

#### Adding the PowerSupply Library

- In the Arduino IDE, go to `Sketch > Include Library > Add .ZIP Library...`. Despite the name, this option can be used to add libraries from a folder. Navigate to the `libraries/PowerSupply` folder in the downloaded project and select it.

#### Loading and Uploading a Sketch

1. Open the Arduino IDE.
2. Open the `.ino` file for the sketch you want to use (found in `control_power_supply`, `pump`, or `test` directories).
3. Connect your Arduino device to your computer using a USB cable.
4. In the Arduino IDE, go to `Tools > Board` and select your Arduino board model.
5. Go to `Tools > Port` and select the port your Arduino is connected to. It usually appears as `COM#` on Windows and `/dev/ttyUSB#` or `/dev/ttyACM#` on Linux and macOS.
6. Click the "Upload" button to compile and upload the sketch to your Arduino board.

#### Troubleshooting

- Ensure that your Arduino board is properly connected and that you have selected the correct board and port in the IDE.
- Linux users might need to adjust permissions to access the serial port. This often involves adding your user to a group like `dialout` or `uucp`.

## Contributing

Feel free to contribute to this project by submitting pull requests or opening issues for any bugs or feature suggestions.

---

Side note: this README was generated with the help of ChatGPT4.
