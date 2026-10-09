# Editor Runtime Pitfalls

## Remote Media Classification

- Before using an ordinary HTTP/HTTPS media-file URL as an SDK clip path, call `getAVFileInfo` on a worker queue to preheat the slow network metadata lookup. Require non-`nil` media info, then switch to the main thread to append and check the returned clip.
- Never perform the first network `getAVFileInfo` lookup on the main thread. Every other SDK call in this flow must return to the main thread unless its own public documentation explicitly marks a thread exception.
- Do not pass a remote M3U8 URL directly. Download the `.m3u8` file locally first and require confirmation that it uses the Meishe-specific format with its additional parameters.
- Do not treat generic HLS conformance as Meishe-format conformance, synthesize undocumented parameters, or claim automatic conversion. Refer unknown format details to Meishe technical support.

## PixelAspectRatio and Display Size

- `getVideoStreamDimension` is the stored pixel size, not necessarily the display size. Do not use it alone for aspect selection or layout.
- Require a video stream and a nonzero PixelAspectRatio denominator, scale width by `num / den`, then swap width and height for 90° or 270° rotation.
- Do not apply rotation before the PAR correction, scale both axes, divide by zero, or silently treat a malformed PAR as verified geometry.

- Do not seek a zero-duration Timeline after deleting its final clip; clear preview and show an empty state.
- Do not remove only UI overlays; remove the corresponding SDK caption/sticker/effect and persisted descriptor.
- Keep ordinary, modular, and compound caption workflows separate.
- Use LiveWindow mapping for gestures; never write UIKit coordinates directly to SDK objects.
- Keep material installation separate from application. Wait for asynchronous completion before querying or applying a package ID.
- Voiceover is incomplete until the recorded file is inserted into an audio track and participates in preview/export.
- Persist stable target relations so captions, stickers, transitions, and effects can be rebuilt after process restoration.
- Stop playback, seek, capture, or compile conflicts before structural editing.

## Default behaviors (opt-out)

The SDK enables several visual behaviors by default; disable them only with the documented opt-out calls.

- Captions fade in by default: to disable, fetch the `NvsStreamingContext` singleton and set `defaultCaptionFade` to `NO`/`false` **before** adding captions (this is a property, not a method).
- Appended clips get a default Fade transition between them: opt out by creating the Timeline with the `NvsCreateTimelineType_DontAddDefaultVideoTransition` flag, or after appending call `setBuiltinTransition:withName:@""` on the video track for that clip.
- Effects render in add order by default: to render by z-value, call `NvsTimeline.enableRenderOrder(byZValue:true)` right after creating the Timeline. When z-values tie, the order is timeline filter → animated sticker → timeline caption (incl. modular caption) → compound caption.
- Image clips zoom by default: after appending an image via `appendClip:`, set `imageMotionMode = NvsStreamingEngineImageClipMotionMode_LetterBoxZoomIn` and `imageMotionAnimationEnabled = false` (requires feature authorization) to disable, or call `enablePropertyVideoFx(true)` to drive motion via property video fx instead.
