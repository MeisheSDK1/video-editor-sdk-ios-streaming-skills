# API Dependency Graph

```text
license -> Context singleton -> delegates
Context -> valid resolution -> Timeline -> tracks -> clips
Timeline + LiveWindow connection -> seek/playback
Timeline + stopped conflicts + compile configuration -> compile callbacks
asset manager -> install completion -> package ID -> semantic target application
capture permission -> Capture LiveWindow -> preview -> capture effects -> recording
detection license/model -> required features/data -> AR effect -> package/parameters -> visible preview
```

Removal proceeds in reverse ownership order. Never use child objects after Timeline removal.
