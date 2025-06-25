#!/usr/bin/env python3
"""
Simple webcam test - No Arduino needed
"""

import cv2
import sys

def test_webcam():
    print("🎥 Testing webcam...")
    print("This will test your camera WITHOUT Arduino")
    print("Press 'q' to quit")
    
    # Try different camera indices
    for camera_index in [0, 1, 2]:
        print(f"\n🔍 Trying camera index {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            print(f"✅ Camera found at index {camera_index}")
            
            # Test frame capture
            ret, frame = cap.read()
            if ret:
                print(f"✅ Frame captured successfully")
                print(f"📐 Resolution: {frame.shape[1]}x{frame.shape[0]}")
                
                # Show video feed
                print("🎬 Starting video feed... Press 'q' to quit")
                
                frame_count = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        print(f"❌ Failed to capture frame {frame_count}")
                        break
                    
                    frame_count += 1
                    
                    # Flip for mirror effect
                    frame = cv2.flip(frame, 1)
                    
                    # Add text overlay
                    cv2.putText(frame, f"Webcam Test - Frame {frame_count}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Show frame
                    cv2.imshow('Webcam Test', frame)
                    
                    # Check for quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                print("✅ Webcam test completed successfully!")
                return True
            else:
                print(f"❌ Cannot capture frames from camera {camera_index}")
                cap.release()
        else:
            print(f"❌ Cannot open camera {camera_index}")
    
    print("❌ No working camera found!")
    print("\n🔧 Troubleshooting:")
    print("1. Check if camera is connected")
    print("2. Close other apps using camera (Teams, Zoom, etc.)")
    print("3. Try external USB camera if built-in doesn't work")
    return False

if __name__ == "__main__":
    test_webcam() 