# Common Types and Cross-Cutting Constraints

## Time

- Editing, playback, seek, caption, sticker, effect, trim, and compile times use `int64_t` microseconds unless a public declaration states otherwise.
- Convert seconds explicitly with `seconds * 1000000` and validate `inPoint`, `outPoint`, `trimIn`, `trimOut`, and `duration` relationships.

## Timeline Resolution

`NvsVideoResolution.imageWidth` must be divisible by 4 and `imageHeight` by 2. `imagePAR` is commonly `{1, 1}`. Select `bitDepth` for the SDR/HDR pipeline.

The Context flag sets the maximum editable pixel area:

- Default: `imageWidth * imageHeight <= 1920 * 1080`.
- With `NvsStreamingContextFlag_Support4KEdit`: `imageWidth * imageHeight <= 3840 * 2160`.

Invalid alignment or an unsupported pixel area causes `createTimeline` to return `nil`.

## Video, Audio, and Compile

- Use `NvsRational` for frame rates and aspect ratios rather than floating-point substitutes.
- `NvsAudioResolution` supplies sample rate, channel count, and sample format. Select values that match the editing target.
- A custom output height requires `NvsCompileVideoResolutionGradeCustom` and a prior `setCustomCompileVideoHeight:` call. The SDK may align the final encoded height.

## Flags, Enums, Coordinates, and Keys

- Combine only flags accepted by the current API domain; do not mix Context, capture, playback, seek, compile, and Timeline-creation flags.
- Verify whether C flags import to Swift as an enum or `OptionSet`.
- Use public `NvsColor`, `NvsRect`, `NvsSize`, and `NvsRational` structures and LiveWindow mapping methods.
- String keys are case- and whitespace-sensitive protocols. Emit only keys verified in public headers, official documentation, or user-authorized public configuration.
