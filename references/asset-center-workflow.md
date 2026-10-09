# Local Asset Center Workflow

1. Read a user-authorized local material description.
2. Validate file existence, semantic asset type, original filename, and license requirements.
3. Retain an `NvsAssetPackageManagerDelegate`, assign it to the manager's weak `delegate`, and install or upgrade with the exact public selector. Do not use a completion-closure overload.
4. For asynchronous installation, treat the immediate result as start/validation status and wait for `didFinishAssetPackageInstallation(_:filePath:type:error:)`. Template packages always complete asynchronously regardless of `sync`.
5. Apply the stable package ID to the selected semantic target.
6. Present the applied instance and editable public properties.
7. Persist the package identity and stable target relation.
8. Remove the applied SDK instance separately from uninstalling the shared package.

Collect required input before application: caption text, custom-sticker image, authorized media/music URL, valid clip or transition boundary, and registered font as applicable. No private network catalog is bundled.
