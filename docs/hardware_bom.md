# Hardware Bill of Materials

## Propulsion system

| Component | Model | Specification | Qty | Role |
|---|---|---|---|---|
| Frame | F450 | 450mm wheelbase, fibreglass arms | 1 | Structural chassis |
| Motor | A2212 1400KV | BLDC, 2–3S, max 12A continuous | 4 | Thrust generation |
| Propeller | 10×4.5 inch | CW + CCW pair | 2 pairs | Lift |
| ESC | Simonk 30A | 30A continuous, 1000–2000 µs PWM | 4 | Motor speed control |
| Battery | LiPo 3S 5000 mAh | 11.1V nominal, 20C discharge | 1 | Power source |
| PDB | XT60 PDB | 4× ESC outputs, 5V BEC | 1 | Power distribution |

## Control and sensing

| Component | Model | Specification | Qty | Role |
|---|---|---|---|---|
| Flight controller | Arduino Uno | ATmega328P, 16 MHz, 32KB flash | 1 | Main controller |
| Gesture sensor | IR analogue | 0–5V output, A0 input | 1 | Hand gesture input |
| Ultrasonic sensor | HC-SR04 | 2–400 cm, 15° beam angle | 4 | Obstacle detection |
| Camera servo | SG90 | 9g, 180° rotation | 1 | Gimbal/camera |

## Wiring summary

```
Battery (3S LiPo)
    │
    ├── PDB ──── ESC FL (pin 9)  ──── Motor FL (CW)
    │       ├── ESC FR (pin 10) ──── Motor FR (CCW)
    │       ├── ESC BL (pin 11) ──── Motor BL (CCW)
    │       └── ESC BR (pin 12) ──── Motor BR (CW)
    │
    └── 5V BEC ─── Arduino Uno
                        │
                        ├── A0  ← IR gesture sensor
                        ├── 2,3 ← HC-SR04 front (TRIG, ECHO)
                        ├── 4,5 ← HC-SR04 back  (TRIG, ECHO)
                        ├── 7,8 ← HC-SR04 left  (TRIG, ECHO)
                        ├── A1,A2 ← HC-SR04 right (TRIG, ECHO)
                        └── 6   → Camera servo signal
```

## Motor rotation directions

```
        FRONT
  FL ↺ ─────── ↻ FR
  (CW)         (CCW)
    │             │
  BL ↻ ─────── ↺ BR
  (CCW)        (CW)
        BACK
```

Diagonal pairs spin in opposite directions to cancel yaw torque.