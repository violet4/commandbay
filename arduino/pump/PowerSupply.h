#ifndef POWERSUPPLY_H
#define POWERSUPPLY_H

#include <Arduino.h>

class PowerSupply {
private:
    static const int OFF = 0;
    static const int ON = 1;

    int state = ON;
    int relayPin;

public:
    PowerSupply(int relay_pin): relayPin(relay_pin) {}
    void on();
    void off();
    void setup();
    char getState();
};

#endif
