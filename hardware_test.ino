/*
  Hardware Test for Sleepiness Detection System
  
  This sketch tests all hardware components independently:
  - Motor control via L298N
  - Buzzer
  - LEDs
  - Serial communication
  
  Use this to verify your wiring before running the main project.
*/

// Pin definitions (same as main project)
const int motorPin1 = 2;     // IN1 on L298N
const int motorPin2 = 3;     // IN2 on L298N
const int enablePin = 9;     // ENA on L298N
const int buzzerPin = 8;     // Buzzer
const int alertLED = 13;     // Built-in LED
const int statusLED = 12;    // External LED

void setup() {
  Serial.begin(9600);
  
  // Initialize all pins
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(alertLED, OUTPUT);
  pinMode(statusLED, OUTPUT);
  
  // Ensure everything is off initially
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  digitalWrite(buzzerPin, LOW);
  digitalWrite(alertLED, LOW);
  digitalWrite(statusLED, LOW);
  
  Serial.println("=================================");
  Serial.println("Hardware Test for Sleepiness Detection");
  Serial.println("=================================");
  Serial.println("Starting component tests...\n");
  
  delay(1000);
}

void loop() {
  testStatusLED();
  delay(1000);
  
  testAlertLED();
  delay(1000);
  
  testBuzzer();
  delay(1000);
  
  testMotor();
  delay(2000);
  
  testCombined();
  delay(3000);
  
  testSerialCommands();
  delay(5000);
}

void testStatusLED() {
  Serial.println("1. Testing Status LED (Pin 12)...");
  
  for(int i = 0; i < 3; i++) {
    digitalWrite(statusLED, HIGH);
    Serial.println("   Status LED ON");
    delay(500);
    digitalWrite(statusLED, LOW);
    Serial.println("   Status LED OFF");
    delay(500);
  }
  
  Serial.println("   ✅ Status LED test complete\n");
}

void testAlertLED() {
  Serial.println("2. Testing Alert LED (Pin 13 - Built-in)...");
  
  for(int i = 0; i < 3; i++) {
    digitalWrite(alertLED, HIGH);
    Serial.println("   Alert LED ON");
    delay(500);
    digitalWrite(alertLED, LOW);
    Serial.println("   Alert LED OFF");
    delay(500);
  }
  
  Serial.println("   ✅ Alert LED test complete\n");
}

void testBuzzer() {
  Serial.println("3. Testing Buzzer (Pin 8)...");
  
  // Test different tones
  Serial.println("   Playing tone 1000Hz for 500ms");
  tone(buzzerPin, 1000, 500);
  delay(700);
  
  Serial.println("   Playing tone 1500Hz for 300ms");
  tone(buzzerPin, 1500, 300);
  delay(500);
  
  Serial.println("   Playing tone 800Hz for 800ms");
  tone(buzzerPin, 800, 800);
  delay(1000);
  
  Serial.println("   ✅ Buzzer test complete\n");
}

void testMotor() {
  Serial.println("4. Testing DC Motor...");
  
  // Test forward direction
  Serial.println("   Motor Forward - Speed 150");
  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 150);
  delay(2000);
  
  // Stop motor
  Serial.println("   Motor Stop");
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  delay(500);
  
  // Test reverse direction
  Serial.println("   Motor Reverse - Speed 150");
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, HIGH);
  analogWrite(enablePin, 150);
  delay(2000);
  
  // Stop motor
  Serial.println("   Motor Stop");
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  delay(500);
  
  // Test different speeds
  Serial.println("   Testing different speeds...");
  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  
  for(int speed = 100; speed <= 255; speed += 50) {
    Serial.print("   Motor Speed: ");
    Serial.println(speed);
    analogWrite(enablePin, speed);
    delay(1000);
  }
  
  // Stop motor
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  
  Serial.println("   ✅ Motor test complete\n");
}

void testCombined() {
  Serial.println("5. Testing Combined Alert System...");
  
  Serial.println("   Activating full alert...");
  
  // Turn on all alert components
  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 200);
  
  tone(buzzerPin, 1000, 2000);
  
  digitalWrite(alertLED, HIGH);
  digitalWrite(statusLED, HIGH);
  
  delay(2000);
  
  // Turn off all components
  Serial.println("   Deactivating alert...");
  
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  
  noTone(buzzerPin);
  digitalWrite(buzzerPin, LOW);
  
  digitalWrite(alertLED, LOW);
  digitalWrite(statusLED, LOW);
  
  Serial.println("   ✅ Combined test complete\n");
}

void testSerialCommands() {
  Serial.println("6. Testing Serial Commands...");
  Serial.println("   Send '0' for alert ON, '1' for alert OFF");
  Serial.println("   Send 't' to run all tests again");
  Serial.println("   Waiting for commands for 5 seconds...\n");
  
  unsigned long startTime = millis();
  
  while(millis() - startTime < 5000) {
    if(Serial.available() > 0) {
      char command = Serial.read();
      
      switch(command) {
        case '0':
          Serial.println("   Command '0' received - Alert ON");
          activateAlert();
          delay(1000);
          deactivateAlert();
          break;
          
        case '1':
          Serial.println("   Command '1' received - Alert OFF");
          deactivateAlert();
          break;
          
        case 't':
          Serial.println("   Command 't' received - Restarting tests");
          return;
          
        default:
          Serial.print("   Unknown command: ");
          Serial.println(command);
          break;
      }
    }
    delay(100);
  }
  
  Serial.println("   ✅ Serial command test complete\n");
}

void activateAlert() {
  digitalWrite(motorPin1, HIGH);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 200);
  
  tone(buzzerPin, 1000, 500);
  
  digitalWrite(alertLED, HIGH);
  digitalWrite(statusLED, HIGH);
}

void deactivateAlert() {
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);
  analogWrite(enablePin, 0);
  
  noTone(buzzerPin);
  digitalWrite(buzzerPin, LOW);
  
  digitalWrite(alertLED, LOW);
  digitalWrite(statusLED, HIGH);  // Keep status LED on when normal
} 