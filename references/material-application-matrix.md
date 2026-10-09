# Material Application Matrix

| Material | Install type | Semantic target | Required input | Removal |
|---|---|---|---|---|
| Video effect | matching video-effect type | Capture/Clip/Track/Timeline effect owner | target and verified parameters | owner effect removal API |
| Transition | video/audio transition type | boundary after a source clip | two adjacent clips | clear/replace transition |
| Caption style | caption-style type | ordinary caption | text | owner caption removal API |
| Compound caption | compound-caption type | compound caption object | required child text | compound-caption removal API |
| Animated sticker | sticker type | Capture/Timeline/Track/Clip | optional custom image for custom form | owner sticker removal API |
| Theme | theme type | Timeline | compatible aspect/media | remove current theme |
| AR Scene | AR type | supported AR effect owner | detection resources and action conditions | effect removal API |
| Makeup/mesh/warp | matching type | supported AR/beauty parameter target | package ID and strength | clear parameter/package and instance |
| Template | template type | template engine | slot media | remove generated Timeline by ownership |

Installation alone never satisfies the application contract.
