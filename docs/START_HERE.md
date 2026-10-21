# NeuroKey bring-up: current laptop EMG route

This guide covers the current laptop-side EMG test. It does not start EOG, SSVEP, the output node, or a car.

## Current signal path

```text
NPG Lite Beast Pack → Bluetooth LE → ChordsPy → LSL → laptop pipeline
```

Use the NPG Lite on battery as intended. Place and secure electrodes according to the manufacturer's EMG setup guidance. Keep leads from tugging, support the arm, and do not touch exposed snaps during acquisition. A snap touch or cable pull can create a large artifact that resembles a command.

## Start the stream and pipeline

From the repository root, start the verified bridge in one terminal:

```powershell
python -m chordspy.connection --protocol ble
```

Connect to the Beast Pack if prompted and wait for the LSL stream. In a second terminal, start the laptop pipeline:

```powershell
python software/unified_pipeline.py
```

Run diagnostics first. Record labelled rest and comfortable forearm contractions. Preserve raw files unchanged and note electrode placement, action, session, and any movement or connection issue.

The direct Bleak script `neurokey_direct_ble.py` was an early exploratory route with packet loss and operating-system GATT disconnects; it is not the active acquisition route.

## Current limitations

- Preliminary clench detection runs on the laptop and has produced false activations during lead movement and ordinary arm movement.
- The code's cooldown is not the one-shot latch described in the roadmap.
- The reported 94.44% score is random overlapping-window hold-out accuracy. It is not cross-validation or new-session performance.
- Training features use 500 ms windows, while live inference currently uses 150 ms windows; resolve this mismatch before relying on the score.
- Local UDP sends were exercised without a powered/listening ESP32 receiver. Do not connect this prototype to a car motor or occupied mobility device.

## Next checks

1. Repeat labeled EMG capture after electrode reapplication and include ordinary movement and lead-motion negatives.
2. Verify the training/live window design and compare thresholds with the SVM using held-out sessions.
3. Test one-shot latch and release-to-rearm on logs before allowing commands.
4. Record EOG separately, then test left/right and up/down navigation with a neutral/reject state.
5. Test manual Wi-Fi commands with a safe low-voltage indicator/load. Confirm STOP, timeout, and Wi-Fi loss before connecting any movement load.
6. Add the 2-second EOG-focus/EMG-confirm gate. Attempt EEG/SSVEP only after EOG and EMG stages pass their own checks.

Never connect this prototype to a person's powered wheelchair. Keep early actuator tests low-voltage, stationary, and supervised.
