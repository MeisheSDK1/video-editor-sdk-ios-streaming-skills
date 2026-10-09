# Thumbnail, Icon, and Waveform Generators

## Icon Generation

Use `NvsIconGenerator` asynchronous icon requests, retain task IDs, consume delegate results, and cancel stale tasks. Timestamps use microseconds. Use only public flags supported for the chosen media identifier.

## Waveform Generation

Use `NvsWaveformDataGenerator` to query duration/sample count and request grouped waveform data. Choose group size from the visible zoom level and avoid unbounded main-thread work. Associate callbacks with task IDs.

## Thumbnail Sequence Views

Timeline sequence descriptions use microsecond `inPoint`, `outPoint`, `trimIn`, and `trimOut`. Use the view's Timeline/X mapping and anchored scaling APIs. Reject callbacks belonging to recycled UI state.
