# Gesture Command Reference

## Gesture vocabulary — 8 commands

| # | Gesture | IR ADC Range | Flight Command | Motor Response |
|---|---|---|---|---|
| 1 | Land | 0–100 | Gradual throttle-down to ground | All motors ramp from current → 1000 µs |
| 2 | Left | 100–200 | Roll left | FL/BL: –50 µs · FR/BR: +50 µs |
| 3 | Down | 200–300 | Descend | All: –50 µs |
| 4 | Backward | 400–500 | Pitch backward | FL/FR: +50 µs · BL/BR: –50 µs |
| 5 | Hover | 450–550 | Hold position | All: 1500 µs (fixed) |
| 6 | Forward | 500–600 | Pitch forward | FL/FR: –50 µs · BL/BR: +50 µs |
| 7 | Right | 700–800 | Roll right | FL/BL: +50 µs · FR/BR: –50 µs |
| 8 | Up | 800–900 | Ascend / take-off | All: +50 µs · ramp on first command |

## Recognition accuracy by gesture

| Gesture | FB Method | ML Method | Flying UAV |
|---|---|---|---|
| Up | 92.5% | 95.0% | 88.0% |
| Down | 90.0% | 93.5% | 85.5% |
| Forward | 88.5% | 92.0% | 84.0% |
| Backward | 87.0% | 91.5% | 83.0% |
| Left | 89.5% | 93.0% | 85.0% |
| Right | 90.5% | 94.0% | 86.0% |
| Hover | 94.0% | 96.5% | 90.5% |
| Land | 95.5% | 97.0% | 91.0% |
| **Mean** | **90.9%** | **94.1%** | **86.6%** |

Source: Report Tables 2.6.1, 2.6.2, 2.6.3 and literature review
(Togo & Ukida 2022, Lee & Yu 2023).

## Safety behaviour

- Gestures are ignored when `isFlying = false` except **Up** (take-off)
  and **Hover** (arm + hold)
- **Obstacle detected** → command overridden with Hover, warning printed
  to serial at 9600 baud
- Unknown ADC value (outside all bands) → state held, no motor change
- All PWM outputs constrained to 1000–2000 µs regardless of input