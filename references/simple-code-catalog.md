# Simple Code Catalog

`simple-code-registry.json` is the executable source of truth.

## Core Units

- `objc.context.initialize`: license and singleton flags.
- `objc.timeline.create`: aligned Timeline creation with return checks.
- `objc.video.append-photo-asset`: append a Photos local identifier.
- `objc.preview.connect`: connect Timeline and LiveWindow.
- `objc.compile.custom-height`: configure required breakpoint-continuation cache entries, set custom height, and compile with Custom grade.
- `objc.timeline.remove`: ownership-aware teardown.

## Recipes

- `recipe.timeline-basic`
- `recipe.photo-clip-preview`
- `recipe.custom-compile`
- `recipe.asset-install-apply`
- `recipe.capture-record`
- `recipe.ar-scene`

Units marked `contract_only` document required bindings but cannot be emitted as completed implementation.
