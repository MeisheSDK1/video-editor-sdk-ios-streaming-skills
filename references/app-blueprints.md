# Application Blueprints

| ID | Product shell | Completion contract |
|---|---|---|
| `short-video-editor` | Import and mult-tool editor | import, persisted Timeline, preview, child tools, restore, export |
| `beauty-camera` | Beauty/AR capture | permission gates, physical preview, capture callbacks, resource gaps |
| `camera-plus-editor` | Capture followed by editing | recorded media enters an editable/exportable Timeline |
| `local-asset-center` | Authorized local materials | install, apply, edit supported properties, remove instance |
| `template-studio` | Template slot editor | install, inspect slots, replace media, preview, export |
| `pip-editor` | Multitrack overlay editor | select, transform, layer, preview, export |
| `quick-splicing-app` | Ordered clip splicing | multiple clips, visible order, transitions, shared Timeline preview/export |
| `full-sdk-showcase` | Capability hub | only implementation-ready modules get runnable entries |
| `incremental-integration` | Existing-host patch | additive staging without replacing navigation or product shell |

Use exactly one product shell. Existing Xcode projects always use `incremental-integration`; another blueprint may guide capability selection but cannot replace the host shell.
