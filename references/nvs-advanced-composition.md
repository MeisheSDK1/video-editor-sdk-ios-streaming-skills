# Advanced Composition Families

This family includes `NvsTimelineGraphCompositor`, storyboard 3D data objects, `NvsMaskRegionInfo`, `NvsMeshWarpInfo`, and related public graph/storyboard/mask/mesh parameters.

## Rules

1. Confirm that the target public API accepts the selected data object or schema.
2. Keep SDK objects, description data, and string protocols separate.
3. Verify coordinate space, normalized ranges, time domain, vertex order, matrix convention, and color space.
4. Install packaged graph or storyboard resources before using their package identity.
5. Re-seek or play after complex structural changes to validate rendering.
6. For undocumented schemas, consult the official Streaming SDK technical topic and do not invent fields.

Keep modules `contract_only` until all required public bindings and a typechecked unit exist.
