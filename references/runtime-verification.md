# Runtime Verification

Use exact evidence levels:

1. `generated`
2. `structurally_validated`
3. `objc_typechecked`
4. `swift_compiled`
5. `xcode_built`
6. `simulator_launched`
7. `device_installed`
8. `flow_executed`
9. `visually_confirmed`

The runtime matrix must scope each claim to device, OS, architecture, implementation language, public capability fingerprint, license mode, resource set, module, code unit, API, flow, and evidence level.

Simulator results do not validate camera, microphone, Photos permission, AR, human detection, device signing, or production resources. Package installation, parameter setter success, ID readback, or detection callbacks do not prove visible AR output.
