# AR Scene 内建特效接入参考

本文是 `AR Scene` 内建特效的独立 skill。其参数 key、类型、范围与默认值在 **iOS StreamingContext 与 EffectSDK 中完全一致**（如 `Beauty Effect`、`Beauty Strength`、`Face Mesh ... Degree`），因此本文档作为「AR Scene 特效」的事实源，可同时服务于两类 SDK；只有「把 effect 加进渲染管线」的接入 API 不同。StreamingContext 与人体检测（人脸/人像分割/手势/Avatar/眼球/高级美颜模型）初始化见 `../nvs-ar-scene.md`，素材包安装（`.arscene` / `.makeup` / `.facemesh` / `.warp`）见 `../nvs-asset-package-manager.md`。

> **跨 SDK 兼容性（参数一致，只换挂载 API）**：本文档的参数表（§AR Scene 常用参数表 起）是 **effect 级别** 的事实源，iOS StreamingContext 与 EffectSDK 共用同一套 key/类型/范围/默认值。生成代码时只需替换「创建并挂载 effect」那一层 API：
> - **iOS StreamingContext（采集）**：`NvsStreamingContext.appendBuiltinCaptureVideoFx("AR Scene")`
> - **iOS StreamingContext（时间线）**：`NvsTimeline.addBuiltinTimelineVideoFx(...)`（本文后续章节给出完整代码）
> - **EffectSDK（鸿蒙/Android 等）**：管线 API 见 `harmony-effectsdk-fx-arscene.md` 的 `scheduler.createVideoEffect(...)` + `scheduler.addRenderEffects([...])`；参数设置沿用本文同一套 `setXxxVal` 语义（鸿蒙为 `setBooleanVal` / `setNumberVal` / `setStringVal`）。
>
> 其余所有参数设置、美颜需求澄清、按描述生成代码的规则，两个 SDK 通用。本文默认给出 iOS StreamingContext 写法；为 EffectSDK 生成时复用同一套参数 key，仅替换挂载 effect 的调用即可。

## 目录

- [使用边界](#使用边界)
- [创建 AR Scene](#创建-ar-scene)
- [AR Scene 常用参数表](#ar-scene-常用参数表)
- [美颜需求澄清](#美颜需求澄清)
- [美颜参数](#美颜参数)
- [美型和微整形](#美型和微整形)
- [美妆参数](#美妆参数)
- [AR 道具](#ar-道具)
- [按用户描述生成代码](#按用户描述生成代码)

## 使用边界

- 用户要接入美颜、美型、微整形、美妆、道具或直接设置 `AR Scene` 参数时，读取本文。
- 用户只问 StreamingContext 初始化、采集预览、编译导出或人体检测模型初始化顺序时，读取 `../nvs-ar-scene.md`。
- 用户要初始化人脸、人像分割、手势、Avatar、眼球或高级美颜模型时，先读取 `../nvs-ar-scene.md`。
- 用户要安装 `.arscene`、`.makeup`、`.facemesh` 或 `.warp` 素材包时，先读取 `../nvs-asset-package-manager.md`，拿到非空 `packageId` / `sceneId` 后再回到本文设置 `AR Scene` 参数。
- `.videofx` 滤镜包、校色包、肤色包是独立视频特效（`NvsTimelineVideoFx` / `NvsCaptureVideoFx` 的其它内置或封装特效），不属于 `AR Scene` 特技；这类包安装后回到 `../nvs-fx.md` / `../nvs-asset-package-manager.md` 创建独立 effect。
- 非常规 `AR Scene` 参数不要猜；常用表没有覆盖时，查 SDK 公开 Headers（`NvsARSceneManipulate.h` 与 effect 内置参数文档）。

## 创建 AR Scene

### 采集预览（实时相机，Objective‑C）

```objc
NvsCaptureVideoFx *arSceneFx = [context appendBuiltinCaptureVideoFx:@"AR Scene"];
if (!arSceneFx) {
    return;
}

[arSceneFx.getARSceneManipulate setDetectionMode:NvsARSceneDetectionMode_SemiImage];
[arSceneFx setBooleanVal:@"Face Mesh Internal Enabled" val:YES];
[arSceneFx setBooleanVal:@"Max Faces Respect Min" val:YES];
[arSceneFx setBooleanVal:@"Single Buffer Mode" val:NO];   // iOS 默认即为 NO
[arSceneFx setBooleanVal:@"Beauty Effect" val:YES];
[arSceneFx setBooleanVal:@"Beauty Shape" val:YES];
```

### 采集预览（实时相机，Swift）

```swift
guard let arSceneFx = context.appendBuiltinCaptureVideoFx("AR Scene") else { return }

arSceneFx.getARSceneManipulate()?.setDetectionMode(NvsARSceneDetectionMode_SemiImage)
arSceneFx.setBooleanVal("Face Mesh Internal Enabled", val: true)
arSceneFx.setBooleanVal("Max Faces Respect Min", val: true)
arSceneFx.setBooleanVal("Single Buffer Mode", val: false)
arSceneFx.setBooleanVal("Beauty Effect", val: true)
arSceneFx.setBooleanVal("Beauty Shape", val: true)
```

### 时间线编辑（Timeline，Objective‑C）

```objc
NvsTimelineVideoFx *arSceneFx =
    [timeline addBuiltinTimelineVideoFx:inPoint duration:duration videoFxName:@"AR Scene"];
if (!arSceneFx) {
    return;
}

[arSceneFx.getARSceneManipulate setDetectionMode:NvsARSceneDetectionMode_Video];
[arSceneFx setBooleanVal:@"Beauty Effect" val:YES];
// ... 其余 setXxxVal 与采集侧一致
```

### 时间线编辑（Timeline，Swift）

```swift
guard let arSceneFx = timeline.addBuiltinTimelineVideoFx(inPoint,
                                                         duration: duration,
                                                         videoFxName: "AR Scene") else { return }

arSceneFx.getARSceneManipulate()?.setDetectionMode(NvsARSceneDetectionMode_Video)
arSceneFx.setBooleanVal("Beauty Effect", val: true)
```

> 注意：采集侧创建是 `NvsStreamingContext -appendBuiltinCaptureVideoFx:`，时间线侧是 `NvsTimeline -addBuiltinTimelineVideoFx:duration:videoFxName:`（是 **add** 不是 append）。两者返回对象分别是 `NvsCaptureVideoFx` / `NvsTimelineVideoFx`，均继承自 `NvsFx`，因此 `getARSceneManipulate`、`setBooleanVal:val:`、`setFloatVal:val:`、`setStringVal:val:`、`setIntVal:val:`、`setColorVal:val:` 全部通用。

AR Scene 检测模式（`NvsARSceneManipulate -setDetectionMode:` 的 `NvsARSceneDetectionMode`）：

| 枚举常量 | 值 |
| --- | --- |
| `NvsARSceneDetectionMode_Video` | `0x01` |
| `NvsARSceneDetectionMode_Image` | `0x02` |
| `NvsARSceneDetectionMode_SemiImage` | `0x10` |
| `NvsARSceneDetectionMode_SingleThread` | `0x04` |
| `NvsARSceneDetectionMode_MultiThread` | `0x08` |

规则：

- 美颜、美型、美妆、道具都优先复用同一个 `arSceneFx`（采集侧一个 capture video fx；时间线侧一个 timeline video fx）。
- 拍摄实时预览使用 `NvsARSceneDetectionMode_SemiImage`，与 `Semi Image` 检测对应；时间线离线处理用 `NvsARSceneDetectionMode_Video`。
- `NvsARSceneManipulate` 全部 public API **必须在 UI 线程调用**；其 `NvsARSceneManipulateDelegate` 回调（`notifyFaceFeatureInfos:` 等）在**后台线程**触发，更新 UI 时要注意线程安全（回到主线程再刷新）。
- **Swift 枚举导入注意**：`NvsARSceneDetectionMode` 是 C `typedef enum`，Swift 中以裸全局常量形式暴露（`NvsARSceneDetectionMode_SemiImage`），可直接传给 `setDetectionMode:`；不要写 `NvsARSceneDetectionMode.SemiImage` 之外的类型限定写法（部分旧头会报 `no member`）。这与 `NvStreamingSdkCore_SDK_Skill_Analysis.md` §26「C 枚举 Swift 导入陷阱」一致。

## AR Scene 生效前提：BuddyHostVideoFrame 引擎标志

`AR Scene` 是基于人脸/人体检测渲染的特效。要让它在**采集预览**与**时间线播放 / seek / 合成**时真正出效果，必须在对应的引擎启动接口里带上 `BuddyHostVideoFrame` 系列标志；否则特效会被静默忽略（画面无变化，且无报错）。按特效挂载位置分两类规则：

### 1. 采集预览（实时相机）

`AR Scene` 加在采集预览上（`appendBuiltinCaptureVideoFx:`）时，开启预览必须给 `startCapturePreview:videoResGrade:flags:aspectRatio:` 的 `flags` 传入 `NvsStreamingEngineCaptureFlag_CaptureBuddyHostVideoFrame`。头文件注释建议它与 `NvsStreamingEngineCaptureFlag_StrictPreviewVideoSize` 一起传入（两者结合用于人脸检测）。若已有其它 capture flag，用按位或 `|` 合并。

Objective‑C：

```objc
int captureFlags = NvsStreamingEngineCaptureFlag_CaptureBuddyHostVideoFrame
                 | NvsStreamingEngineCaptureFlag_StrictPreviewVideoSize;
[context startCapturePreview:deviceIndex
                videoResGrade:NvsVideoCaptureResolutionGradeDefault
                        flags:captureFlags
                  aspectRatio:nil];
```

Swift（裸常量 + `.rawValue` + 整体 `Int32(...)`，沿用 §26「C 枚举 Swift 导入陷阱」）：

```swift
let captureFlags = Int32(
    NvsStreamingEngineCaptureFlag_CaptureBuddyHostVideoFrame.rawValue
    | NvsStreamingEngineCaptureFlag_StrictPreviewVideoSize.rawValue
)
context.startCapturePreview(deviceIndex,
                            videoResGrade: captureResolutionGrade,
                            flags: captureFlags,
                            aspectRatio: nil)
```

### 2. 时间线编辑（Timeline）

`AR Scene` 加在时间线上（`addBuiltinTimelineVideoFx:duration:videoFxName:`）时，**添加特效本身不需要标志**；但播放、seek、合成三个引擎动作必须各自带上对应标志，否则时间线上的 AR Scene 不生效。

| 引擎动作 | 接口 | 需传入的标志 |
| --- | --- | --- |
| 播放 | `playbackTimeline:startTime:endTime:videoSizeMode:preload:flags:` | `NvsStreamingEnginePlaybackFlag_BuddyHostVideoFrame` |
| seek | `seekTimeline:timestamp:videoSizeMode:flags:` | `NvsStreamingEngineSeekFlag_BuddyHostVideoFrame` |
| 合成 | `compileTimeline:startTime:endTime:outputFilePath:videoResolutionGrade:videoBitrateGrade:flags:` | `NvsStreamingEngineCompileFlag_BuddyHostVideoFrame` |

Objective‑C：

```objc
int pbFlags = NvsStreamingEnginePlaybackFlag_BuddyHostVideoFrame;
[_context playbackTimeline:timeline startTime:0 endTime:timeline.duration
                 videoSizeMode:NvsVideoPreviewSizeModeLiveWindowSize preload:NO flags:pbFlags];

int seekFlags = NvsStreamingEngineSeekFlag_BuddyHostVideoFrame;
[_context seekTimeline:timeline timestamp:ts videoSizeMode:NvsVideoPreviewSizeModeLiveWindowSize flags:seekFlags];

int compileFlags = NvsStreamingEngineCompileFlag_BuddyHostVideoFrame;
[_context compileTimeline:timeline startTime:0 endTime:timeline.duration
              outputFilePath:path videoResolutionGrade:NvsCompileVideoResolutionGrade720
              videoBitrateGrade:NvsCompileBitrateGradeMedium flags:compileFlags];
```

Swift：

```swift
let pbFlags = Int32(NvsStreamingEnginePlaybackFlag_BuddyHostVideoFrame.rawValue)
context.playbackTimeline(timeline,
                         startTime: 0,
                         endTime: timeline.duration,
                         videoSizeMode: NvsVideoPreviewSizeMode(rawValue: 1),
                         preload: true,
                         flags: pbFlags)

let seekFlags = Int32(NvsStreamingEngineSeekFlag_BuddyHostVideoFrame.rawValue)
context.seekTimeline(timeline,
                     timestamp: safePosition,
                     videoSizeMode: NvsVideoPreviewSizeMode(rawValue: 1),
                     flags: seekFlags)

let compileFlags = Int32(NvsStreamingEngineCompileFlag_BuddyHostVideoFrame.rawValue)
context.compileTimeline(timeline,
                        startTime: 0,
                        endTime: timeline.duration,
                        outputFilePath: outputPath,
                        videoResolutionGrade: NvsCompileVideoResolutionGrade720,
                        videoBitrateGrade: NvsCompileBitrateGradeMedium,
                        flags: compileFlags)
```

### 3. 片段（Clip）上挂载 —— 不需要引擎标志，改用 raw 方法

如果 `AR Scene` 是加在**片段（`NvsVideoClip`）**上，而非采集预览或时间线，则**不需要**任何 `BuddyHostVideoFrame` 标志；但添加特效必须使用 `NvsVideoClip` 的 **raw 方法**——不带 raw 的 `appendBuiltinFx:` / `insertFx:` 不会让 AR Scene 生效。

Objective‑C：

```objc
// 末尾追加
NvsVideoFx *arSceneFx = [clip appendRawBuiltinFx:@"AR Scene"];
// 或指定位置插入
NvsVideoFx *arSceneFx2 = [clip insertRawBuiltinFx:@"AR Scene" fxIndex:0];
```

Swift：

```swift
guard let arSceneFx = clip.appendRawBuiltinFx("AR Scene") else { return }
// 或
guard let arSceneFx = clip.insertRawBuiltinFx("AR Scene", fxIndex: 0) else { return }
```

> `NvsTimeline` 没有 raw 变体，因此"时间线级 AR Scene"只能走第 2 类的播放 / seek / 合成标志方案；raw 方法仅适用于片段级（`NvsVideoClip` 的 `appendRawBuiltinFx:` / `insertRawBuiltinFx:` / `appendRawPackagedFx:` 等）。

### 速查

| 挂载位置 | 是否需要标志 | 标志挂在哪 | 添加特效的方法 |
| --- | --- | --- | --- |
| 采集预览 | 是 | `startCapturePreview` 的 `flags` | `appendBuiltinCaptureVideoFx:` |
| 时间线 | 是（播放 / seek / 合成各一个） | `playbackTimeline` / `seekTimeline` / `compileTimeline` 的 `flags` | `addBuiltinTimelineVideoFx:duration:videoFxName:` |
| 片段 | 否 | — | `NvsVideoClip.appendRawBuiltinFx:` / `insertRawBuiltinFx:` |

> **Swift 枚举导入注意**：`NvsStreamingEngine*Flag` 是 C `typedef enum`，Swift 中以裸全局常量暴露，底层 `.rawValue` 为 `UInt32`；传给上述接口的 `flags:(int)` / `flags:(Int32)` 参数时须整体包 `Int32(...)`（如 `Int32(NvsStreamingEnginePlaybackFlag_BuddyHostVideoFrame.rawValue)`），不要写 `TypeName.Member` 也不要只写裸名不包 `Int32`。这与本文"采集 / 时间线创建 AR Scene"代码及 `NvStreamingSdkCore_SDK_Skill_Analysis.md` §26 一致。

## AR Scene 常用参数表

Markdown 表格不写 HTML/CSS 样式，保持 skill 解析稳定。本节只保留高频 AR Scene 参数，并按能力拆成小表；`范围` 使用 `最小..最大`，`空` 表示 SDK 未声明范围或该参数一般传字符串/路径。非常规参数再查 SDK 公开 Headers / effect 内置参数文档，不要把完整表复制回其它文档。

直通条件：道具、美颜、高级美颜、美型、美妆、变形、捏脸、LUT 各项开关关闭，所有强度值为 `0`，所有文件路径为空，且 `Force Detect` 为 `false`。

### 道具与基础模式

| 参数 | 类型 | 范围 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `Scene Id` | STRING | 空 | 空 | 道具包 ID；应用 `.arscene` 包时传安装得到的 `packageId`，取消道具传 `""`。 |
| `Single Buffer Mode` | BOOL | 空 | Android 为 `true`，iOS/其它平台为 `false` | 单 buffer 模式，检测与渲染是否使用同一 buffer；开启后会丢弃 `AR Scene` 之前的特效渲染结果，双 buffer 且两个 buffer 不一致时可能出现画面延时。iOS 一般保持 `false`。 |

### 基础美颜

| 参数 | 类型 | 范围 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `Beauty Effect` | BOOL | 空 | `false` | 基础美颜开关；设置基础磨皮、美白、红润前先打开。 |
| `Beauty Strength` | FLOAT | `0..1` | `0.5` | 基础磨皮强度。 |
| `Beauty Whitening` | FLOAT | `0..1` | `0.5` | 美白强度。 |
| `Whitening Lut Enabled` | BOOL | 空 | `false` | 是否启用美白 LUT。 |
| `Whitening Lut File` | STRING | 空 | 空 | 美白 LUT 文件路径；不使用传 `""`。 |
| `Beauty Reddening` | FLOAT | `0..1` | `0.5` | 红润强度。 |

### 检测与高级美颜

| 参数 | 类型 | 范围 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `Unified Max Faces` | INT | `1..8` | `5` | 最多检测人脸数。 |
| `Max Faces Respect Min` | BOOL | 空 | `false` | 多个资源包都有最多人脸数限制时，是否采用最小的限制。 |
| `AI Face Occlusion Enabled` | BOOL | 空 | `false` | 是否开启 AI 人脸遮挡检测；当前只对美妆有效。 |
| `Advanced Beauty Enable` | BOOL | 空 | `false` | 高级美颜开关；使用高级磨皮、去油光、祛黑眼圈等能力前先打开。 |
| `Advanced Beauty Intensity` | FLOAT | `0..1` | `1` | 高级美颜磨皮强度。 |
| `Advanced Beauty Type` | INT | `0..2` | `0` | 高级美颜类型；产品上有时把它划分到“高级磨皮”下，对应 `0`、`1`、`2` 三种磨皮效果：`0` Android 标准效果，`1` iOS 标准效果，`2` 男性效果。 |
| `Advanced Beauty Remove Dark Circles Intensity` | FLOAT | `0..1` | `0` | 高级美颜祛黑眼圈强度。 |
| `Advanced Beauty Remove Nasolabial Folds Intensity` | FLOAT | `0..1` | `0` | 高级美颜祛法令纹强度。 |
| `Advanced Beauty Brighten Eyes Intensity` | FLOAT | `0..1` | `0` | 高级美颜亮眼强度。 |
| `Advanced Beauty Brighten Eyes Lut File` | STRING | 空 | 空 | 高级美颜亮眼 LUT 文件路径，已废弃。 |
| `Advanced Beauty Whiten Teeth Intensity` | FLOAT | `0..1` | `0` | 高级美颜白牙强度。 |
| `Advanced Beauty Whiten Teeth Lut File` | STRING | 空 | 空 | 高级美颜白牙 LUT 文件路径。 |
| `Advanced Beauty Face Lut Intensity` | FLOAT | `0..1` | `0` | 高级美颜人脸 LUT 强度。 |
| `Advanced Beauty Face Lut File` | STRING | 空 | 空 | 高级美颜人脸 LUT 文件路径。 |
| `Advanced Beauty Clear Intensity` | FLOAT | `0..1` | `0` | 高级美颜清晰强度。 |
| `Advanced Beauty Matte Intensity` | FLOAT | `0..1` | `0` | 高级美颜哑光/去油光强度。 |
| `Advanced Beauty Matte Fill Radius` | FLOAT | `3..30` | `15` | 高级美颜哑光/去油光填充半径。 |

### 美型与 Face Mesh 开关

| 参数 | 类型 | 范围 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `Beauty Shape` | BOOL | 空 | `false` | Warp 类型美型开关；使用旧版 warp 参数或外置 warp 资源包时打开。 |
| `Head Size Warp Degree` | FLOAT | `-1..1` | `0` | 旧版头部增大程度。 |
| `Head Size Warp Strategy` | INT | `0..0x7FFFFFFF` | `0` | 旧版头部增大策略；如果使用外置头部增大资源包，需要设置为 `0x7FFFFFFF`。 |
| `Head Size Warp Custom Package Id` | STRING | 空 | 空 | 旧版头部增大自定义资源包 ID。 |
| `Face Mesh Internal Enabled` | BOOL | 空 | `false` | Face Mesh 新版美型开关；使用新版美型 degree 或 `.facemesh` 包时打开。 |

### Face Mesh Degree 参数

所有 `Face Mesh ... Degree` 取值通常为 `-1..1`，默认 `0`；`0` 表示无效果，正负方向以参数说明为准。

| 参数 | 说明 |
| --- | --- |
| `Face Mesh Eye Size Degree` | 大眼程度。 |
| `Face Mesh Eye Corner Stretch Degree` | 眼角拉向外伸程度。 |
| `Face Mesh Face Size Degree` | 瘦脸程度。 |
| `Face Mesh Face Width Degree` | 窄脸程度。 |
| `Face Mesh Face Length Degree` | 小脸/短脸程度。 |
| `Face Mesh Forehead Height Degree` | 额头高度。 |
| `Face Mesh Malar Width Degree` | 颧骨变窄程度。 |
| `Face Mesh Jaw Width Degree` | 下颌变窄程度。 |
| `Face Mesh Chin Length Degree` | 下巴缩短程度。 |
| `Face Mesh Eye Distance Degree` | 眼间距变窄程度。 |
| `Face Mesh Nose Length Degree` | 鼻子拉长程度。 |
| `Face Mesh Nose Width Degree` | 鼻子变窄程度。 |
| `Face Mesh Mouth Size Degree` | 嘴部缩小程度。 |
| `Face Mesh Mouth Corner Lift Degree` | 嘴角上拉程度。 |
| `Face Mesh Temple Width Degree` | 太阳穴增宽程度。 |
| `Face Mesh Head Size Degree` | 头部缩小程度。 |
| `Face Mesh Eye Angle Degree` | 眼睛角度旋转程度，外眼角向上、内眼角向下。 |
| `Face Mesh Nose Bridge Width Degree` | 鼻梁变窄程度。 |
| `Face Mesh Philtrum Length Degree` | 人中缩短程度。 |
| `Face Mesh Eye Arc Degree` | 眼睛弧形程度，眼角向上。 |
| `Face Mesh Eye Width Degree` | 眼睛宽度变大程度。 |
| `Face Mesh Eye Height Degree` | 眼睛高度变大程度。 |
| `Face Mesh Eye Y Offset Degree` | 眼睛向上偏移程度。 |
| `Face Mesh Eyebrow Angle Degree` | 眉毛角度旋转程度，外眼角向上、内眼角向下。 |
| `Face Mesh Eyebrow Thickness Degree` | 眉毛变粗程度。 |
| `Face Mesh Eyebrow X Offset Degree` | 眉毛间距变宽程度。 |
| `Face Mesh Eyebrow Y Offset Degree` | 眉毛向上偏移程度。 |
| `Face Mesh Nose Head Width Degree` | 鼻头变窄程度。 |

### Face Mesh 自定义包 ID 参数

先按 `../nvs-asset-package-manager.md` 安装 `.facemesh`，再把返回的 `packageId` 设置到对应 `Face Mesh ... Custom Package Id` 参数上。

| 参数 | 说明 |
| --- | --- |
| `Face Mesh Eye Size Custom Package Id` | 大眼美型包 ID。 |
| `Face Mesh Eye Corner Stretch Custom Package Id` | 眼角拉向外伸美型包 ID。 |
| `Face Mesh Face Size Custom Package Id` | 瘦脸美型包 ID。 |
| `Face Mesh Face Width Custom Package Id` | 窄脸美型包 ID。 |
| `Face Mesh Face Length Custom Package Id` | 小脸/短脸美型包 ID。 |
| `Face Mesh Forehead Height Custom Package Id` | 额头高度美型包 ID。 |
| `Face Mesh Malar Width Custom Package Id` | 颧骨变窄美型包 ID。 |
| `Face Mesh Jaw Width Custom Package Id` | 下颌变窄美型包 ID。 |
| `Face Mesh Chin Length Custom Package Id` | 下巴缩短美型包 ID。 |
| `Face Mesh Eye Distance Custom Package Id` | 眼间距变窄美型包 ID。 |
| `Face Mesh Nose Length Custom Package Id` | 鼻子拉长美型包 ID。 |
| `Face Mesh Nose Width Custom Package Id` | 鼻子变窄美型包 ID。 |
| `Face Mesh Mouth Size Custom Package Id` | 嘴部缩小美型包 ID。 |
| `Face Mesh Mouth Corner Lift Custom Package Id` | 嘴角上拉美型包 ID。 |
| `Face Mesh Temple Width Custom Package Id` | 太阳穴增宽美型包 ID。 |
| `Face Mesh Head Size Custom Package Id` | 头部缩小美型包 ID。 |
| `Face Mesh Eye Angle Custom Package Id` | 眼睛角度旋转美型包 ID。 |
| `Face Mesh Nose Bridge Width Custom Package Id` | 鼻梁变窄美型包 ID。 |
| `Face Mesh Philtrum Length Custom Package Id` | 人中缩短美型包 ID。 |
| `Face Mesh Eye Arc Custom Package Id` | 眼睛弧形美型包 ID。 |
| `Face Mesh Eye Width Custom Package Id` | 眼睛宽度变大美型包 ID。 |
| `Face Mesh Eye Height Custom Package Id` | 眼睛高度变高美型包 ID。 |
| `Face Mesh Eye Y Offset Custom Package Id` | 眼睛向上偏移美型包 ID。 |
| `Face Mesh Eyebrow Angle Custom Package Id` | 眉毛角度旋转美型包 ID。 |
| `Face Mesh Eyebrow Thickness Custom Package Id` | 眉毛变粗美型包 ID。 |
| `Face Mesh Eyebrow X Offset Custom Package Id` | 眉毛间距变宽美型包 ID。 |
| `Face Mesh Eyebrow Y Offset Custom Package Id` | 眉毛向上偏移美型包 ID。 |
| `Face Mesh Nose Head Width Custom Package Id` | 鼻头变窄美型包 ID。 |

### 美妆

| 参数 | 类型 | 范围 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `Makeup Enabled` | BOOL | 空 | `true` | 美妆开关。 |
| `Makeup Intensity` | FLOAT | `0..1` | `1` | 美妆总强度。 |

美妆包 ID 参数：

| 参数 | 说明 |
| --- | --- |
| `Makeup Lip Package Id` | 美妆口红包 ID。 |
| `Makeup Eyebrow Package Id` | 美妆眉毛包 ID。 |
| `Makeup Eyeshadow Package Id` | 美妆眼影包 ID。 |
| `Makeup Eyelash Package Id` | 美妆睫毛包 ID。 |
| `Makeup Eyeliner Package Id` | 美妆眼线包 ID。 |
| `Makeup Blusher Package Id` | 美妆腮红包 ID。 |
| `Makeup Shadow Package Id` | 美妆阴影包 ID。 |
| `Makeup Brighten Package Id` | 美妆提亮包 ID。 |
| `Makeup Eyeball Package Id` | 美妆眼球包 ID。 |

美妆颜色参数默认值均为 `0, 0, 0, 0`：

| 参数 | 说明 |
| --- | --- |
| `Makeup Lip Color` | 美妆口红颜色。 |
| `Makeup Eyebrow Color` | 美妆眉毛颜色。 |
| `Makeup Eyeshadow Color` | 美妆眼影颜色。 |
| `Makeup Eyelash Color` | 美妆睫毛颜色。 |
| `Makeup Eyeliner Color` | 美妆眼线颜色。 |
| `Makeup Blusher Color` | 美妆腮红颜色。 |
| `Makeup Shadow Color` | 美妆阴影颜色。 |
| `Makeup Brighten Color` | 美妆提亮颜色。 |
| `Makeup Eyeball Color` | 美妆眼球颜色。 |

> iOS 颜色类型：通过 `setColorVal:val:` 传入 `NvsColor *`（`r/g/b/a` 均为 `float`，范围 `0..1`）。Swift 侧构造 `NvsColor(r:g:b:a:)`。

美妆强度参数取值均为 `0..1`，默认值均为 `1`：

| 参数 | 说明 |
| --- | --- |
| `Makeup Lip Intensity` | 美妆口红强度。 |
| `Makeup Eyebrow Intensity` | 美妆眉毛强度。 |
| `Makeup Eyeshadow Intensity` | 美妆眼影强度。 |
| `Makeup Eyelash Intensity` | 美妆睫毛强度。 |
| `Makeup Eyeliner Intensity` | 美妆眼线强度。 |
| `Makeup Blusher Intensity` | 美妆腮红强度。 |
| `Makeup Shadow Intensity` | 美妆阴影强度。 |
| `Makeup Brighten Intensity` | 美妆提亮强度。 |
| `Makeup Eyeball Intensity` | 美妆眼球强度。 |

注：普通磨皮和高级磨皮不是完全互不影响。`Beauty Strength` 控制普通磨皮；`Advanced Beauty Intensity` 控制高级磨皮。当调整 `Beauty Strength` 时，如果 `Advanced Beauty Intensity` 不为 `0`，会叠加影响最终磨皮效果；反过来调整 `Advanced Beauty Intensity` 时，如果 `Beauty Strength` 不为 `0`，也会影响高级磨皮观感。生成代码默认按互斥处理：做普通磨皮时把 `Advanced Beauty Intensity` 置 `0`；做高级磨皮时把 `Beauty Strength` 置 `0`。这不是 SDK 强制规则，如果客户明确要叠加效果，可以保留两个强度并向客户解释会产生混合效果。

注：使用旧版美型包时，要同时将其对应的 `Strategy` 设置为 `0x7FFFFFFF`；新版 Face Mesh 美型包不需要设置 `Strategy`。

## 美颜需求澄清

客户口中的“美颜”大多数时候指 `AR Scene` 特效上的一组能力，不是单个参数。用户只说“接美颜”“加美颜”“实时美颜”但没有列明功能时，先询问需要哪些能力，再生成代码。

建议询问：

```text
你需要接哪些美颜能力？可以选：基础磨皮、高级磨皮、美白、红润、锐化、去油光、祛黑眼圈、祛法令纹、亮眼、白牙、瘦脸、小脸、窄脸、大眼、瘦鼻、下巴、额头、嘴角等。
如果你现在不确定，我可以先按全套美颜控制生成，所有强度默认关闭或为 0。
```

如果用户说“不知道”“你先写”“全都要”“先来一套完整的”，生成完整美颜控制集合。完整集合是指生成状态、UI/方法入口和参数设置方法；默认值保持关闭或 `0`，不要把所有效果默认开到最大。

AR Scene 美颜相关能力：

| 分类 | 能力 | 主要参数或接入方式 |
| --- | --- | --- |
| 基础美肤 | 基础磨皮 | `Beauty Effect`、`Beauty Strength`；默认同时把 `Advanced Beauty Intensity` 置 `0`，避免高级磨皮叠加影响 |
| 基础美肤 | 美白 A | `Beauty Whitening`，`Whitening Lut File` 传 `""`，`Whitening Lut Enabled` 传 `false` |
| 基础美肤 | 美白 B | `Beauty Whitening`，`Whitening Lut File` 使用本地路径，`Whitening Lut Enabled` 传 `true` |
| 基础美肤 | 红润 | `Beauty Reddening`、按需设置 `Reddening Lut File` |
| 基础美肤 | 默认美颜 LUT | `Default Beauty Enabled`、`Default Intensity`、`Default Beauty Lut File` |
| 基础美肤 | 锐化 | `Default Sharpen Enabled` |
| 基础美肤 | 只针对人脸 | `Beauty Face Only` |
| 基础美肤 | 极速模式 | `Beauty Fast Mode Enabled` |
| 高级美颜 | 高级磨皮 | `Advanced Beauty Enable`、`Advanced Beauty Intensity`、`Advanced Beauty Type`；默认同时把 `Beauty Strength` 置 `0`，避免普通磨皮叠加影响 |
| 高级美颜 | 高级磨皮类型 | `Advanced Beauty Type`；产品上有时作为“高级磨皮”的三种效果：`0` Android 标准，`1` iOS 标准，`2` 男性效果 |
| 高级美颜 | 祛黑眼圈 | `Advanced Beauty Remove Dark Circles Intensity` |
| 高级美颜 | 祛法令纹 | `Advanced Beauty Remove Nasolabial Folds Intensity` |
| 高级美颜 | 亮眼 | `Advanced Beauty Brighten Eyes Intensity`、按需设置 `Advanced Beauty Brighten Eyes Lut File` |
| 高级美颜 | 白牙 | `Advanced Beauty Whiten Teeth Intensity`、按需设置 `Advanced Beauty Whiten Teeth Lut File` |
| 高级美颜 | 人脸 LUT | `Advanced Beauty Face Lut Intensity`、`Advanced Beauty Face Lut File` |
| 高级美颜 | 去油光/哑光 | `Advanced Beauty Matte Intensity`、`Advanced Beauty Matte Fill Radius` |
| 高级美颜 | 高级预设 | `Advanced Beauty Presets Enabled`、`Advanced Beauty Presets String` |
| 美型 | 旧版 AR Scene 变形 | `Beauty Shape` 打开后使用 `Eye Size Warp Degree`、`Face Size Warp Degree`、`Nose Width Warp Degree` 等 `... Warp Degree` 参数 |
| 美型 | 新版美型素材包 | 安装 `.facemesh` 后设置 `Face Mesh ... Custom Package Id` 和 `Face Mesh ... Degree` |
| 微整形 | 旧版微整形素材包 | 安装 `.warp` 后设置 `Warp ... Custom Package Id` 和对应 degree 参数 |

生成完整美颜控制集合时，优先包含：

- 基础美肤：基础磨皮、美白 A、美白 B、红润、锐化、只针对人脸、极速模式。
- 高级美颜：高级磨皮三种类型、去油光、祛黑眼圈、祛法令纹、亮眼、白牙、人脸 LUT、高级预设入口。
- 美型/微整形：瘦脸、小脸、窄脸、大眼、眼角、瘦鼻、长鼻、下巴、额头、嘴型、嘴角、缩头等常见入口。

## 美颜参数

iOS setter 与鸿蒙 ArkTS 的对应：`setBooleanVal:val:` ↔ `setBooleanVal(...)`，`setFloatVal:val:` ↔ `setNumberVal(...)`（float），`setIntVal:val:` ↔ `setNumberVal(...)`（int），`setStringVal:val:` ↔ `setStringVal(...)`。

> `setFloatVal:val:` 的 `val` 是 `double`；传入 `0..1` 的 `float`/`CGFloat` 时直接写数值即可（Swift `Double(value)` 或字面量）。`Unified Max Faces`、`Advanced Beauty Type` 这类 INT 用 `setIntVal:val:`。

普通磨皮（Objective‑C）：

```objc
[arSceneFx setBooleanVal:@"Beauty Effect" val:YES];
[arSceneFx setFloatVal:@"Beauty Strength" val:value];
[arSceneFx setFloatVal:@"Advanced Beauty Intensity" val:0];
```

普通磨皮（Swift）：

```swift
arSceneFx.setBooleanVal("Beauty Effect", val: true)
arSceneFx.setFloatVal("Beauty Strength", val: value)
arSceneFx.setFloatVal("Advanced Beauty Intensity", val: 0)
```

说明：默认把高级磨皮强度清为 `0`，避免 `Advanced Beauty Intensity` 和 `Beauty Strength` 叠加。不要为了普通磨皮直接关闭 `Advanced Beauty Enable`，因为客户可能同时使用祛黑眼圈、祛法令纹、亮眼、白牙等高级美颜能力。

高级磨皮（Objective‑C）：

```objc
[arSceneFx setBooleanVal:@"Advanced Beauty Enable" val:YES];
[arSceneFx setIntVal:@"Advanced Beauty Type" val:advancedType]; // 0/1/2，iOS 默认用 1
[arSceneFx setFloatVal:@"Beauty Strength" val:0];
[arSceneFx setFloatVal:@"Advanced Beauty Intensity" val:value];
```

高级磨皮（Swift）：

```swift
arSceneFx.setBooleanVal("Advanced Beauty Enable", val: true)
arSceneFx.setIntVal("Advanced Beauty Type", val: advancedType) // 0/1/2，iOS 默认用 1
arSceneFx.setFloatVal("Beauty Strength", val: 0)
arSceneFx.setFloatVal("Advanced Beauty Intensity", val: value)
```

说明：默认把普通磨皮强度清为 `0`，避免 `Beauty Strength` 和 `Advanced Beauty Intensity` 叠加。如果客户明确希望基础磨皮和高级磨皮同时存在，可以保留两个值，但要说明最终效果会混合，调参时两边都会影响观感。

红润（Objective‑C）：

```objc
[arSceneFx setFloatVal:@"Beauty Reddening" val:value];
```

红润（Swift）：

```swift
arSceneFx.setFloatVal("Beauty Reddening", val: value)
```

去油光（Objective‑C）：

```objc
[arSceneFx setFloatVal:@"Advanced Beauty Matte Intensity" val:value];
```

去油光（Swift）：

```swift
arSceneFx.setFloatVal("Advanced Beauty Matte Intensity", val: value)
```

美白 A（Objective‑C）：

```objc
[arSceneFx setStringVal:@"Whitening Lut File" val:@""];
[arSceneFx setBooleanVal:@"Whitening Lut Enabled" val:NO];
[arSceneFx setFloatVal:@"Beauty Whitening" val:value];
```

美白 A（Swift）：

```swift
arSceneFx.setStringVal("Whitening Lut File", val: "")
arSceneFx.setBooleanVal("Whitening Lut Enabled", val: false)
arSceneFx.setFloatVal("Beauty Whitening", val: value)
```

美白 B（Objective‑C）：

```objc
[arSceneFx setStringVal:@"Whitening Lut File" val:whiteningLutPath]; // 本地/沙盒路径
[arSceneFx setBooleanVal:@"Whitening Lut Enabled" val:YES];
[arSceneFx setFloatVal:@"Beauty Whitening" val:value];
```

美白 B（Swift）：

```swift
arSceneFx.setStringVal("Whitening Lut File", val: whiteningLutPath)
arSceneFx.setBooleanVal("Whitening Lut Enabled", val: true)
arSceneFx.setFloatVal("Beauty Whitening", val: value)
```

## 美型和微整形

先按 `../nvs-asset-package-manager.md` 安装 `.facemesh` 或 `.warp`，得到 `packageId`。

应用（Objective‑C）：

```objc
[arSceneFx setStringVal:customPackageIdParamName val:packageId];
[arSceneFx setFloatVal:degreeParamName val:value];
```

应用（Swift）：

```swift
arSceneFx.setStringVal(customPackageIdParamName, val: packageId)
arSceneFx.setFloatVal(degreeParamName, val: value)
```

demo 常用美型/微整形快捷映射：

本表只列 demo 高频业务映射，方便根据中文功能生成代码；不是完整 SDK 参数表。新增能力或不确定参数时，以本文 [AR Scene 常用参数表](#ar-scene-常用参数表) 为准；常用表没有覆盖时再查 SDK 公开 Headers。

| 功能 | package id 参数 | degree 参数 |
| --- | --- | --- |
| 窄脸 | `Face Mesh Face Width Custom Package Id` | `Face Mesh Face Width Degree` |
| 小脸 | `Face Mesh Face Length Custom Package Id` | `Face Mesh Face Length Degree` |
| 瘦脸 | `Face Mesh Face Size Custom Package Id` | `Face Mesh Face Size Degree` |
| 额头 | `Face Mesh Forehead Height Custom Package Id` | `Face Mesh Forehead Height Degree` |
| 下巴 | `Face Mesh Chin Length Custom Package Id` | `Face Mesh Chin Length Degree` |
| 大眼 | `Face Mesh Eye Size Custom Package Id` | `Face Mesh Eye Size Degree` |
| 眼角 | `Face Mesh Eye Corner Stretch Custom Package Id` | `Face Mesh Eye Corner Stretch Degree` |
| 瘦鼻 | `Face Mesh Nose Width Custom Package Id` | `Face Mesh Nose Width Degree` |
| 长鼻 | `Face Mesh Nose Length Custom Package Id` | `Face Mesh Nose Length Degree` |
| 嘴型 | `Face Mesh Mouth Size Custom Package Id` | `Face Mesh Mouth Size Degree` |
| 嘴角 | `Face Mesh Mouth Corner Lift Custom Package Id` | `Face Mesh Mouth Corner Lift Degree` |
| 缩头 | `Warp Head Size Custom Package Id` | `Head Size Warp Degree` |

旧版 warp strategy（Objective‑C）：

```objc
[arSceneFx setIntVal:@"Forehead Height Warp Strategy" val:0x7fffffff];
[arSceneFx setIntVal:@"Head Size Warp Strategy" val:0x7fffffff];
```

旧版 warp strategy（Swift）：

```swift
arSceneFx.setIntVal("Forehead Height Warp Strategy", val: 0x7fffffff)
arSceneFx.setIntVal("Head Size Warp Strategy", val: 0x7fffffff)
```

## 美妆参数

先按 `../nvs-asset-package-manager.md` 安装 `.makeup`，得到 `packageId`。

应用单妆（Objective‑C）：

```objc
[arSceneFx setStringVal:@"Makeup Compound Package Id" val:@""];
[arSceneFx setFloatVal:@"Makeup Intensity" val:1];
[arSceneFx setStringVal:makeupClassName val:packageId];
[arSceneFx setFloatVal:[NSString stringWithFormat:@"Makeup %@ Intensity", makeupId] val:value];
```

应用单妆（Swift）：

```swift
arSceneFx.setStringVal("Makeup Compound Package Id", val: "")
arSceneFx.setFloatVal("Makeup Intensity", val: 1)
arSceneFx.setStringVal(makeupClassName, val: packageId)
arSceneFx.setFloatVal("Makeup \(makeupId) Intensity", val: value)
```

清空单妆（Objective‑C）：

```objc
[arSceneFx setStringVal:makeupClassName val:@""];
[arSceneFx setFloatVal:[NSString stringWithFormat:@"Makeup %@ Intensity", makeupId] val:0];
```

清空单妆（Swift）：

```swift
arSceneFx.setStringVal(makeupClassName, val: "")
arSceneFx.setFloatVal("Makeup \(makeupId) Intensity", val: 0)
```

demo 常用美妆 className 快捷映射：

本表只列 demo 高频业务映射，方便根据中文美妆分类生成代码；不是完整 SDK 参数表。新增能力或不确定参数时，以本文 [AR Scene 常用参数表](#ar-scene-常用参数表) 为准；常用表没有覆盖时再查 SDK 公开 Headers。

| 分类 | className |
| --- | --- |
| 口红 | `Makeup Lip Package Id` |
| 眼影 | `Makeup Eyeshadow Package Id` |
| 眉毛 | `Makeup Eyebrow Package Id` |
| 睫毛 | `Makeup Eyelash Package Id` |
| 眼线 | `Makeup Eyeliner Package Id` |
| 腮红 | `Makeup Blusher Package Id` |
| 高光 | `Makeup Brighten Package Id` |
| 修容 | `Makeup Shadow Package Id` |
| 美瞳 | `Makeup Eyeball Package Id` |

## AR 道具

先按 `../nvs-asset-package-manager.md` 安装 `.arscene`，得到 `sceneId`。

应用（Objective‑C）：

```objc
[arSceneFx setStringVal:@"Scene Id" val:sceneId];
```

应用（Swift）：

```swift
arSceneFx.setStringVal("Scene Id", val: sceneId)
```

取消（Objective‑C）：

```objc
[arSceneFx setStringVal:@"Scene Id" val:@""];
```

取消（Swift）：

```swift
arSceneFx.setStringVal("Scene Id", val: "")
```

## 按用户描述生成代码

用户说“接入美颜”：

- 用户没有列具体能力时，先按本文“美颜需求澄清”询问客户要哪些功能，不要默认只接基础磨皮。
- 用户不清楚、让先写或要求全套时，生成完整美颜控制集合，默认强度关闭或为 `0`。
- 先按 `../nvs-ar-scene.md` 选择基础人脸、`facecommon`、`advancedbeauty` 等模型和数据包并完成人体检测初始化。
- 采集预览用 `NvsStreamingContext -appendBuiltinCaptureVideoFx:@"AR Scene"`；时间线用 `NvsTimeline -addBuiltinTimelineVideoFx:duration:videoFxName:`。
- 按所需美颜类型调用 `setFloatVal:val:` / `setIntVal:val:` / `setBooleanVal:val:` / `setStringVal:val:`。
- 生成普通磨皮代码时，默认设置 `Beauty Strength = value` 并把 `Advanced Beauty Intensity = 0`；生成高级磨皮代码时，默认设置 `Advanced Beauty Intensity = value` 并把 `Beauty Strength = 0`。
- 这两个强度的互斥处理是默认业务策略，不是 SDK 强制限制。客户问原因时，解释为：`Beauty Strength` 和 `Advanced Beauty Intensity` 同时不为 `0` 会叠加影响最终磨皮效果；客户要混合效果时可以保留两个值一起调。
- 如果用户要的是肤色包、校色包或普通滤镜包，不写到 `AR Scene`；回到 `../nvs-fx.md` / `../nvs-asset-package-manager.md` 创建独立 effect。

用户说“接入美型/微整形”：

- 先按 `../nvs-ar-scene.md` 选择基础人脸和 `facecommon`。
- 按 `../nvs-asset-package-manager.md` 安装 `.facemesh` 或 `.warp`，取得非空 `packageId`。
- 创建或复用 `AR Scene`（采集/时间线任一）。
- 对 `arSceneFx` 设置 custom package id 参数和 degree 参数。

用户说“接入美妆”：

- 先按 `../nvs-ar-scene.md` 选择基础人脸、`facecommon`，眼部美妆按需增加 `eyecontour`。
- 按 `../nvs-asset-package-manager.md` 安装 `.makeup`，取得非空 `packageId`。
- 创建或复用 `AR Scene`。
- 设置 `Makeup ... Package Id` 和 `Makeup ... Intensity`。

用户说“接入道具/AR 道具”：

- 先按 `../nvs-ar-scene.md` 根据道具能力选择模型；道具功能默认包含基础人脸、`facecommon` 和 `fakeface`，再按素材能力增加手势、Avatar、分割等模型。
- 按 `../nvs-asset-package-manager.md` 安装 `.arscene`，取得非空 `sceneId`。
- 创建或复用 `AR Scene`。
- 设置或清空 `Scene Id`。

用户说“直接设置 AR Scene 参数”：

- 先查本文 [AR Scene 常用参数表](#ar-scene-常用参数表)。
- 按参数类型调用 `setFloatVal:val:`（float/double）、`setIntVal:val:`（int）、`setBooleanVal:val:`（bool）、`setStringVal:val:`（string）、`setColorVal:val:`（`NvsColor *`）。
