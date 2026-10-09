# NvsAssetPackageManager

Obtain the manager from `NvsStreamingContext.assetPackageManager`. It installs, upgrades, queries, and uninstalls packaged resources.

## Installation Contract

```text
identify semantic asset type -> validate package and license paths
-> installAssetPackage:license:type:sync:assetPackageId:
-> handle immediate result or asynchronous delegate
-> persist package ID -> apply package ID to the correct SDK owner
```

- Select an explicit `NvsAssetPackageType`; do not infer solely from a filename extension.
- Keep SDK license, package license, and human-detection model license separate.
- The public Swift call is `installAssetPackage(_:license:type:sync:assetPackageId:)`. It has no completion-closure overload.
- For asynchronous installation, set an `NvsAssetPackageManagerDelegate` before starting and wait for `didFinishAssetPackageInstallation(_:filePath:type:error:)` before descriptor queries or application.
- The manager's `delegate` property is weak. Retain the delegate elsewhere for the whole operation. In an existing host, coordinate, forward, or restore delegate ownership rather than silently replacing another consumer.
- Treat the immediate return value as request validation/start status. `NvsAssetPackageManagerError_WorkingInProgress` means the final result is pending; completion comes from the delegate callback. Do not invent an `op` value—the callback supplies package ID, file path, package type, and error.
- Template package installation is asynchronous regardless of the `sync` argument.
- Treat already-installed state according to the public result contract rather than as an unconditional fatal error.
- Installation does not prove application or visual visibility.

## Correct Swift Asynchronous Pattern

```swift
final class AssetPackageInstaller: NSObject, NvsAssetPackageManagerDelegate {
    private let manager: NvsAssetPackageManager

    init(manager: NvsAssetPackageManager) {
        self.manager = manager
        super.init()
        manager.delegate = self // weak: the caller must retain this installer
    }

    func installTemplate(packagePath: String, licensePath: String?) {
        let packageId = NSMutableString()
        let status = manager.installAssetPackage(
            packagePath,
            license: licensePath,
            type: NvsAssetPackageType_Template,
            sync: false,
            assetPackageId: packageId
        )

        if status != NvsAssetPackageManagerError_WorkingInProgress &&
           status != NvsAssetPackageManagerError_NoError &&
           status != NvsAssetPackageManagerError_AlreadyInstalled {
            // Report the immediate start/validation failure.
        }
        // Do not apply a template here while asynchronous work is pending.
    }

    func didFinishAssetPackageInstallation(
        _ assetPackageId: String!,
        filePath assetPackageFilePath: String!,
        type assetPackageType: NvsAssetPackageType,
        error: NvsAssetPackageManagerError
    ) {
        guard error == NvsAssetPackageManagerError_NoError ||
              error == NvsAssetPackageManagerError_AlreadyInstalled else {
            // Report the final installation failure.
            return
        }
        // Match filePath/type to the pending request, then use assetPackageId.
    }
}
```

All manager calls and its completion handling stay on the main thread. If several installs may overlap, maintain pending-operation state keyed by a host-defined request identity plus file path/type; the SDK callback does not provide a closure operation token.

Common package families include video effects, transitions, caption styles, stickers, themes, AR Scene, compound captions, templates, makeup, face mesh, and warp resources. Generate a family only when the current public headers expose its Streaming SDK application path.

## Adjustable Parameters (可调参数)

Packaged effects applied through a `packageId` — for example filters, stickers, and compound captions — return an effect object (`fx`). Beyond ordinary properties, that object exposes a set of **adjustable parameters (可调参数)**: effect variables defined by the package author and modifiable at runtime.

### Read the adjustable parameter list

Use `NvsAssetPackageManager` to pull the package's exposed adjustable parameters by `packageId` and `NvsFxParamType`:

```swift
let assetPackageManager = context.assetPackageManager
let fxExpArr = assetPackageManager.getExpValueList(packageId, type: type)
```

- `packageId`: the stable identifier obtained after installation (see `install-asset-package`).
- `type`: `NvsFxParamType` — `NvsFxParamTypeFloat`, `NvsFxParamTypeInt`, or `NvsFxParamTypeColor` — to fetch numeric vs. color parameters separately.

### Write adjustable parameters to the effect object

Branch on the parameter type and call the expression-variable setters on `fx`:

```swift
if type == NvsFxParamTypeFloat || type == NvsFxParamTypeInt {
    if let doubleValue = value as? Double {
        fx.setExprVar(name, varValue: doubleValue)
    } else if let intValue = value as? Int {
        fx.setExprVar(name, varValue: Double(intValue))
    } else if let intValue = value as? Int32 {
        fx.setExprVar(name, varValue: Double(intValue))
    }
} else if type == NvsFxParamTypeColor {
    if let color = value as? MeicamColor {
        var nColor = color.colorValue()
        fx.setColorExprVar(name, varValue: &nColor)
    }
}
```

- Numeric (Float / Int): `fx.setExprVar(_:varValue:)`, normalizing any integer/float value to `Double`.
- Color: `fx.setColorExprVar(_:varValue:)`, passing the **mutable address** (`&nColor`) of an `NvsColor` obtained from `MeicamColor.colorValue()`.

### Swift call traps

- `NvsFxParamType` is a C `typedef enum`; access it by bare name (`NvsFxParamTypeFloat`, …) and handle the comparison per the enum/flag import rules.
- `fx.setColorExprVar(_:varValue:)` takes an `UnsafeMutablePointer<NvsColor>` (inout); you must pass `&nColor`, never a value or a `NvsColor` literal.
- This capability applies only to **installed** packaged effects. Install the package first (`install-asset-package`); otherwise `packageId` is unavailable and `getExpValueList` returns nothing.
