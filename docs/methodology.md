# Methodology — Gesture-Controlled UAV Propulsion Analysis

## Overview

This project uses a two-phase approach: propulsion system design and
AIML-based analysis in Python, combined with an Arduino Uno gesture
recognition pipeline for flight command translation.

---

## Phase 1 — Propulsion System Design

### Component selection rationale

Three component categories were evaluated before final selection:

**ESC selection** — three candidates compared on current rating, weight,
and cost. Simonk 30A selected for its continuous current headroom over
the A2212 1400KV motor's peak draw (~18A per motor), reliability in
open-loop speed control, and compatibility with standard 1000–2000 µs
PWM protocol.

**Motor selection** — A2212 1400KV selected over higher-KV alternatives.
At 3S LiPo (11.1V), 1400KV gives ~15,500 RPM unloaded, producing
sufficient thrust for a 450mm frame carrying a 0.5–1.0 kg payload with
T/W > 1.5. Higher KV motors (2300KV) were rejected — excessive RPM on
10-inch propellers would breach structural limits.

**MCU selection** — Arduino Uno selected over Raspberry Pi Zero and
ESP32. The ATmega328P's hardware PWM outputs on pins 9–12 provide
precise ESC signal generation without OS scheduling jitter, which is
critical for stable motor control. The Uno's 16 MHz clock gives
sufficient throughput for the 10 Hz control loop.

### Propulsion sizing

| Parameter | Value | Basis |
|---|---|---|
| Frame | F450, 450mm wheelbase | — |
| Motor | A2212 1400KV BLDC | KV × V_pack |
| Propeller | 10×4.5 inch | Frame geometry |
| ESC | Simonk 30A | Motor peak draw |
| Battery | 3S LiPo, 5000 mAh | Endurance target |
| Target T/W | > 1.5 | Hover + manoeuvre margin |
| Target endurance | > 15 minutes | Mission requirement |

---

## Phase 2 — AIML Propulsion Analysis Model

### Model architecture

The Python AIML model (`propulsion_analysis.py`) processes 20 flight
samples and computes 8 propulsion metrics from first principles:

```
drone_propulsion_data.csv
        │
        ├── Thrust-to-Weight Ratio    = Thrust_N / Weight_N
        ├── Flight Time               = (mAh / (I × 1000)) × 60 × 0.8
        ├── Motor Power Consumption   = (RPM / 1000) × Current_A
        ├── Gesture System Power      = P_gesture × Gesture_flag
        ├── Total Power               = Motor_P + Gesture_P
        ├── Battery Capacity          = mAh / 1000
        ├── Battery Voltage           = Total_P / Current_A
        └── Payload Consideration     = (m_payload × g) / Thrust_N
```

The 0.8 factor in flight time represents 80% usable depth of discharge —
the safe operational limit for LiPo cells to prevent capacity degradation.

### Key finding — gesture system power overhead

The GSPC (Gesture System Power Consumption) metric is unique to this
project. It quantifies the electrical overhead introduced by the gesture
recognition pipeline (IR sensor + ADC sampling + serial transmission)
on the total power budget. Mean GSPC = 2.05 W, representing ~1.6% of
total system power — negligible overhead for the functionality gained.

---

## Phase 3 — Gesture Recognition Pipeline

### IR sensor classification

The gesture recognition uses threshold-band classification on the IR
sensor ADC output (10-bit, 0–1023 counts). Each of the 8 gesture classes
occupies a distinct, non-overlapping ADC range, enabling deterministic
classification without a trained ML model on the Arduino.

### Recognition accuracy

Three evaluation conditions from the literature review:

| Condition | Mean Accuracy | Notes |
|---|---|---|
| Feature-Based (FB) | 90.9% | FFT + position features, static |
| Machine Learning (ML) | 94.1% | Threshold classifier, static |
| Flying UAV | 86.6% | Real flight — vibration and noise |

The 7.4% degradation under flying conditions is due to motor vibration
coupling into the IR sensor mount and hand tremor during flight.
This is consistent with Togo & Ukida (2022) who observed similar
degradation under rotor wash conditions.

---

## Limitations and future scope

- IR sensor gesture recognition is sensitive to ambient light variation —
  a IMU-based wearable controller (accelerometer + gyroscope) would
  provide environment-independent recognition
- Arduino Uno's 10 Hz control loop limits attitude response bandwidth —
  a 32-bit flight controller (STM32 F4) running at 1 kHz is the natural
  upgrade path
- Propulsion model uses empirical power scaling — a validated motor
  characterisation test (thrust stand measurement) would improve accuracy
- NSGA-II multi-objective optimisation across motor KV, propeller pitch,
  and battery cell count is the primary algorithmic extension planned

---

## References

- Lee, J-W. and Yu, K-H. (2023) Wearable Drone Controller. *Sensors* 23(5).
- Togo, S. and Ukida, H. (2022) UAV manipulation by hand gesture recognition.
  *SICE Journal* 15(2), 145–161.
- Chen, Y-L. et al. (2022) Development, Control Adjustment, and Gesture
  Recognition of a Quadrotor Helicopter. *IJAST*.