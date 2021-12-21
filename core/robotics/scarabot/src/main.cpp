/**
 * @brief Robot main 
 * 
 * John Marangola - marangol@bc.edu
 */
#include <Arduino.h>
#include <Servo.h>
#include <TeensyStep.h>
#include <LimitSwitch.h>
#include <SerialBuffer.h>
#include <vector>
#include <Axis.h>

const int led = LED_BUILTIN;
const int emagnetPin = 12;
bool emagnetState = false; 

      // STEP pin: 2, DIR pin: 3
StepControl controller;  
RotateControl rotationController;
LimitSwitch zaxis_limit(11, LimitSwitch::digitalMode::NC);
LimitSwitch theta1_limit(10, LimitSwitch::digitalMode::NO);
LimitSwitch theta2_limit(13, LimitSwitch::digitalMode::NC);

Stepper zmot = Stepper(2, 3);
Stepper theta1 = Stepper(4, 5);
Stepper theta2 = Stepper(6, 7);
SerialBuffer serialStream = SerialBuffer(57600);

const double theta1_RR = 20.0;
const double theta2_RR = 16.5;


void toggleElectroMagnet(bool &emagnetState) {
  digitalWrite(emagnetPin, emagnetState ? LOW : HIGH);
  emagnetState = !emagnetState;
}

void home_axis(Stepper& motor, LimitSwitch& limit) {
  while (limit.getStatus()) {
    rotationController.rotateAsync(motor);
  }
  rotationController.stop();
}

void setup() {
  zmot.setMaxSpeed(6000);
  zmot.setAcceleration(10000);
  theta1.setMaxSpeed(1000);
  theta1.setAcceleration(5000);
  theta2.setMaxSpeed(500);
  theta2.setAcceleration(5000);
  pinMode(1, OUTPUT);

  // Configure electromagnet relay GPIO pin:
  pinMode(emagnetPin, OUTPUT);


  // Setup limit swithces 
  zaxis_limit.setup();
  theta1_limit.setup();
  theta2_limit.setup();

  /* Home each axis independently */
  home_axis(theta1, theta1_limit);
  home_axis(theta2, theta2_limit);
  home_axis(zmot, zaxis_limit);
  Serial.begin(115200);
}

int iterations = 0;
String ser_in;
double tmp;
std::vector<double> px;

// Simple serial interface for hand-tuned params
void loop() {
  if (Serial.available()) {
    ser_in = serialStream.waitForSerialInput('\n', 10);
    px = serialStream.parseSerial(ser_in, ',');
    zmot.setTargetAbs(px[0]);
    theta1.setTargetAbs(px[1]);
    theta2.setTargetAbs(px[2]);
    controller.moveAsync(zmot, theta1, theta2);
    Serial.println("recd");
  }
}

double read_num() {
  ser_in = Serial.readStringUntil(',');
  double tmp =  (ser_in[0] == '-') ? -1:1;
  for (int i = 1; i < ser_in.length(); ++i) {
    tmp += (int)(ser_in[i] - '0')*(pow(10, ser_in.length()-i));
  }
  return tmp;
}