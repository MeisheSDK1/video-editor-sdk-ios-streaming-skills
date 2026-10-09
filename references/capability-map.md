# Capability Map

| Intent | Class families | Modules | Recipe |
|---|---|---|---|
| Initialize SDK | `NvsStreamingContext` | `sdk-runtime` | `sdk-initialize` |
| Create editor Timeline | Context, Timeline, tracks | `editor-shell` | `timeline-build` |
| Import Photos media | `PHAsset`, `NvsVideoTrack` | `media-import` | `append-media` |
| Import remote media | `NvsVideoTrack` | `media-import` | ordinary HTTP/HTTPS URL passes directly; M3U8 downloads locally and requires the Meishe-specific extended format |
| Preview and seek | Context, LiveWindow | `timeline-preview` | `connect-livewindow`, `playback-seek` |
| Compile output | Context | `export-compile` | `compile-export` |
| Capture video | Context, Capture Fx | `capture-camera` | `capture-preview`, `capture-recording` |
| Apply material | Asset manager and target owner | `asset-package-service` | `install-asset-package` |
| Adjust package parameters | Asset manager and effect object | `asset-package-service`, `effect-parameter-models` | `adjust-package-params` |
| Install and inspect a template | `NvsAssetPackageManager`, template descriptors | `template-engine` | `install-asset-package`, `inspect-template` |
| Apply adaptive/standard/AE template | Context, template footage, Timeline | template modules | `apply-template`, `postprocess-template` |
| Edit template text/media/trim/crop | descriptors, nested Timelines, captions, clips | `template-editor` | `edit-template` |
| Edit overlays | Caption/sticker families | caption/sticker modules | `caption-edit`, `sticker-edit` |
| Beauty or AR | Context and AR public classes | beauty/AR modules | `human-detection-initialize`, `ar-scene-apply` |
| Custom effect | custom renderer protocols | custom modules | `custom-fx-attach` |
