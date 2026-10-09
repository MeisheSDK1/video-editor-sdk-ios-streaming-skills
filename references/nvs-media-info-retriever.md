# Media Information, Retrievers, and Receivers

- Use `NvsStreamingContext.getAVFileInfo:` to obtain `NvsAVFileInfo`; handle `nil` and inspect duration, size, PAR, frame rate, rotation, bit depth, codec, HDR, sample rate, and channel information as needed.
- For display size, first require at least one video stream. Read the stored size with `getVideoStreamDimension:`, then read `getVideoStreamPixelAspectRatio:` and require `den != 0`. Multiply the width by `num / den`; do not scale the height.
- After applying PixelAspectRatio, read `getVideoStreamRotation:`. Swap the corrected width and height for `NvsVideoRotation_90` or `NvsVideoRotation_270`.
- Use the corrected result for Timeline aspect selection, preview layout, crop coordinates, and export geometry. Use the raw stored dimension only when the caller explicitly needs encoded pixel dimensions.
- Create `NvsVideoFrameRetriever` through the Context. Use microseconds, configure tolerance, and choose a public height grade or explicit height.
- `getAVFileInfo` is a documented exception to the Context main-thread rule. For an ordinary HTTP/HTTPS media file, call it on a worker queue before insertion because network metadata retrieval may be slow; require a non-`nil` result, then return to the main thread for Track/Timeline mutation.
- Apply this thread exception only to the documented retrieval call. Every SDK API without an explicitly documented thread exception must run on the main thread; do not generalize this exception to another Context or non-Context SDK API.
- Use `NvsMediaFileVideoRetriever` for asynchronous segment decoding with task IDs, progress, completion, cancellation, and close.
- Use `NvsVideoFrameReceiver` only with correct frame format, rotation, timestamp, ownership, and callback-thread handling. Avoid blocking work in frame callbacks.
- Classify remote media before inspection or Timeline insertion. Ordinary HTTP/HTTPS media URLs may be SDK paths, but an M3U8 playlist must first be downloaded locally and must use the Meishe-specific extended format. Do not infer compatibility from the `.m3u8` extension or from standard HLS validity.
