# Hardware

## Available project hardware

- NPG Lite Beast Pack biosignal-acquisition kit
- Ten20 conductive electrode paste
- Surface gel electrodes
- Gold electrodes reported for later EEG experiments
- 3D-printed headset prototyping frame
- NodeMCU development board
- Relay module and jumper wires
- Miniature car/chassis available for inspection and rebuilding

Board revisions, electrical ratings, motor-driver type, and battery details will be added only after the labels have been physically checked.

## Headset prototype

The current white headset was printed as an early mechanical prototype based on the [OpenBCI Ultracortex Mark IV](https://github.com/OpenBCI/Ultracortex/tree/master/Mark_IV). It is being used to study fit, electrode-position access, cable routing, and possible mounting positions. The original geometry is not claimed as a NeuroKey design. OpenBCI's Ultracortex repository identifies Aaron Trocola, Conor Russomanno, Joel Murphy, and Aaron Lehr as designers and engineers and distributes the files under the [GNU GPL v3.0 licence](https://github.com/OpenBCI/Ultracortex/blob/master/LICENSE.md).

The printed surface contains visible support marks and rough areas. This is acceptable for checking geometry, but the frame requires finishing and a comfort/safety inspection before anyone wears it for testing.

## Acquisition platform

The NPG Lite Beast Pack is an open-source biosignal development platform from Upside Down Labs. Official documentation describes six input channels and electrode configurations for EMG, EOG, and EEG. NPG Lite firmware and Chords are being used as the acquisition and visualization foundation. NeuroKey will modify and integrate only the parts required for its calibrated assistive-control workflow.

References:

- [NPG Lite Beast Pack documentation](https://docs.upsidedownlabs.tech/kits/npg-lite-kits/npg-lite-beast/index.html)
- [NPG Lite Arduino firmware](https://github.com/upsidedownlabs/NPG-Lite-Arduino-Firmware)
- [Chords Web](https://chords.upsidedownlabs.tech/)

