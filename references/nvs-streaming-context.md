# NvsStreamingContext

## Responsibility and Lifetime

`NvsStreamingContext` is the global Streaming SDK singleton for license-gated initialization, capture, human detection, Timeline creation, playback, seek, compilation, engine state, and asset-package access.

- Call `+[NvsStreamingContext verifySdkLicenseFile:]` before obtaining the singleton.
- Use `sharedInstance` or `sharedInstanceWithFlags:` once and keep flags stable.
- Keep public Context calls on the main thread unless a header explicitly permits an exception.
- Set the appropriate delegates and use callbacks as final evidence for asynchronous operations.
- Do not destroy the singleton during ordinary view-controller transitions.

## Initialization and Timeline Capacity

```objc
BOOL licensed = [NvsStreamingContext verifySdkLicenseFile:licensePath];
if (!licensed) { return; }
NvsStreamingContext *context =
    [NvsStreamingContext sharedInstanceWithFlags:NvsStreamingContextFlag_Support4KEdit];
context.delegate = self;
```

- Default Timeline capacity is `width * height <= 1920 * 1080`.
- With `NvsStreamingContextFlag_Support4KEdit`, capacity is `width * height <= 3840 * 2160`.
- Choose the flag before creating any Timeline. A later Timeline parameter change cannot enable the capability.

## Capture Chain

```text
permission callbacks -> capture delegates -> connect LiveWindow
-> startCapturePreview -> add Capture captions/stickers/effects
-> startRecording or startRecordingWithFx -> recording callbacks -> stopRecording
```

Check each `BOOL` start result. `startRecording:` and `startRecordingWithFx:` have different effect-output semantics. Keep recording configuration keys within the recording domain.

## Timeline Chain

```text
createTimeline -> append tracks and clips -> connectTimeline:withLiveWindow:
-> seek/playback -> stop conflicts -> compile -> removeTimeline:
```

All editing and engine times are microseconds. Check Timeline creation and connection return values before using child objects.

## Custom Compile Height

```objc
[context setCustomCompileVideoHeight:outputHeight];
BOOL started = [context compileTimeline:timeline
                              startTime:0
                                endTime:timeline.duration
                         outputFilePath:outputPath
                   videoResolutionGrade:NvsCompileVideoResolutionGradeCustom
                      videoBitrateGrade:NvsCompileBitrateGradeHigh
                                  flags:0];
```

The start result is not final completion. Handle progress, completion, and failure through the delegate. The encoded height may be aligned.

## Breakpoint-Continuation Compile

Use the `compileConfigurations` overload for every resumable Timeline compile. Both configuration entries are required:

```objc
NSMutableDictionary *config = [NSMutableDictionary dictionary];
config[NVS_COMPILE_ENABLE_BREAKPOINT_CONTINUATION] = @YES;
config[NVS_COMPILE_CACHE_FILE_PATH] = cachePath;

[context setCustomCompileVideoHeight:outputHeight];
BOOL started = [context compileTimeline:timeline
                              startTime:0
                                endTime:timeline.duration
                         outputFilePath:outputPath
                   videoResolutionGrade:NvsCompileVideoResolutionGradeCustom
                      videoBitrateGrade:NvsCompileBitrateGradeHigh
                  compileConfigurations:config
                                  flags:0];
```

- Require a non-empty, writable cache directory owned by the current project or export task.
- Before a new non-resume compile, remove stale contents and recreate the directory.
- If entering the background causes the SDK to stop and report cancellation, retain the cache and wait for that cancellation callback before restarting with the same output path, cache path, and equivalent compile configuration.
- A user cancellation is final and must not resume.
- Remove the cache directory after final success, final failure, user cancellation, or failure to start/restart. Do not remove it for the background cancellation that will be resumed.
- `NVS_COMPILE_CACHE_FILE_DURATION` and `NVS_COMPILE_CACHE_FILE_SIZE` are optional tuning keys; their documented minimums and defaults do not replace the two required entries above.

## Human Detection

Initialize only the required public detection features and data, using matching model and license inputs. Check every return value, avoid hard-coded model filenames, and call `closeHumanDetection` when the feature is no longer needed.

## Failure Checklist

- License verification happened after singleton creation.
- Singleton flags do not support the requested Timeline area.
- A stateful API was called off the allowed thread.
- Preview/playback started before output connection.
- An asynchronous start result was treated as completion.
- Custom compile grade was used without custom height.
- Breakpoint continuation enabled without a non-empty writable cache path, or stale/final cache was not cleaned according to the compile outcome.
