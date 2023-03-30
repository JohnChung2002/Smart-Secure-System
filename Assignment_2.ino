#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 10
#define RST_PIN 9
#define RED_PIN 4
#define GREEN_PIN 5
#define BLUE_PIN 6
#define BUZER_PIN 7

// int ifRead;

// void setup() {
//   Serial.begin(9600);
//   pinMode(A0, INPUT);
// }

// void loop() {
//   ifRead = analogRead(A0);
//   Serial.println(ifRead);
// }

byte readCard[4];
String MasterTag = "C3E86097";
String tagID = "";
bool cardScanned = false;

MFRC522 mfrc522(SS_PIN, RST_PIN);  
LiquidCrystal_I2C lcd(0x27, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);

void offLight() {
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
}

void redLight() {
  analogWrite(RED_PIN, 255);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
}

void yellowLight() {
  analogWrite(RED_PIN, 255);
  analogWrite(GREEN_PIN, 255);
  analogWrite(BLUE_PIN, 0);
}

void greenLight() {
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 255);
  analogWrite(BLUE_PIN, 0);
}

boolean getID() 
{
  if ( !mfrc522.PICC_IsNewCardPresent()) {
    return false;
  }
  if ( !mfrc522.PICC_ReadCardSerial()) {
  return false;
  }
  tagID = "";
  for ( uint8_t i = 0; i < 4; i++) {
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  tagID.toUpperCase();
  mfrc522.PICC_HaltA();
  Serial.println("UID of card scanned is: " + tagID);
  return true;
}

void setup() {
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
    pinMode(BUZER_PIN, OUTPUT);
    Serial.begin(9600);  
    SPI.begin();
    mfrc522.PCD_Init();
    lcd.begin(16, 2);
    lcd.clear();
}

void loop() {
    // redLight();
    // delay(1000);
    // yellowLight();
    // delay(1000);
    // greenLight();
    // delay(1000);
    offLight();
    delay(1000);
    Serial.println("Access Control ");
    Serial.println("Scan Your Card>>");
    int potVal = analogRead(A0);
    Serial.println("Potentiometer Reading: ");
    Serial.println(potVal);
    do {
      cardScanned = getID();
      lcd.clear();
      lcd.print("Waiting for scan");
      if (cardScanned) {
        if (tagID == MasterTag){
          yellowLight();
          delay(1000);
          Serial.println("Access Granted!");
          lcd.clear();
          lcd.print("Access Granted!");
          lcd.setCursor(0, 1); 
          lcd.print("Welcome John!");
          Serial.println("--------------------------");
        }
        else{
          redLight();
          tone(BUZER_PIN, 262, 500);
          Serial.println(" Access Denied!");
          lcd.clear();
          lcd.print("Access Denied!");
          delay(1000);
          Serial.println("--------------------------");
        }
      }
    } while (!cardScanned);
}