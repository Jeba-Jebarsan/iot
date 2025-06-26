/*
  Eye-Controlled Car System with Buzzer Alert
  
  This Arduino sketch controls a DC motor based on eye state:
  - Eyes OPEN → Car RUNS (motor ON)
  - Eyes CLOSED → Car STOPS (motor OFF) + BEEP SOUND
  
  Serial Commands:
  - '0' = Eyes closed → STOP motor + BEEP
  - '1' = Eyes open → RUN motor + STOP BEEP
*/

// Motor Driver L298N Pin Connections
const int motorPin1 = 2;     // IN1 on L298N
const int motorPin2 = 3;     // IN2 on L298N
const int enablePin = 9;     // ENA on L298N (PWM pin for speed control)

// LED indicators
const int runLED = 13;       // Built-in LED for running indication
const int statusLED = 12;    // External LED for status (optional)

// Buzzer for alert sound
const int buzzerPin = 8;     // Buzzer pin for eye-closed alert

// Motor control variables
int motorSpeed = 200;        // Motor speed (0-255)
bool isMotorRunning = false;
bool isBuzzerActive = false;

// Serial communication variables
char receivedChar;
unsigned long lastSignalTime = 0;
const unsigned long TIMEOUT_MS = 3000;  // 3 seconds timeout

// Buzzer control variables
unsigned long lastBeepTime = 0;
const unsigned long BEEP_INTERVAL = 500;  // Beep every 500ms
bool beepState = false;

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
  
  // Initial state - motor off, buzzer off
  stopMotor();
  stopBuzzer();
  
  // Status indication
  digitalWrite(statusLED, HIGH);  // System ready
  
  Serial.println("=== Eye-Controlled Car System with Buzzer ===");
  Serial.println("Commands:");
  Serial.println("'1' = Eyes OPEN → Car RUNS");
  Serial.println("'0' = Eyes CLOSED → Car STOPS + BEEP");
  Serial.println("System ready!");
  
  // Brief startup indication with beep
  for(int i = 0; i < 3; i++) {
    digitalWrite(runLED, HIGH);
    digitalWrite(statusLED, HIGH);
    digitalWrite(buzzerPin, HIGH);
    delay(100);
    digitalWrite(runLED, LOW);
    digitalWrite(statusLED, LOW);
    digitalWrite(buzzerPin, LOW);
    delay(100);
  }
  digitalWrite(statusLED, HIGH);  // Keep status on
  
  Serial.println("🔊 Buzzer test complete!");
}

void loop() {
  // Check for serial data
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    lastSignalTime = millis();
    
    // Process received command
    switch(receivedChar) {
      case '1':
        // Eyes OPEN - RUN the car, STOP beeping
        startMotor();
        stopBuzzer();
        Serial.println("👁️ Eyes OPEN → Car RUNNING + Beep OFF");
        break;
        
      case '0':
        // Eyes CLOSED - STOP the car, START beeping
        stopMotor();
        startBuzzer();
        Serial.println("😴 Eyes CLOSED → Car STOPPED + Beep ON");
        break;
        
      default:
        // Invalid command
        Serial.print("⚠️ Unknown command: ");
        Serial.println(receivedChar);
        break;
    }
  }
  
  // Handle buzzer beeping pattern
  if (isBuzzerActive) {
    if (millis() - lastBeepTime >= BEEP_INTERVAL) {
      beepState = !beepState;
      digitalWrite(buzzerPin, beepState ? HIGH : LOW);
      lastBeepTime = millis();
    }
  }
  
  // Check for communication timeout
  if (millis() - lastSignalTime > TIMEOUT_MS && lastSignalTime != 0) {
    // If no signal for 3 seconds, stop motor and start beeping for safety
    stopMotor();
    startBuzzer();
    Serial.println("⚠️ Communication timeout → Car STOPPED + Safety BEEP");
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

void startBuzzer() {
  if (!isBuzzerActive) {
    isBuzzerActive = true;
    lastBeepTime = millis();
    beepState = true;
    digitalWrite(buzzerPin, HIGH);
    Serial.println("🔊 Buzzer STARTED - Eyes closed alert!");
  }
}

void stopBuzzer() {
  if (isBuzzerActive) {
    isBuzzerActive = false;
    beepState = false;
    digitalWrite(buzzerPin, LOW);
    Serial.println("🔇 Buzzer STOPPED - Eyes open!");
  }
}

// Function to change motor speed via serial (send 's' followed by speed value)
void changeMotorSpeed(int newSpeed) {
  if (newSpeed >= 0 && newSpeed <= 255) {
    motorSpeed = newSpeed;
    if (isMotorRunning) {
      analogWrite(enablePin, motorSpeed);
    }
    Serial.print("⚡ Speed changed to: ");
    Serial.println(motorSpeed);
  } else {
    Serial.println("❌ Invalid speed. Use 0-255");
  }
} 