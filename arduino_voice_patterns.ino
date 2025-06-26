/*
  Eye-Controlled Car with Voice Pattern System
  
  Different beep patterns represent different messages:
  - Eyes OPEN → Car RUNS (no sound)
  - Eyes CLOSED → Car STOPS + Voice Pattern
  
  Voice Patterns:
  - "Hey Wake Up!" = Short-Short-Long beeps
  - "Stay Alert!" = Long-Short-Long beeps  
  - "Driver!" = Three quick beeps
  - "Open Eyes!" = Rising tone pattern
*/

// Motor Driver L298N Pin Connections
const int motorPin1 = 2;     // IN1 on L298N
const int motorPin2 = 3;     // IN2 on L298N
const int enablePin = 9;     // ENA on L298N (PWM pin for speed control)

// Audio output
const int speakerPin = 8;    // Speaker/Buzzer pin

// LED indicators
const int runLED = 13;       // Built-in LED for running indication
const int statusLED = 12;    // External LED for status (optional)

// Motor control variables
int motorSpeed = 200;        // Motor speed (0-255)
bool isMotorRunning = false;
bool isVoiceActive = false;

// Serial communication variables
char receivedChar;
unsigned long lastSignalTime = 0;
const unsigned long TIMEOUT_MS = 3000;  // 3 seconds timeout

// Voice pattern control
unsigned long lastVoiceTime = 0;
const unsigned long VOICE_INTERVAL = 3000;  // Voice every 3 seconds
int currentVoicePattern = 0;

// Musical notes (frequencies in Hz)
#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_B4  494
#define NOTE_C5  523

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize motor control pins
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);
  
  // Initialize LED pins
  pinMode(runLED, OUTPUT);
  pinMode(statusLED, OUTPUT);
  
  // Initialize speaker pin
  pinMode(speakerPin, OUTPUT);
  
  // Initial state - motor off, voice off
  stopMotor();
  stopVoice();
  
  // Status indication
  digitalWrite(statusLED, HIGH);  // System ready
  
  Serial.println("=== Eye-Controlled Car with Voice Patterns ===");
  Serial.println("Commands:");
  Serial.println("'1' = Eyes OPEN → Car RUNS");
  Serial.println("'0' = Eyes CLOSED → Car STOPS + Voice Alert");
  Serial.println("System ready!");
  
  // Startup voice pattern
  playStartupVoice();
  
  Serial.println("🔊 Voice pattern system ready!");
}

void loop() {
  // Check for serial data
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    lastSignalTime = millis();
    
    // Process received command
    switch(receivedChar) {
      case '1':
        // Eyes OPEN - RUN the car, STOP voice
        startMotor();
        stopVoice();
        Serial.println("👁️ Eyes OPEN → Car RUNNING + Voice OFF");
        break;
        
      case '0':
        // Eyes CLOSED - STOP the car, START voice alerts
        stopMotor();
        startVoice();
        Serial.println("😴 Eyes CLOSED → Car STOPPED + Voice ON");
        break;
        
      default:
        // Invalid command
        Serial.print("⚠️ Unknown command: ");
        Serial.println(receivedChar);
        break;
    }
  }
  
  // Handle voice patterns when active
  if (isVoiceActive) {
    if (millis() - lastVoiceTime >= VOICE_INTERVAL) {
      playWakeUpVoicePattern();
      lastVoiceTime = millis();
    }
  }
  
  // Check for communication timeout
  if (millis() - lastSignalTime > TIMEOUT_MS && lastSignalTime != 0) {
    // If no signal for 3 seconds, stop motor and start voice for safety
    stopMotor();
    startVoice();
    Serial.println("⚠️ Communication timeout → Safety Voice Alert");
    lastSignalTime = 0;  // Reset to avoid repeated messages
  }
  
  // Small delay
  delay(50);
}

void startMotor() {
  if (!isMotorRunning) {
    // Run motor forward
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
    analogWrite(enablePin, motorSpeed);
    isMotorRunning = true;
    
    // Turn on running LED
    digitalWrite(runLED, HIGH);
    
    Serial.print("🚗 Motor STARTED at speed: ");
    Serial.println(motorSpeed);
  }
}

void stopMotor() {
  if (isMotorRunning) {
    // Stop motor
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    analogWrite(enablePin, 0);
    isMotorRunning = false;
    
    // Turn off running LED
    digitalWrite(runLED, LOW);
    
    Serial.println("🛑 Motor STOPPED");
  }
}

void startVoice() {
  if (!isVoiceActive) {
    isVoiceActive = true;
    lastVoiceTime = millis();
    Serial.println("🔊 Voice alerts STARTED");
    
    // Immediate first alert
    playWakeUpVoicePattern();
  }
}

void stopVoice() {
  if (isVoiceActive) {
    isVoiceActive = false;
    Serial.println("🔇 Voice alerts STOPPED");
  }
}

void playStartupVoice() {
  Serial.println("🎵 Playing: 'System Ready'");
  
  // "System Ready" pattern: C-E-G-C ascending
  tone(speakerPin, NOTE_C4, 200);
  delay(250);
  tone(speakerPin, NOTE_E4, 200);
  delay(250);
  tone(speakerPin, NOTE_G4, 200);
  delay(250);
  tone(speakerPin, NOTE_C5, 300);
  delay(400);
  noTone(speakerPin);
}

void playWakeUpVoicePattern() {
  // Cycle through different wake up patterns
  currentVoicePattern = (currentVoicePattern + 1) % 5;
  
  switch(currentVoicePattern) {
    case 0:
      playHeyWakeUpPattern();
      break;
    case 1:
      playStayAlertPattern();
      break;
    case 2:
      playDriverPattern();
      break;
    case 3:
      playOpenEyesPattern();
      break;
    case 4:
      playUrgentAlertPattern();
      break;
  }
}

void playHeyWakeUpPattern() {
  Serial.println("🗣️ Playing: 'Hey Wake Up!'");
  
  // "Hey Wake Up!" = Short-Short-Long pattern
  tone(speakerPin, NOTE_A4, 150);  // Hey
  delay(200);
  tone(speakerPin, NOTE_A4, 150);  // Wake  
  delay(200);
  tone(speakerPin, NOTE_C5, 400);  // Up!
  delay(500);
  noTone(speakerPin);
}

void playStayAlertPattern() {
  Serial.println("🗣️ Playing: 'Stay Alert!'");
  
  // "Stay Alert!" = Long-Short-Long pattern
  tone(speakerPin, NOTE_G4, 300);  // Stay
  delay(350);
  tone(speakerPin, NOTE_B4, 150);  // A-
  delay(200);
  tone(speakerPin, NOTE_G4, 300);  // lert!
  delay(500);
  noTone(speakerPin);
}

void playDriverPattern() {
  Serial.println("🗣️ Playing: 'Driver!'");
  
  // "Driver!" = Three quick ascending beeps
  tone(speakerPin, NOTE_C4, 100);
  delay(150);
  tone(speakerPin, NOTE_E4, 100);
  delay(150);
  tone(speakerPin, NOTE_G4, 200);
  delay(400);
  noTone(speakerPin);
}

void playOpenEyesPattern() {
  Serial.println("🗣️ Playing: 'Open Eyes!'");
  
  // "Open Eyes!" = Rising tone pattern
  for(int freq = NOTE_C4; freq <= NOTE_C5; freq += 50) {
    tone(speakerPin, freq, 50);
    delay(60);
  }
  tone(speakerPin, NOTE_C5, 200);
  delay(400);
  noTone(speakerPin);
}

void playUrgentAlertPattern() {
  Serial.println("🗣️ Playing: 'URGENT ALERT!'");
  
  // Urgent alert = Fast alternating high/low tones
  for(int i = 0; i < 6; i++) {
    tone(speakerPin, NOTE_C5, 100);
    delay(120);
    tone(speakerPin, NOTE_C4, 100);
    delay(120);
  }
  noTone(speakerPin);
}

// Function to test all voice patterns
void testAllVoicePatterns() {
  Serial.println("🧪 Testing all voice patterns...");
  
  playHeyWakeUpPattern();
  delay(1000);
  playStayAlertPattern();
  delay(1000);
  playDriverPattern();
  delay(1000);
  playOpenEyesPattern();
  delay(1000);
  playUrgentAlertPattern();
  delay(1000);
  
  Serial.println("✅ Voice pattern test complete!");
} 