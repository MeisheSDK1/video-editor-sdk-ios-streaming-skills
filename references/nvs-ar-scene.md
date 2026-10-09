# Human Detection and AR Scene

## Ordered Setup

```text
verify SDK license -> obtain Streaming Context
-> initialize required primary detection features
-> initialize required extensions and data
-> install/select authorized AR resources
-> create the supported AR Scene effect
-> set verified parameters -> confirm on physical-device preview
```

Use matching model, license, feature, and data inputs. Initialize only capabilities required by the request, check every return value, and do not hard-code delivery filenames.

## Parameters and Visibility

- Parameter keys are case- and whitespace-sensitive.
- Verify key name, type, range, effect family, and required package before emission.
- Basic Beauty and AR Scene use different parameter systems.
- Some makeup, mesh, or warp effects require both a valid package identity and nonzero strength.
- Package installation, setter success, ID readback, or face callbacks do not prove visible rendering.

For invisible output check license, model/data readiness, physical device, camera preview, subject conditions, package type, application target, action prompt, key spelling/type, and strength. Close human detection when it is no longer needed.

## Full AR Scene Parameter Reference

The complete `AR Scene` parameter table (key / type / range / default), plus the beauty, face-mesh, makeup, and prop code samples, lives in the dedicated builtin-effect skill: `builtin_effects/ar-scene.md`. Its parameter keys are identical across iOS StreamingContext and EffectSDK; use it as the single source of truth when emitting `AR Scene` parameters.
