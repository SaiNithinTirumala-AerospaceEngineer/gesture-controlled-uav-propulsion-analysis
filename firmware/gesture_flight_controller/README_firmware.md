# Firmware — Gesture Flight Controller

## Hardware requirements

| Component | Specification | Pin |
|---|---|---|
| Arduino Uno | ATmega328P, 16 MHz | — |
| IR gesture sensor | Analogue output, 0–5V | A0 |
| HC-SR04 (front) | Ultrasonic, 2–400 cm | TRIG=2, ECHO=3 |
| HC-SR04 (back) | Ultrasonic, 2–400 cm | TRIG=4, ECHO=5 |
| HC-SR04 (left) | Ultrasonic, 2–400 cm | TRIG=7, ECHO=8 |
| HC-SR04 (right) | Ultrasonic, 2–400 cm | TRIG=A1, ECHO=A2 |
| ESC — Front-left | Simonk 30A, 1000–2000 µs | PWM 9 |
| ESC — Front-right | Simonk 30A, 1000–2000 µs | PWM 10 |
| ESC — Back-left | Simonk 30A, 1000–2000 µs | PWM 11 |
| ESC — Back-right | Simonk 30A, 1000–2000 µs | PWM 12 |
| Camera servo | Standard servo, 0–180° | PWM 6 |

## Motor layout

```
        FRONT
   FL (CW)  FR (CCW)
      9  ↑↑  10
         ||
      11  ↓↓  12
   BL (CCW) BR (CW)
        BACK
```

CW = clockwise, CCW = counter-clockwise.
Diagonal pairs spin the same direction to cancel torque.

## Gesture vocabulary

| Gesture | IR ADC Range | Command | PWM output |
|---|---|---|---|
| Land | 0–100 | Gradual throttle-down | 1000–1500 ramping down |
| Left | 100–200 | Roll left | FL/BL –50, FR/BR +50 |
| Down | 200–300 | Descend | All –50 µs |
| Backward | 400–500 | Pitch back | FL/FR +50, BL/BR –50 |
| Hover | 450–550 | Hold position | All 1500 µs |
| Forward | 500–600 | Pitch forward | FL/FR –50, BL/BR +50 |
| Right | 700–800 | Roll right | FL/BL +50, FR/BR –50 |
| Up | 800–900 | Ascend / take-off | All +50 µs |

## Upload instructions

1. Install [Arduino IDE](https://www.arduino.cc/en/software) v2.x
2. Connect Arduino Uno via USB
3. Open `gesture_flight_controller.ino`
4. Select **Tools → Board → Arduino Uno**
5. Select **Tools → Port → COMx** (your Arduino port)
6. Click **Upload** (Ctrl+U)
7. Open **Serial Monitor** at **9600 baud** to view live state output

## Safety notes

- Always test with propellers removed first
- ESC arming sequence runs on power-up — keep clear for 2 seconds
- Obstacle avoidance threshold: 30 cm — adjust `OBSTACLE_DIST_CM` if needed
- Never run at full throttle indoors without propeller guards
