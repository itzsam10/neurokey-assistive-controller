# NeuroKey: current bring-up notes

This page records the current development route and what remains unverified. It is intended to help reproduce the laptop-side EMG test without presenting future stages as completed.

## Current status

- Active route: **NPG Lite Beast Pack → BLE → ChordsPy → LSL → laptop**.
- Preliminary forearm clench detection has been demonstrated on the laptop.
- False activations have occurred during lead movement and ordinary arm movement.
- The laptop sent UDP command datagrams locally. The physical ESP32 receiver and relay were not powered or listening, so end-to-end actuation has not been demonstrated.

The direct Bleak script (`neurokey_direct_ble.py`) was an early experiment with packet loss and operating-system GATT disconnects. Use the ChordsPy/LSL bridge for current acquisition.

## Start the EMG pipeline

From the repository root, use the Python environment where project dependencies are installed.

**Terminal 1 — BLE-to-LSL bridge:**

```powershell
python -m chordspy.connection --protocol ble
```

Connect to the NPG Lite if prompted and leave the bridge running. Confirm that it reports a live stream.

**Terminal 2 — NeuroKey pipeline:**

```powershell
python software/unified_pipeline.py
```

Run diagnostics first. Check the signal at rest and during a comfortable forearm contraction. A large spike alone does not prove a clean muscle signal: touching a snap, pulling a lead, shifting the arm, or changing electrode contact can also cause large changes.

For each recording, keep the arm supported, avoid touching electrode snaps, secure leads to reduce tugging, and note the action, trial, electrode placement, and any movement or connection interruption. Preserve raw recordings unchanged; analyze copies and retain session labels.

## Detector and planned features

The current prototype uses filtered EMG features with a trained classifier/threshold to detect a clench-like event. It can still respond to non-command activity. The team is integrating one-shot latching: a sustained event should fire once, and quiet release should be required before re-arming.

These features are planned, not yet verified:

- Latch and release-state behavior in the live pipeline.
- EOG navigation followed by a 2-second window in which EMG confirmation is enabled.
- EOG, SSVEP, and multimodal integration.
- ESP32 receipt of the laptop's UDP command and physical relay response.
- Car or home-load control.

Do not present the reported 94.44% random-window hold-out result as cross-validation or expected performance on a new session. Its windows overlap by 50%, so adjacent windows may be similar. Validation must hold out complete sessions and include ordinary movement and lead-motion negatives. Report false activations with a defined test duration; do not claim a zero rate.

## Recommended next checks

1. Reproduce the live EMG stream and save a labeled rest/contraction recording.
2. Repeat with fresh electrode placement in a separate session. Include ordinary arm movements and safe lead-motion tests as negative examples.
3. Verify the latch on recorded and live data before sending commands. A sustained contraction must fire once; re-arming must require release.
4. Test UDP reception with the ESP32 and a safe low-voltage indicator/load, without biosignal control. Check STOP, timeout, and Wi-Fi-loss behavior.
5. After those checks pass, combine the EMG event with the 2-second EOG confirmation gate.
6. Add SSVEP and a small unoccupied car demonstrator as later stages; test each modality alone before integration.

Never connect this prototype to a person's powered wheelchair. Keep early output tests low-voltage, stationary, and supervised. Do not wire a microcontroller GPIO directly to a motor, relay coil, or battery voltage.

## References

- [NPG Lite Beast Pack](https://docs.upsidedownlabs.tech/kits/npg-lite-kits/npg-lite-beast/index.html)
- [Chords-Python](https://github.com/upsidedownlabs/Chords-Python)
- [NPG Lite board documentation](https://docs.upsidedownlabs.tech/hardware/bioamp/neuro-play-ground-lite/index.html)
- [OpenBCI Ultracortex Mark IV design](https://github.com/OpenBCI/Ultracortex/tree/master/Mark_IV)
