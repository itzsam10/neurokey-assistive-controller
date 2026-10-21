# Hardware inventory and status

Only use ratings confirmed from the physical board labels and manufacturer documentation. This list records the team's reported inventory; unknown electrical ratings remain unknown until photographed and checked.

## Biosignal acquisition

- **NPG Lite Beast Pack:** firmware flashed; BLE signal display and ChordsPy/LSL laptop acquisition demonstrated.
- **Electrodes and paste:** Ten gold electrodes, disposable gel electrodes, and Ten20 paste are available. Forearm EMG has been recorded with surface electrodes. Gold-cup scalp EEG has not been validated.
- **Printed headset:** an OpenBCI Ultracortex-derived frame has been printed. It is an early mechanical study model and is not a required part of the current EMG/EOG stage. Do not assume it fits the gold electrodes or has been validated for EEG.

## Output and mobility parts

Reported as available or intended for the later demonstrator:

- NodeMCU ESP8266 development board.
- HW-130 motor-driver board (exact model/revision and ratings still need a clear label check).
- Four dual-shaft DC gear motors (voltage/current ratings not recorded here).
- Relay module and jumper wires (input voltage and contact ratings unverified).
- A friend's small car/chassis may be available as a base; the project car has not been built or wired.
- No verified motor battery/power solution has been selected for the four-motor platform.

The old sealed lead-acid battery measured about 0.64 V and should be treated as unusable pending proper battery testing/replacement. Do not use the old power bank or an unverified battery as the motor supply. Before ordering or wiring a supply, record motor rated voltage and stall current, driver continuous/peak current, battery chemistry/series count, connector polarity, and an appropriate fuse.

## Safe output architecture

The ESP8266/ESP32 GPIO must only drive a compatible logic input or a properly designed driver stage; it must not directly drive a motor, relay coil, or battery voltage. Test the receiver first with a low-voltage indicator/load, with the motor stage disconnected. Use explicit commands such as `MOTOR_STOP`, bounded movement time, a local watchdog timeout, and a physical stop. Avoid toggle-only commands for motion or safety outputs.

No physical output test has been completed. See [firmware status](../firmware/README.md).
