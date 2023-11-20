#include <AFMotor.h>

// Frequencies of musical notes
const int melody[] = {262, 294, 330, 349, 392, 440, 494, 523};

class Pump {
    AF_DCMotor motor;
    int speed;
    unsigned long seconds_remaining;
    unsigned long larger_seconds_remaining;
    bool is_on;

    void updatePumpState() {
        if (seconds_remaining > 0)
            on();
        else off();
    }
    void on() {
        if (!is_on) {
            is_on = true;
            motor.run(FORWARD);
        }
    }
    void off() {
        if (is_on) {
            is_on = false;
            motor.run(RELEASE);
        }
    }
public:
    static const int maximum = 255;
    Pump(int motor_num) : motor(motor_num), speed(0), seconds_remaining(0), is_on(false) {}

    void setSpeed(int new_speed) {
        speed = max(min(new_speed, maximum), 0);
        motor.setSpeed(speed);
    }

    void decrement_seconds(unsigned long decrease_seconds) {
        // prevent underflow
        if (decrease_seconds >= seconds_remaining)
            seconds_remaining = 0;
        else
            seconds_remaining -= decrease_seconds;
        updatePumpState();
    }
    void add_seconds(unsigned long increase_seconds) {
        larger_seconds_remaining = seconds_remaining + increase_seconds;
        // prevent overflow
        if (seconds_remaining < larger_seconds_remaining)
            seconds_remaining = larger_seconds_remaining;
        updatePumpState();
    }
};

class Button {
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

class Speaker {
    const int speakerPin;

public:
    Speaker(int speaker_pin): speakerPin(speaker_pin) {}

    void setup() const {pinMode(speakerPin, OUTPUT);}
    //void tone(int value) const {tone(speakerPin, value);}
    //void off() const {noTone(speakerPin);}
};

class Looper {
    unsigned long last_loop_start;
    unsigned long this_loop_start;
    bool first;
    unsigned long delta;
public:
    Looper(): last_loop_start(0), this_loop_start(0), first(true) {}

    unsigned long newLoop() {
        // without this we might return an unreasonably large number
        if (first) {
            first = false;
            return last_loop_start;  // 0
        }
        last_loop_start = this_loop_start;
        this_loop_start = millis();
        delta = this_loop_start - last_loop_start;
        return delta;
    }
};

Looper looper;

Pump pump(2);
Button button(A0);
Speaker speaker(9);

void setup() {
    button.setup();
    speaker.setup();
}

unsigned long delta;
void loop() {
    delta = looper.newLoop();
    pump.decrement_seconds(delta);
    if (button.justPressed())
        pump.add_seconds(1);
    else {
        // pump.off();
    }
}
