# Media Convertors

## NvsMediaFileConvertor

Create the convertor, set its delegate, start with the exact public selector spelling, retain the task ID, and handle progress, completion, failure, and cancellation. Do not “correct” an unusual selector spelling when the public header uses it.

## NvsPassthroughConvertor

Use passthrough only when source codecs, containers, tracks, and requested operation meet the public contract. Build valid file-info inputs, retain the task ID, and handle error code/string and cancellation.

Use Timeline plus `compileTimeline` for editing, effects, captions, multitrack composition, or re-rendering. Use ordinary conversion for format conversion; consider passthrough only when rendering is unnecessary and compatibility is confirmed.
