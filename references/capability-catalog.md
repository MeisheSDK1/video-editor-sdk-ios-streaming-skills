# Capability Catalog

| Goal | Core modules | Required inputs |
|---|---|---|
| Camera recording | `capture-camera` | R0, R2, writable output |
| Beauty/AR camera | `beauty-camera`, `ar-scene` | camera plus R8/R9 as required |
| Short video editor | `editor-shell`, child editors, `export-compile` | R0, R1, R3 |
| Captions and stickers | `caption-editor`, `sticker-editor` | text or image plus R4/R5/R6 |
| Music and voiceover | `music-editor`, `voiceover-editor` | authorized audio, microphone for recording |
| Packaged materials | `asset-package-service`, `local-asset-center` | package file, license when required |
| Templates | `template-engine`, `template-editor` | verified template package and slot media |
| Custom rendering | custom effect modules | renderer implementation and R12 |
| Media inspection/conversion | `media-tools` | accessible media and writable output |

Use `full-sdk-showcase` only for modules whose public bindings and implementation state permit generation.
