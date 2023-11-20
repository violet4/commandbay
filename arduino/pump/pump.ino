#ifndef PUMP
#define PUMP

#include <AFMotor.h>
#include <string.h>
#include "PowerSupply.h"

static const uint8_t buttonPin = A0;
const int speaker_pin = 9;
const int ps_relay_pin = 52;


// Frequencies of musical notes
const int melody[] = {262, 294, 330, 349, 392, 440, 494, 523};

class TimedActuator {
private:
    bool is_on;
    long seconds_remaining;
    long larger_seconds_remaining;

    virtual void do_on() = 0;
    virtual void do_off() = 0;
public:
    TimedActuator(): is_on(false), seconds_remaining(0) {}
    virtual void setup() {}
    long getSecondsRemaining() {
        return seconds_remaining;
    }
    void decrement_seconds(long decrease_seconds) {
        if (!is_on) return;
        // prevent underflow
        if (decrease_seconds >= seconds_remaining) {
            seconds_remaining = 0;
            do_off();
            is_on = false;
        }
        else
            seconds_remaining -= decrease_seconds;
    }
    void add_seconds(long increase_seconds) {
        if (increase_seconds>0 && !is_on) {
            is_on = true;
            do_on();
        }
        larger_seconds_remaining = seconds_remaining + increase_seconds;
        // prevent overflow
        if (seconds_remaining < larger_seconds_remaining)
            seconds_remaining = larger_seconds_remaining;
    }
};


class SerialActuator: public TimedActuator {
private:
    void do_on() {Serial.write("on\n");}
    void do_off() {Serial.write("off\n");}
public:
    void setup() override {
        Serial.begin(9600);
    }
};

class PowerSupplyActuator: public TimedActuator {
private:
    PowerSupply powerSupply;
    void do_on() {powerSupply.on();}
    void do_off() {powerSupply.off();}
public:
    PowerSupplyActuator(PowerSupply power_supply): powerSupply(power_supply) {}
    void setup() override {powerSupply.setup();}
};

class PumpActuator: public TimedActuator {
private:
    AF_DCMotor motor;
    int speed;

    void do_on() {motor.run(FORWARD);}
    void do_off() {motor.run(RELEASE);}

public:
    static const int maximum = 255;
    PumpActuator(int motor_num) : motor(motor_num), speed(0) {}

    void setSpeed(int new_speed) {
        speed = max(min(new_speed, maximum), 0);
        motor.setSpeed(speed);
    }

};

class Button {
private:
    const int buttonPin;  // Analog
    bool is_pressed;
    bool was_pressed;
public:
    Button(int button_pin): buttonPin(button_pin), is_pressed(false), was_pressed(false) {}

    void setup() const {
        pinMode(buttonPin, INPUT);
    }
    bool pressed() const {
        return analogRead(buttonPin) >= 512;
    }
    // triggers at the exact moment when button starts being activated
    bool justPressed() {
        was_pressed = is_pressed;
        is_pressed = pressed();
        if (is_pressed && !was_pressed) {
            return true;
        }
        return false;
    }
};

class AddTimeHandler {
private:
    long seconds;
    long return_seconds;
    long new_seconds;
    virtual long checkMoreSeconds() = 0;
public:
    AddTimeHandler(): seconds(0){};
    void update() {
        new_seconds = checkMoreSeconds();
        if (new_seconds > 0) {
            if (seconds + new_seconds > seconds)
                seconds += new_seconds;
        }
    }
    virtual void setup() {}
    long popNewSeconds() {
        return_seconds = seconds;
        seconds = 0;
        return return_seconds;
    }
};

class ButtonAddTimeHandler: public AddTimeHandler {
private:
    Button button;
    long checkMoreSeconds() override {
        return (long)button.justPressed();
    }
public:
    ButtonAddTimeHandler(Button input_button): button(input_button) {}
};

class SerialAddTimeHandler : public AddTimeHandler {
private:
    int receivedInt;
    long checkMoreSeconds() override {
        if (Serial.available() <= 0) {
            return 0;
        }
        receivedInt = Serial.parseInt();
        return (Serial.read() == '\n') ? receivedInt*1000 : 0;
    }
public:
    SerialAddTimeHandler(): receivedInt(0) {}
    void setup() {Serial.begin(9600);}
};


class Speaker {
private:
    const int speakerPin;

public:
    Speaker(int speaker_pin): speakerPin(speaker_pin) {}
    void setup() {pinMode(speaker_pin, OUTPUT);}
    // void tone(int freq) {tone(speakerPin, freq);}
    // void noTone() {noTone(speakerPin);}
};

class Looper {
private:
    long last_loop_start;
    long this_loop_start;
    bool first;
    long delta;
public:
    Looper(): last_loop_start(0), this_loop_start(0), first(true) {}

    long newLoop() {
        // without this we might return an unreasonably large number
        if (first) {
            first = false;
            return last_loop_start;  // 0
        }
        last_loop_start = this_loop_start;
        this_loop_start = (long)millis();
        delta = this_loop_start - last_loop_start;
        return delta;
    }
};

Looper looper{};
Speaker speaker(speaker_pin);
Button button(buttonPin);

AddTimeHandler* add_time_handler = new SerialAddTimeHandler();
// AddTimeHandler* add_time_handler = new ButtonAddTimeHandler(button);
PowerSupply powerSupply(ps_relay_pin);

// TimedActuator* actuator = new PowerSupplyActuator(powerSupply);
TimedActuator* actuator = new SerialActuator();
// TimedActuator* actuator = new PumpActuator(2);

void setup() {
    add_time_handler->setup();
    actuator->setup();
}

long delta;
long additional_seconds;
void loop() {
    delta = looper.newLoop();
    actuator->decrement_seconds(delta);

    add_time_handler->update();
    additional_seconds = add_time_handler->popNewSeconds();
    if (additional_seconds > 0)
        actuator->add_seconds(additional_seconds);
}

#endif
