#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <SharpIR.h>

#define BUTTON_PIN 1

#define RED_PIN 2
#define GREEN_PIN 3
#define BLUE_PIN 4

#define SERVO_PIN 5

#define BUZER_PIN 7

#define USECHO_PIN 8
#define USTRIG_PIN 6

#define RST_PIN 9
#define SS_PIN 10

#define ENTRY_SENSOR A1
#define EXIT_SENSOR A2

#define ENTRY_THRESHOLD 200 // adjust this value for your sensor
#define EXIT_THRESHOLD 200 // adjust this value for your sensor

#define DOOR_HEIGHT 185

byte readCard[4];
String MasterTag = "C3E86097";
String ExitTag = "A6D715E";
String tagID = "";
bool personInside = false;
int personCount = 0;
String serialInput = "";
String serialOutput = "";
String entryExitStatus = "";
bool cardScanned = false;
bool waitingForCard = false;
bool waitingForInput = false;
float duration, distance, tempDistance, height, weight, bmi;
bool alarmMode = false;

MFRC522 mfrc522(SS_PIN, RST_PIN);  
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);
Servo doorServo;

void offLight() {
  digitalWrite(RED_PIN, LOW);
  digitalWrite(GREEN_PIN, LOW);
  digitalWrite(BLUE_PIN, LOW);
}

void redLight() {
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, LOW);
  digitalWrite(BLUE_PIN, LOW);
}

void yellowLight() {
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, LOW);
}

void greenLight() {
  digitalWrite(RED_PIN, LOW);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, LOW);
}

void blueLight() {
  digitalWrite(RED_PIN, LOW);
  digitalWrite(GREEN_PIN, LOW);
  digitalWrite(BLUE_PIN, HIGH);
}

void alarm() {
  tone(BUZER_PIN, 262, 500);
}

void noStopDelay(int interval) {
  long startDelayTime = millis();
  while (true) {
    if (millis() - startDelayTime >= interval) {
      return;
    }
  }
}

bool waitForRemoteApprove() {
  long startTime = millis();
  while (Serial.available() == 0) {
    if (!waitingForInput) {
      Serial.println("Wait for approval..");
      lcd.clear();
      lcd.print("Wait for approval..");
      waitingForInput = true;
    }
    serialInput = Serial.readString();
    if (serialInput != "") {
      Serial.print(serialInput);
      bool status = (serialInput == "Approved");
      if (!status) {
        denyAccess();
      }
      waitingForInput = false;
      return status; 
    }
    if (millis() - startTime >= 5000) {
      denyAccess();
      waitingForInput = false;
      return false;
    }
  }  
}

void approveAccess() {
  greenLight();
  Serial.println("Access Granted!");
  lcd.clear();
  lcd.print("Access Granted!");
  lcd.setCursor(0, 1); 
  lcd.print("Welcome John!");
  doorServo.write(180);
  noStopDelay(1000);
}

void denyAccess() {
  Serial.println("Access Denied!");
  lcd.clear();
  lcd.print("Access Denied!");
  redLight();
  alarm();
  noStopDelay(1000);
}

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

float getWeight() {
  return mapFloat(analogRead(A0), 0, 1023, 0, 100);
}

float calcDistance() {
  digitalWrite(USTRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(USTRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(USTRIG_PIN, LOW);
  // Measure the response from the HC-SR04 Echo Pin
  duration = pulseIn(USECHO_PIN, HIGH);
  // Determine distance from duration ,use 343 metres per second as speed of sound
  tempDistance = (duration / 2) * 0.0343;
  if (tempDistance >= 400 || tempDistance <= 2) {
    return distance;
  }
  if (distance > tempDistance) {
    return tempDistance;
  }
  return distance;
}

float getHeight() {
  return (DOOR_HEIGHT - distance);
}

float calcBMI() {
  if (height != NAN) {
    return (weight / pow((height/100), 2));
  }
  return NAN;
}

bool getID() {
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return false;
  }
  if (!mfrc522.PICC_ReadCardSerial()) {
    return false;
  }
  tagID = "";
  for ( uint8_t i = 0; i < 4; i++) {
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  tagID.toUpperCase();
  mfrc522.PICC_HaltA();
  return true;
}

bool checkIDInDatabase() {
  Serial.println(tagID);
  long startTime = millis();
  while (Serial.available() == 0) {
    if (!waitingForInput) {
      Serial.println("Checking Database..");
      waitingForInput = true;
    }
    serialInput = Serial.readString();
    if (serialInput != "") {
      Serial.print(serialInput);
      bool status = (serialInput == "Exists");
      waitingForInput = false;
      return status; 
    }
    if (millis() - startTime >= 5000) {
      waitingForInput = false;
      return false;
    }
  }  
}

void startInOutScan() {
  approveAccess();
  entryExitStatus = "Start";
  while (entryExitStatus != "") {
    entryExitStatus = checkInOut();
    if (entryExitStatus == "Entry" || entryExitStatus == "Exit") {
      serialOutput = entryExitStatus + "|" + String(height) + "|" + String(weight) + "|" + String(bmi);
      Serial.println(serialOutput);
    }
  }
  Serial.print("Number of persons in room: ");
  Serial.println(personCount);
}

String checkInOut() {
  long startTime = millis();
  long waitingStartTime;
  int entrySensorReading = 0;
  int exitSensorReading = 0;
  distance = DOOR_HEIGHT;
  weight = getWeight();
  do {
    entrySensorReading = analogRead(ENTRY_SENSOR);
    exitSensorReading = analogRead(EXIT_SENSOR);

    // Check if the person entered the room
    if (entrySensorReading < ENTRY_THRESHOLD) {
      Serial.println("Person entered the room! Triggered Entry Point 1");
      waitingStartTime = millis();
      do {
        if (millis() - waitingStartTime >= 5000) {
          return "False Positive";
        }
        distance = calcDistance();
      } while (analogRead(EXIT_SENSOR) > EXIT_THRESHOLD);
      Serial.println("Triggered Entry Point 2");
      height = getHeight();
      bmi = calcBMI();
      personInside = true;
      personCount += 1;
      return "Entry";
    }

    // Check if the person exited the room
    if (exitSensorReading < EXIT_THRESHOLD) {
      Serial.println("Person exited the room! Triggered Exit Point 1");
      waitingStartTime = millis();
      do {
        if (millis() - waitingStartTime >= 5000) {
          return "False Positive";
        }
        distance = calcDistance();
      } while (analogRead(ENTRY_SENSOR) > ENTRY_THRESHOLD);
      Serial.println("Triggered Exit Point 2");
      personCount -= 1;
      if (personCount == 0) {
        personInside = false;
      }
      height = getHeight();
      bmi = calcBMI();
      return "Exit";
    }
    // Wait a short time before checking again
    if (millis() - startTime >= 5000) {
      return "";
    }
    noStopDelay(100);
  } while (true);
}

void setup() {
  pinMode(BUTTON_PIN, INPUT);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(BUZER_PIN, OUTPUT);
  doorServo.attach(SERVO_PIN);
  pinMode(USTRIG_PIN, OUTPUT);
  pinMode(USECHO_PIN, INPUT);
  Serial.begin(9600);  
  SPI.begin();
  mfrc522.PCD_Init();
  lcd.begin(16, 2);
  lcd.clear();
}

void loop() {
  // noStopDelay(500);
  // greenLight();
  // noStopDelay(500);
  // redLight();
  // noStopDelay(500);
  // offLight();
  // noStopDelay(200);
  // yellowLight();
  // noStopDelay(500);
  // blueLight();
  // noStopDelay(500);
  // noStopDelay(5000);
  // Serial.print("Original Point 1: ");
  // Serial.println(analogRead(A1));
  // Serial.print("Original Point 2: ");
  // Serial.println(analogRead(A2));
  // setCurrentIRThreshold();
  // noStopDelay(1000);
  // checkInOut();
  
  noStopDelay(1000);
  offLight();
  Serial.println("Access Control ");
  Serial.println("Scan Your Card>>");
  do {
    if (Serial.available() != 0) {
      String command = Serial.readString();
      if (command == "Alarm On") {
        alarmMode = true;
      } else if (command == "Alarm Off") {
        alarmMode = false;
      }
    }
    if (alarmMode) {
      alarm();
      redLight();
      noStopDelay(250);
      offLight();
      noStopDelay(250);
    }
    cardScanned = getID();
    if (!waitingForCard) {
      lcd.clear();
      lcd.print("Waiting for scan");
      doorServo.write(90);
      waitingForCard = true;
    }
    if (cardScanned) {
      waitingForCard = false;
      if (tagID == ExitTag){ 
        startInOutScan();
      } else {
        if (checkIDInDatabase()) {
          yellowLight();
          if (waitForRemoteApprove()) {
            startInOutScan();
          }
        } else {
          denyAccess();
        }
      }
      Serial.println("--------------------------");
    }
  } while (!cardScanned);
}