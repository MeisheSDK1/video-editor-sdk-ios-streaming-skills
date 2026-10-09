# API Call-Order Map

## Timeline

```text
verify license -> choose Context flags -> singleton -> validate resolution
-> create Timeline -> add tracks -> add clips -> connect LiveWindow -> seek/play
-> stop conflicts -> configure compile -> compile -> callbacks -> remove Timeline
```

## Media Path Classification

```text
classify input
-> local file: pass full local path
-> Photos asset: pass non-empty PHAsset.localIdentifier
-> ordinary HTTP/HTTPS media file: worker queue getAVFileInfo(URL) preheat
   -> require non-nil media info -> main thread append/insert/add with complete URL
-> M3U8: download .m3u8 locally -> confirm Meishe-specific extended format
   -> pass local playlist path
-> append/insert/add on main thread -> require non-nil clip -> report the exact failure stage
```

## Capture

```text
permissions -> delegates -> connect Capture LiveWindow -> start preview
-> add Capture effects -> start recording -> recording callbacks -> stop recording
```

## Media Display Size

```text
getAVFileInfo -> require non-nil info and at least one video stream
-> getVideoStreamDimension(0) as stored pixel size
-> getVideoStreamPixelAspectRatio(0) -> require denominator != 0
-> corrected width = stored width * numerator / denominator
-> getVideoStreamRotation(0) -> swap corrected width/height for 90 or 270
-> use corrected display size for aspect, preview, crop, and export geometry
```

## Packaged Material

```text
validate resource/type -> retain delegate owner -> assign weak manager.delegate
-> install/upgrade with assetPackageId output argument
-> inspect immediate start/validation status
-> async install: wait for didFinishAssetPackageInstallation:filePath:type:error:
-> match file path/type -> require final success -> query stable package ID
-> create/apply instance -> edit properties
-> remove instance -> optionally uninstall shared package
```

Do not generate a completion-closure overload. Template packages use the asynchronous completion path regardless of the `sync` argument. Use `didFinishAssetPackageUpgrading:filePath:type:error:` for upgrade completion.

## Custom Compile

```text
stop conflicts -> choose project/task-owned writable cache directory
-> non-resume: clear stale cache -> create cache directory
-> compileConfigurations: enable breakpoint continuation + set cache path
-> setCustomCompileVideoHeight:
-> compileTimeline with Custom grade and compileConfigurations
-> background cancellation: retain cache -> wait for cancellation callback
   -> restart with same output/cache paths and equivalent configuration
-> final success/failure/user cancellation: clear cache -> delegate result
```

## Template Workflow

```text
install Template package -> wait for completion -> require package ID
-> query aspect + footage/caption/compound-caption descriptors recursively
-> adaptive: change aspect -> require success -> query descriptors again
-> create NvsTemplateFootageInfo entries -> create template Timeline -> require non-nil
-> recursively resolve main/internal Timeline objects
-> standard or VariantImageSize geometry post-process
-> edit text/media/source trim/picture crop -> refresh preview
-> compile through Context callbacks -> remove owned Timeline
```

## Default Behaviors (opt-out)

```text
# captions: set defaultCaptionFade = false on the NvsStreamingContext singleton
#   BEFORE the "add captions" step (property, not a method)
verify license -> ... -> singleton -> set defaultCaptionFade=false (if no fade wanted)
-> create Timeline (+ NvsCreateTimelineType_DontAddDefaultVideoTransition if no default transition wanted)
-> enableRenderOrder(byZValue:true) (right after create, if z-ordered rendering wanted)
-> add tracks -> add clips -> setBuiltinTransition(index, withName:"") (per clip, to drop default fade)
-> append image clip -> set imageMotionMode=LetterBoxZoomIn + imageMotionAnimationEnabled=false (or enablePropertyVideoFx(true))
-> connect LiveWindow -> seek/play -> ...
```
