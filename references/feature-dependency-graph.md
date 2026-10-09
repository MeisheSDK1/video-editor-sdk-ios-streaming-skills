# Feature Dependency Graph

```text
editor shell -> media import + state store + Timeline preview + export
clip editor -> editor shell
caption/sticker/filter/transition/music -> editor shell or clip editor
voiceover -> music editor + microphone permission
beauty camera -> capture camera + parameter models
AR/makeup/segmentation -> capture camera + asset packages + required detection resources
template editor -> template engine + media import + export
PIP -> editor shell + clip editor
quick splicing -> import + preview + transitions + export
custom transition -> custom video effect contract + transition editor
```

Use the registry as the machine-readable source of truth.
