# API Domain List

The complete machine-readable public inventory is `sdk-signature-map.json`. Group APIs into these domains:

- P0: license, singleton, Timeline, tracks/clips, LiveWindow, playback/seek, compile, asset manager, capture preview/recording.
- P1: captions, stickers, transitions, common effects, audio editing, human detection, AR Scene, templates.
- P2: retrievers, generators, convertors, graph/mask/mesh, package-specific editors, custom video effects.
- P3: rare callbacks, value objects, specialized render paths, custom audio/transition rendering, and public members without an independent emission unit.

For every member store the class, exact selector or symbol, domain, priority, module IDs, recipe IDs, and processing state. Keep low-frequency public members discoverable even when `contract_only`.
