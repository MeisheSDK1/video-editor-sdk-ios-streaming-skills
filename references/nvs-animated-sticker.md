# Animated Sticker Class Families

Animated stickers can belong to Capture, Timeline, Track, Clip, or a video-effect container. Use only the creation, query, and removal methods exposed by that owner.

- Install a packaged sticker before using its package ID.
- Use a creation overload with `customImagePath:` for a custom-image sticker.
- Use microseconds for `inPoint` and `duration`.
- Apply public scale, translation, rotation, flip, opacity, Z-order, volume, and keyframe APIs according to the concrete sticker type.
- Use LiveWindow coordinate mapping and SDK bounding vertices for interaction.
- Treat body, in-animation, out-animation, and loop-animation packages as distinct resource types.
- Persist stable target relations and remove the SDK instance, not only the interaction overlay.
