# Laptop software

`unified_pipeline.py` is a development snapshot of the laptop-side forearm EMG pipeline. It connects to the LSL stream, records labelled data, trains an RBF-SVM, and can dispatch a UDP datagram when its current event criteria are met.

This snapshot is **experimental**. It has no verified one-shot latch or two-second EOG context gate, and its live 150 ms windows do not match the 500 ms windows used for training. The reported random-window score is not a new-session performance estimate. False activations have been observed during lead movement and ordinary arm movement.

The UDP receiver and relay were not powered/listening during the local test. Keep any output disconnected while validating the detector. Do not use this code to control a powered wheelchair or safety-critical device.

## Run the laptop prototype

Install the dependencies listed in the repository's `requirements.txt`, and install/configure the upstream ChordsPy BLE bridge separately. From the repository root, run:

```powershell
python -m chordspy.connection --protocol ble
```

Then in another terminal:

```powershell
python software/unified_pipeline.py
```

Run diagnostics and recording first. The data and model paths are relative to the current working directory, so launch from the repository root.
