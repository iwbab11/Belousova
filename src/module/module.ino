#include <Adafruit_Sensor.h>

#include <DHT.h>
#include <DHT_U.h>

#include <Servo.h>
#include <DHT.h>

#define PIN_SERVO 9
#define PIN_DHT 2
#define PIN_TRIG 7
#define PIN_ECHO 6
#define PIN_LIGHT A0
#define PIN_LAMP 13
#define TEMP_MAX 30
#define LIGNT_NIGHT 300
#define CAR_CM 20
#define OPEN 90
#define CLOSED 0

Servo servo;
DHT dht(PIN_DHT, DHT11);
bool autoMode = false;
bool isOpen = false;
float t, h;
int light;
long dist;
String status = "OK";
unsigned long lastRead = 0;

void setup() {
    Serial.begin(9600);
    servo.attach(PIN_SERVO);
    servo.write(CLOSED);
    dht.begin();
    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);
    pinMode(PIN_LAMP, OUTPUT);
}

void loop() {
    if (Serial.available()) command(Serial.readStringUntil('\n'));
    if (millis() - lastRead >= 500) {
        lastRead = millis();
        readSensors();
        if (autoMode && status == "OK") gate(dist < CAR_CM);
    }
}

void gate(bool open) {
    isOpen = open;
    servo.write(open ? OPEN : CLOSED);
}

void command(String cmd) {
    cmd.trim();
    if (cmd == "M") autoMode = false;
    else if (cmd == "A") autoMode = true;
    else if (cmd == "O" && !autoMode) gate(true);
    else if (cmd == "C" && !autoMode) gate(false);
    else if (cmd == "T") selfTest();
    else if (cmd == "R") {autoMode = false; gate(false);}
}

long readDist() {
    digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10); digitalWrite(PIN_TRIG, LOW);
    long us = pulseIn(PIN_ECHO, HIGH, 30000);
    return us = 0 ? 999 : us / 58;
}

void readSensors() {
    t = dht.readTemperature();
    h = dht.readHumidity();
    light = analogRead(PIN_LIGHT);
    dist = readDist();
    if (isnan(t) || isnan(h)) status = "NO_SIGNAL";
    else if (t > TEMP_MAX) status = "OVERHEAT";
    else status = "OK";
    digitalWrite(PIN_LAMP, light < LIGNT_NIGHT);
    Serial.print("DATA;");
    Serial.print(autoMode ? "AUTO;" : "MANUAL;");
    Serial.print(isOpen ? "OPEN;" : "CLOSED;");
    Serial.print(dist); Serial.print(";");
    Serial.print(t, 1); Serial.print(";");
    Serial.print(h, 0); Serial.print(";");
    Serial.print(light); Serial.print(";");
    Serial.print(light < LIGNT_NIGHT ? "NIGHT;" : "DAY;");
    Serial.println(status);
}

void selfTest() {
    Serial.println(isnan(dht.readTemperature()) ? "TEST;DHT11;FAIL нет сигнала" : "TEST;DHT11;OK");
    Serial.print("TEST;HC-SR04;"); Serial.println(readDist());
    Serial.print("TEST;LIGHT;"); Serial.println(analogRead(PIN_LIGHT));
    servo.write(OPEN); delay(700); servo.write(CLOSED); delay(700);
    gate(isOpen);
    Serial.println("TEST;SERVO;OK, проверить движение");
}
