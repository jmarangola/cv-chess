#include <Arduino.h>
#include <Servo.h>
#include <TeensyStep.h>

const int led = LED_BUILTIN;

Stepper motor(2, 3);       // STEP pin: 2, DIR pin: 3
StepControl controller;    // Use default settings 
Servo gripper_servo; 

void setup() {
  motor.setMaxSpeed(6000);
  motor.setAcceleration(50000);
  pinMode(1, OUTPUT);
  Serial.begin(9600);
  gripper_servo.attach(1);
}

void loop() {
  /*motor.setTargetRel(-20000);  // Set target position to 1000 steps from current position
  controller.move(motor);    // Do the move
  delay(500);
  motor.setTargetRel(20000);
  controller.move(motor);
  delay(500);*/
  gripper_servo.write(0); //Turn clockwise at high speed
  delay(300);
  gripper_servo.detach();//Stop. You can use deatch function or use write(x), as x is the middle of 0-180 which is 90, but some lack of precision may change this value
  delay(2000);
  gripper_servo.attach(1);//Always use attach function after detach to re-connect your servo with the board
  Serial.println("0");//Turn left high speed
  gripper_servo.write(180);
  delay(3000);
  gripper_servo.detach();//Stop
  delay(2000);
  gripper_servo.attach(1);


}
