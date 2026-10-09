# Complete Editor Architecture

A complete editor implements this chain:

```text
media selection -> aspect/resolution -> persisted project description
-> Timeline reconstruction -> LiveWindow connection -> playback/seek
-> child editors and applied-material state -> compile/export
```

Recommended skill-owned roles are `StreamingContextController`, `MediaImporter`, `TimelineSession`, `EditorCoordinator`, `CommandController`, `OverlayController`, `PlaybackController`, `VoiceoverController`, `AssetPackageController`, `ExportController`, and `ProjectStore`.

Each edit command validates target ownership and time domain, stops conflicting state, calls the SDK, checks the return, updates the project description, refreshes overlays, and creates an undo snapshot.

Preview or recording alone is not a complete editor.
