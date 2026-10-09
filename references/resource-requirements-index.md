# Resource Requirements

| Key | Resource | Validation |
|---|---|---|
| R0 | user-supplied dynamic framework and SDK license | public headers, architecture, embed/sign plan, license result, authorized bundle identifier |
| R1 | local media, ordinary HTTP/HTTPS media URL, local Meishe-specific M3U8, or `PHAsset.localIdentifier` | permission, network/file accessibility, worker-queue `getAVFileInfo` preheat and main-thread append for ordinary remote media, non-empty identity, M3U8 localization and confirmed format source, SDK clip return |
| R2 | camera/microphone device | privacy descriptions, permission callback, physical device |
| R3 | LiveWindow and writable output URL | connection result, aspect, directory, callback |
| R4 | packaged material and material license | correct type, installation completion, package ID |
| R5 | fonts and caption resources | registration, text input, supported property |
| R6 | sticker/custom image | authorized image and valid target |
| R7 | filter/transition/theme packages | type, boundary, semantic application |
| R8 | human-detection models/data/licenses | matching feature/data initialization result |
| R9 | AR/makeup/shaping resources | detection readiness, package, action, strength |
| R10 | template package/license, slot media, required reverse files, and optional custom-resource directory | Template package type, stable package ID, aspect, recursive footage/caption descriptors, replaceability, forward/reverse paths, Timeline creation, post-processing, and output result |
| R11 | custom app media/resources | user-authorized source |
| R12 | custom-render shaders/resources | callback thread, ownership, cleanup |

The skill does not download, bundle, or invent protected resources. Missing production resources remain explicit user/business inputs.

Before device QA, confirm that the generated target bundle identifier is authorized by the supplied SDK license. A successful app signature or installation does not prove SDK authorization. Classify `The current app is not authorised!` as an SDK-license/app-identity mismatch and stop before Timeline, preview, or compile claims.
