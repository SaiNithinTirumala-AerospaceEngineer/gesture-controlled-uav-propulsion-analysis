/*
 * gesture_flight_controller.ino
 * ------------------------------
 * Gesture-controlled quadrotor UAV flight controller.
 *
 * Reads hand gesture commands from an IR sensor, maps them to
 * flight control outputs (motor PWM signals), and performs basic
 * obstacle avoidance using four HC-SR04 ultrasonic sensors.
 *
 * Hardware:
 *   - Arduino Uno (ATmega328P, 16 MHz)
 *   - IR gesture sensor on A0
 *   - 4x HC-SR04 ultrasonic sensors (front, back, left, right)
 *   - 4x BLDC motors via ESC (PWM pins 9, 10, 11, 12)
 *   - Servo for camera/gimbal on pin 6
 *   - A2212 1400KV motors + Simonk 30A ESCs
 *
 * Gesture vocabulary (IR sensor ADC threshold bands, 0-1023):
 *   0  - 100  : Land
 *   100 - 200 : Left  (roll left)
 *   200 - 300 : Down  (descend)
 *   300 - 400 : Idle  (no command)
 *   400 - 500 : Backward (pitch back)
 *   450 - 550 : Hover (hold position)
 *   500 - 600 : Forward (pitch forward)
 *   700 - 800 : Right (roll right)
 *   800 - 900 : Up    (ascend)
 *
 * PWM output range: 1000-2000 us (standard ESC protocol)
 *   1000 us = motors off / minimum throttle
 *   1500 us = 50% throttle (hover point)
 *   2000 us = full throttle
 *
 * Obstacle avoidance threshold: 30 cm
 * If obstacle detected, motor in that direction is throttled back
 * and a warning is printed to serial.
 *
 * Project: Design and Analysis of Propulsion System of
 *          Gesture Control UAV Using AIML
 * Institution: Malla Reddy College of Engineering & Technology
 * Authors: Shaik Nawaz, Tirumala Sai Nithin, V. Himabindu
 * Year: 2023-2024
 *
 * Usage:
 *   1. Wire hardware as per docs/hardware_bom.md
 *   2. Upload via Arduino IDE (Tools -> Board: Arduino Uno)
 *   3. Open Serial Monitor at 9600 baud to view state output
 */

#include <Servo.h>

// ── Pin definitions ───────────────────────────────────────────────────────────
const int MOTOR_FL_PIN  = 9;    // Front-left motor ESC
const int MOTOR_FR_PIN  = 10;   // Front-right motor ESC
const int MOTOR_BL_PIN  = 11;   // Back-left motor ESC
const int MOTOR_BR_PIN  = 12;   // Back-right motor ESC
const int CAMERA_PIN    = 6;    // Camera/gimbal servo

const int GESTURE_PIN   = A0;   // IR gesture sensor (analogue)

// HC-SR04 ultrasonic sensor pins (trigger, echo pairs)
const int TRIG_FRONT = 2;  const int ECHO_FRONT = 3;
const int TRIG_BACK  = 4;  const int ECHO_BACK  = 5;
const int TRIG_LEFT  = 7;  const int ECHO_LEFT  = 8;
const int TRIG_RIGHT = A1; const int ECHO_RIGHT = A2;

// ── Constants ─────────────────────────────────────────────────────────────────
const int PWM_MIN           = 1000;   // ESC minimum (motors off)
const int PWM_HOVER         = 1500;   // ESC hover throttle
const int PWM_MAX           = 2000;   // ESC maximum throttle
const int PWM_STEP          = 50;     // Throttle increment per command
const float OBSTACLE_DIST_CM = 30.0; // Obstacle avoidance threshold
const int LOOP_DELAY_MS     = 100;    // Main loop period (10 Hz)
const int SERIAL_BAUD       = 9600;

// ── Gesture threshold bands (IR ADC values 0-1023) ───────────────────────────
const int GESTURE_LAND_MAX      = 100;
const int GESTURE_LEFT_MAX      = 200;
const int GESTURE_DOWN_MAX      = 300;
const int GESTURE_BACKWARD_MAX  = 500;
const int GESTURE_HOVER_LOW     = 450;
const int GESTURE_HOVER_HIGH    = 550;
const int GESTURE_FORWARD_MAX   = 600;
const int GESTURE_RIGHT_MAX     = 800;
const int GESTURE_UP_MAX        = 900;

// ── State ─────────────────────────────────────────────────────────────────────
Servo cameraServo;
int throttleFl, throttleFr, throttleBl, throttleBr;
bool isFlying = false;
String currentState = "IDLE";

// ── Function prototypes ───────────────────────────────────────────────────────
void initMotors();
void armESCs();
void setMotors(int fl, int fr, int bl, int br);
void hover();
void land();
void ascend();
void descend();
void pitchForward();
void pitchBackward();
void rollLeft();
void rollRight();
float readUltrasonic(int trigPin, int echoPin);
bool obstacleDetected(int direction);
void handleGesture(int gestureValue);
void printState(int gestureValue);

// ── Setup ─────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(SERIAL_BAUD);
    Serial.println(F("Gesture Flight Controller — Initialising"));

    // Motor ESC pins
    pinMode(MOTOR_FL_PIN, OUTPUT);
    pinMode(MOTOR_FR_PIN, OUTPUT);
    pinMode(MOTOR_BL_PIN, OUTPUT);
    pinMode(MOTOR_BR_PIN, OUTPUT);

    // Ultrasonic trigger pins
    pinMode(TRIG_FRONT, OUTPUT); pinMode(ECHO_FRONT, INPUT);
    pinMode(TRIG_BACK,  OUTPUT); pinMode(ECHO_BACK,  INPUT);
    pinMode(TRIG_LEFT,  OUTPUT); pinMode(ECHO_LEFT,  INPUT);
    pinMode(TRIG_RIGHT, OUTPUT); pinMode(ECHO_RIGHT, INPUT);

    // Camera servo
    cameraServo.attach(CAMERA_PIN);
    cameraServo.write(90);   // Centre position

    // Initialise motors and arm ESCs
    initMotors();
    armESCs();

    Serial.println(F("Initialisation complete. Awaiting gesture commands."));
    Serial.println(F("State: IDLE"));
}

// ── Main loop ─────────────────────────────────────────────────────────────────
void loop() {
    int gestureValue = analogRead(GESTURE_PIN);
    handleGesture(gestureValue);
    printState(gestureValue);
    delay(LOOP_DELAY_MS);
}

// ── Motor control ─────────────────────────────────────────────────────────────

void initMotors() {
    throttleFl = PWM_MIN;
    throttleFr = PWM_MIN;
    throttleBl = PWM_MIN;
    throttleBr = PWM_MIN;
    setMotors(PWM_MIN, PWM_MIN, PWM_MIN, PWM_MIN);
}

void armESCs() {
    /*
     * ESC arming sequence — send minimum throttle for 2 seconds.
     * Required on power-up so ESCs calibrate their input range.
     */
    Serial.println(F("Arming ESCs..."));
    setMotors(PWM_MIN, PWM_MIN, PWM_MIN, PWM_MIN);
    delay(2000);
    Serial.println(F("ESCs armed."));
}

void setMotors(int fl, int fr, int bl, int br) {
    /*
     * Write PWM values to all four ESCs.
     * Values are constrained to safe operating range.
     * Motor layout (top view):
     *   FL (CW)  --- FR (CCW)
     *      |             |
     *   BL (CCW) --- BR (CW)
     */
    throttleFl = constrain(fl, PWM_MIN, PWM_MAX);
    throttleFr = constrain(fr, PWM_MIN, PWM_MAX);
    throttleBl = constrain(bl, PWM_MIN, PWM_MAX);
    throttleBr = constrain(br, PWM_MIN, PWM_MAX);

    analogWrite(MOTOR_FL_PIN, map(throttleFl, PWM_MIN, PWM_MAX, 0, 255));
    analogWrite(MOTOR_FR_PIN, map(throttleFr, PWM_MIN, PWM_MAX, 0, 255));
    analogWrite(MOTOR_BL_PIN, map(throttleBl, PWM_MIN, PWM_MAX, 0, 255));
    analogWrite(MOTOR_BR_PIN, map(throttleBr, PWM_MIN, PWM_MAX, 0, 255));
}

// ── Flight commands ───────────────────────────────────────────────────────────

void hover() {
    setMotors(PWM_HOVER, PWM_HOVER, PWM_HOVER, PWM_HOVER);
    isFlying    = true;
    currentState = "HOVER";
}

void land() {
    // Gradually reduce throttle to prevent hard landing
    for (int t = throttleFl; t >= PWM_MIN; t -= 20) {
        setMotors(t, t, t, t);
        delay(50);
    }
    setMotors(PWM_MIN, PWM_MIN, PWM_MIN, PWM_MIN);
    isFlying    = false;
    currentState = "LANDED";
}

void ascend() {
    if (obstacleDetected(0)) {
        Serial.println(F("WARNING: Obstacle above — ascent blocked"));
        hover();
        return;
    }
    int t = constrain(throttleFl + PWM_STEP, PWM_MIN, PWM_MAX);
    setMotors(t, t, t, t);
    currentState = "ASCENDING";
}

void descend() {
    int t = constrain(throttleFl - PWM_STEP, PWM_MIN, PWM_MAX);
    setMotors(t, t, t, t);
    currentState = "DESCENDING";
}

void pitchForward() {
    if (obstacleDetected(1)) {
        Serial.println(F("WARNING: Obstacle ahead — forward blocked"));
        hover();
        return;
    }
    // Increase rear motors, decrease front — nose pitches down → forward motion
    setMotors(PWM_HOVER - PWM_STEP, PWM_HOVER - PWM_STEP,
              PWM_HOVER + PWM_STEP, PWM_HOVER + PWM_STEP);
    currentState = "FORWARD";
}

void pitchBackward() {
    if (obstacleDetected(2)) {
        Serial.println(F("WARNING: Obstacle behind — backward blocked"));
        hover();
        return;
    }
    setMotors(PWM_HOVER + PWM_STEP, PWM_HOVER + PWM_STEP,
              PWM_HOVER - PWM_STEP, PWM_HOVER - PWM_STEP);
    currentState = "BACKWARD";
}

void rollLeft() {
    if (obstacleDetected(3)) {
        Serial.println(F("WARNING: Obstacle left — roll blocked"));
        hover();
        return;
    }
    // Increase right motors, decrease left — drone rolls left
    setMotors(PWM_HOVER - PWM_STEP, PWM_HOVER + PWM_STEP,
              PWM_HOVER - PWM_STEP, PWM_HOVER + PWM_STEP);
    currentState = "ROLLING LEFT";
}

void rollRight() {
    if (obstacleDetected(4)) {
        Serial.println(F("WARNING: Obstacle right — roll blocked"));
        hover();
        return;
    }
    setMotors(PWM_HOVER + PWM_STEP, PWM_HOVER - PWM_STEP,
              PWM_HOVER + PWM_STEP, PWM_HOVER - PWM_STEP);
    currentState = "ROLLING RIGHT";
}

// ── Obstacle detection ────────────────────────────────────────────────────────

float readUltrasonic(int trigPin, int echoPin) {
    /*
     * HC-SR04 distance measurement.
     * Trigger: 10us pulse on TRIG pin
     * Echo: pulse width proportional to distance
     * Distance (cm) = duration (us) / 58.0
     * Valid range: 2 cm to 400 cm
     */
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 30000);  // 30ms timeout
    if (duration == 0) return 400.0;                // No echo = clear path
    return duration / 58.0;
}

bool obstacleDetected(int direction) {
    /*
     * direction: 0=above(front proxy), 1=front, 2=back, 3=left, 4=right
     */
    float dist;
    switch (direction) {
        case 0: dist = readUltrasonic(TRIG_FRONT, ECHO_FRONT); break;
        case 1: dist = readUltrasonic(TRIG_FRONT, ECHO_FRONT); break;
        case 2: dist = readUltrasonic(TRIG_BACK,  ECHO_BACK);  break;
        case 3: dist = readUltrasonic(TRIG_LEFT,  ECHO_LEFT);  break;
        case 4: dist = readUltrasonic(TRIG_RIGHT, ECHO_RIGHT); break;
        default: return false;
    }
    return dist < OBSTACLE_DIST_CM;
}

// ── Gesture handler ───────────────────────────────────────────────────────────

void handleGesture(int gestureValue) {
    /*
     * Map IR sensor ADC reading to flight command.
     * Threshold bands match gesture_recognition_data.csv.
     */
    if (gestureValue <= GESTURE_LAND_MAX) {
        land();
    }
    else if (gestureValue <= GESTURE_LEFT_MAX) {
        if (isFlying) rollLeft();
    }
    else if (gestureValue <= GESTURE_DOWN_MAX) {
        if (isFlying) descend();
    }
    else if (gestureValue >= GESTURE_HOVER_LOW &&
             gestureValue <= GESTURE_HOVER_HIGH) {
        hover();
    }
    else if (gestureValue <= GESTURE_BACKWARD_MAX) {
        if (isFlying) pitchBackward();
    }
    else if (gestureValue <= GESTURE_FORWARD_MAX) {
        if (isFlying) pitchForward();
    }
    else if (gestureValue <= GESTURE_RIGHT_MAX) {
        if (isFlying) rollRight();
    }
    else if (gestureValue <= GESTURE_UP_MAX) {
        if (!isFlying) {
            // Take-off sequence — ramp up to hover throttle
            for (int t = PWM_MIN; t <= PWM_HOVER; t += 20) {
                setMotors(t, t, t, t);
                delay(30);
            }
            isFlying = true;
        }
        ascend();
    }
    else {
        // Unknown gesture — maintain current state
        currentState = "IDLE";
    }
}

// ── Serial output ─────────────────────────────────────────────────────────────

void printState(int gestureValue) {
    Serial.print(F("Gesture: ")); Serial.print(gestureValue);
    Serial.print(F("  State: ")); Serial.print(currentState);
    Serial.print(F("  Throttle FL/FR/BL/BR: "));
    Serial.print(throttleFl); Serial.print(F("/"));
    Serial.print(throttleFr); Serial.print(F("/"));
    Serial.print(throttleBl); Serial.print(F("/"));
    Serial.println(throttleBr);

    // Obstacle distances (printed every 5th loop to reduce serial spam)
    static int loopCount = 0;
    if (++loopCount % 5 == 0) {
        Serial.print(F("  Obstacles (cm) F/B/L/R: "));
        Serial.print(readUltrasonic(TRIG_FRONT, ECHO_FRONT), 1);
        Serial.print(F(" / "));
        Serial.print(readUltrasonic(TRIG_BACK, ECHO_BACK), 1);
        Serial.print(F(" / "));
        Serial.print(readUltrasonic(TRIG_LEFT, ECHO_LEFT), 1);
        Serial.print(F(" / "));
        Serial.println(readUltrasonic(TRIG_RIGHT, ECHO_RIGHT), 1);
    }
}
