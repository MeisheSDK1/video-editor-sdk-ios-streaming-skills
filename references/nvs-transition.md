# Video and Audio Transitions

Video transitions live on `NvsVideoTrack` between adjacent `NvsVideoClip` objects. Use the source clip index with built-in, packaged, or custom transition APIs. Query the transition and actual duration after setting it.

Audio transitions live on `NvsAudioTrack`; never mix video and audio transition objects.

## Guards

- The source clip must have a following destination clip.
- Install a packaged transition with the correct asset type before using its package ID.
- Use a public built-in transition name for built-in transitions.
- Trim, speed, and available source material may limit the actual transition duration.
- A final clip cannot have an outgoing transition.
