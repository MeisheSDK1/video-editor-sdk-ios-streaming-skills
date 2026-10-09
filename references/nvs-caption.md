# Caption Class Families

Captions can belong to Capture, Timeline, Track, Clip, or a video-effect container. Determine the owner before creating, querying, or removing a caption.

## Caption Kinds

- Use the owner's ordinary caption API for standard styled text.
- Use the owner's modular caption API for modular renderer/context/animation behavior.
- Use the corresponding compound-caption API for multi-part packaged captions.
- Install packaged caption resources before creation.

Use microseconds for `inPoint`, `duration`, and position queries. Ordinary, modular, and compound captions do not expose identical property sets.

## Text, Styling, and Interaction

Apply only properties supported by the current caption kind: text, font, size, color, outline, shadow, background, alignment, spacing, transform, Z order, spans, and text layout. Use LiveWindow mapping for gestures and SDK bounding vertices for overlay refresh.

Persist the caption descriptor and stable owner relation. Removal must delete both the SDK object and persisted descriptor; removing only the UI overlay is incomplete.
