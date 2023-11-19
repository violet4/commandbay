#include <AFMotor.h>

// Frequencies of musical notes
const int melody[] = {262, 294, 330, 349, 392, 440, 494, 523};

class Pump {
    AF_DCMotor motor;
    static const int maximum = 255;
    int speed;
public:
    Pump(int motor_num) : motor(motor_num), speed(0) {}

    void setSpeed(int new_speed) {
        speed = max(min(new_speed, maximum), 0);
        motor.setSpeed(speed);
    }
    void on() {motor.run(FORWARD);}
    void off() {motor.run(RELEASE);}
};

class Button {
    const int buttonPin;  // Analog
public:
    Button(int button_pin): buttonPin(button_pin) {}

    void setup() const {
        pinMode(buttonPin, INPUT);
    }
    bool pressed() const {
        return analogRead(buttonPin) >= 512;
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

Pump pump(2);
Button button(A0);
Speaker speaker(9);

void setup() {
    button.setup();
    speaker.setup();
}

void loop() {
    if (button.pressed()) {
        pump.on();
    }
    else {
        pump.off();
    }
}
