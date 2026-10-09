# Effect Class Families

## Choose the Owner First

| Owner | Typical effect scope |
|---|---|
| `NvsStreamingContext` | Capture effects and capture beauty |
| `NvsVideoClip` | Clip effects and clip beauty |
| `NvsVideoTrack` | Track effects |
| `NvsTimeline` | Timeline-range effects |
| `NvsAudioClip` | Audio effects |

The same user term, such as “filter,” maps to different APIs, time domains, and lifetimes at each level.

## Effect Identity and Parameters

- Built-in effects use a public effect name.
- Packaged effects require prior installation and a package ID of the correct type.
- Beauty uses dedicated public creation APIs.
- Custom effects use an object implementing the public renderer protocol.
- Parameter keys are case- and whitespace-sensitive. Verify the key, type, range, and effect family before emission.
- Do not copy Capture keys to Clip/Track/Timeline effects or mix basic Beauty and AR Scene parameter systems.

Effect order changes rendering. Preserve indexes and re-check the result after insertion, move, or removal.
