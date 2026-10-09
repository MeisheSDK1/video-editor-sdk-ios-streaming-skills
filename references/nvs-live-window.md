# NvsLiveWindow

`NvsLiveWindow` is the display and coordinate-mapping target for capture or Timeline preview. It does not own the Context or Timeline.

## Connection and Geometry

- Connect capture with `connectCapturePreviewWithLiveWindow:`.
- Connect editing with `connectTimeline:withLiveWindow:`.
- Connect only after the LiveWindow is attached to a visible window and has non-empty bounds. In UIKit, perform the connection from `viewDidAppear:` or an equivalent post-layout callback. Connecting a zero-sized or non-drawable Metal-backed LiveWindow can abort during render-pass creation.
- Require a successful connection before preview, playback, or seek.
- Select fill mode with Timeline aspect ratio, media ratio, and visible container geometry considered together.
- Stop engine use before releasing the view.

## Coordinate Mapping

Use public canonical/view and normalized/view mapping methods for caption and sticker hit testing, dragging, scaling, and rotation. Never pass UIKit gesture coordinates directly to Timeline objects.

Use `clearVideoFrame` for the final-clip empty state and reconnect when media is added. Treat screenshots as visual evidence only for the exact frame and flow captured.
