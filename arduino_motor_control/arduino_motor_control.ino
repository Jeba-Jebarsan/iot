/*
  Sleepiness Detection Motor Control
  
  This Arduino sketch controls a DC motor using an L298N Motor Driver
  based on serial input from the Python sleepiness detection script.
  
  Hardware connections:
  - Arduino Uno
  - L298N Motor Driver
  - DC Motor
  - Optional: Buzzer for audio alert
  
  Serial Commands:
  - '0' = Eyes closed (sleepy) → Spin motor + buzzer
  - '1' = Eyes open (awake) → Stop motor + stop buzzer
  
  Created for Sleepiness Detection Project
*/

// Motor Driver L298N Pin Connections
const int motorPin1 = 2;     // IN1 on L298N
const int motorPin2 = 3;     // IN2 on L298N
const int enablePin = 9;     // ENA on L298N (PWM pin for speed control)

// Optional Buzzer Pin
const int buzzerPin = 8;     // Connect buzzer positive to pin 8

// Optional LED indicators
const int alertLED = 13;     // Built-in LED for alert indication
const int statusLED = 12;    // External LED for status (optional)

// Motor control variables
int motorSpeed = 200;        // Motor speed (0-255)
bool isMotorRunning = false;
bool isBuzzerOn = false;

// Serial communication variables
char receivedChar;
unsigned long lastSignalTime = 0;
const unsigned long TIMEOUT_MS = 5000;  // 5 seconds timeout

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize motor control pins
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);
  
  // Initialize buzzer and LED pins
  pinMode(buzzerPin, OUTPUT);
  pinMode(alertLED, OUTPUT);
  pinMode(statusLED, OUTPUT);
  
  // Initial state - motor off
  stopMotor();
  stopBuzzer();
  
  // Status indication
  digitalWrite(statusLED, HIGH);  // System ready
  
  Serial.println("Arduino Sleepiness Detection Motor Control Started");
  Serial.println("Waiting for commands from Python script...");
  Serial.println("Commands: '0' = Sleepy (motor ON), '1' = Awake (motor OFF)");
  
  // Brief startup indication
  for(int i = 0; i < 3; i++) {
    digitalWrite(alertLED, HIGH);
    delay(200);
    digitalWrite(alertLED, LOW);
    delay(200);
  }
}

void loop() {
  // Check for serial data
  if (Serial.available() > 0) {
    receivedChar = Serial.read();
    lastSignalTime = millis();
    
    // Process received command
    switch(receivedChar) {
      case '0':
        // Eyes closed - sleepy detected
        activateAlert();
        Serial.println("Alert: Sleepiness detected! Motor activated.");
        break;
        
      case '1':
        // Eyes open - awake
        deactivateAlert();
        Serial.println("Status: Person is awake. Motor stopped.");
        break;
        
      default:
        // Invalid command
        Serial.print("Warning: Unknown command received: ");
        Serial.println(receivedChar);
        break;
    }
  }
  
  // Check for communication timeout
  if (millis() - lastSignalTime > TIMEOUT_MS && lastSignalTime != 0) {
    // If no signal for 5 seconds, stop motor for safety
    deactivateAlert();
    Serial.println("Warning: Communication timeout. Motor stopped for safety.");
    lastSignalTime = 0;  // Reset to avoid repeated messages
  }
  
  // Small delay to prevent overwhelming the serial buffer
  delay(50);
}

void activateAlert() {
  // Start motor rotation
  startMotor();
  
  // Activate buzzer
  startBuzzer();
  
  // Turn on alert LED
  digitalWrite(alertLED, HIGH);
  
  // Status LED blinks rapidly when alert is active
  digitalWrite(statusLED, !digitalRead(statusLED));
}

void deactivateAlert() {
  // Stop motor
  stopMotor();
  
  // Stop buzzer
  stopBuzzer();
  
  // Turn off alert LED
  digitalWrite(alertLED, LOW);
  
  // Status LED steady on when system is normal
  digitalWrite(statusLED, HIGH);
}

void startMotor() {
  if (!isMotorRunning) {
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
    analogWrite(enablePin, motorSpeed);
    isMotorRunning = true;
    
    Serial.print("Motor started at speed: ");
    Serial.println(motorSpeed);
  }
}

void stopMotor() {
  if (isMotorRunning) {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    analogWrite(enablePin, 0);
    isMotorRunning = false;
    
    Serial.println("Motor stopped");
  }
}

void startBuzzer() {
  if (!isBuzzerOn) {
    // Create buzzer pattern for alert
    tone(buzzerPin, 1000, 500);  // 1000Hz tone for 500ms
    isBuzzerOn = true;
    
    Serial.println("Buzzer activated");
  }
}

void stopBuzzer() {
  if (isBuzzerOn) {
    noTone(buzzerPin);
    digitalWrite(buzzerPin, LOW);
    isBuzzerOn = false;
    
    Serial.println("Buzzer stopped");
  }
}

// Function to change motor speed (can be called via serial commands if needed)
void changeMotorSpeed(int newSpeed) {
  if (newSpeed >= 0 && newSpeed <= 255) {
    motorSpeed = newSpeed;
    if (isMotorRunning) {
      analogWrite(enablePin, motorSpeed);
    }
    Serial.print("Motor speed changed to: ");
    Serial.println(motorSpeed);
  } else {
    Serial.println("Error: Invalid motor speed. Use value between 0-255");
  }
}

// Function to reverse motor direction (for different alert patterns)
void reverseMotor() {
  if (isMotorRunning) {
    // Briefly stop motor
    stopMotor();
    delay(100);
    
    // Start in opposite direction
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);
    analogWrite(enablePin, motorSpeed);
    isMotorRunning = true;
    
    Serial.println("Motor direction reversed");
  }
}

// Test function - can be used for initial hardware testing
void testHardware() {
  Serial.println("Testing hardware components...");
  
  // Test LEDs
  digitalWrite(alertLED, HIGH);
  digitalWrite(statusLED, HIGH);
  delay(1000);
  digitalWrite(alertLED, LOW);
  digitalWrite(statusLED, LOW);
  
  // Test buzzer
  tone(buzzerPin, 800, 500);
  delay(600);
  
  // Test motor
  startMotor();
  delay(2000);
  stopMotor();
  delay(500);
  
  // Reverse direction test
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, HIGH);
  analogWrite(enablePin, motorSpeed);
  delay(2000);
  stopMotor();
  
  Serial.println("Hardware test completed");
} 