import cv2
import dlib
import numpy as np
import serial
import time
from scipy.spatial import distance
import threading
import sys

class SleepinessDetector:
    def __init__(self, arduino_port='COM3', baud_rate=9600):
        """
        Initialize the sleepiness detector
        
        Args:
            arduino_port (str): The COM port where Arduino is connected (change as needed)
            baud_rate (int): Serial communication baud rate
        """
        # Eye Aspect Ratio threshold
        self.EAR_THRESHOLD = 0.21
        self.CONSECUTIVE_FRAMES = 20  # Number of consecutive frames below threshold to trigger alert
        
        # Initialize counters
        self.frame_counter = 0
        self.sleepy_counter = 0
        
        # Initialize face detector and shape predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        
        # Define eye landmarks indices
        self.LEFT_EYE_POINTS = list(range(42, 48))
        self.RIGHT_EYE_POINTS = list(range(36, 42))
        
        # Initialize Arduino connection
        self.arduino = None
        self.setup_arduino(arduino_port, baud_rate)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            sys.exit()
            
        print("Sleepiness Detection System Started!")
        print(f"EAR Threshold: {self.EAR_THRESHOLD}")
        print("Press 'q' to quit")

    def setup_arduino(self, port, baud_rate):
        """Setup Arduino serial connection"""
        try:
            self.arduino = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            print(f"Arduino connected on {port}")
            # Send initial signal
            self.send_to_arduino('1')  # Eyes open initially
        except Exception as e:
            print(f"Warning: Could not connect to Arduino on {port}")
            print(f"Error: {e}")
            print("Continuing without Arduino connection...")
            self.arduino = None

    def send_to_arduino(self, signal):
        """Send signal to Arduino"""
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(signal.encode())
                self.arduino.flush()
            except Exception as e:
                print(f"Error sending to Arduino: {e}")

    def calculate_ear(self, eye_points):
        """
        Calculate Eye Aspect Ratio (EAR)
        
        Args:
            eye_points: Array of eye landmark coordinates
            
        Returns:
            float: Eye Aspect Ratio value
        """
        # Vertical eye landmarks
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        
        # Horizontal eye landmark
        C = distance.euclidean(eye_points[0], eye_points[3])
        
        # Calculate EAR
        ear = (A + B) / (2.0 * C)
        return ear

    def extract_eye_points(self, shape, eye_indices):
        """Extract eye coordinates from facial landmarks"""
        points = []
        for i in eye_indices:
            x = shape.part(i).x
            y = shape.part(i).y
            points.append((x, y))
        return np.array(points)

    def draw_eye_contour(self, frame, eye_points):
        """Draw eye contour on frame"""
        hull = cv2.convexHull(eye_points)
        cv2.drawContours(frame, [hull], -1, (0, 255, 0), 1)

    def process_frame(self, frame):
        """Process single frame for sleepiness detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        for face in faces:
            # Get facial landmarks
            landmarks = self.predictor(gray, face)
            
            # Extract eye coordinates
            left_eye = self.extract_eye_points(landmarks, self.LEFT_EYE_POINTS)
            right_eye = self.extract_eye_points(landmarks, self.RIGHT_EYE_POINTS)
            
            # Calculate EAR for both eyes
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            
            # Average EAR
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Draw eye contours
            self.draw_eye_contour(frame, left_eye)
            self.draw_eye_contour(frame, right_eye)
            
            # Check if eyes are closed
            if avg_ear < self.EAR_THRESHOLD:
                self.frame_counter += 1
                
                if self.frame_counter >= self.CONSECUTIVE_FRAMES:
                    self.sleepy_counter += 1
                    # Send signal to Arduino - eyes closed (sleepy)
                    self.send_to_arduino('0')
                    
                    # Draw alert on frame
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "WAKE UP!", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                self.frame_counter = 0
                # Send signal to Arduino - eyes open
                self.send_to_arduino('1')
            
            # Display EAR value and status
            cv2.putText(frame, f"EAR: {avg_ear:.3f}", (10, frame.shape[0] - 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Threshold: {self.EAR_THRESHOLD}", (10, frame.shape[0] - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw face rectangle
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        return frame

    def run(self):
        """Main detection loop"""
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display frame
                cv2.imshow('Sleepiness Detection System', processed_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        
        # Send final signal to Arduino
        if self.arduino:
            self.send_to_arduino('1')  # Turn off motor
            time.sleep(0.1)
            self.arduino.close()
            
        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()
        print("System shut down successfully!")

def main():
    """Main function"""
    print("=== Sleepiness Detection System ===")
    print("Make sure you have:")
    print("1. Arduino connected and programmed")
    print("2. Webcam connected")
    print("3. shape_predictor_68_face_landmarks.dat file in the same directory")
    print("4. Good lighting for face detection")
    print()
    
    # You may need to change the COM port based on your system
    # Check Device Manager on Windows to find the correct port
    arduino_port = input("Enter Arduino COM port (e.g., COM3) or press Enter for COM3: ").strip()
    if not arduino_port:
        arduino_port = 'COM3'
    
    try:
        detector = SleepinessDetector(arduino_port=arduino_port)
        detector.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure all dependencies are installed and hardware is connected properly")

if __name__ == "__main__":
    main() 