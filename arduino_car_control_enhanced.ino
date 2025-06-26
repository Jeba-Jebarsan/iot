/*
  Enhanced Eye-Controlled Car System
  
  Combines your current system with voice patterns:
  - Eyes OPEN → Car RUNS (no sound)
  - Eyes CLOSED → Car STOPS + Voice Patterns + Buzzer
  
  Features:
  - Motor control (existing)
  - Simple buzzer beeps (existing) 
  - Musical voice patterns (NEW!)
  - LED indicators (existing)
*/

// Motor Driver L298N Pin Connections
const int motorPin1 = 2;     // IN1 on L298N
const int motorPin2 = 3;     // IN2 on L298N
const int enablePin = 9;     // ENA on L298N (PWM pin for speed control)

// Audio output
const int buzzerPin = 8;     // Buzzer/Speaker pin for both beeps and patterns

// LED indicators
const int runLED = 13;       // Built-in LED for running indication
const int statusLED = 12;    // External LED for status (optional)

// Motor control variables
int motorSpeed = 200;        // Motor speed (0-255)
bool isMotorRunning = false;
bool isBuzzerActive = false;
bool isVoiceActive = false;

// Serial communication variables
char receivedChar;
unsigned long lastSignalTime = 0;
const unsigned long TIMEOUT_MS = 3000;  // 3 seconds timeout

// Buzzer control variables (simple beeps)
unsigned long lastBeepTime = 0;
const unsigned long BEEP_INTERVAL = 500;  // Simple beep every 500ms
bool beepState = false;

// Voice pattern control (musical patterns)
unsigned long lastVoiceTime = 0;
const unsigned long VOICE_INTERVAL = 3000;  // Voice pattern every 3 seconds
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

// Alert mode selection
enum AlertMode {
  SIMPLE_BEEP,    // Just beeping
  VOICE_PATTERNS, // Musical voice patterns
  BOTH_ALERTS     // Both beeping and voice patterns
};

AlertMode currentAlertMode = BOTH_ALERTS;  // Default: use both

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
  
  // Initialize buzzer pin
  pinMode(buzzerPin, OUTPUT);
  
  // Initial state - motor off, all alerts off
  stopMotor();
  stopAllAlerts();
  
  // Status indication
  digitalWrite(statusLED, HIGH);  // System ready
  digitalWrite(runLED, HIGH);     // Alert LED ON initially (car stopped)
  
  Serial.println("=== Enhanced Eye-Controlled Car System ===");
  Serial.println("Commands:");
  Serial.println("'1' = Eyes OPEN → Car RUNS");
  Serial.println("'0' = Eyes CLOSED → Car STOPS + Alerts");
  Serial.println("'b' = Switch to Simple Beep mode");
  Serial.println("'v' = Switch to Voice Pattern mode");
  Serial.println("'a' = Switch to Both Alerts mode");
  Serial.println("'t' = Test all voice patterns");
  Serial.println("System ready!");
  
  // Startup sequence with voice pattern
  playStartupVoice();
  
  Serial.println("🔊 Enhanced alert system ready!");
  Serial.print("Current mode: ");
  printCurrentMode();
}

void loop() {
  // Check for serial data
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    lastSignalTime = millis();
    
    // Process received command
    switch(receivedChar) {
      case '1':
        // Eyes OPEN - RUN the car, STOP all alerts
        startMotor();
        stopAllAlerts();
        Serial.println("👁️ Eyes OPEN → Car RUNNING + Alerts OFF");
        break;
        
      case '0':
        // Eyes CLOSED - STOP the car, START alerts
        stopMotor();
        startAlerts();
        Serial.println("😴 Eyes CLOSED → Car STOPPED + Alerts ON");
        break;
        
      case 'b':
        // Switch to simple beep mode
        currentAlertMode = SIMPLE_BEEP;
        Serial.println("🔔 Switched to: Simple Beep mode");
        break;
        
      case 'v':
        // Switch to voice pattern mode
        currentAlertMode = VOICE_PATTERNS;
        Serial.println("🎵 Switched to: Voice Pattern mode");
        break;
        
      case 'a':
        // Switch to both alerts mode
        currentAlertMode = BOTH_ALERTS;
        Serial.println("🔊 Switched to: Both Alerts mode");
        break;
        
      case 't':
        // Test all voice patterns
        testAllVoicePatterns();
        break;
        
      default:
        // Invalid command
        Serial.print("⚠️ Unknown command: ");
        Serial.println(receivedChar);
        break;
    }
  }
  
  // Handle active alerts based on current mode
  if (isBuzzerActive || isVoiceActive) {
    handleAlerts();
  }
  
  // Check for communication timeout
  if (millis() - lastSignalTime > TIMEOUT_MS && lastSignalTime != 0) {
    // If no signal for 3 seconds, stop motor and start alerts for safety
    stopMotor();
    startAlerts();
    Serial.println("⚠️ Communication timeout → Safety Alerts");
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
    
    // Turn OFF running LED when car runs (normal state)
    digitalWrite(runLED, LOW);
    
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
    
    // Turn ON LED when motor stops (alert state)
    digitalWrite(runLED, HIGH);
    
    Serial.println("🛑 Motor STOPPED");
  }
}

void startAlerts() {
  switch(currentAlertMode) {
    case SIMPLE_BEEP:
      startSimpleBeep();
      break;
    case VOICE_PATTERNS:
      startVoicePatterns();
      break;
    case BOTH_ALERTS:
      startSimpleBeep();
      startVoicePatterns();
      break;
  }
}

void stopAllAlerts() {
  stopSimpleBeep();
  stopVoicePatterns();
}

void startSimpleBeep() {
  if (!isBuzzerActive) {
    isBuzzerActive = true;
    lastBeepTime = millis();
    beepState = true;
    digitalWrite(buzzerPin, HIGH);
    Serial.println("🔔 Simple beep STARTED");
  }
}

void stopSimpleBeep() {
  if (isBuzzerActive) {
    isBuzzerActive = false;
    beepState = false;
    digitalWrite(buzzerPin, LOW);
    Serial.println("🔇 Simple beep STOPPED");
  }
}

void startVoicePatterns() {
  if (!isVoiceActive) {
    isVoiceActive = true;
    lastVoiceTime = millis();
    Serial.println("🎵 Voice patterns STARTED");
    
    // Play immediate voice pattern
    playWakeUpVoicePattern();
  }
}

void stopVoicePatterns() {
  if (isVoiceActive) {
    isVoiceActive = false;
    Serial.println("🎵 Voice patterns STOPPED");
  }
}

void handleAlerts() {
  // Handle simple beeping pattern
  if (isBuzzerActive && currentAlertMode != VOICE_PATTERNS) {
    if (millis() - lastBeepTime >= BEEP_INTERVAL) {
      beepState = !beepState;
      // Only do simple beep if not playing voice pattern
      if (!isPlayingVoicePattern()) {
        digitalWrite(buzzerPin, beepState ? HIGH : LOW);
      }
      lastBeepTime = millis();
    }
  }
  
  // Handle voice patterns
  if (isVoiceActive) {
    if (millis() - lastVoiceTime >= VOICE_INTERVAL) {
      playWakeUpVoicePattern();
      lastVoiceTime = millis();
    }
  }
}

bool isPlayingVoicePattern() {
  // Simple check - assume voice pattern is playing for 1 second after trigger
  return (isVoiceActive && (millis() - lastVoiceTime < 1000));
}

void playStartupVoice() {
  Serial.println("🎵 Playing: 'System Ready'");
  
  // "System Ready" pattern: C-E-G-C ascending
  tone(buzzerPin, NOTE_C4, 200);
  delay(250);
  tone(buzzerPin, NOTE_E4, 200);
  delay(250);
  tone(buzzerPin, NOTE_G4, 200);
  delay(250);
  tone(buzzerPin, NOTE_C5, 300);
  delay(400);
  noTone(buzzerPin);
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
  tone(buzzerPin, NOTE_A4, 150);  // Hey
  delay(200);
  tone(buzzerPin, NOTE_A4, 150);  // Wake  
  delay(200);
  tone(buzzerPin, NOTE_C5, 400);  // Up!
  delay(500);
  noTone(buzzerPin);
}

void playStayAlertPattern() {
  Serial.println("🗣️ Playing: 'Stay Alert!'");
  
  // "Stay Alert!" = Long-Short-Long pattern
  tone(buzzerPin, NOTE_G4, 300);  // Stay
  delay(350);
  tone(buzzerPin, NOTE_B4, 150);  // A-
  delay(200);
  tone(buzzerPin, NOTE_G4, 300);  // lert!
  delay(500);
  noTone(buzzerPin);
}

void playDriverPattern() {
  Serial.println("🗣️ Playing: 'Driver!'");
  
  // "Driver!" = Three quick ascending beeps
  tone(buzzerPin, NOTE_C4, 100);
  delay(150);
  tone(buzzerPin, NOTE_E4, 100);
  delay(150);
  tone(buzzerPin, NOTE_G4, 200);
  delay(400);
  noTone(buzzerPin);
}

void playOpenEyesPattern() {
  Serial.println("🗣️ Playing: 'Open Eyes!'");
  
  // "Open Eyes!" = Rising tone pattern
  for(int freq = NOTE_C4; freq <= NOTE_C5; freq += 50) {
    tone(buzzerPin, freq, 50);
    delay(60);
  }
  tone(buzzerPin, NOTE_C5, 200);
  delay(400);
  noTone(buzzerPin);
}

void playUrgentAlertPattern() {
  Serial.println("🗣️ Playing: 'URGENT ALERT!'");
  
  // Urgent alert = Fast alternating high/low tones
  for(int i = 0; i < 6; i++) {
    tone(buzzerPin, NOTE_C5, 100);
    delay(120);
    tone(buzzerPin, NOTE_C4, 100);
    delay(120);
  }
  noTone(buzzerPin);
}

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

void printCurrentMode() {
  switch(currentAlertMode) {
    case SIMPLE_BEEP:
      Serial.println("Simple Beep only");
      break;
    case VOICE_PATTERNS:
      Serial.println("Voice Patterns only");
      break;
    case BOTH_ALERTS:
      Serial.println("Both Beep + Voice Patterns");
      break;
  }
} 