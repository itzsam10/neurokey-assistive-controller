# NeuroKey

NeuroKey is our final-year engineering project exploring a low-cost assistive control system for people who have difficulty using conventional switches, remotes, or joysticks.

The system is being designed to read a voluntary eye, blink, jaw, or facial-muscle signal through an NPG Lite Beast Pack. A reliable detected action can then be used to navigate a simple menu and operate a low-voltage home-control demonstration, request caregiver assistance, or control a small mobility prototype.

## Current status

This project is under active development. We have completed the initial research, system architecture, hardware selection, and an early 3D-printed headset prototype. Hardware inspection and biosignal recording are the next steps.

### Completed

- Defined the problem and intended user group
- Selected the NPG Lite Beast Pack for biosignal acquisition
- Purchased gold electrodes and Ten20 conductive paste
- Developed the initial system architecture and implementation plan
- Created and 3D printed an early headset design
- Defined safety and validation requirements

### In progress

- Inspecting and documenting the available hardware
- Recording jaw EMG and eye-movement EOG signals
- Developing personalized calibration and event detection

### Planned

- Standalone detection on the NPG Lite controller
- Wireless communication with an output controller
- Low-voltage home-control and caregiver-alert demonstrations
- Safety-limited miniature mobility demonstration
- Two-target SSVEP experiment
- Repeatability, response-time, and false-activation testing

## Proposed system

```text
Electrodes
    |
    v
NPG Lite Beast Pack
    |
    | signal filtering and intentional-action detection
    v
Wireless output controller
    |
    +-- low-voltage home-control demonstration
    +-- caregiver assistance alert
    +-- miniature mobility platform
```

A laptop will be used during development for viewing signals, saving recordings, and calibration. The main EOG/EMG demonstration is intended to run on the embedded controller without laptop-based inference.

## Repository layout

- `docs/` — architecture, design decisions, and project updates
- `hardware/` — component information and 3D-model files
- `firmware/` — embedded code for acquisition and output control
- `signal-processing/` — analysis and calibration tools
- `results/` — measured test results
- `media/` — prototype photographs and demonstration media

## Team

- Samith R
- Nithin Patel GB
- Rajmohan RA
- Suhas RM

## Scope and safety

NeuroKey is an academic prototype. It is not a clinically validated medical device or a finished powered-wheelchair controller. Mobility testing is limited to a small, unoccupied platform. Human-connected signal recording is performed with battery-powered acquisition hardware, and all actuator demonstrations use low-voltage circuits.


