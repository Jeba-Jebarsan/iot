#!/usr/bin/env python3
"""
Simplified Sleepiness Detection System (No dlib required)

This version uses OpenCV's built-in face detection instead of dlib
to avoid compilation issues on Windows.
"""

import cv2
import numpy as np
import serial
import time
import sys

class SimpleSleepinessDetector:
    def __init__(self, arduino_port='COM3', baud_rate=9600):
        # Detection parameters
        self.FACE_ABSENT_THRESHOLD = 30
        self.EYE_CLOSED_THRESHOLD = 20
        
        # Counters
        self.face_absent_counter = 0
        self.eye_closed_counter = 0
        self.no_face_counter = 0
        
        # Load OpenCV cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Initialize Arduino connection
        self.arduino = None
        self.setup_arduino(arduino_port, baud_rate)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            sys.exit()
            
        print("Simplified Sleepiness Detection System Started!")
        print("Press 'q' to quit")

    def setup_arduino(self, port, baud_rate):
        try:
            self.arduino = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)
            print(f"Arduino connected on {port}")
            self.send_to_arduino('1')
        except Exception as e:
            print(f"Warning: Could not connect to Arduino on {port}")
            print(f"Error: {e}")
            self.arduino = None

    def send_to_arduino(self, signal):
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(signal.encode())
                self.arduino.flush()
            except Exception as e:
                print(f"Error sending to Arduino: {e}")

    def detect_sleepiness(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            self.no_face_counter += 1
            self.eye_closed_counter = 0
            
            if self.no_face_counter > self.FACE_ABSENT_THRESHOLD:
                return False, "No face detected"
            else:
                return False, f"Searching for face... ({self.no_face_counter})"
        
        # Face detected
        self.no_face_counter = 0
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Extract face region for eye detection
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Detect eyes
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
        
        # Draw detected eyes
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        
        # Simple sleepiness logic
        if len(eyes) < 2:
            self.eye_closed_counter += 1
            
            if self.eye_closed_counter > self.EYE_CLOSED_THRESHOLD:
                return True, f"DROWSINESS ALERT! ({self.eye_closed_counter})"
            else:
                return False, f"Eyes possibly closed... ({self.eye_closed_counter})"
        else:
            self.eye_closed_counter = 0
            return False, f"Eyes open ({len(eyes)} eyes detected)"

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                is_sleepy, status = self.detect_sleepiness(frame)
                
                if is_sleepy:
                    self.send_to_arduino('0')
                    cv2.putText(frame, "WAKE UP!", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                else:
                    self.send_to_arduino('1')
                
                cv2.putText(frame, status, (10, frame.shape[0] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Sleepiness Detection', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.arduino:
            self.send_to_arduino('1')
            time.sleep(0.1)
            self.arduino.close()
            
        self.cap.release()
        cv2.destroyAllWindows()
        print("System shut down successfully!")

def main():
    print("=== Simplified Sleepiness Detection System ===")
    
    arduino_port = input("Enter Arduino COM port (e.g., COM3) or press Enter for COM3: ").strip()
    if not arduino_port:
        arduino_port = 'COM3'
    
    try:
        detector = SimpleSleepinessDetector(arduino_port=arduino_port)
        detector.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 