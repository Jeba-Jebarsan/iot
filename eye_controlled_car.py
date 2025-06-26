#!/usr/bin/env python3
"""
Eye-Controlled Car System

Controls a car based on eye state:
- Eyes OPEN → Car RUNS
- Eyes CLOSED → Car STOPS
"""

import cv2
import numpy as np
import serial
import time
import sys

class EyeControlledCar:
    def __init__(self, arduino_port='COM4', baud_rate=9600):
        # Detection parameters
        self.EYE_CLOSED_THRESHOLD = 15  # frames to consider eyes truly closed
        
        # Counters
        self.eye_closed_counter = 0
        self.no_face_counter = 0
        self.frame_count = 0
        
        # Car state
        self.car_running = False
        
        # Load OpenCV cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Initialize Arduino connection
        self.arduino = None
        self.setup_arduino(arduino_port, baud_rate)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Error: Could not open webcam")
            sys.exit()
            
        print("🚗 Eye-Controlled Car System Started!")
        print("👁️ Eyes OPEN = Car RUNS")
        print("😴 Eyes CLOSED = Car STOPS")
        print("Press 'q' to quit")

    def setup_arduino(self, port, baud_rate):
        try:
            self.arduino = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)
            print(f"✅ Arduino connected on {port}")
            self.send_to_arduino('0')  # Start with car stopped
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to Arduino on {port}")
            print(f"Error: {e}")
            self.arduino = None

    def send_to_arduino(self, signal):
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(signal.encode())
                self.arduino.flush()
            except Exception as e:
                print(f"❌ Error sending to Arduino: {e}")

    def detect_eye_state(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            self.no_face_counter += 1
            self.eye_closed_counter = 0
            return False, "❌ No driver detected - Car STOPPED", 0
        
        # Face detected - reset no face counter
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
        
        # Eye state logic
        if len(eyes) < 2:  # Less than 2 eyes detected
            self.eye_closed_counter += 1
            
            if self.eye_closed_counter > self.EYE_CLOSED_THRESHOLD:
                return False, f"😴 Eyes CLOSED - Car STOPPED ({self.eye_closed_counter})", len(eyes)
            else:
                return None, f"🤔 Checking... ({self.eye_closed_counter})", len(eyes)
        else:
            # 2+ eyes detected (eyes open)
            self.eye_closed_counter = 0
            return True, f"👁️ Eyes OPEN - Car RUNNING ({len(eyes)} eyes)", len(eyes)

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                self.frame_count += 1
                frame = cv2.flip(frame, 1)
                
                # Detect eye state
                eyes_open, status, eye_count = self.detect_eye_state(frame)
                
                # Control car based on eye state
                if eyes_open is True:  # Eyes definitely open
                    if not self.car_running:
                        self.send_to_arduino('1')  # Start car
                        self.car_running = True
                        print("🚗 CAR STARTED - Eyes are open!")
                    
                    # Green background when running
                    cv2.rectangle(frame, (0, 0), (frame.shape[1], 80), (0, 100, 0), -1)
                    cv2.putText(frame, "CAR RUNNING", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, "Eyes Open - Driving", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                elif eyes_open is False:  # Eyes definitely closed
                    if self.car_running:
                        self.send_to_arduino('0')  # Stop car
                        self.car_running = False
                        print("🛑 CAR STOPPED - Eyes are closed!")
                    
                    # Red background when stopped
                    cv2.rectangle(frame, (0, 0), (frame.shape[1], 80), (0, 0, 150), -1)
                    cv2.putText(frame, "CAR STOPPED", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, "Eyes Closed - Safety Stop", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display status
                status_y = 120 if eyes_open is not None else 100
                cv2.putText(frame, status, (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display car state
                car_state = "🚗 RUNNING" if self.car_running else "🛑 STOPPED"
                cv2.putText(frame, f"Car: {car_state}", (10, frame.shape[0] - 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Display frame info
                cv2.putText(frame, f"Frame: {self.frame_count}", (10, frame.shape[0] - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Instructions
                cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
                
                # Show frame
                cv2.imshow('Eye-Controlled Car', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        print("🧹 Cleaning up...")
        
        # Stop car before exit
        if self.arduino:
            self.send_to_arduino('0')  # Stop car
            time.sleep(0.1)
            self.arduino.close()
            
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ System shut down safely!")

def main():
    print("🚗 === Eye-Controlled Car System ===")
    print("Control your car with your eyes!")
    print()
    
    arduino_port = input("Enter Arduino COM port (e.g., COM4) or press Enter for COM4: ").strip()
    if not arduino_port:
        arduino_port = 'COM4'
    
    try:
        car = EyeControlledCar(arduino_port=arduino_port)
        car.run()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 