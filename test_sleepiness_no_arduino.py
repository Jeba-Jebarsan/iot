#!/usr/bin/env python3
"""
Test Sleepiness Detection WITHOUT Arduino
Perfect for testing the face/eye detection before connecting hardware
"""

import cv2
import numpy as np
import time

class SleepinessTestDetector:
    def __init__(self):
        # Detection parameters
        self.EYE_CLOSED_THRESHOLD = 20  # frames to consider sleepy
        
        # Counters
        self.eye_closed_counter = 0
        self.no_face_counter = 0
        self.total_frames = 0
        self.alert_count = 0
        
        # Load OpenCV cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Error: Could not open webcam")
            exit()
            
        print("🚨 Sleepiness Detection Test (No Arduino)")
        print("📝 Instructions:")
        print("   - Look at camera normally (eyes should be detected)")
        print("   - Close eyes for 3+ seconds to trigger alert")
        print("   - Press 'q' to quit")
        print("   - Press 'r' to reset counters")
        print()

    def detect_sleepiness(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            self.no_face_counter += 1
            self.eye_closed_counter = 0
            return False, "❌ No face detected", 0
        
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
        
        # Sleepiness logic
        if len(eyes) < 2:
            self.eye_closed_counter += 1
            
            if self.eye_closed_counter > self.EYE_CLOSED_THRESHOLD:
                self.alert_count += 1
                return True, f"🚨 DROWSINESS ALERT! ({self.eye_closed_counter})", len(eyes)
            else:
                return False, f"😴 Eyes possibly closed... ({self.eye_closed_counter})", len(eyes)
        else:
            self.eye_closed_counter = 0
            return False, f"👁️ Eyes open ({len(eyes)} eyes detected)", len(eyes)

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Could not read frame")
                    break
                
                self.total_frames += 1
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect sleepiness
                is_sleepy, status, eye_count = self.detect_sleepiness(frame)
                
                # Draw status information
                if is_sleepy:
                    # ALERT STATE - Red background
                    cv2.rectangle(frame, (0, 0), (frame.shape[1], 100), (0, 0, 255), -1)
                    cv2.putText(frame, "WAKE UP!", (10, 40),
                              cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                    cv2.putText(frame, "DROWSINESS DETECTED!", (10, 80),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    print(f"🚨 ALERT #{self.alert_count}: Drowsiness detected!")
                
                # Display status
                status_y = frame.shape[0] - 120 if is_sleepy else frame.shape[0] - 80
                cv2.putText(frame, status, (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Display statistics
                stats = [
                    f"Frame: {self.total_frames}",
                    f"Eyes: {eye_count}",
                    f"Alerts: {self.alert_count}",
                    f"No face: {self.no_face_counter}"
                ]
                
                for i, stat in enumerate(stats):
                    cv2.putText(frame, stat, (10, frame.shape[0] - 40 + i*15),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                # Instructions
                cv2.putText(frame, "Press 'q' to quit, 'r' to reset", (10, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Show frame
                cv2.imshow('Sleepiness Detection Test', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset counters
                    self.eye_closed_counter = 0
                    self.alert_count = 0
                    self.total_frames = 0
                    print("🔄 Counters reset!")
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        
        print("\n📊 Test Results:")
        print(f"   Total frames processed: {self.total_frames}")
        print(f"   Drowsiness alerts: {self.alert_count}")
        print(f"   Times no face detected: {self.no_face_counter}")
        print("✅ Test completed successfully!")

def main():
    print("🧪 === Sleepiness Detection Test (No Arduino Required) ===")
    print("This tests the computer vision part without hardware")
    print()
    
    try:
        detector = SleepinessTestDetector()
        detector.run()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 