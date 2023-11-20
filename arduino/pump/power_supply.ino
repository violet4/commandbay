#include "PowerSupply.h"

const int relay_pin = 52;

void PowerSupply::on() {
    digitalWrite(relayPin, LOW);
    digitalWrite(LED_BUILTIN, HIGH);
    state = ON;
}
void PowerSupply::off() {
    digitalWrite(relayPin, HIGH);
    digitalWrite(LED_BUILTIN, LOW);
    state = OFF;
}
void PowerSupply::setup() {
    pinMode(relayPin, OUTPUT);
}
char PowerSupply::getState() {
    return state==ON?'1':'0';
}

// PowerSupply powerSupply(relay_pin);

// void setup() {
//   Serial.begin(9600);
//   pinMode(LED_BUILTIN, OUTPUT);
//   powerSupply.setup();
// }

// void loop() {
//   if (Serial.available() <= 0) {
//     return;
//   }
//   // Read the incoming integer
//   int receivedInt = Serial.parseInt();

//   // Check for newline character
//   if (Serial.read() == '\n') {
//     if (receivedInt==0) powerSupply.off();
//     else if (receivedInt==1) powerSupply.on();
//     else if (receivedInt==2) Serial.println(powerSupply.getState());
//   }

// }
