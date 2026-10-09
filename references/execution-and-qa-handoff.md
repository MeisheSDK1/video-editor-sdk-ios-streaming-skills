# Execution and QA Handoff

Project edits do not authorize building, signing, installing, device control, or screenshots. State this non-blocking assumption before implementation when it affects the task.

## Build Handoff

Provide a filled command after generation, for example:

```bash
xcodebuild -project /absolute/App.xcodeproj -scheme App -configuration Debug -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build
```

Use actual paths, scheme, configuration, and destination. Do not leave placeholders.

## Optional Execution

Run only when explicitly requested. A simulator build does not validate camera, microphone, Photos authorization, AR, human detection, signing, or production resources. Device QA requires a signing identity, compatible device, authorized SDK artifacts, license, and selected models/materials.

Report the exact highest achieved evidence level without promotion.

For a physical-device run, keep the sequence explicit: generate, structurally validate, build for `iphoneos/arm64`, sign, install, launch, execute the requested flow, then visually confirm. A successful unsigned device build proves compilation and linking only. A missing Development Team, signing identity, or provisioning profile blocks installation but is not an SDK API failure. Never read, retain, or fill Apple Account credentials; hand credential entry back to the user.

For new-app validation, generate and execute the default Swift template. An Objective-C validation target is a separate compatibility check and does not substitute for validating the default Swift output.
