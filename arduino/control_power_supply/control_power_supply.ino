#include "PowerSupply.h"

const int ps_relay_pin = 52;

PowerSupply powerSupply(ps_relay_pin);

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  powerSupply.setup();
}

void loop() {
  if (Serial.available() <= 0) {
    return;
  }
  // Read the incoming integer
  int receivedInt = Serial.parseInt();

  // Check for newline character
  if (Serial.read() == '\n') {
    if (receivedInt==0) powerSupply.off();
    else if (receivedInt==1) powerSupply.on();
    else if (receivedInt==2) Serial.println(powerSupply.getState());
  }

}
