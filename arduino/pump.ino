#include <AFMotor.h>

AF_DCMotor motor2(2);  // Motor 2
AF_DCMotor motor3(3);  // Motor 3
AF_DCMotor motor4(4);  // Motor 4

const int buttonPin = A0;  // Analog pin A0 is connected to the button
int buttonValue = 0;

const int speakerPin = 9; // Use the appropriate output pin for your board
const int melody[] = {262, 294, 330, 349, 392, 440, 494, 523}; // Frequencies of musical notes

void setup() {
  pinMode(buttonPin, INPUT);
  pinMode(speakerPin, OUTPUT);
  motor2.setSpeed(255);  // Set speed to maximum
  motor3.setSpeed(255);
  motor4.setSpeed(255);
}

void loop() {
  buttonValue = analogRead(buttonPin);  // Read analog value from the button pin

  if (buttonValue > 512) {  // Assuming the button value goes above 512 when pressed
    motor2.run(FORWARD);    // Turn on all motors when button is pressed
    tone(speakerPin, 262);  // Play a single note for Motor 1
    delay(500);             // Play each note for 500ms
    noTone(speakerPin);     // Turn off the tone
    motor2.run(RELEASE);    // Stop Motor 1

    motor3.run(FORWARD);    // Start Motor 3
    motor4.run(FORWARD);    // Start Motor 4
  }
  else {
    motor2.run(RELEASE);    // Stop Motor 1 when button is not pressed
    motor3.run(RELEASE);    // Stop Motor 3 when button is not pressed
    motor4.run(RELEASE);    // Stop Motor 4 when button is not pressed
    noTone(speakerPin);     // Turn off the tone
  }
}
