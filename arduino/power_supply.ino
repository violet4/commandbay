const int OFF = 0;
const int ON = 1;

const int relayPin = 52;

int state = ON;

void lightOn() {
  digitalWrite(relayPin, LOW);
  digitalWrite(LED_BUILTIN, HIGH);
  state = ON;
}
void lightOff() {
  digitalWrite(relayPin, HIGH);
  digitalWrite(LED_BUILTIN, LOW);
  state = OFF;
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(relayPin, OUTPUT);
}

void loop() {
  if (Serial.available() <= 0) {
    return;
  }
  // Read the incoming integer
  int receivedInt = Serial.parseInt();

  // Check for newline character
  if (Serial.read() == '\n') {
    if (receivedInt==0) lightOff();
    else if (receivedInt==1) lightOn();
    else if (receivedInt==2) Serial.write(state==ON?"1\n":"0\n");
  }

}
