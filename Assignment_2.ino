#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

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

#define ENTRY_THRESHOLD 200
#define EXIT_THRESHOLD 200 

byte readCard[4];
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
int unlockID = NAN;
int weightThreshold = 2;
int doorHeight = 185;
String currentUserInfo[5];
int invalidTries = 0;

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
  int frequency = 2000;
  int stepSize = 100; 
  
  for (int x = 0; x < 2; x++) {
    for (int i = 0; i < 500; i += 100) {  
      tone(BUZER_PIN, frequency);  
      noStopDelay(50);  
      noTone(BUZER_PIN);  
      frequency -= stepSize;  
      if (frequency > 2000) { 
        frequency = 500;
      }
    }
    noTone(BUZER_PIN);
  }
}

void accessGrantedTone() {
  tone(BUZER_PIN, 440); // 440Hz frequency (A4)
  noStopDelay(100);
  tone(BUZER_PIN, 523); // 523Hz frequency (C5)
  noStopDelay(100);
  tone(BUZER_PIN, 659); // 659Hz frequency (E5)
  noStopDelay(100);
  noTone(BUZER_PIN); // Stop the tone
}

void accessDeniedTone() {
  tone(BUZER_PIN, 440, 200); // Play a 440Hz tone for 200ms
  noStopDelay(200);
  noTone(BUZER_PIN); // Turn off the tone
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
  serialOutput = "Unlock|Entry|Pending|" + currentUserInfo[1] + "|Card";
  Serial.println(serialOutput);
  while (Serial.available() == 0) {
    serialInput = Serial.readString();
    if (serialInput != "") {
      unlockID = serialInput.toInt();
      break;
    }
  }
  while (Serial.available() == 0) {
    if (!waitingForInput) {
      lcd.clear();
      lcd.print("Wait for approval..");
      waitingForInput = true;
    }
    serialInput = Serial.readString();
    if (serialInput != "") {
      bool status = (serialInput == "Approved");
      if (!status) {
        denyAccess();
      }
      waitingForInput = false;
      return status; 
    }
    if (millis() - startTime >= 30000) {
      denyAccess();
      waitingForInput = false;
      serialOutput = "Update|Failed|" + String(unlockID); 
      Serial.println(serialOutput);
      return false;
    }
  }  
}

void approveAccess() {
  greenLight();
  accessGrantedTone();
  Serial.println("Access Granted!");
  lcd.clear();
  lcd.print("Access Granted!");
  lcd.setCursor(0, 1); 
  if (currentUserInfo[1] != "") {
    serialOutput = "Welcome " + currentUserInfo[2] + "!";
    lcd.print(serialOutput);
  }
  doorServo.write(180);
  noStopDelay(1000);
}

void denyAccess() {
  Serial.println("Access Denied!");
  lcd.clear();
  lcd.print("Access Denied!");
  redLight();
  accessDeniedTone();
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
  duration = pulseIn(USECHO_PIN, HIGH);
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
  return (doorHeight - distance);
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

void splitStringUserInfo(String input) {
  int currentIndex = 0;  
  while (input.length() > 0) {  
    int delimiterIndex = input.indexOf("|");  
    if (delimiterIndex == -1) {  
      currentUserInfo[currentIndex] = input;
      input = "";  
    } else { 
      currentUserInfo[currentIndex] = input.substring(0, delimiterIndex);
      input = input.substring(delimiterIndex + 1);
    }
    currentIndex++;  
  }
}

bool checkIDInDatabase() {
  serialOutput = "Request|" + tagID;
  Serial.println(serialOutput);
  long startTime = millis();
  while (Serial.available() == 0) {
    if (!waitingForInput) {
      waitingForInput = true;
    }
    serialInput = Serial.readString();
    if (serialInput != "") {
      if (serialInput == "Invalid") {
        waitingForInput = false;
        return false;
      } else {
        splitStringUserInfo(serialInput);
        waitingForInput = false;
        return true;
      }
    }
    if (millis() - startTime >= 5000) {
      waitingForInput = false;
      return false;
    }
  }  
}

bool weightCheck() {
  float userWeight = currentUserInfo[3].toFloat();
  weight = getWeight();
  return (weight >= userWeight - weightThreshold && weight <= userWeight + weightThreshold);
}

void startInOutScan() {
  approveAccess();
  entryExitStatus = "Start";
  while (entryExitStatus != "") {
    entryExitStatus = checkInOut();
    if (entryExitStatus == "Entry" || entryExitStatus == "Exit") {
      serialOutput = entryExitStatus + "|" + String(weight) + "|" + String(height) + "|" + String(bmi);
      Serial.println(serialOutput);
      noStopDelay(2000);
    }
  }
  serialOutput = "People|" + String(personCount);
  Serial.println(serialOutput);
  memset(currentUserInfo, 0, sizeof(currentUserInfo));
  personCount = 0;
  alarmMode = false;
  invalidTries = 0;
}

String checkInOut() {
  long startTime = millis();
  long waitingStartTime;
  int entrySensorReading = 0;
  int exitSensorReading = 0;
  distance = doorHeight;
  weight = getWeight();
  do {
    entrySensorReading = analogRead(ENTRY_SENSOR);
    exitSensorReading = analogRead(EXIT_SENSOR);

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
      height = getHeight();
      bmi = calcBMI();
      return "Exit";
    }
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
  noStopDelay(1000);
  offLight();
  do {
    if (invalidTries >= 3 && alarmMode == false) {
      alarmMode = true;
    }
    if (Serial.available() != 0) {
      String command = Serial.readString();
      if (command == "Alarm On") {
        alarmMode = true;
      } else if (command == "Alarm Off") {
        alarmMode = false;
        invalidTries = 0;
      } else if (command == "Remote Unlock") {
        startInOutScan();
        waitingForCard = false;
        offLight();
      } else if (command.indexOf("WeightThresholdUpdate|") != -1) {
        serialOutput = "Weight Threshold original " + String(weightThreshold);
        Serial.println(serialOutput);
        weightThreshold = command.substring(22).toInt();
        serialOutput = "Weight Threshold Updated to " + String(weightThreshold);
        Serial.println(serialOutput);
      } else if (command.indexOf("DoorHeightUpdate|") != -1) {
        serialOutput = "Door Height original " + String(doorHeight);
        Serial.println(serialOutput);
        doorHeight = command.substring(17).toInt();
        serialOutput = "Door Height Updated to " + String(doorHeight);
        Serial.println(serialOutput);
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
      offLight();
      lcd.clear();
      lcd.print("Waiting for scan");
      doorServo.write(90);
      waitingForCard = true;
    }
    if (cardScanned) {
      waitingForCard = false;
      if (tagID == ExitTag){
        Serial.println("Unlock|Exit|Success");
        startInOutScan();
      } else {
        if (checkIDInDatabase()) {
          yellowLight();
          if (weightCheck()) {
            startInOutScan();
          } else {
            if (waitForRemoteApprove()) {
              startInOutScan();
            }
          }
        } else {
          invalidTries += 1;
          denyAccess();
        }
      }
      unlockID = NAN;
      Serial.println("--------------------------");
    }
  } while (!cardScanned);
}
