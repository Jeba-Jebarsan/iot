#!/usr/bin/env python3
"""
Test Enhanced Eye-Controlled Car System

Quick test script to manually test all the new voice patterns
without needing webcam or eye detection.
"""

import serial
import time
import sys

def test_enhanced_arduino(port='COM4'):
    """Test all enhanced Arduino features"""
    
    print("🔊 === Enhanced Arduino System Test ===")
    print()
    
    try:
        # Connect to Arduino
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        print(f"✅ Connected to Arduino on {port}")
        print()
        
        # Test sequence
        tests = [
            ("🔊 Test: Both Alerts Mode", 'a'),
            ("🚗 Test: Start Car (Eyes Open)", '1'),
            ("⏰ Wait 2 seconds...", None),
            ("🛑 Test: Stop Car + Alerts (Eyes Closed)", '0'),
            ("⏰ Wait 5 seconds to hear alerts...", None),
            ("🔔 Test: Simple Beep Mode", 'b'),
            ("🛑 Test: Eyes Closed (Simple Beep)", '0'),
            ("⏰ Wait 3 seconds...", None),
            ("🎵 Test: Voice Pattern Mode", 'v'),
            ("🛑 Test: Eyes Closed (Voice Patterns)", '0'),
            ("⏰ Wait 5 seconds...", None),
            ("🧪 Test: All Voice Patterns", 't'),
            ("⏰ Wait 8 seconds for all patterns...", None),
            ("🚗 Test: Start Car (Stop Alerts)", '1'),
            ("✅ Test Complete!", None)
        ]
        
        for i, (description, command) in enumerate(tests, 1):
            print(f"{i:2d}. {description}")
            
            if command:
                arduino.write(command.encode())
                arduino.flush()
                
                # Read Arduino response
                time.sleep(0.1)
                while arduino.in_waiting:
                    response = arduino.readline().decode().strip()
                    if response:
                        print(f"    Arduino: {response}")
            
            # Wait times for different actions
            if "Wait 2 seconds" in description:
                time.sleep(2)
            elif "Wait 3 seconds" in description:
                time.sleep(3)
            elif "Wait 5 seconds" in description:
                time.sleep(5)
            elif "Wait 8 seconds" in description:
                time.sleep(8)
            else:
                time.sleep(0.5)
            
            print()
        
        # Final state - stop everything
        arduino.write('1'.encode())  # Start car (stops alerts)
        arduino.close()
        
        print("🎉 Enhanced system test completed!")
        print("🔊 You should have heard:")
        print("   - Both alerts (beeps + voice patterns)")
        print("   - Simple beeps only")  
        print("   - Voice patterns only")
        print("   - All 5 voice patterns in sequence")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("1. Arduino is connected")
        print("2. Enhanced code is uploaded")
        print("3. Serial Monitor is closed")

def manual_test(port='COM4'):
    """Manual testing mode"""
    
    print("🎮 === Manual Test Mode ===")
    print("Commands:")
    print("  1 = Eyes open (car start)")
    print("  0 = Eyes closed (car stop + alerts)")
    print("  b = Switch to beep mode")
    print("  v = Switch to voice pattern mode")
    print("  a = Switch to both alerts mode")
    print("  t = Test all voice patterns")
    print("  q = Quit")
    print()
    
    try:
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)
        print(f"✅ Connected to Arduino on {port}")
        print("Type commands (or 'q' to quit):")
        
        while True:
            command = input("> ").strip().lower()
            
            if command == 'q':
                break
            elif command in ['1', '0', 'b', 'v', 'a', 't']:
                arduino.write(command.encode())
                arduino.flush()
                
                # Read Arduino response
                time.sleep(0.1)
                while arduino.in_waiting:
                    response = arduino.readline().decode().strip()
                    if response:
                        print(f"Arduino: {response}")
            else:
                print("❌ Invalid command!")
        
        arduino.close()
        print("👋 Manual test ended")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🔧 Enhanced Arduino Test Script")
    print()
    
    # Get COM port
    port = input("Enter Arduino COM port (or press Enter for COM4): ").strip()
    if not port:
        port = 'COM4'
    
    print()
    print("Choose test mode:")
    print("1. Automatic Test (runs all tests)")
    print("2. Manual Test (you control)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        test_enhanced_arduino(port)
    elif choice == '2':
        manual_test(port)
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 