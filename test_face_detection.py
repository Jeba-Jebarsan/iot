#!/usr/bin/env python3
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
