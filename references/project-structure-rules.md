# Project Structure Rules

- Keep view controllers focused on lifecycle, permission UI, view binding, and navigation.
- Route SDK work through context, Timeline session, editor coordinator, command, overlay, playback, capture, asset, export, and persistence controllers.
- Declare Timeline ownership as `EDITOR_OWNED` or `HOST_OWNED`. A host-owned Timeline cannot be removed or rebuilt without explicit permission.
- Persist reconstructable JSON with stable IDs, atomic replacement, and explicit schema migration. Never persist SDK object pointers.
- Keep bounded in-memory undo/redo snapshots and persist only the latest project state.
- Stop conflicting engine operations before structural mutation, compile, or removal.
- Clear LiveWindow and present an empty state after deleting the final clip; reconnect on new media.
- Keep Timeline geometry, LiveWindow container, fill mode, coordinate mapping, and compile geometry consistent.
- Treat incremental application as a preflighted transaction: identical files are no-ops and any conflict produces zero host writes.
