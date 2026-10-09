# API Constraint Map

| Area | Guard |
|---|---|
| Context | license first; stable singleton flags; main thread by default |
| Timeline | width % 4 == 0; height % 2 == 0; pixel area within Context capacity; check `nil` |
| Photos clip | permission, live `PHAsset`, non-empty local identifier, returned clip non-`nil` |
| Remote media path | ordinary HTTP/HTTPS URL: worker-queue `getAVFileInfo` preheat, require non-`nil`, then main-thread append; validate returned clip |
| M3U8 clip | download playlist locally first; require confirmed Meishe-specific extended format; never infer or synthesize private parameters |
| Media display size | require video stream; stored dimension -> validate PAR denominator -> width × num/den -> swap for 90°/270° rotation |
| Time | microseconds and valid interval ordering |
| Preview | successful output connection before preview/playback/seek |
| Structural edit | stop conflicting engine operation and preserve ownership |
| Package | main thread; exact selector includes `assetPackageId:`; no completion closure; retain delegate because manager delegate is weak; immediate result is not async completion; wait for installation/upgrading delegate callback before application; template installs asynchronously regardless of `sync` |
| Template | install as Template; stable package ID; recursively map footage/caption descriptors; distinguish standard from VariantImageSize; check every create/replace/post-process stage |
| Compile | writable output; custom height before Custom grade; resumable compile requires both breakpoint-continuation enable and a non-empty writable cache path in `compileConfigurations`; clear stale cache before non-resume, retain only across background interruption, clear after final success/failure/user cancellation; delegate is final result |
| AR | matching license/model/features/data/package/parameters and physical-device visibility |
| Custom rendering | SDK callback thread, transient-object ownership, graphics-state restoration |
| Caption | default fade-in ON; set `NvsStreamingContext.defaultCaptionFade = NO`/`false` before adding captions to disable (property) |
| Clips | default Fade transition ON between appended clips; opt out via `NvsCreateTimelineType_DontAddDefaultVideoTransition` flag at create time, or `setBuiltinTransition:withName:@""` on the track afterward |
| Effects order | render by add order by default; `enableRenderOrder(byZValue:true)` sorts by zValue (tie order: timeline filter → animated sticker → timeline caption incl. modular → compound caption) |
| Image clip | default zoom animation ON when appending an image; opt out via `imageMotionMode = NvsStreamingEngineImageClipMotionMode_LetterBoxZoomIn` + `imageMotionAnimationEnabled = false` (needs feature authorization), or `enablePropertyVideoFx(true)` |
