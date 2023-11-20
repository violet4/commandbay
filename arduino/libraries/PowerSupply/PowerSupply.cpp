#include "Arduino.h"
#include "PowerSupply.h"

const int relay_pin = 52;

PowerSupply::PowerSupply(int relay_pin): relayPin(relay_pin) {}

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
