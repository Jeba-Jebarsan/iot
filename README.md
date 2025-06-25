# 🚨 Sleepiness Detection System

An AI-powered drowsiness detection system that uses computer vision to monitor eye movements and automatically activates an alert system when sleepiness is detected.

## 🎯 How It Works

1. **Computer Vision**: Uses OpenCV and dlib to detect faces and calculate Eye Aspect Ratio (EAR)
2. **Real-time Monitoring**: Continuously monitors your eyes through webcam
3. **Smart Detection**: When EAR falls below 0.21 (eyes closed), it detects drowsiness
4. **Arduino Integration**: Sends signals to Arduino to control physical alerts
5. **Immediate Response**: Activates motor and buzzer to wake you up

## 📋 Hardware Requirements

### Essential Components:
- **Arduino Uno** (or compatible board)
- **L298N Motor Driver Module**
- **DC Motor** (3-12V)
- **USB Cable** (Arduino to Computer)
- **Jumper Wires** (Male-to-Male and Male-to-Female)
- **Breadboard** (optional, for prototyping)
- **Power Supply** (9V battery or 12V adapter for motor)

### Optional Components:
- **Buzzer** (5V active buzzer)
- **LEDs** (for status indication)
- **220Ω Resistors** (for LEDs)

### Computer Requirements:
- **Webcam** (built-in or external)
- **Python 3.7+**
- **Windows/macOS/Linux**

## 🔌 Wiring Diagram

```
Arduino Uno → L298N Motor Driver
========================
Pin 2    → IN1
Pin 3    → IN2
Pin 9    → ENA (Enable A)
GND      → GND
5V       → VCC (Logic Power)

L298N → DC Motor
================
OUT1     → Motor Wire 1
OUT2     → Motor Wire 2

L298N → External Power
======================
12V      → External 9-12V Power Supply (+)
GND      → External Power Supply (-)

Optional: Arduino → Buzzer
==========================
Pin 8    → Buzzer (+)
GND      → Buzzer (-)

Optional: Arduino → LEDs
========================
Pin 12   → Status LED (+) via 220Ω resistor
Pin 13   → Alert LED (built-in)
GND      → LED (-)
```

### Detailed Wiring Instructions:

1. **L298N Motor Driver Connections:**
   ```
   Arduino Pin 2  → L298N IN1
   Arduino Pin 3  → L298N IN2
   Arduino Pin 9  → L298N ENA
   Arduino 5V     → L298N VCC
   Arduino GND    → L298N GND
   ```

2. **Motor Connections:**
   ```
   DC Motor Wire 1 → L298N OUT1
   DC Motor Wire 2 → L298N OUT2
   ```

3. **Power Supply:**
   ```
   9V Battery (+) → L298N 12V
   9V Battery (-) → L298N GND
   ```

4. **Optional Buzzer:**
   ```
   Arduino Pin 8 → Buzzer (+)
   Arduino GND   → Buzzer (-)
   ```

## 🛠️ Software Setup

### Step 1: Install Python Dependencies

```bash
# Install pip if not already installed
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Alternative: Install packages individually
pip install opencv-python dlib numpy scipy pyserial cmake
```

### Step 2: Download Face Landmarks Model

Download the dlib facial landmarks predictor:

1. **Option A: Direct Download**
   ```bash
   # Download the file (68.6 MB)
   curl -O http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   
   # Extract the file
   bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
   ```

2. **Option B: Manual Download**
   - Visit: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   - Download and extract to project folder
   - Ensure the file is named: `shape_predictor_68_face_landmarks.dat`

### Step 3: Arduino Setup

1. **Install Arduino IDE**
   - Download from: https://www.arduino.cc/en/software
   - Install and open Arduino IDE

2. **Connect Arduino**
   - Connect Arduino Uno to computer via USB
   - Select correct board: Tools → Board → Arduino Uno
   - Select correct port: Tools → Port → (your COM port)

3. **Upload Arduino Code**
   - Open `arduino_motor_control.ino` in Arduino IDE
   - Click "Upload" button
   - Wait for "Done uploading" message

### Step 4: Find Arduino COM Port

**Windows:**
1. Open Device Manager
2. Expand "Ports (COM & LPT)"
3. Look for "Arduino Uno (COM#)" - note the COM number

**macOS/Linux:**
```bash
# List available ports
ls /dev/tty.*
# Look for something like /dev/ttyUSB0 or /dev/ttyACM0
```

## 🚀 Usage Instructions

### Step 1: Hardware Setup
1. Wire all components according to the wiring diagram
2. Connect external power supply to L298N (9V battery recommended)
3. Ensure all connections are secure

### Step 2: Test Arduino Connection
1. Open Arduino IDE Serial Monitor (Tools → Serial Monitor)
2. Set baud rate to 9600
3. You should see startup messages
4. Test by typing '0' and '1' in the serial monitor

### Step 3: Run Python Script
```bash
# Navigate to project directory
cd /path/to/sleepiness-detection

# Run the detection script
python sleepiness_detection.py
```

### Step 4: Configure COM Port
- When prompted, enter your Arduino COM port (e.g., COM3)
- Or press Enter to use default COM3

### Step 5: Position Yourself
1. Sit 2-3 feet from webcam
2. Ensure good lighting on your face
3. Look directly at camera for initial detection

### Step 6: Test the System
1. Keep eyes open - motor should be OFF
2. Close eyes for 3+ seconds - motor should turn ON
3. Open eyes - motor should turn OFF immediately

## ⚙️ Configuration Options

### Adjusting Sensitivity

**In Python script (`sleepiness_detection.py`):**
```python
# Change EAR threshold (lower = more sensitive)
self.EAR_THRESHOLD = 0.21  # Default: 0.21

# Change consecutive frames needed to trigger alert
self.CONSECUTIVE_FRAMES = 20  # Default: 20 frames
```

**In Arduino code (`arduino_motor_control.ino`):**
```cpp
// Change motor speed (0-255)
int motorSpeed = 200;  // Default: 200

// Change timeout duration
const unsigned long TIMEOUT_MS = 5000;  // Default: 5 seconds
```

### Custom COM Port
```python
# Edit in main() function
arduino_port = 'COM5'  # Change to your port
```

## 📊 How Eye Aspect Ratio (EAR) Works

The system calculates EAR using facial landmarks:

```
EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)

Where p1, p2, p3, p4, p5, p6 are eye landmark points
```

- **EAR > 0.21**: Eyes are open
- **EAR < 0.21**: Eyes are closed (sleepy)
- **Consecutive frames**: Prevents false alarms from blinking

## 🔧 Troubleshooting

### Common Issues:

**1. "Could not open webcam"**
- Check if webcam is connected and working
- Close other applications using webcam
- Try changing camera index in code: `cv2.VideoCapture(1)`

**2. "Could not connect to Arduino"**
- Verify COM port number
- Ensure Arduino is connected via USB
- Check if Arduino IDE Serial Monitor is open (close it)
- Try different USB cable

**3. "No module named 'dlib'"**
- Install Visual Studio Build Tools (Windows)
- Install cmake: `pip install cmake`
- Reinstall dlib: `pip install dlib`

**4. Motor not spinning:**
- Check all wiring connections
- Verify external power supply is connected
- Test motor with Arduino IDE Serial Monitor
- Ensure L298N jumpers are in place

**5. "shape_predictor_68_face_landmarks.dat not found"**
- Download the file from dlib website
- Place in same directory as Python script
- Check filename is exactly correct

### Advanced Troubleshooting:

**Python Script Debug Mode:**
```python
# Add debug prints in process_frame function
print(f"EAR: {avg_ear:.3f}, Threshold: {self.EAR_THRESHOLD}")
print(f"Frame counter: {self.frame_counter}")
```

**Arduino Serial Debug:**
- Open Arduino IDE Serial Monitor
- Observe messages when running Python script
- Should see "Alert: Sleepiness detected!" when eyes closed

## 🎮 Testing & Calibration

### Initial Testing:
1. **Hardware Test**: Use Arduino's `testHardware()` function
2. **Software Test**: Run Python script with good lighting
3. **Integration Test**: Test complete system workflow

### Calibration Tips:
- **Lighting**: Ensure consistent, bright lighting on face
- **Distance**: Maintain 2-3 feet from webcam
- **Angle**: Face should be straight toward camera
- **Threshold**: Adjust EAR_THRESHOLD based on your eye shape

## 📈 Customization Ideas

### Enhanced Features:
- **Multiple Alert Types**: Add vibration motor, sound patterns
- **Data Logging**: Record sleepiness episodes with timestamps
- **Mobile Notifications**: Send alerts to smartphone
- **Machine Learning**: Train custom drowsiness model
- **Web Interface**: Create web dashboard for monitoring

### Hardware Upgrades:
- **Servo Motor**: For more precise movement patterns
- **RGB LEDs**: Color-coded alert levels
- **PIR Sensor**: Detect if person left the desk
- **IoT Integration**: ESP32 for wireless connectivity

## 📚 Code Structure

```
sleepiness-detection/
├── sleepiness_detection.py     # Main Python script
├── arduino_motor_control.ino   # Arduino sketch
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── shape_predictor_68_face_landmarks.dat  # Facial landmarks model
```

## 🤝 Contributing

Feel free to improve this project:
1. Fork the repository
2. Create feature branch
3. Submit pull request

## 📄 License

This project is open source. Use it for educational and personal projects.

## ⚠️ Safety Notice

- **Motor Safety**: Ensure motor is securely mounted
- **Power Supply**: Use appropriate voltage for your motor
- **Extended Use**: Take regular breaks from computer work
- **Medical Advice**: This is not a substitute for proper sleep

## 🎯 Next Steps

After getting the basic system working:
1. Experiment with different EAR thresholds
2. Add more sophisticated alert patterns
3. Implement data logging features
4. Consider adding machine learning improvements

---

**Happy coding! Stay awake and alert! 🚨👁️** 