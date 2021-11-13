#include <Arduino.h>
#include <Servo.h>
#include <TeensyStep.h>
#include <LimitSwitch.h>

const int led = LED_BUILTIN;

Stepper motor(2, 3);       // STEP pin: 2, DIR pin: 3
StepControl controller;    // Use default settings 
Servo gripper_servo; 

LimitSwitch zaxis(11, LimitSwitch::digitalMode::NC);

void setup() {
  motor.setMaxSpeed(6000);
  motor.setAcceleration(50000);
  pinMode(1, OUTPUT);
  Serial.begin(9600);
  zaxis.setup();
}

void loop() {
  /*motor.setTargetRel(-20000);  // Set target position to 1000 steps from current position
  controller.move(motor);    // Do the move
  delay(500);
  motor.setTargetRel(20000);
  controller.move(motor);
  delay(500);*/

  Serial << zaxis.getStatus();


}
