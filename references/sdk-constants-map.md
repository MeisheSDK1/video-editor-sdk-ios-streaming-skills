# SDK Constants Map

Keep only public, header-verified constants in generated code.

Critical constants include:

- `NvsStreamingContextFlag_Support4KEdit`
- `NvsCompileVideoResolutionGradeCustom`
- public compile bitrate grades selected by the user requirement
- `NVS_COMPILE_ENABLE_BREAKPOINT_CONTINUATION` and `NVS_COMPILE_CACHE_FILE_PATH` together for resumable compilation
- optional `NVS_COMPILE_CACHE_FILE_DURATION` and `NVS_COMPILE_CACHE_FILE_SIZE` only when the caller requests cache-segment tuning
- public audio sample formats used by `NvsAudioResolution`
- public asset package types matching the requested material
- public capture/playback/seek/compile flags accepted by the chosen overload

String parameters for effects, AR, recording, and compile are case-sensitive protocols. Verify each key and domain before use; do not treat this file as an exhaustive undocumented key table.
