# Concept

## Hardware connections

- **Mac**: connects through AirPlay to Pi
- **Pi**: runs Shairplay Sync, connects through AUX to speaker
- **Acton III**: the speaker
- **Microphone**: we have a small one, let's keep that one for now
  - Could upgrade to a microphone array, or perhaps dispersed throughout the room?

## Software

- On the Pi:
  - **Wake word detection**: openWakeWord still works, although we could switch to an alternative if the accuracy is not high enough with 16-bit audio.
  - **Text to speech (TTS)**: Piper (possibly alternatives if not natural-sounding enough)
- If delay is noticable, a quick mode for preset commands would help

## Problems

- If we want to be able to interrupt Bobot, we need to cancel its own sound. This is fortunately feasible since the delay is known and consistent.

## Ideas / envisioned use cases

- Wake word detection should be very fast, so that you don't have to wait before speaking your query
- Speaker recognition!
- Could look into Home Assistant to integrate with other devices?
- It could be proactive: if it's going to rain, warn before you're about to leave the house
- Integrate with calendar
- Expand to multiple rooms
- Improve wake word detection over time
  - This resets once the microphone changes though

# MVP checklist

- [ ] install shairport on pi and connect to acton permanently
- [ ] connect mic to pi directly (skip board)
- [ ]
