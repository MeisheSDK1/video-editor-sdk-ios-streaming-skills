# NvsTimeline

## Responsibility

`NvsTimeline` is the editing container for video/audio tracks, Timeline captions, compound captions, animated stickers, video effects, themes, and graph compositors. Create and remove it through `NvsStreamingContext`.

## Creation

```objc
NvsVideoResolution videoRes = {0};
videoRes.imageWidth = width;
videoRes.imageHeight = height;
videoRes.imagePAR = (NvsRational){1, 1};
NvsRational fps = {30, 1};
NvsAudioResolution audioRes = {48000, 2, NvsAudSmpFmt_S16};
NvsTimeline *timeline = [context createTimeline:&videoRes
                                       videoFps:&fps
                                    audioEditRes:&audioRes];
if (timeline == nil) { return; }
```

Require width divisible by 4, height divisible by 2, and pixel area within the Context flag limit.

## Tracks and Timeline Objects

- Add tracks with `appendVideoTrack` and `appendAudioTrack`; query and remove by the public index APIs.
- Add Timeline captions, compound captions, stickers, and effects only through Timeline-level APIs.
- Install packaged resources first, then use the matching package type and package ID.
- Use microseconds for `inPoint`, `duration`, and query positions.
- Do not mix Track/Clip-local time with Timeline time.

## Geometry, State, and Removal

Any video-size change must retain alignment and Context capacity. Re-evaluate LiveWindow fill mode, coordinate mapping, and compile height after a geometry change.

Stop conflicting engine operations before structural mutation. When finished, call `[context removeTimeline:timeline]` according to the declared ownership contract. Never continue using child objects after removal.
