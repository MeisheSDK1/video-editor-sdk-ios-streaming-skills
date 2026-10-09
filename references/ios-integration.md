# iOS Integration

`NvStreamingSdkCore.framework` is the user-supplied dynamic SDK artifact, not a package-manager dependency.

## New Project

- Add the framework to the app target and configure Embed & Sign.
- Import its public module/headers in Objective-C or Swift as exposed by the artifact.
- Add only privacy usage descriptions required by selected modules.
- Provide a valid SDK license before singleton initialization and confirm that it authorizes the target bundle identifier.
- Add authorized model and material resources through explicit resource contracts.

## Existing Host

Stage source and `patch-manifest.json` first. Do not overwrite project files, navigation, delegates, build settings, signing, or host-owned Timeline state. Describe target-membership and Embed & Sign steps for the host when automatic project editing is unsafe.

## Swift Mapping

Treat Objective-C declarations as truth. Compile-check imported names, nullability, C enums/options, structures, delegates, blocks, and error-output parameters. Fall back to the Objective-C prototype when a Swift name has not been verified.
