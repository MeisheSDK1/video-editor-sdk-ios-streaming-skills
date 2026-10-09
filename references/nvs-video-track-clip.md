# NvsVideoTrack and NvsVideoClip

## Object Model

`NvsVideoTrack` owns video or image clips and transitions between adjacent clips. `NvsVideoClip` owns trim, speed, audio volume, image motion, blend properties, and Clip-level effects, captions, and stickers.

## Photos Assets

The string argument named `filePath` can receive a `PHAsset.localIdentifier` for a Photos image or video:

```objc
NSString *identifier = asset.localIdentifier;
NvsVideoClip *clip = [videoTrack appendClip:identifier];
if (clip == nil) {
    // Report permission, availability, identifier, or media compatibility failure.
}
```

- Prefer the identifier for Photos assets instead of exporting a temporary file.
- Verify Photos permission, asset availability, and a non-empty identifier.
- Use a full file path for ordinary local media.
- Check the returned clip from every append, insert, or add operation.

## Remote Media and M3U8

- An ordinary HTTP or HTTPS media URL may be used as the string `filePath`, but preheat it before the append, insert, or add operation because the first remote metadata lookup can be slow.
- On a worker queue, call `NvsStreamingContext.getAVFileInfo` with the complete URL and require a non-`nil` result. This method is a documented cross-thread Context exception.
- After preheating, switch to the main thread before calling any Track append, insert, or add API. Every SDK API must run on the main thread unless its public documentation explicitly marks a thread exception; do not generalize the `getAVFileInfo` exception to another SDK API.
- Validate the URL scheme and completeness, then check the returned `NvsVideoClip`. Network reachability, successful media-info preheat, and a non-`nil` appended clip are separate evidence stages.
- Do not pass a remote `.m3u8` URL directly. Download the `.m3u8` file into an app-accessible local directory first, then pass its local file path.
- The accepted playlist is the Meishe-specific M3U8 format and contains additional parameters beyond a standard M3U8/HLS playlist. Do not claim that an arbitrary standard or third-party playlist is compatible.
- Never guess, synthesize, or silently add Meishe-specific playlist parameters, and never claim automatic conversion from a standard M3U8. Ask the user to contact Meishe technical support for the exact format when its producer or extensions are unknown.
- Handle HTTP status, download failure, cancellation, temporary files, atomic placement, and cleanup. Report download success separately from clip-append success.

## Clip Operations

- Append with `appendClip:` or its trim overload.
- Insert with `insertClip:clipIndex:`.
- Place at a Timeline position with `addClip:inPoint:`.
- Require `0 <= trimIn < trimOut`; all time values use microseconds.
- Use public speed, reverse, image-motion, opacity, blend, fade, and effect APIs only after checking the target clip type.

## Transitions and State

Set a transition using the source clip index; a destination clip must exist. Install packaged transitions before use. Stop conflicting playback or compile state before structural mutations and refresh persisted state after a successful SDK result.
