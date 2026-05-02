# Gesture-Controlled UAV — Propulsion System Analysis Using AIML

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Arduino](https://img.shields.io/badge/Firmware-Arduino%20Uno-teal)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## Problem statement

Conventional drone controllers require dedicated hardware and pilot training,
limiting accessibility and operational flexibility. This project designs and
analyses the propulsion system of a gesture-controlled quadrotor UAV, using
AIML (Artificial Intelligence and Machine Learning) techniques to model
thrust-to-weight ratio, power consumption, battery sizing, and payload
capacity — and an Arduino Uno-based gesture recognition pipeline to translate
hand commands into flight control signals.

---

## System overview

*Repository under active development — results, firmware, and full
documentation will be added in subsequent commits.*

---

## Repository structure

```
gesture-controlled-uav-propulsion-analysis/
├── src/                              ← Python analysis modules
│   ├── propulsion_analysis.py        ← Core AIML model — 8 propulsion metrics
│   ├── thrust_weight_analysis.py     ← T/W ratio deep-dive + design heatmap
│   ├── power_consumption_analysis.py ← Motor vs gesture system power split
│   ├── battery_sizing_analysis.py    ← Capacity, voltage, flight time trade
│   ├── payload_analysis.py           ← Payload vs T/W safety envelope
│   └── gesture_performance.py        ← Recognition accuracy + confusion matrix
├── firmware/
│   └── gesture_flight_controller/
│       ├── gesture_flight_controller.ino  ← Complete Arduino firmware
│       └── README_firmware.md             ← Wiring + upload guide
├── data/                             ← CSV input files
├── results/                          ← Generated plots
├── assets/
│   ├── hardware/                     ← Component photographs
│   └── solidworks/                   ← CAD views
├── docs/
│   ├── methodology.md
│   ├── hardware_bom.md
│   └── gesture_command_table.md
├── requirements.txt
└── LICENSE
```

---

## How to run

```bash
git clone https://github.com/SaiNithinTirumala-AerospaceEngineer/gesture-controlled-uav-propulsion-analysis.git
cd gesture-controlled-uav-propulsion-analysis
pip install -r requirements.txt

python src/propulsion_analysis.py
python src/thrust_weight_analysis.py
python src/power_consumption_analysis.py
python src/battery_sizing_analysis.py
python src/payload_analysis.py
python src/gesture_performance.py
```

---

## References

- Hadri, S. (2018) *Hand Gestures for Drone Control Using Deep Learning*. University of Oklahoma.
- Lee, J-W. and Yu, K-H. (2023) Wearable Drone Controller: Machine Learning-Based Hand
  Gesture Recognition and Vibrotactile Feedback. *Sensors*, 23(5), 2666.
- Togo, S. and Ukida, H. (2022) UAV manipulation by hand gesture recognition.
  *SICE Journal of Control, Measurement, and System Integration*, 15(2), 145–161.
- Chen, Y-L. et al. (2022) Development, Control Adjustment, and Gesture Recognition
  of a Quadrotor Helicopter. *International Journal of Automation and Smart Technology*.