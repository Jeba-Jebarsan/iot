#!/usr/bin/env python3
"""
Sleepiness Detection System Setup Script

This script helps set up the sleepiness detection project by:
1. Checking system requirements
2. Downloading required files
3. Testing hardware connections
4. Verifying installation

Run this script before running the main sleepiness detection system.
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import bz2
import shutil
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required. Please upgrade Python.")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_and_install_packages():
    """Check and install required Python packages"""
    print_header("Checking Python Packages")
    
    required_packages = [
        'opencv-python',
        'dlib',
        'numpy',
        'scipy',
        'pyserial',
        'cmake'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✅ OpenCV version: {cv2.__version__}")
            elif package == 'dlib':
                import dlib
                print(f"✅ dlib version: {dlib.version}")
            elif package == 'numpy':
                import numpy
                print(f"✅ NumPy version: {numpy.__version__}")
            elif package == 'scipy':
                import scipy
                print(f"✅ SciPy version: {scipy.__version__}")
            elif package == 'pyserial':
                import serial
                print(f"✅ PySerial version: {serial.__version__}")
            elif package == 'cmake':
                import cmake
                print(f"✅ CMake available")
        except ImportError:
            print(f"❌ {package} not found")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def download_face_landmarks():
    """Download the dlib facial landmarks predictor"""
    print_header("Downloading Facial Landmarks Model")
    
    model_file = "shape_predictor_68_face_landmarks.dat"
    
    if os.path.exists(model_file):
        print(f"✅ {model_file} already exists")
        return True
    
    print("📥 Downloading facial landmarks model (68.6 MB)...")
    print("This may take a few minutes depending on your internet connection.")
    
    url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    compressed_file = "shape_predictor_68_face_landmarks.dat.bz2"
    
    try:
        # Download the compressed file
        print("Downloading...")
        urllib.request.urlretrieve(url, compressed_file)
        print("✅ Download completed")
        
        # Extract the file
        print("Extracting...")
        with bz2.BZ2File(compressed_file, 'rb') as source:
            with open(model_file, 'wb') as target:
                shutil.copyfileobj(source, target)
        
        # Remove compressed file
        os.remove(compressed_file)
        print(f"✅ {model_file} extracted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        print("\nManual download instructions:")
        print(f"1. Visit: {url}")
        print(f"2. Download and extract to: {model_file}")
        return False

def test_webcam():
    """Test webcam functionality"""
    print_header("Testing Webcam")
    
    try:
        import cv2
        
        # Try to open webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Could not open webcam (index 0)")
            # Try index 1
            cap = cv2.VideoCapture(1)
            if not cap.isOpened():
                print("❌ Could not open webcam (index 1)")
                return False
            else:
                print("✅ Webcam found at index 1")
        else:
            print("✅ Webcam found at index 0")
        
        # Test frame capture
        ret, frame = cap.read()
        if ret:
            print(f"✅ Webcam resolution: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("❌ Could not capture frame from webcam")
            cap.release()
            return False
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Webcam test failed: {e}")
        return False

def find_arduino_ports():
    """Find available Arduino ports"""
    print_header("Scanning for Arduino")
    
    try:
        import serial.tools.list_ports
        
        ports = list(serial.tools.list_ports.comports())
        arduino_ports = []
        
        for port in ports:
            if 'arduino' in port.description.lower() or 'uno' in port.description.lower():
                arduino_ports.append(port.device)
                print(f"✅ Arduino found on: {port.device} - {port.description}")
            else:
                print(f"ℹ️  Available port: {port.device} - {port.description}")
        
        if not arduino_ports:
            print("❌ No Arduino detected")
            print("\nTroubleshooting:")
            print("1. Ensure Arduino is connected via USB")
            print("2. Install Arduino drivers if needed")
            print("3. Check Device Manager (Windows) for COM ports")
            return None
        
        return arduino_ports[0] if arduino_ports else None
        
    except Exception as e:
        print(f"❌ Port scanning failed: {e}")
        return None

def test_serial_connection(port):
    """Test serial connection to Arduino"""
    if not port:
        return False
    
    print(f"\n🔌 Testing connection to {port}...")
    
    try:
        import serial
        import time
        
        # Try to connect
        ser = serial.Serial(port, 9600, timeout=2)
        time.sleep(2)  # Wait for Arduino to initialize
        
        # Send test command
        ser.write(b'1')
        ser.flush()
        
        # Try to read response
        time.sleep(0.5)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode().strip()
            print(f"✅ Arduino responded: {response}")
        else:
            print("✅ Connection established (no response expected)")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Serial connection failed: {e}")
        return False

def create_test_script():
    """Create a simple test script"""
    print_header("Creating Test Scripts")
    
    test_script = """#!/usr/bin/env python3
# Quick test script for sleepiness detection components

import cv2
import dlib
import numpy as np

def test_face_detection():
    print("Testing face detection...")
    
    # Initialize detector and predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit test")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        
        for face in faces:
            # Draw face rectangle
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Get landmarks
            landmarks = predictor(gray, face)
            
            # Draw eye points
            for i in range(36, 48):  # Eye landmarks
                x = landmarks.part(i).x
                y = landmarks.part(i).y
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
        
        cv2.putText(frame, f"Faces detected: {len(faces)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Face Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Face detection test completed")

if __name__ == "__main__":
    test_face_detection()
"""
    
    with open("test_face_detection.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created test_face_detection.py")

def main():
    """Main setup function"""
    print("🚨 Sleepiness Detection System Setup")
    print("This script will help you set up your drowsiness detection system")
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Check and install packages
    if success and not check_and_install_packages():
        success = False
    
    # Download face landmarks model
    if success and not download_face_landmarks():
        success = False
    
    # Test webcam
    if success and not test_webcam():
        success = False
    
    # Find Arduino
    arduino_port = find_arduino_ports()
    if arduino_port:
        test_serial_connection(arduino_port)
    
    # Create test scripts
    create_test_script()
    
    # Final summary
    print_header("Setup Summary")
    
    if success:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Wire your Arduino according to the README")
        print("2. Upload arduino_motor_control.ino to your Arduino")
        print("3. Run: python test_face_detection.py")
        print("4. Run: python sleepiness_detection.py")
        
        if arduino_port:
            print(f"\n💡 Your Arduino was detected on: {arduino_port}")
    else:
        print("❌ Setup encountered issues")
        print("Please check the error messages above and resolve them")
        print("Refer to the README.md for troubleshooting help")

if __name__ == "__main__":
    main() 