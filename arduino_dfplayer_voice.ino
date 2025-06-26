/*
  Eye-Controlled Car with DFPlayer Mini Voice System
  
  Plays actual human voice MP3 files:
  - "Hey wake up!"
  - "Open your eyes!"
  - "Stay alert driver!"
  
  Hardware Requirements:
  - DFPlayer Mini MP3 Module
  - MicroSD Card with voice files
  - Speaker (8Ω 3W recommended)
*/

#include "SoftwareSerial.h"
#include "DFRobotDFPlayerMini.h"

// Motor Driver L298N Pin Connections
const int motorPin1 = 2;     // IN1 on L298N
const int motorPin2 = 3;     // IN2 on L298N
const int enablePin = 9;     // ENA on L298N

// DFPlayer Mini connections
const int dfPlayerRX = 10;   // Connect to DFPlayer TX
const int dfPlayerTX = 11;   // Connect to DFPlayer RX

// LED indicators
const int runLED = 13;       // Built-in LED
const int statusLED = 12;    // Status LED

// Create software serial for DFPlayer
SoftwareSerial mySoftwareSerial(dfPlayerRX, dfPlayerTX);
DFRobotDFPlayerMini myDFPlayer;

// Motor control variables
int motorSpeed = 200;
bool isMotorRunning = false;
bool isVoiceActive = false;

// Serial communication
char receivedChar;
unsigned long lastSignalTime = 0;
const unsigned long TIMEOUT_MS = 3000;

// Voice control
unsigned long lastVoiceTime = 0;
const unsigned long VOICE_INTERVAL = 4000;  // Voice every 4 seconds
int currentVoiceTrack = 1;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  mySoftwareSerial.begin(9600);
  
  // Initialize motor pins
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);
  
  // Initialize LED pins
  pinMode(runLED, OUTPUT);
  pinMode(statusLED, OUTPUT);
  
  Serial.println("=== Eye-Controlled Car with Voice System ===");
  Serial.println("Initializing DFPlayer Mini...");
  
  // Initialize DFPlayer
  if (!myDFPlayer.begin(mySoftwareSerial)) {
    Serial.println("❌ DFPlayer Mini initialization failed!");
    Serial.println("Check connections and SD card");
    while(true) {
      // Blink error pattern
      digitalWrite(statusLED, HIGH);
      delay(200);
      digitalWrite(statusLED, LOW);
      delay(200);
    }
  }
  
  Serial.println("✅ DFPlayer Mini initialized successfully");
  
  // Set volume (0-30)
  myDFPlayer.volume(25);
  delay(100);
  
  // Initial state
  stopMotor();
  stopVoice();
  digitalWrite(statusLED, HIGH);
  
  Serial.println("Voice files on SD card:");
  Serial.println("001.mp3 - 'Hey wake up!'");
  Serial.println("002.mp3 - 'Open your eyes!'");
  Serial.println("003.mp3 - 'Stay alert driver!'");
  Serial.println("004.mp3 - 'Safety first!'");
  Serial.println("005.mp3 - 'System ready!'");
  
  // Play startup message
  Serial.println("🔊 Playing startup message...");
  myDFPlayer.play(5);  // Play "System ready!"
  delay(2000);
  
  Serial.println("System ready for eye control!");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    lastSignalTime = millis();
    
    switch(receivedChar) {
      case '1':
        // Eyes OPEN - Start car, stop voice
        startMotor();
        stopVoice();
        Serial.println("👁️ Eyes OPEN → Car RUNNING");
        break;
        
      case '0':
        // Eyes CLOSED - Stop car, start voice alerts
        stopMotor();
        startVoice();
        Serial.println("😴 Eyes CLOSED → Car STOPPED + Voice Alert");
        break;
        
      case 't':
        // Test all voice files
        testAllVoiceFiles();
        break;
        
      default:
        Serial.print("⚠️ Unknown command: ");
        Serial.println(receivedChar);
        break;
    }
  }
  
  // Handle voice alerts
  if (isVoiceActive) {
    if (millis() - lastVoiceTime >= VOICE_INTERVAL) {
      playWakeUpVoice();
      lastVoiceTime = millis();
    }
  }
  
  // Communication timeout check
  if (millis() - lastSignalTime > TIMEOUT_MS && lastSignalTime != 0) {
    stopMotor();
    startVoice();
    Serial.println("⚠️ Communication timeout → Safety Alert");
    lastSignalTime = 0;
  }
  
  delay(50);
}

void startMotor() {
  if (!isMotorRunning) {
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
    analogWrite(enablePin, motorSpeed);
    isMotorRunning = true;
    digitalWrite(runLED, HIGH);
    
    Serial.println("🚗 Motor STARTED");
  }
}

void stopMotor() {
  if (isMotorRunning) {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    analogWrite(enablePin, 0);
    isMotorRunning = false;
    digitalWrite(runLED, LOW);
    
    Serial.println("🛑 Motor STOPPED");
  }
}

void startVoice() {
  if (!isVoiceActive) {
    isVoiceActive = true;
    lastVoiceTime = millis();
    Serial.println("🔊 Voice alerts STARTED");
    
    // Play immediate alert
    playWakeUpVoice();
  }
}

void stopVoice() {
  if (isVoiceActive) {
    isVoiceActive = false;
    myDFPlayer.stop();
    Serial.println("🔇 Voice alerts STOPPED");
  }
}

void playWakeUpVoice() {
  // Cycle through different voice messages
  currentVoiceTrack = (currentVoiceTrack % 4) + 1;  // Files 1-4
  
  String message;
  switch(currentVoiceTrack) {
    case 1:
      message = "Hey wake up!";
      break;
    case 2:
      message = "Open your eyes!";
      break;
    case 3:
      message = "Stay alert driver!";
      break;
    case 4:
      message = "Safety first!";
      break;
  }
  
  Serial.print("🗣️ Playing: ");
  Serial.println(message);
  
  myDFPlayer.play(currentVoiceTrack);
}

void testAllVoiceFiles() {
  Serial.println("🧪 Testing all voice files...");
  
  for(int i = 1; i <= 5; i++) {
    Serial.print("Playing file ");
    Serial.print(i);
    Serial.println(".mp3");
    
    myDFPlayer.play(i);
    delay(3000);  // Wait 3 seconds between files
  }
  
  Serial.println("✅ Voice test complete!");
}

void setVolume(int vol) {
  if(vol >= 0 && vol <= 30) {
    myDFPlayer.volume(vol);
    Serial.print("🔊 Volume set to: ");
    Serial.println(vol);
  }
} 