#!/usr/bin/env python3
"""
Eye Detection Analysis Tool
Shows exactly how the system detects open vs closed eyes
"""

import cv2
import numpy as np

class EyeDetectionAnalyzer:
    def __init__(self):
        # Load classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Detection parameters
        self.EYE_THRESHOLD = 2  # Minimum eyes needed to consider "open"
        
        # Statistics
        self.eye_history = []
        self.frame_count = 0
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Error: Could not open webcam")
            exit()
            
        print("👁️ Eye Detection Analyzer")
        print("📋 This will show you exactly how eye detection works")
        print("🎯 Instructions:")
        print("   - Look normally at camera")
        print("   - Slowly close your eyes and open them")
        print("   - Watch the eye count and detection rectangles")
        print("   - Press 'q' to quit, 'c' to clear history")
        print()

    def analyze_eyes(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return 0, "No face detected", None, None
        
        # Get largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        # Draw face rectangle (blue)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, f"Face: {w}x{h}", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Extract face region
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Detect eyes with different sensitivity levels
        eyes_normal = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
        eyes_sensitive = self.eye_cascade.detectMultiScale(roi_gray, 1.05, 3)
        eyes_less_sensitive = self.eye_cascade.detectMultiScale(roi_gray, 1.3, 7)
        
        # Draw detected eyes
        for i, (ex, ey, ew, eh) in enumerate(eyes_normal):
            # Green rectangle for detected eyes
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            cv2.putText(roi_color, f"E{i+1}", (ex, ey-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Determine eye status
        eye_count = len(eyes_normal)
        if eye_count >= 2:
            status = "👁️ EYES OPEN"
            color = (0, 255, 0)  # Green
        elif eye_count == 1:
            status = "😑 ONE EYE"
            color = (0, 255, 255)  # Yellow
        else:
            status = "😴 EYES CLOSED"
            color = (0, 0, 255)  # Red
        
        return eye_count, status, eyes_sensitive, eyes_less_sensitive

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                self.frame_count += 1
                frame = cv2.flip(frame, 1)
                
                # Analyze eyes
                eye_count, status, eyes_sens, eyes_less = self.analyze_eyes(frame)
                
                # Update history
                self.eye_history.append(eye_count)
                if len(self.eye_history) > 30:  # Keep last 30 frames
                    self.eye_history.pop(0)
                
                # Calculate statistics
                avg_eyes = sum(self.eye_history) / len(self.eye_history) if self.eye_history else 0
                recent_frames = self.eye_history[-10:] if len(self.eye_history) >= 10 else self.eye_history
                recent_avg = sum(recent_frames) / len(recent_frames) if recent_frames else 0
                
                # Draw main status
                status_color = (0, 255, 0) if eye_count >= 2 else (0, 0, 255)
                cv2.putText(frame, status, (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                
                # Draw detailed information
                info_lines = [
                    f"Frame: {self.frame_count}",
                    f"Eyes detected: {eye_count}",
                    f"Avg (30f): {avg_eyes:.1f}",
                    f"Recent (10f): {recent_avg:.1f}",
                    f"Sensitive: {len(eyes_sens) if eyes_sens is not None else 0}",
                    f"Less sens: {len(eyes_less) if eyes_less is not None else 0}"
                ]
                
                for i, line in enumerate(info_lines):
                    cv2.putText(frame, line, (10, 80 + i*25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Draw eye detection graph
                if len(self.eye_history) > 1:
                    self.draw_eye_graph(frame)
                
                # Draw threshold line
                cv2.putText(frame, f"Threshold: {self.EYE_THRESHOLD} eyes = OPEN", 
                           (10, frame.shape[0] - 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                # Instructions
                cv2.putText(frame, "Try: Open eyes -> Close eyes -> Open eyes", 
                           (10, frame.shape[0] - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                cv2.putText(frame, "Press 'q' to quit, 'c' to clear", 
                           (10, frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
                
                # Show frame
                cv2.imshow('Eye Detection Analyzer', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.eye_history.clear()
                    self.frame_count = 0
                    print("🔄 History cleared!")
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            self.cleanup()

    def draw_eye_graph(self, frame):
        """Draw a small graph showing eye detection history"""
        graph_x = frame.shape[1] - 200
        graph_y = 50
        graph_w = 180
        graph_h = 100
        
        # Draw graph background
        cv2.rectangle(frame, (graph_x, graph_y), (graph_x + graph_w, graph_y + graph_h), 
                     (50, 50, 50), -1)
        cv2.rectangle(frame, (graph_x, graph_y), (graph_x + graph_w, graph_y + graph_h), 
                     (255, 255, 255), 1)
        
        # Draw threshold line
        threshold_y = graph_y + graph_h - int((self.EYE_THRESHOLD / 4.0) * graph_h)
        cv2.line(frame, (graph_x, threshold_y), (graph_x + graph_w, threshold_y), 
                (0, 255, 255), 1)
        cv2.putText(frame, "Threshold", (graph_x + 5, threshold_y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
        
        # Draw eye count history
        if len(self.eye_history) > 1:
            points = []
            for i, count in enumerate(self.eye_history[-30:]):  # Last 30 points
                x = graph_x + int((i / 29) * graph_w) if len(self.eye_history) > 1 else graph_x
                y = graph_y + graph_h - int((count / 4.0) * graph_h)  # Scale to 0-4 eyes
                points.append((x, y))
            
            # Draw lines between points
            for i in range(len(points) - 1):
                color = (0, 255, 0) if self.eye_history[-(30-i)] >= 2 else (0, 0, 255)
                cv2.line(frame, points[i], points[i+1], color, 2)
        
        # Graph labels
        cv2.putText(frame, "Eye Count History", (graph_x, graph_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        
        print("\n📊 Eye Detection Analysis Results:")
        if self.eye_history:
            avg_eyes = sum(self.eye_history) / len(self.eye_history)
            print(f"   Average eyes detected: {avg_eyes:.1f}")
            print(f"   Total frames analyzed: {len(self.eye_history)}")
            
            # Count open vs closed frames
            open_frames = sum(1 for count in self.eye_history if count >= 2)
            closed_frames = len(self.eye_history) - open_frames
            print(f"   Eyes open frames: {open_frames} ({open_frames/len(self.eye_history)*100:.1f}%)")
            print(f"   Eyes closed frames: {closed_frames} ({closed_frames/len(self.eye_history)*100:.1f}%)")
        
        print("✅ Analysis completed!")

if __name__ == "__main__":
    analyzer = EyeDetectionAnalyzer()
    analyzer.run() 