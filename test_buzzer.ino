/*
  Simple Buzzer Test
  
  Tests the buzzer on pin 8
  - Beeps 3 times on startup
  - Then beeps every 2 seconds
*/

const int buzzerPin = 8;

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  
  Serial.println("🔊 Buzzer Test Starting...");
  
  // Test beeps on startup
  for(int i = 0; i < 3; i++) {
    Serial.print("Beep ");
    Serial.println(i + 1);
    
    digitalWrite(buzzerPin, HIGH);
    delay(200);
    digitalWrite(buzzerPin, LOW);
    delay(300);
  }
  
  Serial.println("✅ Startup beeps complete!");
  Serial.println("🔄 Continuous beeping every 2 seconds...");
}

void loop() {
  // Beep pattern: ON for 100ms, OFF for 1900ms (total 2 seconds)
  digitalWrite(buzzerPin, HIGH);
  delay(100);
  digitalWrite(buzzerPin, LOW);
  delay(1900);
  
  Serial.println("🔊 Beep!");
} 