# Template Installation, Application, Post-processing, and Editing

## Scope and Classification

Use only public Streaming SDK APIs. Product labels such as adaptive, standard, and AE template are workflow classifications, not permission to depend on an external orchestrator, crop model, AI selector, material service, or sample-project helper.

- Identify the workflow from package metadata, public descriptors, Timeline creation flags, and object capabilities.
- Use `NvsCreateTimelineType_VariantImageSize`, never the raw value `8`, when selecting the variant-image-size post-processing path. A product may call that path an AE-template workflow, but the public enum itself does not carry that product label.
- Keep automatic content analysis, AI shot selection, reverse-media generation, and any unbundled crop-model implementation `contract_only` unless their public Streaming SDK entry points and generated code have been independently verified.
- Do not confuse `NvsTimeline.applyThemeTemplate` with a replaceable-footage template created by `NvsStreamingContext.createTimeline(_:templateFootages:)`.

## Install and Inspect

1. Install or upgrade the package as `NvsAssetPackageType_Template` with `installAssetPackage(_:license:type:sync:assetPackageId:)`. There is no completion-closure overload. Retain and assign an `NvsAssetPackageManagerDelegate`, then wait for `didFinishAssetPackageInstallation(_:filePath:type:error:)`; template installation is asynchronous regardless of `sync`. Handle the documented already-installed result.
2. Require a stable non-empty package ID. Installation success is not evidence that Timeline creation, replacement, preview, or export succeeded.
3. Query `getTemplateFootages`, `getTemplateCaptions`, `getTemplateCampoundCaptions`, and `getTemplateCurrentAspectRatio`.
4. For each `NvsTemplateFootageDesc`, preserve `footageId`, type, `canReplace`, tags, all `correspondingClipInfos`, and recursive `timelineClipFootages`. One footage can map to multiple clips or clips inside nested Timelines.
5. Preserve caption and compound-caption `replaceId` values and nested descriptor paths. At runtime, resolve public template attachments such as `NVS_TEMPLATE_KEY_REPLACE_ID`; never locate an editable object by visible text or list order alone.
6. Treat video/image, video-only, image-only, audio, and freeze-frame footage separately. Supply `reverseFilePath` when a descriptor requires reverse media; do not reuse the forward path as fabricated reverse output.

## Apply by Template Type

### Adaptive Template

- Query the current and host-supported aspect choices.
- Call `changeTemplateAspectRatio(_:aspectRatio:)`, require `true`, then query all descriptors again. A ratio change may alter slots, nesting, and output geometry; discard stale index mappings.
- Build the footage array and create the Timeline only after the selected media is ready.
- Automatic analysis, shot selection, or template matching that has no verified public Core entry point remains a host contract.

### Standard Template

- Create one `NvsTemplateFootageInfo` per selected footage identity, setting `footageId`, `filePath`, and `reverseFilePath` as required.
- Call the public template Timeline creation overload that matches the requested flags, FPS, and audio resolution. Require a non-`nil` Timeline.
- Resolve editable clips recursively with descriptor track/clip indices and nested-Timeline paths. Do not assume one slot maps to one clip.

### AE or Variant-image-size Template

- Use the same installation, descriptor, footage, and Timeline creation workflow.
- Select post-processing by testing `timeline.getCreationFlags()` against `NvsCreateTimelineType_VariantImageSize` and by checking each clip's public ref-image and raw-filter capabilities.
- Preserve or rebuild a valid reference image size and aspect-fill behavior where required. Do not apply the standard path's ref-size removal unconditionally.

## Media and Thread Rules

- `NvsTemplateFootageInfo.filePath` may use an ordinary local media path or a valid `PHAsset.localIdentifier`.
- For ordinary HTTP/HTTPS media, perform the slow `getAVFileInfo` warm-up on a worker queue, require non-`nil`, then return to the main thread for every other SDK call. Localize and validate M3U8 separately.
- All SDK APIs run on the main thread unless their own public documentation explicitly states a thread exception.
- Template Timeline failure must distinguish invalid/uninstalled package ID, invalid media, missing reverse media, unsupported aspect, authorization/resource failure, and Context state conflict.

## Post-process Replacement Geometry

After Timeline creation or media replacement, recursively visit video tracks, clips, and every `getInternalTimeline` result.

- Skip non-replaceable internal template assets.
- Calculate media display size with stored dimension, PixelAspectRatio correction, and 90/270-degree rotation before applying geometry.
- Inspect ref-image size, fill mode, raw-filter processing mode, property FX, crop/mask state, and transform state before editing.
- Generate built-in FX names or parameter keys only when they are verified by public documentation or bundled constant references. Do not copy private helper strings.
- In the variant-image-size path, retain a valid reference size and align any generated reference width to a multiple of 4 and height to a multiple of 2.
- If the clip's public processing mode or required objects do not support crop editing, return an unsupported state instead of reporting success.
- Record Timeline creation, media replacement, and geometry post-processing as separate result stages.

## Secondary Editing

### Text

- Resolve ordinary and compound captions from their descriptor `replaceId` and nested path.
- Use `NvsCaption.setText` for an ordinary caption and `NvsCompoundCaption.setText(_:text:)` for a compound-caption item.
- If one replace ID maps to multiple objects, require an explicit single-item or group-edit choice.

### Media Replacement

- Require `canReplace == true`.
- Resolve every corresponding clip, including grouped clips and clips inside internal Timelines.
- Call the public file-path replacement API and check its result, then rerun display-size and crop/transform post-processing. Never replace only the first clip when one footage maps to several.

### Source Trim

- Use microseconds and require `0 <= trimIn < trimOut` within the source range and template duration contract.
- After a public trim/move operation, recheck Timeline duration, adjacent transitions, reverse mapping, and all members of a grouped footage.

### Picture Crop

- Keep source-time trim separate from picture crop.
- Use corrected display dimensions and update crop, transform, reference size, and public template attachments according to the standard or variant-image-size branch.

Stop conflicting playback, seek, or compile activity before structural or geometry edits. Perform SDK mutations on the main thread, then reconnect or seek preview. Read playback and compile progress from Context delegates.

## Evidence Boundary

Package installation, descriptor lookup, setter return, Timeline creation, build success, and visual correctness are distinct evidence levels. A helper implementation from an example application is not runtime Skill evidence. Keep any workflow without dependency-closed generated source and verification as `contract_only`.
