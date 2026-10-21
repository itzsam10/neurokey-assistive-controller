# Firmware and output integration status

No NeuroKey ESP32/ESP8266 relay or motor receiver firmware is currently verified in this repository.

## What has been tested

The laptop-side EMG pipeline sent UDP datagrams locally to port 4210. During that test the ESP32 receiver and relay were not powered or listening. This verifies only that the laptop code attempted a local UDP send; packet receipt, relay switching, and motor control have not been demonstrated. No sub-millisecond latency measurement was recorded.

## Planned bench sequence

1. Confirm the exact receiver board, motor-driver/relay module, input logic levels, supply ratings, and wiring from their labels and documentation.
2. Implement and test a manual receiver command with the EMG detector disconnected.
3. Use explicit, idempotent commands (for example `LIGHT_ON`, `LIGHT_OFF`, `STOP`) instead of `TOGGLE` for safety-relevant actions.
4. Add sequence numbers or command IDs, stale-command rejection, a local timeout/watchdog, and a physical stop.
5. Test with an LED or other safe low-voltage load; disconnect the motor driver during this stage.
6. Test motors with wheels raised and short time-bounded commands, then test only an unoccupied small platform in a clear area.
7. Connect the biosignal controller only after manual communications and fault behavior pass.

A Wi-Fi link is not itself a safety mechanism: the receiver must stop locally if packets become stale or the connection disappears. Do not use this academic prototype with a person's powered wheelchair.
