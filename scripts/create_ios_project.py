#!/usr/bin/env python3
"""Create or stage a dependency-closed iOS Streaming SDK project skeleton."""

from __future__ import annotations

import argparse
import json
import plistlib
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
from compose_modules import compose, split_ids  # noqa: E402

PRIVACY_KEYS = {
    "camera": ("NSCameraUsageDescription", "Camera access is required for video capture."),
    "microphone": ("NSMicrophoneUsageDescription", "Microphone access is required for recording audio."),
    "photo-library-read": ("NSPhotoLibraryUsageDescription", "Photo Library access is required to import selected media."),
    "photo-library-add": ("NSPhotoLibraryAddUsageDescription", "Photo Library access is required to save exported media.")
}

SWIFT_UNIT_IDS = {
    "objc.context.initialize": "swift.context.initialize",
    "objc.timeline.create": "swift.timeline.create",
    "objc.video.append-photo-asset": "swift.video.append-photo-asset",
    "objc.preview.connect": "swift.preview.connect",
    "objc.compile.custom-height": "swift.compile.custom-height",
    "objc.timeline.remove": "swift.timeline.remove",
}


def adapt_plan_for_language(plan: dict, language: str) -> dict:
    plan["language"] = language
    plan["signature_truth"] = "objective-c-public-headers"
    if language != "swift":
        return plan
    plan["simple_code_ids"] = [SWIFT_UNIT_IDS.get(item, item) for item in plan.get("simple_code_ids", [])]
    for recipe in plan.get("recipe_details", []):
        recipe["simple_code_ids"] = [SWIFT_UNIT_IDS.get(item, item) for item in recipe.get("simple_code_ids", [])]
    plan["verification_states"] = {
        module_id: ("swift_compiled_unit" if state == "objc_compiled_unit" else state)
        for module_id, state in plan.get("verification_states", {}).items()
    }
    return plan


def safe_name(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "", value.replace(" ", "_"))
    if not result or result[0].isdigit():
        result = f"Meishe{result}"
    return result


def write_text(path: Path, value: str, force: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.write_text(value, encoding="utf-8")


def copy_template(template: Path, destination: Path, app_name: str, force: bool) -> list[Path]:
    copied = []
    for source in sorted(template.iterdir()):
        if not source.is_file():
            continue
        name = "Info.plist" if source.name == "Info.plist.template" else source.name
        target = destination / name
        value = source.read_text(encoding="utf-8").replace("__APP_NAME__", app_name)
        write_text(target, value, force)
        copied.append(target)
    return copied


def controller_source(language: str) -> dict[str, str]:
    if language == "swift":
        return {
            "MSIOStreamingContract.swift": """import Foundation

#if canImport(NvStreamingSdkCore)
import NvStreamingSdkCore
#endif

enum MSIOTimelineOwnership: String, Codable {
    case editorOwned = "EDITOR_OWNED"
    case hostOwned = "HOST_OWNED"
}

#if canImport(NvStreamingSdkCore)
enum MSIOStreamingContract {
    static func context(licensePath: String, flags: NvsStreamingContextFlag) -> NvsStreamingContext? {
        precondition(Thread.isMainThread, "NvsStreamingContext must be initialized on the main thread.")
        guard !licensePath.isEmpty, NvsStreamingContext.verifySdkLicenseFile(licensePath) else { return nil }
        return NvsStreamingContext.sharedInstance(withFlags: flags)
    }

    static func timeline(
        context: NvsStreamingContext,
        width: UInt32,
        height: UInt32,
        flags: NvsStreamingContextFlag
    ) -> NvsTimeline? {
        precondition(Thread.isMainThread, "Timeline creation must run on the main thread.")
        guard width % 4 == 0, height % 2 == 0 else { return nil }
        let pixels = UInt64(width) * UInt64(height)
        let supports4K = (flags.rawValue & NvsStreamingContextFlag_Support4KEdit.rawValue) != 0
        let limit: UInt64 = supports4K ? 3_840 * 2_160 : 1_920 * 1_080
        guard pixels <= limit else { return nil }

        var video = NvsVideoResolution(
            imageWidth: width,
            imageHeight: height,
            imagePAR: NvsRational(num: 1, den: 1),
            bitDepth: NvsVideoResolutionBitDepth(rawValue: 0)
        )
        var fps = NvsRational(num: 30, den: 1)
        var audio = NvsAudioResolution(
            sampleRate: 48_000,
            sampleFormat: NvsAudioSampleFormat(rawValue: 1),
            channelCount: 2
        )
        return context.createTimeline(&video, videoFps: &fps, audioEditRes: &audio)
    }

    static func appendPhotosIdentifier(_ identifier: String, to track: NvsVideoTrack) -> NvsVideoClip? {
        precondition(Thread.isMainThread, "Timeline mutation must run on the main thread.")
        guard !identifier.isEmpty else { return nil }
        return track.appendClip(identifier)
    }

    static func compileTimeline(
        _ timeline: NvsTimeline,
        context: NvsStreamingContext,
        outputPath: String,
        height: UInt32
    ) -> Bool {
        precondition(Thread.isMainThread, "Compilation must start on the main thread.")
        guard !outputPath.isEmpty, height > 0, timeline.duration > 0 else { return false }
        context.stop()
        context.setCustomCompileVideoHeight(height)
        return context.compileTimeline(
            timeline,
            startTime: 0,
            endTime: timeline.duration,
            outputFilePath: outputPath,
            videoResolutionGrade: NvsCompileVideoResolutionGradeCustom,
            videoBitrateGrade: NvsCompileBitrateGradeHigh,
            flags: 0
        )
    }
}
#endif
"""
        }
    return {
        "MSIOStreamingContract.h": """#import <Foundation/Foundation.h>

typedef NS_ENUM(NSInteger, MSIOTimelineOwnership) {
    MSIOTimelineOwnershipEditorOwned,
    MSIOTimelineOwnershipHostOwned
};

#if __has_include(<NvStreamingSdkCore/NvStreamingSdkCore.h>)
#import <NvStreamingSdkCore/NvStreamingSdkCore.h>

NS_ASSUME_NONNULL_BEGIN
@interface MSIOStreamingContract : NSObject
+ (nullable NvsStreamingContext *)contextWithLicense:(NSString *)licensePath flags:(NvsStreamingContextFlag)flags;
+ (nullable NvsTimeline *)timelineWithContext:(NvsStreamingContext *)context width:(unsigned int)width height:(unsigned int)height flags:(NvsStreamingContextFlag)flags;
+ (nullable NvsVideoClip *)appendPhotosIdentifier:(NSString *)identifier toTrack:(NvsVideoTrack *)track;
+ (BOOL)compileTimeline:(NvsTimeline *)timeline context:(NvsStreamingContext *)context outputPath:(NSString *)outputPath height:(unsigned int)height;
@end
NS_ASSUME_NONNULL_END
#endif
""",
        "MSIOStreamingContract.m": """#import "MSIOStreamingContract.h"

#if __has_include(<NvStreamingSdkCore/NvStreamingSdkCore.h>)
@implementation MSIOStreamingContract
+ (NvsStreamingContext *)contextWithLicense:(NSString *)licensePath flags:(NvsStreamingContextFlag)flags {
    NSAssert(NSThread.isMainThread, @"NvsStreamingContext must be initialized on the main thread.");
    if (licensePath.length == 0) { return nil; }
    if (![NvsStreamingContext verifySdkLicenseFile:licensePath]) { return nil; }
    return [NvsStreamingContext sharedInstanceWithFlags:flags];
}
+ (NvsTimeline *)timelineWithContext:(NvsStreamingContext *)context width:(unsigned int)width height:(unsigned int)height flags:(NvsStreamingContextFlag)flags {
    NSAssert(NSThread.isMainThread, @"Timeline creation must run on the main thread.");
    if (context == nil) { return nil; }
    if (width % 4 != 0 || height % 2 != 0) { return nil; }
    uint64_t pixels = (uint64_t)width * (uint64_t)height;
    uint64_t limit = (flags & NvsStreamingContextFlag_Support4KEdit) ? (uint64_t)3840 * 2160 : (uint64_t)1920 * 1080;
    if (pixels > limit) { return nil; }
    NvsVideoResolution video = {0};
    video.imageWidth = width;
    video.imageHeight = height;
    video.imagePAR = (NvsRational){1, 1};
    NvsRational fps = {30, 1};
    NvsAudioResolution audio = {48000, 2, NvsAudSmpFmt_S16};
    return [context createTimeline:&video videoFps:&fps audioEditRes:&audio];
}
+ (NvsVideoClip *)appendPhotosIdentifier:(NSString *)identifier toTrack:(NvsVideoTrack *)track {
    NSAssert(NSThread.isMainThread, @"Timeline mutation must run on the main thread.");
    if (track == nil || identifier.length == 0) { return nil; }
    return [track appendClip:identifier];
}
+ (BOOL)compileTimeline:(NvsTimeline *)timeline context:(NvsStreamingContext *)context outputPath:(NSString *)outputPath height:(unsigned int)height {
    NSAssert(NSThread.isMainThread, @"Compilation must start on the main thread.");
    if (timeline == nil || context == nil || outputPath.length == 0 || height == 0 || timeline.duration <= 0) { return NO; }
    [context stop];
    [context setCustomCompileVideoHeight:height];
    return [context compileTimeline:timeline startTime:0 endTime:timeline.duration outputFilePath:outputPath videoResolutionGrade:NvsCompileVideoResolutionGradeCustom videoBitrateGrade:NvsCompileBitrateGradeHigh flags:0];
}
@end
#endif
"""
    }


def objc_runtime_view_controller(app_name: str) -> str:
    title = app_name.replace("\\", "\\\\").replace('"', '\\"')
    return f'''#import "ViewController.h"
#import "MSIOStreamingContract.h"

@import Photos;
@import PhotosUI;

#if __has_include(<NvStreamingSdkCore/NvStreamingSdkCore.h>)
@interface ViewController () <PHPickerViewControllerDelegate, NvsStreamingContextDelegate>
@property (nonatomic, strong) NvsStreamingContext *context;
@property (nonatomic, strong) NvsTimeline *timeline;
@property (nonatomic, strong) NvsVideoTrack *videoTrack;
@property (nonatomic, strong) NvsLiveWindow *liveWindow;
@property (nonatomic, strong) UILabel *statusLabel;
@property (nonatomic, copy) NSString *compileOutputPath;
@property (nonatomic, assign) BOOL previewConnected;
@end

@implementation ViewController

- (void)viewDidLoad {{
    [super viewDidLoad];
    self.title = @"{title}";
    self.view.backgroundColor = UIColor.systemBackgroundColor;
    [self buildInterface];
    [self initializeSDK];
}}

- (void)viewDidAppear:(BOOL)animated {{
    [super viewDidAppear:animated];
    [self connectPreviewWhenDrawable];
}}

- (void)buildInterface {{
    self.liveWindow = [[NvsLiveWindow alloc] initWithFrame:CGRectZero];
    self.liveWindow.translatesAutoresizingMaskIntoConstraints = NO;
    self.liveWindow.backgroundColor = UIColor.blackColor;

    self.statusLabel = UILabel.new;
    self.statusLabel.accessibilityIdentifier = @"skillValidationStatus";
    self.statusLabel.text = @"STARTING";
    self.statusLabel.numberOfLines = 0;
    self.statusLabel.textAlignment = NSTextAlignmentCenter;

    UIButton *pickButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [pickButton setTitle:@"Pick a Photos video" forState:UIControlStateNormal];
    pickButton.accessibilityIdentifier = @"pickPhotosVideo";
    [pickButton addTarget:self action:@selector(pickVideo) forControlEvents:UIControlEventTouchUpInside];

    UIButton *playButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [playButton setTitle:@"Play Timeline" forState:UIControlStateNormal];
    playButton.accessibilityIdentifier = @"playTimeline";
    [playButton addTarget:self action:@selector(playTimeline) forControlEvents:UIControlEventTouchUpInside];

    UIButton *exportButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [exportButton setTitle:@"Compile 720p" forState:UIControlStateNormal];
    exportButton.accessibilityIdentifier = @"compileTimeline";
    [exportButton addTarget:self action:@selector(compileTimeline) forControlEvents:UIControlEventTouchUpInside];

    UIStackView *buttons = [[UIStackView alloc] initWithArrangedSubviews:@[pickButton, playButton, exportButton]];
    buttons.axis = UILayoutConstraintAxisVertical;
    buttons.spacing = 12;

    UIStackView *stack = [[UIStackView alloc] initWithArrangedSubviews:@[self.liveWindow, self.statusLabel, buttons]];
    stack.axis = UILayoutConstraintAxisVertical;
    stack.spacing = 16;
    stack.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:stack];
    [NSLayoutConstraint activateConstraints:@[
        [stack.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor constant:16],
        [stack.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:20],
        [stack.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-20],
        [self.liveWindow.heightAnchor constraintEqualToAnchor:self.liveWindow.widthAnchor multiplier:9.0 / 16.0]
    ]];
}}

- (void)initializeSDK {{
    NSAssert(NSThread.isMainThread, @"SDK initialization must run on the main thread.");
    NSString *licensePath = [NSBundle.mainBundle pathForResource:@"meishesdk" ofType:@"lic"];
    NvsStreamingContextFlag flags = NvsStreamingContextFlag_Support4KEdit;
    self.context = [MSIOStreamingContract contextWithLicense:licensePath ?: @"" flags:flags];
    if (self.context == nil) {{ [self setStatus:@"LICENSE_OR_CONTEXT_FAILED"]; return; }}
    self.context.delegate = self;

    self.timeline = [MSIOStreamingContract timelineWithContext:self.context width:1280 height:720 flags:flags];
    if (self.timeline == nil) {{ [self setStatus:@"TIMELINE_CREATE_FAILED"]; return; }}
    self.videoTrack = [self.timeline appendVideoTrack];
    if (self.videoTrack == nil) {{ [self setStatus:@"VIDEO_TRACK_CREATE_FAILED"]; return; }}
    [self setStatus:@"SDK_READY TIMELINE_1280x720"];
}}

- (void)connectPreviewWhenDrawable {{
    if (self.previewConnected || self.context == nil || self.timeline == nil) {{ return; }}
    [self.view layoutIfNeeded];
    if (self.liveWindow.window == nil || CGRectIsEmpty(self.liveWindow.bounds)) {{
        [self setStatus:@"LIVEWINDOW_NOT_DRAWABLE"];
        return;
    }}
    if (![self.context connectTimeline:self.timeline withLiveWindow:self.liveWindow]) {{
        [self setStatus:@"LIVEWINDOW_CONNECT_FAILED"];
        return;
    }}
    self.previewConnected = YES;
    [self setStatus:@"SDK_READY TIMELINE_1280x720 CONNECTED"];
}}

- (void)pickVideo {{
    if (self.videoTrack == nil) {{ [self setStatus:@"SDK_NOT_READY"]; return; }}
    PHAuthorizationStatus status = [PHPhotoLibrary authorizationStatusForAccessLevel:PHAccessLevelReadWrite];
    if (status == PHAuthorizationStatusNotDetermined) {{
        __weak typeof(self) weakSelf = self;
        [PHPhotoLibrary requestAuthorizationForAccessLevel:PHAccessLevelReadWrite handler:^(PHAuthorizationStatus result) {{
            dispatch_async(dispatch_get_main_queue(), ^{{
                if (result == PHAuthorizationStatusAuthorized || result == PHAuthorizationStatusLimited) {{
                    [weakSelf presentVideoPicker];
                }} else {{
                    [weakSelf setStatus:@"PHOTOS_PERMISSION_DENIED"];
                }}
            }});
        }}];
        return;
    }}
    if (status != PHAuthorizationStatusAuthorized && status != PHAuthorizationStatusLimited) {{
        [self setStatus:@"PHOTOS_PERMISSION_DENIED"];
        return;
    }}
    [self presentVideoPicker];
}}

- (void)presentVideoPicker {{
    PHPickerConfiguration *configuration = [[PHPickerConfiguration alloc] initWithPhotoLibrary:PHPhotoLibrary.sharedPhotoLibrary];
    configuration.filter = PHPickerFilter.videosFilter;
    configuration.selectionLimit = 1;
    PHPickerViewController *picker = [[PHPickerViewController alloc] initWithConfiguration:configuration];
    picker.delegate = self;
    [self presentViewController:picker animated:YES completion:nil];
}}

- (void)picker:(PHPickerViewController *)picker didFinishPicking:(NSArray<PHPickerResult *> *)results {{
    [picker dismissViewControllerAnimated:YES completion:nil];
    NSString *identifier = results.firstObject.assetIdentifier;
    if (identifier.length == 0) {{ [self setStatus:@"NO_PHASSET_LOCAL_IDENTIFIER"]; return; }}
    [self.context stop];
    NvsVideoClip *clip = [MSIOStreamingContract appendPhotosIdentifier:identifier toTrack:self.videoTrack];
    if (clip == nil) {{ [self setStatus:@"APPEND_LOCAL_IDENTIFIER_FAILED"]; return; }}
    BOOL sought = [self.context seekTimeline:self.timeline timestamp:0 videoSizeMode:NvsVideoPreviewSizeModeLiveWindowSize flags:0];
    [self setStatus:sought ? @"LOCAL_IDENTIFIER_APPENDED SEEK_OK" : @"LOCAL_IDENTIFIER_APPENDED SEEK_FAILED"];
}}

- (void)playTimeline {{
    if (self.timeline.duration <= 0) {{ [self setStatus:@"SELECT_VIDEO_FIRST"]; return; }}
    BOOL started = [self.context playbackTimeline:self.timeline startTime:0 endTime:self.timeline.duration videoSizeMode:NvsVideoPreviewSizeModeLiveWindowSize preload:YES flags:0];
    [self setStatus:started ? @"PLAYBACK_STARTED" : @"PLAYBACK_START_FAILED"];
}}

- (void)compileTimeline {{
    if (self.timeline.duration <= 0) {{ [self setStatus:@"SELECT_VIDEO_FIRST"]; return; }}
    NSString *directory = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
    self.compileOutputPath = [directory stringByAppendingPathComponent:@"skill-validation-output.mp4"];
    [NSFileManager.defaultManager removeItemAtPath:self.compileOutputPath error:nil];
    BOOL started = [MSIOStreamingContract compileTimeline:self.timeline context:self.context outputPath:self.compileOutputPath height:720];
    [self setStatus:started ? @"COMPILE_STARTED CUSTOM_HEIGHT_720" : @"COMPILE_START_FAILED"];
}}

- (void)didCompileProgress:(NvsTimeline *)timeline progress:(int)progress {{
    [self setStatus:[NSString stringWithFormat:@"COMPILE_PROGRESS_%d", progress]];
}}

- (void)didCompileCompleted:(NvsTimeline *)timeline isCanceled:(BOOL)isCanceled {{
    BOOL exists = [NSFileManager.defaultManager fileExistsAtPath:self.compileOutputPath];
    [self setStatus:(!isCanceled && exists) ? @"COMPILE_SUCCEEDED" : @"COMPILE_CANCELED_OR_MISSING_OUTPUT"];
}}

- (void)didCompileFailed:(NvsTimeline *)timeline {{ [self setStatus:@"COMPILE_FAILED"]; }}

- (void)didPlaybackEOF:(NvsTimeline *)timeline {{ [self setStatus:@"PLAYBACK_EOF"]; }}

- (void)setStatus:(NSString *)status {{
    NSLog(@"SKILL_STATUS %@", status);
    dispatch_async(dispatch_get_main_queue(), ^{{ self.statusLabel.text = status; }});
}}

- (void)dealloc {{
    if (self.context.delegate == self) {{ self.context.delegate = nil; }}
    [self.context stop];
    if (self.timeline != nil) {{ [self.context removeTimeline:self.timeline]; }}
}}

@end
#else
@implementation ViewController
- (void)viewDidLoad {{
    [super viewDidLoad];
    self.view.backgroundColor = UIColor.systemBackgroundColor;
}}
@end
#endif
'''


def swift_runtime_view_controller(app_name: str) -> str:
    title = app_name.replace("\\", "\\\\").replace('"', '\\"')
    return f'''import UIKit
import Photos
import PhotosUI
import NvStreamingSdkCore

final class ViewController: UIViewController, PHPickerViewControllerDelegate, NvsStreamingContextDelegate {{
    private let contextFlags = NvsStreamingContextFlag_Support4KEdit
    private let liveWindow: NvsLiveWindow = NvsLiveWindow()!
    private let statusLabel = UILabel()
    private var context: NvsStreamingContext?
    private var timeline: NvsTimeline?
    private var videoTrack: NvsVideoTrack?
    private var compileOutputPath = ""
    private var previewConnected = false

    override func viewDidLoad() {{
        super.viewDidLoad()
        title = "{title}"
        view.backgroundColor = .systemBackground
        buildInterface()
        initializeSDK()
    }}

    override func viewDidAppear(_ animated: Bool) {{
        super.viewDidAppear(animated)
        connectPreviewWhenDrawable()
    }}

    private func buildInterface() {{
        liveWindow.translatesAutoresizingMaskIntoConstraints = false
        liveWindow.backgroundColor = .black

        statusLabel.accessibilityIdentifier = "skillValidationStatus"
        statusLabel.text = "STARTING"
        statusLabel.numberOfLines = 0
        statusLabel.textAlignment = .center

        let pickButton = makeButton(title: "Pick a Photos video", identifier: "pickPhotosVideo", action: #selector(pickVideo))
        let playButton = makeButton(title: "Play Timeline", identifier: "playTimeline", action: #selector(playTimeline))
        let exportButton = makeButton(title: "Compile 720p", identifier: "compileTimeline", action: #selector(compileTimeline))
        let buttons = UIStackView(arrangedSubviews: [pickButton, playButton, exportButton])
        buttons.axis = .vertical
        buttons.spacing = 12

        let stack = UIStackView(arrangedSubviews: [liveWindow, statusLabel, buttons])
        stack.axis = .vertical
        stack.spacing = 16
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            liveWindow.heightAnchor.constraint(equalTo: liveWindow.widthAnchor, multiplier: 9.0 / 16.0)
        ])
    }}

    private func makeButton(title: String, identifier: String, action: Selector) -> UIButton {{
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        button.accessibilityIdentifier = identifier
        button.addTarget(self, action: action, for: .touchUpInside)
        return button
    }}

    private func initializeSDK() {{
        precondition(Thread.isMainThread, "SDK initialization must run on the main thread.")
        guard let licensePath = Bundle.main.path(forResource: "meishesdk", ofType: "lic") else {{
            setStatus("LICENSE_RESOURCE_MISSING")
            return
        }}
        guard let context = MSIOStreamingContract.context(licensePath: licensePath, flags: contextFlags) else {{
            setStatus("LICENSE_OR_CONTEXT_FAILED")
            return
        }}
        self.context = context
        context.delegate = self

        guard let timeline = MSIOStreamingContract.timeline(
            context: context,
            width: 1_280,
            height: 720,
            flags: contextFlags
        ) else {{
            setStatus("TIMELINE_CREATE_FAILED")
            return
        }}
        self.timeline = timeline
        guard let videoTrack = timeline.appendVideoTrack() else {{
            setStatus("VIDEO_TRACK_CREATE_FAILED")
            return
        }}
        self.videoTrack = videoTrack
        setStatus("SDK_READY TIMELINE_1280x720")
    }}

    private func connectPreviewWhenDrawable() {{
        guard !previewConnected, let context, let timeline else {{ return }}
        view.layoutIfNeeded()
        guard liveWindow.window != nil, !liveWindow.bounds.isEmpty else {{
            setStatus("LIVEWINDOW_NOT_DRAWABLE")
            return
        }}
        guard context.connect(timeline, with: liveWindow) else {{
            setStatus("LIVEWINDOW_CONNECT_FAILED")
            return
        }}
        previewConnected = true
        setStatus("SDK_READY TIMELINE_1280x720 CONNECTED")
    }}

    @objc private func pickVideo() {{
        guard videoTrack != nil else {{ setStatus("SDK_NOT_READY"); return }}
        let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)
        if status == .notDetermined {{
            PHPhotoLibrary.requestAuthorization(for: .readWrite) {{ [weak self] result in
                DispatchQueue.main.async {{
                    guard let self else {{ return }}
                    if result == .authorized || result == .limited {{
                        self.presentVideoPicker()
                    }} else {{
                        self.setStatus("PHOTOS_PERMISSION_DENIED")
                    }}
                }}
            }}
            return
        }}
        guard status == .authorized || status == .limited else {{
            setStatus("PHOTOS_PERMISSION_DENIED")
            return
        }}
        presentVideoPicker()
    }}

    private func presentVideoPicker() {{
        var configuration = PHPickerConfiguration(photoLibrary: .shared())
        configuration.filter = .videos
        configuration.selectionLimit = 1
        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = self
        present(picker, animated: true)
    }}

    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {{
        picker.dismiss(animated: true)
        guard let identifier = results.first?.assetIdentifier, !identifier.isEmpty else {{
            setStatus("NO_PHASSET_LOCAL_IDENTIFIER")
            return
        }}
        guard let context, let timeline, let videoTrack else {{ setStatus("SDK_NOT_READY"); return }}
        context.stop()
        guard MSIOStreamingContract.appendPhotosIdentifier(identifier, to: videoTrack) != nil else {{
            setStatus("APPEND_LOCAL_IDENTIFIER_FAILED")
            return
        }}
        let sought = context.seekTimeline(
            timeline,
            timestamp: 0,
            videoSizeMode: NvsVideoPreviewSizeModeLiveWindowSize,
            flags: 0
        )
        setStatus(sought ? "LOCAL_IDENTIFIER_APPENDED SEEK_OK" : "LOCAL_IDENTIFIER_APPENDED SEEK_FAILED")
    }}

    @objc private func playTimeline() {{
        guard let context, let timeline, timeline.duration > 0 else {{ setStatus("SELECT_VIDEO_FIRST"); return }}
        let started = context.playbackTimeline(
            timeline,
            startTime: 0,
            endTime: timeline.duration,
            videoSizeMode: NvsVideoPreviewSizeModeLiveWindowSize,
            preload: true,
            flags: 0
        )
        setStatus(started ? "PLAYBACK_STARTED" : "PLAYBACK_START_FAILED")
    }}

    @objc private func compileTimeline() {{
        guard let context, let timeline, timeline.duration > 0 else {{ setStatus("SELECT_VIDEO_FIRST"); return }}
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        compileOutputPath = documents.appendingPathComponent("skill-validation-output.mp4").path
        try? FileManager.default.removeItem(atPath: compileOutputPath)
        let started = MSIOStreamingContract.compileTimeline(
            timeline,
            context: context,
            outputPath: compileOutputPath,
            height: 720
        )
        setStatus(started ? "COMPILE_STARTED CUSTOM_HEIGHT_720" : "COMPILE_START_FAILED")
    }}

    func didCompileProgress(_ timeline: NvsTimeline!, progress: Int32) {{
        setStatus("COMPILE_PROGRESS_\\(progress)")
    }}

    func didCompileCompleted(_ timeline: NvsTimeline!, isCanceled: Bool) {{
        let exists = FileManager.default.fileExists(atPath: compileOutputPath)
        setStatus(!isCanceled && exists ? "COMPILE_SUCCEEDED" : "COMPILE_CANCELED_OR_MISSING_OUTPUT")
    }}

    func didCompileFailed(_ timeline: NvsTimeline!) {{ setStatus("COMPILE_FAILED") }}
    func didPlaybackEOF(_ timeline: NvsTimeline!) {{ setStatus("PLAYBACK_EOF") }}

    private func setStatus(_ status: String) {{
        print("SKILL_STATUS \\(status)")
        if Thread.isMainThread {{
            statusLabel.text = status
        }} else {{
            DispatchQueue.main.async {{ [weak self] in self?.statusLabel.text = status }}
        }}
    }}

    deinit {{
        context?.delegate = nil
        context?.stop()
        if let context, let timeline {{ _ = context.remove(timeline) }}
    }}
}}
'''


def pbxproj(app: str, bundle_id: str, language: str, source_names: list[str], framework: bool, resource_names: list[str]) -> str:
    source_refs = []
    source_build = []
    source_phase = []
    children = []
    resource_refs = []
    resource_build = []
    resource_phase = []
    for index, name in enumerate(source_names, start=1):
        ref = f"A1{index:022X}"[-24:]
        build = f"B1{index:022X}"[-24:]
        file_type = "sourcecode.swift" if name.endswith(".swift") else ("sourcecode.c.objc" if name.endswith(".m") else "sourcecode.c.h")
        source_refs.append(f"\t\t{ref} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = {file_type}; path = {name}; sourceTree = \"<group>\"; }};")
        children.append(f"\t\t\t\t{ref} /* {name} */,")
        if name.endswith((".m", ".swift")):
            source_build.append(f"\t\t{build} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {ref} /* {name} */; }};")
            source_phase.append(f"\t\t\t\t{build} /* {name} in Sources */,")
    for index, name in enumerate(resource_names, start=1):
        ref = f"C2{index:022X}"[-24:]
        build = f"D2{index:022X}"[-24:]
        resource_refs.append(f"\t\t{ref} /* {Path(name).name} */ = {{isa = PBXFileReference; lastKnownFileType = file; path = {name}; sourceTree = \"<group>\"; }};")
        resource_build.append(f"\t\t{build} /* {Path(name).name} in Resources */ = {{isa = PBXBuildFile; fileRef = {ref} /* {Path(name).name} */; }};")
        resource_phase.append(f"\t\t\t\t{build} /* {Path(name).name} in Resources */,")
        children.append(f"\t\t\t\t{ref} /* {Path(name).name} */,")
    framework_build = ""
    framework_ref = ""
    framework_child = ""
    framework_phase = ""
    embed_phase = ""
    embed_phase_id = ""
    target_phases = ""
    framework_settings = ""
    if framework:
        framework_build = "\t\tF10000000000000000000001 /* NvStreamingSdkCore.framework in Frameworks */ = {isa = PBXBuildFile; fileRef = F10000000000000000000002 /* NvStreamingSdkCore.framework */; };\n\t\tF10000000000000000000003 /* NvStreamingSdkCore.framework in Embed Frameworks */ = {isa = PBXBuildFile; fileRef = F10000000000000000000002 /* NvStreamingSdkCore.framework */; settings = {ATTRIBUTES = (CodeSignOnCopy, RemoveHeadersOnCopy, ); }; };"
        framework_ref = "\t\tF10000000000000000000002 /* NvStreamingSdkCore.framework */ = {isa = PBXFileReference; lastKnownFileType = wrapper.framework; path = Frameworks/NvStreamingSdkCore.framework; sourceTree = \"<group>\"; };"
        framework_child = "\t\t\t\tF10000000000000000000002 /* NvStreamingSdkCore.framework */,"
        framework_phase = "\t\t\t\tF10000000000000000000001 /* NvStreamingSdkCore.framework in Frameworks */,"
        embed_phase_id = "\t\t\t\tF10000000000000000000004 /* Embed Frameworks */,"
        embed_phase = """/* Begin PBXCopyFilesBuildPhase section */
\t\tF10000000000000000000004 /* Embed Frameworks */ = {
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 10;
\t\t\tfiles = (F10000000000000000000003 /* NvStreamingSdkCore.framework in Embed Frameworks */, );
\t\t\tname = "Embed Frameworks";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t};
/* End PBXCopyFilesBuildPhase section */"""
        framework_settings = '\n\t\t\t\tFRAMEWORK_SEARCH_PATHS = "$(PROJECT_DIR)/Frameworks";\n\t\t\t\tLD_RUNPATH_SEARCH_PATHS = "$(inherited) @executable_path/Frameworks";'
    swift_setting = "\n\t\t\t\tSWIFT_VERSION = 5.0;" if language == "swift" else ""
    objc_prefix = "-fobjc-arc" if language == "objc" else ""
    return f"""// !$*UTF8*$!
{{
\tarchiveVersion = 1;
\tclasses = {{}};
\tobjectVersion = 56;
\tobjects = {{
/* Begin PBXBuildFile section */
{chr(10).join(source_build)}
{chr(10).join(resource_build)}
{framework_build}
/* End PBXBuildFile section */
{embed_phase}
/* Begin PBXFileReference section */
{chr(10).join(source_refs)}
{chr(10).join(resource_refs)}
\t\tC10000000000000000000001 /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\tC10000000000000000000002 /* {app}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {app}.app; sourceTree = BUILT_PRODUCTS_DIR; }};
{framework_ref}
/* End PBXFileReference section */
/* Begin PBXFrameworksBuildPhase section */
\t\tD10000000000000000000001 = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (
{framework_phase}
\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXFrameworksBuildPhase section */
/* Begin PBXGroup section */
\t\tE10000000000000000000001 = {{isa = PBXGroup; children = (
{chr(10).join(children)}
\t\t\t\tC10000000000000000000001 /* Info.plist */,
{framework_child}
\t\t\t\tE10000000000000000000002 /* Products */,
\t\t\t); sourceTree = "<group>"; }};
\t\tE10000000000000000000002 /* Products */ = {{isa = PBXGroup; children = (C10000000000000000000002 /* {app}.app */, ); name = Products; sourceTree = "<group>"; }};
/* End PBXGroup section */
/* Begin PBXNativeTarget section */
\t\tF20000000000000000000001 /* {app} */ = {{isa = PBXNativeTarget; buildConfigurationList = F20000000000000000000002; buildPhases = (
\t\t\t\tD10000000000000000000002 /* Sources */,
\t\t\t\tD10000000000000000000001 /* Frameworks */,
\t\t\t\tD10000000000000000000003 /* Resources */,
{embed_phase_id}
\t\t\t); buildRules = (); dependencies = (); name = {app}; productName = {app}; productReference = C10000000000000000000002 /* {app}.app */; productType = "com.apple.product-type.application"; }};
/* End PBXNativeTarget section */
/* Begin PBXProject section */
\t\tF30000000000000000000001 /* Project object */ = {{isa = PBXProject; attributes = {{BuildIndependentTargetsInParallel = 1; LastUpgradeCheck = 2600; TargetAttributes = {{F20000000000000000000001 = {{CreatedOnToolsVersion = 26.0; }}; }}; }}; buildConfigurationList = F30000000000000000000002; compatibilityVersion = "Xcode 14.0"; developmentRegion = en; hasScannedForEncodings = 0; knownRegions = (en, Base, ); mainGroup = E10000000000000000000001; productRefGroup = E10000000000000000000002; projectDirPath = ""; projectRoot = ""; targets = (F20000000000000000000001 /* {app} */, ); }};
/* End PBXProject section */
/* Begin PBXResourcesBuildPhase section */
\t\tD10000000000000000000003 /* Resources */ = {{isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (
{chr(10).join(resource_phase)}
\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXResourcesBuildPhase section */
/* Begin PBXSourcesBuildPhase section */
\t\tD10000000000000000000002 /* Sources */ = {{isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = (
{chr(10).join(source_phase)}
\t\t\t); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXSourcesBuildPhase section */
/* Begin XCBuildConfiguration section */
\t\tF40000000000000000000001 /* Debug */ = {{isa = XCBuildConfiguration; buildSettings = {{ALWAYS_SEARCH_USER_PATHS = NO; CLANG_ENABLE_MODULES = YES; CLANG_ENABLE_OBJC_ARC = YES; GCC_C_LANGUAGE_STANDARD = gnu17; IPHONEOS_DEPLOYMENT_TARGET = 15.0; SDKROOT = iphoneos; }}; name = Debug; }};
\t\tF40000000000000000000002 /* Release */ = {{isa = XCBuildConfiguration; buildSettings = {{ALWAYS_SEARCH_USER_PATHS = NO; CLANG_ENABLE_MODULES = YES; CLANG_ENABLE_OBJC_ARC = YES; GCC_C_LANGUAGE_STANDARD = gnu17; IPHONEOS_DEPLOYMENT_TARGET = 15.0; SDKROOT = iphoneos; }}; name = Release; }};
\t\tF40000000000000000000003 /* Debug */ = {{isa = XCBuildConfiguration; buildSettings = {{CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; GENERATE_INFOPLIST_FILE = NO; INFOPLIST_FILE = Info.plist; MARKETING_VERSION = 1.0; OTHER_CFLAGS = "{objc_prefix}"; PRODUCT_BUNDLE_IDENTIFIER = {bundle_id}; PRODUCT_NAME = "$(TARGET_NAME)"; TARGETED_DEVICE_FAMILY = "1,2";{swift_setting}{framework_settings}\n\t\t\t}}; name = Debug; }};
\t\tF40000000000000000000004 /* Release */ = {{isa = XCBuildConfiguration; buildSettings = {{CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; GENERATE_INFOPLIST_FILE = NO; INFOPLIST_FILE = Info.plist; MARKETING_VERSION = 1.0; OTHER_CFLAGS = "{objc_prefix}"; PRODUCT_BUNDLE_IDENTIFIER = {bundle_id}; PRODUCT_NAME = "$(TARGET_NAME)"; TARGETED_DEVICE_FAMILY = "1,2";{swift_setting}{framework_settings}\n\t\t\t}}; name = Release; }};
/* End XCBuildConfiguration section */
/* Begin XCConfigurationList section */
\t\tF20000000000000000000002 = {{isa = XCConfigurationList; buildConfigurations = (F40000000000000000000003 /* Debug */, F40000000000000000000004 /* Release */, ); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; }};
\t\tF30000000000000000000002 = {{isa = XCConfigurationList; buildConfigurations = (F40000000000000000000001 /* Debug */, F40000000000000000000002 /* Release */, ); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; }};
/* End XCConfigurationList section */
\t}};
\trootObject = F30000000000000000000001 /* Project object */;
}}
"""


def patch_plist(path: Path, permissions: list[str]) -> None:
    with path.open("rb") as handle:
        data = plistlib.load(handle)
    for permission in permissions:
        if permission in PRIVACY_KEYS:
            key, value = PRIVACY_KEYS[permission]
            data[key] = value
    with path.open("wb") as handle:
        plistlib.dump(data, handle, sort_keys=False)


def build_manifest(args: argparse.Namespace, plan: dict) -> dict:
    return {
        "schema_revision": 1,
        "mode": args.mode,
        "bundle_id": args.bundle_id,
        "target_name": args.target_name or safe_name(args.app_name),
        "language": args.language,
        "timeline_ownership": args.timeline_ownership,
        "plan": plan,
        "external_resources": {
            "dynamic_framework": bool(args.framework),
            "sdk_license": bool(args.license),
            "human_models": bool(args.human_models_dir),
            "resource_bundle": bool(args.resource_bundle)
        },
        "host_actions": [
            "Add generated source files to the selected target.",
            "Embed and sign the user-supplied NvStreamingSdkCore.framework.",
            "Provide an authorized SDK license before singleton initialization.",
            "Review minimal privacy usage descriptions and resource gaps."
        ]
    }


def apply_incremental(staging: Path, host: Path, force: bool) -> None:
    payload = staging / "Controllers"
    targets = [(source, host / "MeisheStreaming" / source.name) for source in payload.glob("*") if source.is_file()]
    conflicts = [str(target) for source, target in targets if target.exists() and target.read_bytes() != source.read_bytes()]
    if conflicts:
        raise FileExistsError("Host conflicts prevent transactional apply: " + ", ".join(conflicts))
    for source, target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a dependency-closed iOS project skeleton or additive integration staging area.")
    parser.add_argument("output_dir", nargs="?")
    parser.add_argument("--bundle-id", default="com.example.meishestreaming")
    parser.add_argument("--app-name", default="MeisheStreamingApp")
    parser.add_argument("--language", choices=["objc", "swift"], default="swift", help="Generated source language; new apps default to Swift.")
    parser.add_argument("--ui-language", choices=["en", "zh-CN"], default="en")
    parser.add_argument("--features", default="")
    parser.add_argument("--blueprint", default="")
    parser.add_argument("--modules", default="sdk-runtime")
    parser.add_argument("--mode", choices=["new-app", "incremental", "api-only"], default="new-app")
    parser.add_argument("--host-project")
    parser.add_argument("--target-name")
    parser.add_argument("--timeline-ownership", choices=["EDITOR_OWNED", "HOST_OWNED"], default="EDITOR_OWNED")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run-plan", action="store_true")
    parser.add_argument("--framework")
    parser.add_argument("--license")
    parser.add_argument("--human-models-dir")
    parser.add_argument("--resource-bundle")
    parser.add_argument("--list-features", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.list_features:
        features = sorted(path.parent.name for path in (ROOT / "assets" / "ios-feature-templates").glob("*/feature.json"))
        print(json.dumps(features, indent=2))
        return 0
    modules = split_ids(args.modules)
    blueprints = split_ids(args.blueprint)
    if args.mode == "incremental" and not blueprints:
        blueprints = ["incremental-integration"]
    plan = adapt_plan_for_language(compose(modules, blueprints, args.mode), args.language)
    if args.dry_run_plan:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    if not args.output_dir:
        parser.error("output_dir is required unless --dry-run-plan or --list-features is used")
    output = Path(args.output_dir).expanduser().resolve()
    if output.exists() and any(output.iterdir()) and not args.force:
        raise FileExistsError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    app = safe_name(args.target_name or args.app_name)
    manifest = build_manifest(args, plan)
    if args.mode == "new-app":
        template = ROOT / "assets" / f"ios-template-{args.language}"
        sources = copy_template(template, output, args.app_name, args.force)
        controllers = controller_source(args.language)
        for name, content in controllers.items():
            target = output / name
            write_text(target, content, args.force)
            sources.append(target)
        patch_plist(output / "Info.plist", plan["privacy_usage_descriptions"])
        has_framework = bool(args.framework)
        if args.framework:
            source_framework = Path(args.framework).expanduser().resolve()
            if not source_framework.is_dir():
                raise FileNotFoundError(f"Framework directory does not exist: {source_framework}")
            destination = output / "Frameworks" / "NvStreamingSdkCore.framework"
            if destination.exists() and args.force:
                shutil.rmtree(destination)
            if not destination.exists():
                shutil.copytree(source_framework, destination, symlinks=True)
            if args.language == "objc":
                write_text(output / "ViewController.m", objc_runtime_view_controller(args.app_name), True)
            else:
                write_text(output / "ViewController.swift", swift_runtime_view_controller(args.app_name), True)
        resource_names = []
        if args.license:
            source_license = Path(args.license).expanduser().resolve()
            if not source_license.is_file():
                raise FileNotFoundError(f"SDK license does not exist: {source_license}")
            license_destination = output / "Resources" / "meishesdk.lic"
            license_destination.parent.mkdir(parents=True, exist_ok=True)
            if license_destination.exists() and not args.force:
                raise FileExistsError(f"Refusing to overwrite existing file: {license_destination}")
            shutil.copy2(source_license, license_destination)
            resource_names.append("Resources/meishesdk.lic")
        source_names = [path.name for path in sources if path.suffix in {".h", ".m", ".swift"}]
        project_dir = output / f"{app}.xcodeproj"
        project_dir.mkdir(parents=True, exist_ok=True)
        write_text(project_dir / "project.pbxproj", pbxproj(app, args.bundle_id, args.language, source_names, has_framework, resource_names), args.force)
    else:
        controllers_dir = output / "Controllers"
        for name, content in controller_source(args.language).items():
            write_text(controllers_dir / name, content, args.force)
        sample = output / "Sample" / "IntegrationUsage.txt"
        write_text(sample, "Use the generated controllers after the host supplies license, Context flags, permissions, Timeline ownership, LiveWindow, and selected resources.\n", args.force)
    write_text(output / "patch-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", args.force)
    if args.mode == "incremental" and args.apply:
        if not args.host_project:
            parser.error("--host-project is required with incremental --apply")
        apply_incremental(output, Path(args.host_project).expanduser().resolve(), args.force)
    print(json.dumps({"output": str(output), "project": f"{app}.xcodeproj" if args.mode == "new-app" else None, "plan": plan}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
