# Custom Effects and Transitions

Attach a renderer only through the public custom Capture, Clip, Timeline, Audio Fx, or transition API supported by the selected owner. Keep the renderer alive for the complete SDK lifetime of the instance.

## Renderer Contract

- Initialize lightweight state in the public initialization callback.
- Preload graphics resources in the designated preload stage.
- Process each frame/block without network, disk, or long blocking work.
- Respect input/output texture or sample-buffer ownership, dimensions, rotation, pixel format, and color space.
- Do not retain helper or frame objects valid only for the current callback.
- Restore graphics state required by the SDK after rendering.
- Use thread-safe lightweight snapshots for dynamic parameters.
- Release shaders, textures, buffers, caches, and other resources in cleanup callbacks.

Custom transitions receive both sides and progress. Validate progress semantics and release every helper-owned resource through the public lifecycle.
