# NvsAudioTrack and NvsAudioClip

`NvsAudioTrack` owns music, voiceover, and other audio clips. A clip can own Audio Fx; adjacent audio clips can have an `NvsAudioTransition`.

## Core Operations

- Append, insert, or place clips using a full, accessible file path.
- Use microseconds for trim and Timeline positions; require `trimIn < trimOut` within source bounds.
- Check every returned `NvsAudioClip`.
- Set left/right channel volume and speed through public Track/Clip APIs. Preserve pitch only when requested and supported by the chosen overload.
- Add built-in or custom Audio Fx through Audio Clip methods, never Video Fx methods.
- Add transitions only when the following audio clip exists; query the returned transition to confirm application.

Voiceover is complete only after the recorded file is inserted on an audio track, persisted, previewed, and included in compile output.
