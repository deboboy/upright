#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import math
import struct
import textwrap
import zlib

ROOT = Path(__file__).resolve().parents[1]


def write(rel, content):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def write_json(rel, data):
    write(rel, json.dumps(data, indent=2) + "\n")


def id_for(label):
    return hashlib.sha1(label.encode("utf-8")).hexdigest()[:24].upper()


def fmt_list(items, indent="    "):
    if not items:
        return "(\n        );"
    rendered = ",\n".join(f"{indent}{item}" for item in items)
    return f"(\n{rendered},\n{indent[:-4]});"


def fmt_dict(items, indent="    "):
    rendered = ";\n".join(f"{indent}{k} = {v}" for k, v in items.items())
    return f"{{\n{rendered};\n{indent[:-4]}}}"


def png_icon(path, size=1024):
    bg = (8, 103, 132)
    fg = (246, 255, 255)
    accent = (255, 198, 87)

    def px(x, y):
        cx = cy = size / 2
        r = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if r < size * 0.31:
            return fg
        if size * 0.31 <= r < size * 0.335:
            return accent
        # Simple posture spine line.
        spine_x = int(cx + math.sin((y / size) * math.pi * 2) * size * 0.08)
        if abs(x - spine_x) <= 18 and size * 0.16 < y < size * 0.84:
            return accent
        return bg

    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            raw.extend(px(x, y))

    def chunk(kind, data):
        return struct.pack("!I", len(data)) + kind + data + struct.pack("!I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack("!IIBBBBB", size, size, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def pbxproj():
    ids = {}
    def gid(label):
        return ids.setdefault(label, id_for(label))

    source_files = [
        "AppDelegate.swift",
        "SceneDelegate.swift",
        "RootViewController.swift",
        "NativeBridge.swift",
        "HeadphoneMotionAdapter.swift",
        "MotionSample.swift",
        "BridgeMessage.swift",
        "BridgeError.swift",
    ]
    web_files = ["index.html", "app.js", "bridge-sdk.js", "posture-core.js", "mock-bridge.js", "mock-traces.json", "styles.css"]
    frameworks = ["WebKit.framework", "CoreMotion.framework", "AVFAudio.framework"]

    main_group = gid("Project")
    app_group = gid("Upright group")
    web_group = gid("Web group")
    products_group = gid("Products")
    product_ref = gid("Upright.app ref")
    target = gid("Upright target")
    project = gid("PBXProject")
    sources_phase = gid("Sources phase")
    frameworks_phase = gid("Frameworks phase")
    resources_phase = gid("Resources phase")
    shell_phase = gid("Copy Web phase")
    target_debug = gid("Target Debug")
    target_release = gid("Target Release")
    project_debug = gid("Project Debug")
    project_release = gid("Project Release")
    target_configs = gid("Target Configs")
    project_configs = gid("Project Configs")

    source_ref = {f: gid(f"{f} ref") for f in source_files}
    source_build = {f: gid(f"{f} in Sources") for f in source_files}
    web_ref = {f: gid(f"web/{f} ref") for f in web_files}
    framework_ref = {f: gid(f"{f} ref") for f in frameworks}
    framework_build = {f: gid(f"{f} in Frameworks") for f in frameworks}
    resource_refs = {
        "Info.plist": gid("Info.plist ref"),
        "LaunchScreen.storyboard": gid("LaunchScreen.storyboard ref"),
        "Assets.xcassets": gid("Assets.xcassets ref"),
    }
    resource_build = {
        "LaunchScreen.storyboard": gid("LaunchScreen.storyboard in Resources"),
        "Assets.xcassets": gid("Assets.xcassets in Resources"),
    }

    def file_ref(label, path, filetype, tree="<group>", name=None):
        name_part = f"; name = {name};" if name else ""
        return f"{label} /* {path} */ = {{isa = PBXFileReference; lastKnownFileType = {filetype}; path = {path}; sourceTree = {tree};{name_part} }};"

    lines = []
    add = lines.append
    add("// !$*UTF8*$!")
    add("{")
    add("\tarchiveVersion = 1;")
    add("\tclasses = {")
    add("\t};")
    add("\tobjectVersion = 56;")
    add("\tobjects = {")

    add("\t\t/* Begin PBXBuildFile section */")
    for f in source_files:
        add(f"\t\t{source_build[f]} /* {f} in Sources */ = {{isa = PBXBuildFile; fileRef = {source_ref[f]} /* {f} */; }};")
    for f in frameworks:
        add(f"\t\t{framework_build[f]} /* {f} in Frameworks */ = {{isa = PBXBuildFile; fileRef = {framework_ref[f]} /* {f} */; }};")
    add(f"\t\t{resource_build['LaunchScreen.storyboard']} /* LaunchScreen.storyboard in Resources */ = {{isa = PBXBuildFile; fileRef = {resource_refs['LaunchScreen.storyboard']} /* LaunchScreen.storyboard */; }};")
    add(f"\t\t{resource_build['Assets.xcassets']} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {resource_refs['Assets.xcassets']} /* Assets.xcassets */; }};")
    add("\t\t/* End PBXBuildFile section */")

    add("\t\t/* Begin PBXFileReference section */")
    for f in source_files:
        add(file_ref(f"{source_ref[f]} /* {f} */", f, "sourcecode.swift"))
    for f in web_files:
        add(file_ref(f"{web_ref[f]} /* {f} */", f, "text" if f.endswith((".html", ".js", ".json", ".css")) else "unknown", name=f))
    for f in frameworks:
        add(file_ref(f"{framework_ref[f]} /* {f} */", f"System/Library/Frameworks/{f}", "wrapper.framework", tree="SDKROOT", name=f))
    add(file_ref(f"{product_ref} /* Upright.app */", "Upright.app", "wrapper.application", tree="BUILT_PRODUCTS_DIR"))
    add(file_ref(f"{resource_refs['Info.plist']} /* Info.plist */", "Info.plist", "text.plist.xml"))
    add(file_ref(f"{resource_refs['LaunchScreen.storyboard']} /* LaunchScreen.storyboard */", "LaunchScreen.storyboard", "file.storyboard"))
    add(file_ref(f"{resource_refs['Assets.xcassets']} /* Assets.xcassets */", "Assets.xcassets", "folder.assetcatalog"))
    add("\t\t/* End PBXFileReference section */")

    add("\t\t/* Begin PBXFrameworksBuildPhase section */")
    add(f"\t\t{frameworks_phase} /* Frameworks */ = {{")
    add("\t\t\tisa = PBXFrameworksBuildPhase;")
    add("\t\t\tbuildActionMask = 2147483647;")
    add("\t\t\tfiles = " + fmt_list([f"{framework_build[f]} /* {f} in Frameworks */" for f in frameworks]))
    add("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    add("\t\t};")
    add("\t\t/* End PBXFrameworksBuildPhase section */")

    add("\t\t/* Begin PBXGroup section */")
    add(f"\t\t{main_group} /* Project */ = {{")
    add("\t\t\tisa = PBXGroup;")
    add("\t\t\tchildren = " + fmt_list([f"{app_group} /* Upright */", f"{products_group} /* Products */"]))
    add("\t\t\tsourceTree = \"<group>\";")
    add("\t\t};")
    add(f"\t\t{app_group} /* Upright */ = {{")
    add("\t\t\tisa = PBXGroup;")
    add("\t\t\tchildren = " + fmt_list([f"{source_ref[f]} /* {f} */" for f in source_files] + [f"{resource_refs['Info.plist']} /* Info.plist */", f"{resource_refs['LaunchScreen.storyboard']} /* LaunchScreen.storyboard */", f"{resource_refs['Assets.xcassets']} /* Assets.xcassets */", f"{web_group} /* Web */"]))
    add("\t\t\tpath = Upright;")
    add("\t\t\tsourceTree = \"<group>\";")
    add("\t\t};")
    add(f"\t\t{web_group} /* Web */ = {{")
    add("\t\t\tisa = PBXGroup;")
    add("\t\t\tchildren = " + fmt_list([f"{web_ref[f]} /* {f} */" for f in web_files]))
    add("\t\t\tpath = web;")
    add("\t\t\tsourceTree = \"<group>\";")
    add("\t\t};")
    add(f"\t\t{products_group} /* Products */ = {{")
    add("\t\t\tisa = PBXGroup;")
    add("\t\t\tchildren = " + fmt_list([f"{product_ref} /* Upright.app */"]))
    add("\t\t\tname = Products;")
    add("\t\t\tsourceTree = \"<group>\";")
    add("\t\t};")
    add("\t\t/* End PBXGroup section */")

    add("\t\t/* Begin PBXNativeTarget section */")
    add(f"\t\t{target} /* Upright */ = {{")
    add("\t\t\tisa = PBXNativeTarget;")
    add(f"\t\t\tbuildConfigurationList = {target_configs} /* Build configuration list for PBXNativeTarget \"Upright\" */;")
    add("\t\t\tbuildPhases = " + fmt_list([f"{sources_phase} /* Sources */", f"{frameworks_phase} /* Frameworks */", f"{resources_phase} /* Resources */", f"{shell_phase} /* Copy Web */"]))
    add("\t\t\tbuildRules = " + fmt_list([]))
    add("\t\t\tdependencies = " + fmt_list([]))
    add("\t\t\tname = Upright;")
    add("\t\t\tproductName = Upright;")
    add(f"\t\t\tproductReference = {product_ref} /* Upright.app */;")
    add("\t\t\tproductType = \"com.apple.product-type.application\";")
    add("\t\t};")
    add("\t\t/* End PBXNativeTarget section */")

    add("\t\t/* Begin PBXProject section */")
    add(f"\t\t{project} /* Project object */ = {{")
    add("\t\t\tisa = PBXProject;")
    add("\t\t\tattributes = {")
    add("\t\t\t\tBuildIndependentTargetsInParallel = 1;")
    add("\t\t\t\tLastSwiftUpdateCheck = 1500;")
    add("\t\t\t\tLastUpgradeCheck = 1500;")
    add("\t\t\t\tTargetAttributes = {")
    add(f"\t\t\t\t\t{target} /* Upright */ = {{")
    add("\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;")
    add("\t\t\t\t\t};")
    add("\t\t\t\t};")
    add("\t\t\t};")
    add(f"\t\t\tbuildConfigurationList = {project_configs} /* Build configuration list for PBXProject \"Project\" */;")
    add("\t\t\tcompatibilityVersion = \"Xcode 14.0\";")
    add("\t\t\tdevelopmentRegion = en;")
    add("\t\t\thasScannedForEncodings = 0;")
    add("\t\t\tknownRegions = " + fmt_list(["en", "Base"]))
    add(f"\t\t\tmainGroup = {main_group} /* Project */;")
    add(f"\t\t\tproductRefGroup = {products_group} /* Products */;")
    add("\t\t\tprojectDirPath = \"\";")
    add("\t\t\tprojectRoot = \"\";")
    add("\t\t\ttargets = " + fmt_list([f"{target} /* Upright */"]))
    add("\t\t};")
    add("\t\t/* End PBXProject section */")

    add("\t\t/* Begin PBXResourcesBuildPhase section */")
    add(f"\t\t{resources_phase} /* Resources */ = {{")
    add("\t\t\tisa = PBXResourcesBuildPhase;")
    add("\t\t\tbuildActionMask = 2147483647;")
    add("\t\t\tfiles = " + fmt_list([f"{resource_build['LaunchScreen.storyboard']} /* LaunchScreen.storyboard in Resources */", f"{resource_build['Assets.xcassets']} /* Assets.xcassets in Resources */"]))
    add("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    add("\t\t};")
    add("\t\t/* End PBXResourcesBuildPhase section */")

    add("\t\t/* Begin PBXShellScriptBuildPhase section */")
    add(f"\t\t{shell_phase} /* Copy Web */ = {{")
    add("\t\t\tisa = PBXShellScriptBuildPhase;")
    add("\t\t\tbuildActionMask = 2147483647;")
    add("\t\t\tfiles = " + fmt_list([]))
    add("\t\t\tinputPaths = " + fmt_list(["${SRCROOT}/web/"]))
    add("\t\t\toutputPaths = " + fmt_list(["${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/web/"]))
    add("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    add("\t\t\tshellPath = /bin/sh;")
    add('\t\t\tshellScript = "set -e\\nmkdir -p \\"${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/web\\"\\nrsync -a --delete \\"${SRCROOT}/web/\\" \\"${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/web/\\"\\n";')
    add("\t\t\tshowEnvVarsInLog = 0;")
    add("\t\t};")
    add("\t\t/* End PBXShellScriptBuildPhase section */")

    add("\t\t/* Begin PBXSourcesBuildPhase section */")
    add(f"\t\t{sources_phase} /* Sources */ = {{")
    add("\t\t\tisa = PBXSourcesBuildPhase;")
    add("\t\t\tbuildActionMask = 2147483647;")
    add("\t\t\tfiles = " + fmt_list([f"{source_build[f]} /* {f} in Sources */" for f in source_files]))
    add("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    add("\t\t};")
    add("\t\t/* End PBXSourcesBuildPhase section */")

    def xc_build(label, name, debug):
        common = {
            "ALWAYS_SEARCH_USER_PATHS": "NO",
            "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
            "CLANG_ENABLE_MODULES": "YES",
            "CLANG_ENABLE_OBJC_ARC": "YES",
            "CODE_SIGN_STYLE": "Automatic",
            "CURRENT_PROJECT_VERSION": "1",
            "DEVELOPMENT_TEAM": '""',
            "ENABLE_PREVIEWS": "YES",
            "INFOPLIST_FILE": "Upright/Info.plist",
            "IPHONEOS_DEPLOYMENT_TARGET": "14.0",
            "LD_RUNPATH_SEARCH_PATHS": fmt_list(['"$(inherited)"', '"@executable_path/Frameworks"'], indent="\t\t\t\t"),
            "MARKETING_VERSION": "1.0",
            "PRODUCT_BUNDLE_IDENTIFIER": "com.lastmyle.upright",
            "PRODUCT_NAME": '"$(TARGET_NAME)"',
            "SDKROOT": "iphoneos",
            "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator",
            "SWIFT_VERSION": "5.0",
            "TARGETED_DEVICE_FAMILY": '"1,2"',
            "ALWAYS_EMBED_SWIFT_STANDARD_LIBRARIES": "YES",
        }
        if debug:
            common.update({
                "COPY_PHASE_STRIP": "NO",
                "DEBUG_INFORMATION_FORMAT": "dwarf",
                "ENABLE_TESTABILITY": "YES",
                "GCC_OPTIMIZATION_LEVEL": "0",
                "GCC_PREPROCESSOR_DEFINITIONS": fmt_list(['"DEBUG=1"', '"$(inherited)"'], indent="\t\t\t\t"),
                "MTL_ENABLE_DEBUG_INFO": "INCLUDE_SOURCE",
                "ONLY_ACTIVE_ARCH": "YES",
                "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG",
                "SWIFT_OPTIMIZATION_LEVEL": '"-Onone"',
            })
        else:
            common.update({
                "COPY_PHASE_STRIP": "YES",
                "DEBUG_INFORMATION_FORMAT": '"dwarf-with-dsym"',
                "ENABLE_TESTABILITY": "NO",
                "GCC_OPTIMIZATION_LEVEL": "s",
                "GCC_PREPROCESSOR_DEFINITIONS": fmt_list(['"$(inherited)"'], indent="\t\t\t\t"),
                "MTL_ENABLE_DEBUG_INFO": "NO",
                "ONLY_ACTIVE_ARCH": "NO",
                "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "",
                "SWIFT_OPTIMIZATION_LEVEL": '"-O"',
            })
        add(f"\t\t{label} /* {name} */ = {{")
        add("\t\t\tisa = XCBuildConfiguration;")
        add("\t\t\tbuildSettings = " + fmt_dict(common, indent="\t\t\t\t"))
        add(f"\t\t\tname = {name};")
        add("\t\t};")

    add("\t\t/* Begin XCBuildConfiguration section */")
    xc_build(target_debug, "Debug", True)
    xc_build(target_release, "Release", False)
    xc_build(project_debug, "Debug", True)
    xc_build(project_release, "Release", False)
    add("\t\t/* End XCBuildConfiguration section */")

    add("\t\t/* Begin XCConfigurationList section */")
    add(f"\t\t{target_configs} /* Build configuration list for PBXNativeTarget \"Upright\" */ = {{")
    add("\t\t\tisa = XCConfigurationList;")
    add("\t\t\tbuildConfigurations = " + fmt_list([f"{target_debug} /* Debug */", f"{target_release} /* Release */"]))
    add("\t\t\tdefaultConfigurationIsVisible = 0;")
    add("\t\t\tdefaultConfigurationName = Release;")
    add("\t\t};")
    add(f"\t\t{project_configs} /* Build configuration list for PBXProject \"Project\" */ = {{")
    add("\t\t\tisa = XCConfigurationList;")
    add("\t\t\tbuildConfigurations = " + fmt_list([f"{project_debug} /* Debug */", f"{project_release} /* Release */"]))
    add("\t\t\tdefaultConfigurationIsVisible = 0;")
    add("\t\t\tdefaultConfigurationName = Release;")
    add("\t\t};")
    add("\t\t/* End XCConfigurationList section */")

    add("\t};")
    add(f"\trootObject = {project} /* Project object */;")
    add("}")
    return "\n".join(lines) + "\n"


def scheme(target_id):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1500" version="1.7">
   <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES">
      <BuildActionEntries>
         <BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">
            <BuildableReference
               BuildableIdentifier="primary"
               BlueprintIdentifier="{target_id}"
               BuildableName="Upright.app"
               BlueprintName="Upright"
               ReferencedContainer="container:Upright.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" language="" systemLanguage="" shouldUseLaunchSchemeArgsEnv="YES">
   </TestAction>
   <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES">
      <BuildableProductRunnable runnableDebuggingMode="0">
         <BuildableReference
            BuildableIdentifier="primary"
            BlueprintIdentifier="{target_id}"
            BuildableName="Upright.app"
            BlueprintName="Upright"
            ReferencedContainer="container:Upright.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES">
      <BuildableProductRunnable runnableDebuggingMode="0">
         <BuildableReference
            BuildableIdentifier="primary"
            BlueprintIdentifier="{target_id}"
            BuildableName="Upright.app"
            BlueprintName="Upright"
            ReferencedContainer="container:Upright.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction buildConfiguration="Debug"></AnalyzeAction>
   <ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"></ArchiveAction>
</Scheme>
'''


write("README.md", r'''
# Upright

Upright is a hybrid iOS posture-tracking app: a thin Swift/WKWebView shell owns AirPods motion access, while the product experience lives in a portable web codebase.

## What is included

- **iOS shell**: Swift app with `WKWebView`, Core Motion headphone-motion adapter, native bridge, haptics, speech, and settings actions.
- **Web app**: no-build static SPA for onboarding, session state, posture scoring, timer, charts, and history.
- **Bridge SDK**: versioned JS interface matching the Swift bridge contract.
- **Browser dev shim**: replays recorded AirPods motion traces so the web app can be tested without an iPhone.
- **Docs**: architecture, bridge contract, and iPhone/AirPods test plan.

## Repo layout

```text
ios/Upright/                         Swift iOS shell
ios/Upright.xcodeproj/               Xcode project
web/                                 Static web app + bridge SDK + mock traces
docs/                                Architecture and test docs
scripts/create_repo_files.py         Regenerates this repo layout
```

## Local web dev

```bash
npm run serve
```

Open `http://localhost:5173`. The app uses the mock AirPods trace by default in a normal browser.

## iPhone test

1. Open `ios/Upright.xcodeproj` in Xcode on a Mac.
2. Select your iPhone as the run destination.
3. Sign with your Apple ID / development team.
4. Run the `Upright` scheme.
5. Connect compatible AirPods and grant motion permission when prompted.
6. In the app, tap **Start Session**. Motion samples stream from AirPods into the web UI.

## Native bridge v1

Calls:

- `ready()`
- `headphones.getStatus()`
- `headphones.requestPermission()`
- `headphones.startUpdates({ sampleRateHz })`
- `headphones.stopUpdates()`
- `headphones.calibrateNeutral()`

Events:

- `motion`
- `status`
- `interruption`
- `error`

See `docs/bridge-contract.md` for schemas.
''')

write("package.json", r'''
{
  "name": "upright",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "serve": "python3 -m http.server 5173 --directory web",
    "check": "node --check web/app.js && node --check web/bridge-sdk.js && node --check web/posture-core.js && node --check web/mock-bridge.js"
  }
}
''')

write(".gitignore", r'''
.DS_Store
DerivedData/
*.xcuserstate
*.xccheckout
node_modules/
dist/
.env
''')

write("LICENSE", r'''
MIT License

Copyright (c) 2026 Last Myle Engineering

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')

write("docs/architecture.md", r'''
# Architecture

Upright uses a three-layer design:

1. **Native iOS shell**: Swift, `WKWebView`, `CMHeadphoneMotionManager`, permission handling, lifecycle hooks, haptics, speech, and settings actions.
2. **Bridge layer**: `web/bridge-sdk.js` plus `ios/Upright/NativeBridge.swift` define a narrow, versioned RPC/event contract.
3. **Web app layer**: static SPA owns onboarding, session state, posture scoring, timer logic, charts, history, and exports.

## Data flow

- JS calls native through `window.webkit.messageHandlers.nativeBridgeWithReply.postMessage(...)`.
- Native replies with promise results through `WKScriptMessageHandlerWithReply`.
- Native pushes streams back to JS with `window.__dispatchNativeEvent(type, payload)`.
- Motion samples use radians for raw values; the web app converts to degrees for display.

## Responsibility split

Native owns:

- AirPods/headphone motion permission and availability.
- Motion update start/stop.
- Sanitized motion samples and connection/interruption events.
- Haptics, speech, and app-settings actions.

Web owns:

- Neutral calibration UX and posture math.
- Slouch detection thresholds and hysteresis.
- Focus timer, alerts, charts, session summaries, and history.
- Mock/browser development mode.
''')

write("docs/bridge-contract.md", r'''
# Bridge Contract

API version: `1`

## Request schema

```json
{ "id": "req_123", "module": "headphones", "method": "startUpdates", "params": { "sampleRateHz": 25 } }
```

## Response shape

Promise resolves to the method result, or rejects/returns an error string from native.

## Status

```ts
type PermissionState = 'unknown' | 'granted' | 'denied' | 'restricted';
type ConnectionState = 'unavailable' | 'disconnected' | 'connected' | 'active';

type HeadphoneStatus = {
  platform: 'ios-native-shell';
  apiVersion: '1';
  supported: boolean;
  permission: PermissionState;
  connection: ConnectionState;
  deviceMotionAvailable: boolean;
  deviceName?: string;
  sampleRateHz?: number;
};
```

## Motion sample

```ts
type MotionSample = {
  ts: number;
  source: 'airpods';
  attitude: { pitch: number; roll: number; yaw: number };
  quaternion?: { x: number; y: number; z: number; w: number };
  rotationRate?: { x: number; y: number; z: number };
  gravity?: { x: number; y: number; z: number };
  userAcceleration?: { x: number; y: number; z: number };
};
```

## Events

```json
{ "type": "status", "payload": { "connection": "connected", "permission": "granted" } }
{ "type": "motion", "payload": { "ts": 1718910000000, "source": "airpods", "attitude": { "pitch": 0.08, "roll": -0.03, "yaw": 0.11 } } }
{ "type": "interruption", "payload": { "reason": "airpods_disconnected" } }
{ "type": "error", "payload": { "code": "permission_denied", "message": "Headphone motion permission denied" } }
```
''')

write("docs/iphone-test-plan.md", r'''
# iPhone / AirPods Test Plan

## Prerequisites

- Mac with current Xcode.
- iPhone paired with the Mac.
- AirPods model supported by `CMHeadphoneMotionManager`.
- Apple ID / development team for signing.

## Build and run

1. Open `ios/Upright.xcodeproj`.
2. Select the `Upright` scheme.
3. Select your physical iPhone as the destination.
4. Choose a signing team in the target settings if Xcode prompts.
5. Run.

## Permission flow

1. Put on supported AirPods.
2. Launch Upright.
3. Tap **Request Permission**.
4. Grant the iOS motion prompt.
5. Tap **Start Session**.

Expected: `connection` becomes `connected` or `active`, `permission` becomes `granted`, and motion samples begin streaming.

## Failure states to verify

- Permission denied.
- Unsupported or missing AirPods.
- AirPods disconnected mid-session.
- Motion temporarily unavailable.
- App backgrounded while a session is active.
- Web app opened in Safari instead of native shell.

The web app should still boot and fall back to mock mode when native support is unavailable.
''')

write("web/index.html", r'''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#08111f" />
  <title>Upright</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <main class="app-shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Hybrid posture coach</p>
        <h1>Upright</h1>
      </div>
      <span id="modeBadge" class="badge">Detecting…</span>
    </header>

    <section class="grid">
      <article class="card status-card">
        <div class="section-title">
          <h2>Sensor</h2>
          <button id="settingsBtn" class="ghost" type="button">Settings</button>
        </div>
        <dl class="status-list">
          <div><dt>Mode</dt><dd id="modeValue">—</dd></div>
          <div><dt>Permission</dt><dd id="permissionValue">—</dd></div>
          <div><dt>Connection</dt><dd id="connectionValue">—</dd></div>
          <div><dt>Device</dt><dd id="deviceValue">—</dd></div>
          <div><dt>Rate</dt><dd id="rateValue">—</dd></div>
        </dl>
        <div class="button-row">
          <button id="permissionBtn" class="primary" type="button">Request Permission</button>
          <button id="calibrateBtn" class="secondary" type="button">Calibrate Neutral</button>
        </div>
      </article>

      <article class="card posture-card">
        <div class="section-title">
          <h2>Posture</h2>
          <span id="posturePill" class="pill unknown">Unknown</span>
        </div>
        <div class="gauge">
          <div id="gaugeFill" class="gauge-fill"></div>
          <strong id="scoreValue">0</strong>
          <span>slouch score</span>
        </div>
        <p id="postureCopy" class="muted">Start a session to begin tracking.</p>
      </article>

      <article class="card timer-card">
        <div class="section-title">
          <h2>Focus Timer</h2>
          <span id="timerLabel" class="timer-label">25:00</span>
        </div>
        <div class="button-row">
          <button id="startBtn" class="primary wide" type="button">Start Session</button>
          <button id="stopBtn" class="danger wide" type="button" disabled>Stop</button>
        </div>
        <div class="mini-actions">
          <button id="hapticBtn" class="ghost small" type="button">Haptic</button>
          <button id="speakBtn" class="ghost small" type="button">Speak</button>
          <button id="resetBtn" class="ghost small" type="button">Reset</button>
        </div>
      </article>

      <article class="card chart-card">
        <div class="section-title">
          <h2>Motion</h2>
          <span id="sampleCount" class="muted">0 samples</span>
        </div>
        <canvas id="motionChart" width="900" height="260" aria-label="Pitch and roll chart"></canvas>
      </article>

      <article class="card log-card">
        <div class="section-title">
          <h2>Events</h2>
          <button id="clearLogBtn" class="ghost small" type="button">Clear</button>
        </div>
        <ul id="eventLog" class="event-log"></ul>
      </article>
    </section>
  </main>

  <script type="module" src="./bridge-sdk.js"></script>
  <script type="module" src="./posture-core.js"></script>
  <script type="module" src="./mock-bridge.js"></script>
  <script type="module" src="./app.js"></script>
</body>
</html>
''')

write("web/styles.css", r'''
:root {
  color-scheme: dark;
  --bg: #08111f;
  --panel: rgba(255, 255, 255, 0.075);
  --panel-strong: rgba(255, 255, 255, 0.12);
  --text: #f3fbff;
  --muted: #9fb4c6;
  --line: rgba(255, 255, 255, 0.14);
  --good: #3ee5a4;
  --warn: #ffd166;
  --bad: #ff6b6b;
  --blue: #2dd4bf;
  --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
}

* { box-sizing: border-box; }
html, body { margin: 0; min-height: 100%; }
body {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at 20% 10%, rgba(45, 212, 191, 0.22), transparent 32rem),
    radial-gradient(circle at 90% 0%, rgba(124, 58, 237, 0.18), transparent 28rem),
    var(--bg);
  color: var(--text);
}

button {
  border: 0;
  border-radius: 999px;
  padding: 0.85rem 1.1rem;
  color: #06101d;
  font-weight: 800;
  cursor: pointer;
  transition: transform 160ms ease, opacity 160ms ease;
}
button:active { transform: scale(0.98); }
button:disabled { opacity: 0.45; cursor: not-allowed; }
.primary { background: linear-gradient(135deg, var(--good), var(--blue)); }
.secondary { background: rgba(255,255,255,0.88); }
.danger { background: var(--bad); color: white; }
.ghost { background: rgba(255,255,255,0.1); color: var(--text); border: 1px solid var(--line); }
.small { padding: 0.55rem 0.75rem; font-size: 0.85rem; }
.wide { width: 100%; }

.app-shell { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.hero { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 22px; }
.eyebrow { margin: 0 0 0.35rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.16em; font-size: 0.75rem; font-weight: 800; }
h1 { margin: 0; font-size: clamp(2.4rem, 8vw, 5.2rem); line-height: 0.9; letter-spacing: -0.08em; }
h2 { margin: 0; font-size: 1.05rem; }
.grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
.card {
  grid-column: span 6;
  background: linear-gradient(180deg, var(--panel-strong), var(--panel));
  border: 1px solid var(--line);
  border-radius: 28px;
  padding: 20px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(18px);
}
.status-card, .timer-card { grid-column: span 4; }
.posture-card { grid-column: span 4; }
.chart-card { grid-column: span 8; }
.log-card { grid-column: span 4; }
.section-title { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 16px; }
.status-list { display: grid; gap: 10px; margin: 0; }
.status-list div { display: flex; justify-content: space-between; gap: 16px; padding: 10px 0; border-bottom: 1px solid var(--line); }
dt { color: var(--muted); }
dd { margin: 0; font-weight: 800; text-align: right; }
.button-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.mini-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.badge, .pill, .timer-label {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.45rem 0.7rem;
  background: rgba(255,255,255,0.12);
  color: var(--text);
  font-weight: 900;
  font-size: 0.8rem;
}
.pill.good { background: rgba(62, 229, 164, 0.18); color: var(--good); }
.pill.warning { background: rgba(255, 209, 102, 0.18); color: var(--warn); }
.pill.slouch { background: rgba(255, 107, 107, 0.18); color: var(--bad); }
.pill.unknown { color: var(--muted); }
.muted { color: var(--muted); }
.gauge {
  position: relative;
  display: grid;
  place-items: center;
  height: 210px;
  border-radius: 28px;
  background:
    radial-gradient(circle, rgba(255,255,255,0.08) 0 58%, transparent 59%),
    conic-gradient(from 180deg, var(--good), var(--warn), var(--bad), var(--good));
  overflow: hidden;
}
.gauge::after {
  content: "";
  position: absolute;
  inset: 18px;
  border-radius: 22px;
  background: rgba(8, 17, 31, 0.9);
}
.gauge-fill {
  position: absolute;
  inset: 0;
  background: rgba(8, 17, 31, 0.72);
  clip-path: polygon(0 0, 100% 0, 100% var(--score, 0%), 0 var(--score, 0%));
  transition: clip-path 180ms ease;
}
.gauge strong { position: relative; z-index: 1; font-size: 4rem; letter-spacing: -0.08em; }
.gauge span { position: relative; z-index: 1; color: var(--muted); font-weight: 800; }
#motionChart { width: 100%; height: 260px; border-radius: 20px; background: rgba(0,0,0,0.18); }
.event-log { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; max-height: 270px; overflow: auto; }
.event-log li { padding: 8px 10px; border-radius: 14px; background: rgba(255,255,255,0.08); color: var(--muted); font-size: 0.86rem; }

@media (max-width: 820px) {
  .grid { grid-template-columns: 1fr; }
  .card, .status-card, .timer-card, .posture-card, .chart-card, .log-card { grid-column: 1; }
  .hero { align-items: flex-start; }
}
''')

write("web/bridge-sdk.js", r'''
const handlers = window.webkit?.messageHandlers;
const nativeHandler = handlers?.nativeBridgeWithReply || handlers?.nativeBridge;

class UprightNativeBridge {
  constructor() {
    this.listeners = new Map();
    this.nativeHandler = nativeHandler || null;
  }

  get isNative() {
    return Boolean(this.nativeHandler);
  }

  async call(module, method, params = {}) {
    if (!this.nativeHandler) {
      throw new Error('Native bridge unavailable; running in browser mock mode.');
    }
    return this.nativeHandler.postMessage({ module, method, params });
  }

  async ready() {
    return this.call('app', 'ready');
  }

  get headphones() {
    return {
      getStatus: () => this.call('headphones', 'getStatus'),
      requestPermission: () => this.call('headphones', 'requestPermission'),
      startUpdates: (opts = {}) => this.call('headphones', 'startUpdates', opts),
      stopUpdates: () => this.call('headphones', 'stopUpdates'),
      calibrateNeutral: () => this.call('headphones', 'calibrateNeutral'),
    };
  }

  get app() {
    return {
      haptic: (kind = 'subtle') => this.call('app', 'haptic', { kind }),
      speak: (text) => this.call('app', 'speak', { text }),
      openSettings: () => this.call('app', 'openSettings'),
      log: (event, payload = {}) => this.call('app', 'log', { event, payload }),
    };
  }

  on(event, callback) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(callback);
    return () => this.listeners.get(event)?.delete(callback);
  }

  _emit(event, payload) {
    this.listeners.get(event)?.forEach((callback) => callback(payload));
    window.dispatchEvent(new CustomEvent(`upright:${event}`, { detail: payload }));
  }
}

const bridge = new UprightNativeBridge();
window.UprightBridge = bridge;
window.__nativeBridge = bridge;
window.__dispatchNativeEvent = (event, payload) => bridge._emit(event, payload);
''')

write("web/posture-core.js", r'''
export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function radiansToDegrees(value) {
  return value * 180 / Math.PI;
}

export class PostureEngine {
  constructor() {
    this.neutral = { pitch: 0, roll: 0, yaw: 0 };
    this.samples = [];
    this.state = 'unknown';
    this.score = 0;
    this.warningHigh = 55;
    this.slouchHigh = 72;
    this.warningLow = 35;
  }

  calibrate(samples = this.samples) {
    const usable = samples.slice(-40);
    if (!usable.length) return this.neutral;
    const avg = usable.reduce((acc, sample) => {
      acc.pitch += sample.attitude.pitch;
      acc.roll += sample.attitude.roll;
      acc.yaw += sample.attitude.yaw;
      return acc;
    }, { pitch: 0, roll: 0, yaw: 0 });
    const count = usable.length;
    this.neutral = {
      pitch: avg.pitch / count,
      roll: avg.roll / count,
      yaw: avg.yaw / count,
    };
    return this.neutral;
  }

  update(sample) {
    this.samples.push(sample);
    if (this.samples.length > 180) this.samples.shift();

    const pitchDelta = sample.attitude.pitch - this.neutral.pitch;
    const rollDelta = sample.attitude.roll - this.neutral.roll;
    const pitchPenalty = Math.abs(pitchDelta) * 160;
    const rollPenalty = Math.abs(rollDelta) * 80;
    const nextScore = clamp(pitchPenalty + rollPenalty, 0, 100);
    this.score = Math.round(nextScore);

    if (this.state === 'unknown') {
      this.state = nextScore >= this.slouchHigh ? 'slouch' : nextScore >= this.warningHigh ? 'warning' : 'good';
    } else if (this.state === 'good' && nextScore >= this.warningHigh) {
      this.state = 'warning';
    } else if (this.state === 'warning' && nextScore >= this.slouchHigh) {
      this.state = 'slouch';
    } else if (this.state === 'slouch' && nextScore < this.warningLow) {
      this.state = 'warning';
    } else if (this.state === 'warning' && nextScore < this.warningLow) {
      this.state = 'good';
    }

    return {
      state: this.state,
      score: this.score,
      neutral: this.neutral,
      pitchDegrees: radiansToDegrees(sample.attitude.pitch),
      rollDegrees: radiansToDegrees(sample.attitude.roll),
      yawDegrees: radiansToDegrees(sample.attitude.yaw),
    };
  }

  recent(count = 80) {
    return this.samples.slice(-count);
  }
}
''')

write("web/mock-bridge.js", r'''
import { radiansToDegrees } from './posture-core.js';

const fallbackSamples = Array.from({ length: 40 }, (_, index) => {
  const t = index / 39;
  return {
    ts: Date.now() + index * 250,
    source: 'airpods-mock',
    attitude: {
      pitch: 0.02 + Math.sin(t * Math.PI * 2) * 0.025 + t * 0.16,
      roll: -0.01 + Math.cos(t * Math.PI * 2) * 0.018,
      yaw: 0.03 + Math.sin(t * Math.PI) * 0.02,
    },
    gravity: { x: 0, y: Math.sin(t), z: -1 },
  };
});

export class UprightMockBridge {
  constructor(traces = fallbackSamples) {
    this.listeners = new Map();
    this.traces = Array.isArray(traces) ? traces : fallbackSamples;
    this.index = 0;
    this.timer = null;
    this.active = false;
    this.status = {
      platform: 'browser-mock',
      apiVersion: '1',
      supported: true,
      permission: 'granted',
      connection: 'connected',
      deviceMotionAvailable: true,
      deviceName: 'Mock AirPods Trace',
      sampleRateHz: 25,
    };
  }

  get isNative() { return false; }

  async ready() { return { platform: 'browser-mock', apiVersion: '1' }; }

  async call(module, method, params = {}) {
    if (module === 'headphones' && method === 'getStatus') return this.status;
    if (module === 'headphones' && method === 'requestPermission') return this.status.permission;
    if (module === 'headphones' && method === 'startUpdates') return this.startUpdates(params);
    if (module === 'headphones' && method === 'stopUpdates') return this.stopUpdates();
    if (module === 'headphones' && method === 'calibrateNeutral') return { ok: true, neutral: { pitch: 0.02, roll: -0.01, yaw: 0.03 } };
    if (module === 'app' && method === 'ready') return this.ready();
    if (module === 'app' && method === 'haptic') return navigator.vibrate?.(18);
    if (module === 'app' && method === 'speak') return undefined;
    if (module === 'app' && method === 'openSettings') return undefined;
    if (module === 'app' && method === 'log') return undefined;
    throw new Error(`Mock bridge does not implement ${module}.${method}`);
  }

  get headphones() {
    return {
      getStatus: () => this.call('headphones', 'getStatus'),
      requestPermission: () => this.call('headphones', 'requestPermission'),
      startUpdates: (opts = {}) => this.call('headphones', 'startUpdates', opts),
      stopUpdates: () => this.call('headphones', 'stopUpdates'),
      calibrateNeutral: () => this.call('headphones', 'calibrateNeutral'),
    };
  }

  get app() {
    return {
      haptic: (kind = 'subtle') => this.call('app', 'haptic', { kind }),
      speak: (text) => this.call('app', 'speak', { text }),
      openSettings: () => this.call('app', 'openSettings'),
      log: (event, payload = {}) => this.call('app', 'log', { event, payload }),
    };
  }

  on(event, callback) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(callback);
    return () => this.listeners.get(event)?.delete(callback);
  }

  _emit(event, payload) {
    this.listeners.get(event)?.forEach((callback) => callback(payload));
    window.dispatchEvent(new CustomEvent(`upright:${event}`, { detail: payload }));
  }

  async startUpdates(opts = {}) {
    if (this.active) return;
    this.active = true;
    this.status.connection = 'active';
    this.status.sampleRateHz = opts.sampleRateHz || 25;
    this._emit('status', this.status);
    const interval = Math.max(40, Math.round(1000 / this.status.sampleRateHz));
    this.timer = setInterval(() => this.tick(), interval);
    this.tick();
  }

  stopUpdates() {
    this.active = false;
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
    this.status.connection = 'connected';
    this._emit('status', this.status);
  }

  tick() {
    const sample = this.traces[this.index % this.traces.length];
    this.index += 1;
    this._emit('motion', { ...sample, ts: Date.now() });
  }
}

export async function createMockBridge() {
  try {
    const response = await fetch('./mock-traces.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('mock trace fetch failed');
    const json = await response.json();
    return new UprightMockBridge(json.samples || json);
  } catch (error) {
    console.warn('Using embedded mock motion trace.', error);
    return new UprightMockBridge();
  }
}
''')

write("web/app.js", r'''
import { PostureEngine, radiansToDegrees } from './posture-core.js';
import { UprightBridge } from './bridge-sdk.js';
import { createMockBridge } from './mock-bridge.js';

const $ = (selector) => document.querySelector(selector);

const els = {
  modeBadge: $('#modeBadge'),
  modeValue: $('#modeValue'),
  permissionValue: $('#permissionValue'),
  connectionValue: $('#connectionValue'),
  deviceValue: $('#deviceValue'),
  rateValue: $('#rateValue'),
  posturePill: $('#posturePill'),
  scoreValue: $('#scoreValue'),
  postureCopy: $('#postureCopy'),
  timerLabel: $('#timerLabel'),
  sampleCount: $('#sampleCount'),
  gaugeFill: $('#gaugeFill'),
  canvas: $('#motionChart'),
  log: $('#eventLog'),
};

const engine = new PostureEngine();
let bridge = null;
let sessionActive = false;
let timerRemaining = 25 * 60;
let timerId = null;
let samples = [];

function log(message) {
  const li = document.createElement('li');
  li.textContent = `${new Date().toLocaleTimeString()} — ${message}`;
  els.log.prepend(li);
  while (els.log.children.length > 40) els.log.lastChild.remove();
}

function setStatus(status) {
  els.modeValue.textContent = status?.platform || '—';
  els.permissionValue.textContent = status?.permission || '—';
  els.connectionValue.textContent = status?.connection || '—';
  els.deviceValue.textContent = status?.deviceName || '—';
  els.rateValue.textContent = status?.sampleRateHz ? `${status.sampleRateHz} Hz` : '—';
}

function setPosture(result) {
  if (!result) return;
  els.posturePill.textContent = result.state;
  els.posturePill.className = `pill ${result.state}`;
  els.scoreValue.textContent = result.score;
  els.postureCopy.textContent =
    result.state === 'good' ? 'Nice. Keep your head stacked over your shoulders.' :
    result.state === 'warning' ? 'Small drift detected. Roll shoulders back and reset your neutral.' :
    'Slouch detected. Sit tall and take a quick reset breath.';
  els.gaugeFill.style.setProperty('--score', `${Math.max(4, result.score)}%`);
}

function drawChart() {
  const ctx = els.canvas.getContext('2d');
  const rect = els.canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const width = Math.max(300, Math.floor(rect.width * dpr));
  const height = Math.floor(260 * dpr);
  if (els.canvas.width !== width || els.canvas.height !== height) {
    els.canvas.width = width;
    els.canvas.height = height;
  }
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = 'rgba(0,0,0,0.16)';
  ctx.fillRect(0, 0, width, height);

  const data = samples.slice(-90);
  if (data.length < 2) {
    ctx.fillStyle = '#9fb4c6';
    ctx.font = `${16 * dpr}px system-ui`;
    ctx.fillText('Start a session to stream motion.', 24 * dpr, 42 * dpr);
    return;
  }

  const plot = (key, color) => {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 3 * dpr;
    data.forEach((sample, index) => {
      const x = (index / Math.max(1, data.length - 1)) * width;
      const y = height / 2 - sample[key] * 4.2 * dpr;
      if (index === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
  };

  ctx.strokeStyle = 'rgba(255,255,255,0.16)';
  ctx.lineWidth = 1 * dpr;
  ctx.beginPath();
  ctx.moveTo(0, height / 2);
  ctx.lineTo(width, height / 2);
  ctx.stroke();

  plot('pitch', '#3ee5a4');
  plot('roll', '#ffd166');

  ctx.fillStyle = '#9fb4c6';
  ctx.font = `${12 * dpr}px system-ui`;
  ctx.fillText('pitch', 18 * dpr, 24 * dpr);
  ctx.fillStyle = '#ffd166';
  ctx.fillText('roll', 72 * dpr, 24 * dpr);
}

function updateTimerLabel() {
  const m = Math.floor(timerRemaining / 60).toString().padStart(2, '0');
  const s = Math.floor(timerRemaining % 60).toString().padStart(2, '0');
  els.timerLabel.textContent = `${m}:${s}`;
}

function startTimer() {
  stopTimer();
  timerId = setInterval(() => {
    timerRemaining = Math.max(0, timerRemaining - 1);
    updateTimerLabel();
    if (timerRemaining === 0) {
      bridge?.app.haptic?.('alert');
      bridge?.app.speak?.('Focus interval complete. Take a posture reset.');
      stopSession();
    }
  }, 1000);
}

function stopTimer() {
  if (timerId) clearInterval(timerId);
  timerId = null;
}

async function startSession() {
  if (!bridge) return;
  const status = await bridge.headphones.getStatus();
  setStatus(status);
  if (status.permission !== 'granted') {
    await bridge.headphones.requestPermission();
  }
  await bridge.headphones.startUpdates({ sampleRateHz: 25 });
  sessionActive = true;
  $('#startBtn').disabled = true;
  $('#stopBtn').disabled = false;
  $('#permissionBtn').disabled = true;
  $('#calibrateBtn').disabled = false;
  timerRemaining = 25 * 60;
  updateTimerLabel();
  startTimer();
  log('Session started.');
}

async function stopSession() {
  if (!bridge) return;
  await bridge.headphones.stopUpdates();
  sessionActive = false;
  $('#startBtn').disabled = false;
  $('#stopBtn').disabled = true;
  $('#permissionBtn').disabled = false;
  stopTimer();
  log('Session stopped.');
}

async function refreshStatus() {
  if (!bridge) return;
  try {
    const status = await bridge.headphones.getStatus();
    setStatus(status);
  } catch (error) {
    log(`Status failed: ${error.message}`);
  }
}

async function handleMotion(sample) {
  samples.push({ pitch: sample.attitude.pitch, roll: sample.attitude.roll, ts: sample.ts });
  if (samples.length > 240) samples.shift();
  const result = engine.update(sample);
  setPosture(result);
  els.sampleCount.textContent = `${samples.length} samples`;
  drawChart();
}

async function calibrate() {
  try {
    const result = await bridge.headphones.calibrateNeutral();
    engine.neutral = result.neutral || engine.calibrate();
    log(`Neutral calibrated: pitch ${radiansToDegrees(engine.neutral.pitch).toFixed(1)}°, roll ${radiansToDegrees(engine.neutral.roll).toFixed(1)}°`);
  } catch (error) {
    engine.calibrate();
    log(`Calibration fallback used: ${error.message}`);
  }
}

async function boot() {
  try {
    bridge = new UprightBridge();
    await bridge.ready();
    if (!bridge.isNative) {
      bridge = await createMockBridge();
    }
    els.modeBadge.textContent = bridge.isNative ? 'Native shell' : 'Browser mock';
    els.modeBadge.classList.toggle('mock', !bridge.isNative);
    bridge.on('motion', handleMotion);
    bridge.on('status', (status) => {
      setStatus(status);
      log(`Status: ${status.connection} / ${status.permission}`);
    });
    bridge.on('interruption', (payload) => log(`Interruption: ${payload.reason}`));
    bridge.on('error', (payload) => log(`Error: ${payload.code} — ${payload.message}`));
    await refreshStatus();
    drawChart();
    log(bridge.isNative ? 'Native bridge ready.' : 'Mock bridge ready.');
  } catch (error) {
    log(`Boot failed: ${error.message}`);
    bridge = await createMockBridge();
    els.modeBadge.textContent = 'Browser mock';
    bridge.on('motion', handleMotion);
    bridge.on('status', setStatus);
    await refreshStatus();
  }
}

$('#startBtn').addEventListener('click', startSession);
$('#stopBtn').addEventListener('click', stopSession);
$('#permissionBtn').addEventListener('click', async () => {
  const permission = await bridge.headphones.requestPermission();
  log(`Permission result: ${permission}`);
  await refreshStatus();
});
$('#calibrateBtn').addEventListener('click', calibrate);
$('#settingsBtn').addEventListener('click', () => bridge.app.openSettings());
$('#hapticBtn').addEventListener('click', () => bridge.app.haptic('subtle'));
$('#speakBtn').addEventListener('click', () => bridge.app.speak('Posture check. Roll shoulders back and lengthen your spine.'));
$('#resetBtn').addEventListener('click', () => {
  samples = [];
  engine.samples = [];
  engine.state = 'unknown';
  setPosture({ state: 'unknown', score: 0 });
  els.sampleCount.textContent = '0 samples';
  timerRemaining = 25 * 60;
  updateTimerLabel();
  drawChart();
});
$('#clearLogBtn').addEventListener('click', () => els.log.replaceChildren());
window.addEventListener('resize', drawChart);

boot();
''')

write("web/mock-traces.json", json.dumps({
  "name": "mock-airpods-neutral-to-slouch",
  "sampleRateHz": 25,
  "samples": [
    {
      "ts": 0,
      "source": "airpods-mock",
      "attitude": {"pitch": round(0.01 + i * 0.006, 4), "roll": round(-0.01 + math.sin(i / 4) * 0.012, 4), "yaw": round(0.02 + math.cos(i / 6) * 0.01, 4)},
      "gravity": {"x": round(math.sin(i / 8) * 0.02, 4), "y": round(math.cos(i / 8) * 0.02, 4), "z": -1},
    }
    for i in range(80)
  ]
}, indent=2) + "\n")

write("ios/Upright/Info.plist", r'''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>$(EXECUTABLE_NAME)</string>
  <key>CFBundleIdentifier</key>
  <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>$(PRODUCT_NAME)</string>
  <key>CFBundleDisplayName</key>
  <string>Upright</string>
  <key>CFBundlePackageType</key>
  <string>$(PRODUCT_BUNDLE_PACKAGE_TYPE)</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSRequiresIPhoneOS</key>
  <true/>
  <key>UIApplicationSceneManifest</key>
  <dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <false/>
    <key>UISceneConfigurations</key>
    <dict>
      <key>UIWindowSceneSessionRoleApplication</key>
      <array>
        <dict>
          <key>UISceneConfigurationName</key>
          <string>Default Configuration</string>
          <key>UISceneDelegateClassName</key>
          <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
        </dict>
      </array>
    </dict>
  </dict>
  <key>UILaunchStoryboardName</key>
  <string>LaunchScreen</string>
  <key>UISupportedInterfaceOrientations</key>
  <array>
    <string>UIInterfaceOrientationPortrait</string>
  </array>
  <key>NSMotionUsageDescription</key>
  <string>Upright uses headphone motion to help you track posture and stay upright.</string>
  <key>UIApplicationSupportsIndirectInputEvents</key>
  <true/>
</dict>
</plist>
''')

write("ios/Upright/LaunchScreen.storyboard", r'''
<?xml version="1.0" encoding="UTF-8"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="22504" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" launchScreen="YES" useTraitCollections="YES" useSafeAreas="YES" colorMatched="YES" initialViewController="01J-lp-oVM">
    <device id="retina6_12" orientation="portrait" appearance="light"/>
    <dependencies>
        <plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="22504"/>
        <capability name="Safe area layout guides" minToolsVersion="9.0"/>
        <capability name="documents saved in the Xcode 8 format" minToolsVersion="8.0"/>
    </dependencies>
    <scenes>
        <scene sceneID="EHf-IW-A2E">
            <objects>
                <viewController id="01J-lp-oVM" sceneMemberID="viewController">
                    <view key="view" contentMode="scaleToFill" id="Ze5-6b-2t3">
                        <rect key="frame" x="0.0" y="0.0" width="393" height="852"/>
                        <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
                        <viewLayoutGuide key="safeArea" id="Bcu-3y-fUS"/>
                        <color key="backgroundColor" red="0.031372549019607843" green="0.066666666666666666" blue="0.12156862745098039" alpha="1" colorSpace="custom" customColorSpace="sRGB"/>
                    </view>
                </viewController>
                <placeholder placeholderIdentifier="IBFirstResponder" id="iYj-Kq-Ea1" userLabel="First Responder" sceneMemberID="firstResponder"/>
            </objects>
            <point key="canvasLocation" x="53" y="375"/>
        </scene>
    </scenes>
</document>
''')

write("ios/Upright/AppDelegate.swift", r'''
import UIKit

@main
final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        true
    }

    func application(
        _ application: UIApplication,
        configurationForConnecting connectingSceneSession: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        let configuration = UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
        configuration.delegateClass = SceneDelegate.self
        return configuration
    }
}
''')

write("ios/Upright/SceneDelegate.swift", r'''
import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = RootViewController()
        self.window = window
        window.makeKeyAndVisible()
    }
}
''')

write("ios/Upright/BridgeError.swift", r'''
import Foundation

enum BridgeError: Error, LocalizedError {
    case invalidRequest(String)
    case permissionDenied
    case unsupportedDevice
    case motionUnavailable
    case alreadyActive
    case notStarted
    case unknown(String)

    var code: String {
        switch self {
        case .invalidRequest: return "invalid_request"
        case .permissionDenied: return "permission_denied"
        case .unsupportedDevice: return "unsupported_device"
        case .motionUnavailable: return "motion_unavailable"
        case .alreadyActive: return "already_active"
        case .notStarted: return "not_started"
        case .unknown: return "unknown"
        }
    }

    var errorDescription: String? {
        switch self {
        case .invalidRequest(let message): return message
        case .permissionDenied: return "Headphone motion permission denied"
        case .unsupportedDevice: return "Supported AirPods are not connected"
        case .motionUnavailable: return "Headphone motion is temporarily unavailable"
        case .alreadyActive: return "Motion updates are already active"
        case .notStarted: return "Motion updates have not started"
        case .unknown(let message): return message
        }
    }
}
''')

write("ios/Upright/BridgeMessage.swift", r'''
import Foundation

struct BridgeRequest {
    let id: String
    let module: String
    let method: String
    let params: [String: Any]

    init?(body: Any) {
        guard let dict = body as? [String: Any],
              let id = dict["id"] as? String,
              let module = dict["module"] as? String,
              let method = dict["method"] as? String else {
            return nil
        }
        self.id = id
        self.module = module
        self.method = method
        self.params = dict["params"] as? [String: Any] ?? [:]
    }
}

struct BridgeEvent {
    let type: String
    let payload: [String: Any]
}
''')

write("ios/Upright/MotionSample.swift", r'''
import CoreMotion
import Foundation

struct Vector3: Codable {
    let x: Double
    let y: Double
    let z: Double

    func dictionary() -> [String: Any] {
        ["x": x, "y": y, "z": z]
    }
}

struct Attitude: Codable {
    let pitch: Double
    let roll: Double
    let yaw: Double

    func dictionary() -> [String: Any] {
        ["pitch": pitch, "roll": roll, "yaw": yaw]
    }
}

struct Quaternion: Codable {
    let x: Double
    let y: Double
    let z: Double
    let w: Double

    func dictionary() -> [String: Any] {
        ["x": x, "y": y, "z": z, "w": w]
    }
}

struct MotionSample: Codable {
    let ts: TimeInterval
    let source: String
    let attitude: Attitude
    let quaternion: Quaternion?
    let rotationRate: Vector3?
    let gravity: Vector3?
    let userAcceleration: Vector3?

    func dictionary() -> [String: Any] {
        var result: [String: Any] = [
            "ts": ts,
            "source": source,
            "attitude": attitude.dictionary()
        ]
        if let quaternion { result["quaternion"] = quaternion.dictionary() }
        if let rotationRate { result["rotationRate"] = rotationRate.dictionary() }
        if let gravity { result["gravity"] = gravity.dictionary() }
        if let userAcceleration { result["userAcceleration"] = userAcceleration.dictionary() }
        return result
    }

    static func from(_ motion: CMDeviceMotion) -> MotionSample {
        let attitude = motion.attitude
        let rotation = motion.rotationRate
        let gravity = motion.gravity
        let acceleration = motion.userAcceleration
        return MotionSample(
            ts: Date().timeIntervalSince1970 * 1000,
            source: "airpods",
            attitude: Attitude(pitch: attitude.pitch, roll: attitude.roll, yaw: attitude.yaw),
            quaternion: Quaternion(x: motion.attitude.quaternion.x, y: motion.attitude.quaternion.y, z: motion.attitude.quaternion.z, w: motion.attitude.quaternion.w),
            rotationRate: Vector3(x: rotation.x, y: rotation.y, z: rotation.z),
            gravity: Vector3(x: gravity.x, y: gravity.y, z: gravity.z),
            userAcceleration: Vector3(x: acceleration.x, y: acceleration.y, z: acceleration.z)
        )
    }
}
''')

write("ios/Upright/HeadphoneMotionAdapter.swift", r'''
import AVFAudio
import CoreMotion
import Foundation

final class HeadphoneMotionAdapter {
    private let manager = CMHeadphoneMotionManager()
    private let queue = OperationQueue()
    private var motionHandler: ((MotionSample) -> Void)?
    private var errorHandler: ((BridgeError) -> Void)?
    private var recentSamples: [MotionSample] = []
    private var currentSampleRateHz: Int = 25

    var authorizationStatus: CMAuthorizationStatus {
        CMHeadphoneMotionManager.authorizationStatus()
    }

    var isDeviceMotionAvailable: Bool {
        manager.isDeviceMotionAvailable
    }

    var isDeviceMotionActive: Bool {
        manager.isDeviceMotionActive
    }

    var isConnectionStatusActive: Bool {
        if #available(iOS 15.0, *) {
            return manager.isConnectionStatusActive
        }
        return false
    }

    var sampleRateHz: Int? {
        isDeviceMotionActive ? currentSampleRateHz : nil
    }

    func requestPermission(completion: @escaping (CMAuthorizationStatus) -> Void) {
        guard authorizationStatus == .notDetermined else {
            completion(authorizationStatus)
            return
        }

        let timeout = DispatchWorkItem { [weak self] in
            self?.manager.stopDeviceMotionUpdates()
            completion(CMHeadphoneMotionManager.authorizationStatus())
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 5, execute: timeout)

        manager.deviceMotionUpdateInterval = 1.0
        manager.startDeviceMotionUpdates(to: queue) { [weak self] _, _ in
            timeout.cancel()
            self?.manager.stopDeviceMotionUpdates()
            completion(CMHeadphoneMotionManager.authorizationStatus())
        }
    }

    func startUpdates(
        sampleRateHz: Int = 25,
        onMotion: @escaping (MotionSample) -> Void,
        onError: @escaping (BridgeError) -> Void
    ) {
        guard authorizationStatus == .authorized else {
            onError(.permissionDenied)
            return
        }
        guard manager.isDeviceMotionAvailable else {
            onError(.motionUnavailable)
            return
        }

        motionHandler = onMotion
        errorHandler = onError
        currentSampleRateHz = max(1, sampleRateHz)
        manager.deviceMotionUpdateInterval = 1.0 / Double(currentSampleRateHz)

        manager.startDeviceMotionUpdates(to: queue) { [weak self] motion, error in
            guard let self else { return }
            if let error {
                onError(.unknown(error.localizedDescription))
                return
            }
            guard let motion else { return }
            let sample = MotionSample.from(motion)
            self.recentSamples.append(sample)
            if self.recentSamples.count > 80 {
                self.recentSamples.removeFirst(self.recentSamples.count - 80)
            }
            onMotion(sample)
        }
    }

    func stopUpdates() {
        manager.stopDeviceMotionUpdates()
        motionHandler = nil
        errorHandler = nil
    }

    func calibrateNeutral() -> BridgeError.Result<[String: Double]> {
        let usable = recentSamples.suffix(40)
        guard !usable.isEmpty else {
            return .success(["pitch": 0, "roll": 0, "yaw": 0])
        }
        var pitch = 0.0
        var roll = 0.0
        var yaw = 0.0
        for sample in usable {
            pitch += sample.attitude.pitch
            roll += sample.attitude.roll
            yaw += sample.attitude.yaw
        }
        let count = Double(usable.count)
        return .success(["pitch": pitch / count, "roll": roll / count, "yaw": yaw / count])
    }
}

extension HeadphoneMotionAdapter {
    enum Result<Value> {
        case success(Value)
        case failure(BridgeError)
    }
}
''')

write("ios/Upright/NativeBridge.swift", r'''
import AVFAudio
import Foundation
import UIKit
import WebKit

final class NativeBridge: NSObject {
    weak var webView: WKWebView?
    private let adapter: HeadphoneMotionAdapter
    private var observers: [NSObjectProtocol] = []
    private var active = false

    init(adapter: HeadphoneMotionAdapter) {
        self.adapter = adapter
        super.init()
        installObservers()
    }

    deinit {
        observers.forEach { NotificationCenter.default.removeObserver($0) }
        adapter.stopUpdates()
    }

    func install(in configuration: WKWebViewConfiguration) {
        configuration.preferences.javaScriptEnabled = true
        if #available(iOS 14.0, *) {
            configuration.userContentController.add(self, contentWorld: .page, name: "nativeBridgeWithReply")
        } else {
            configuration.userContentController.add(self, name: "nativeBridge")
        }
    }

    func handle(_ request: BridgeRequest, replyHandler: @escaping (Any?, String?) -> Void) {
        switch (request.module, request.method) {
        case ("app", "ready"):
            reply(["platform": "ios-native-shell", "apiVersion": "1"], replyHandler)
        case ("headphones", "getStatus"):
            reply(statusDictionary(), replyHandler)
        case ("headphones", "requestPermission"):
            requestPermission(replyHandler)
        case ("headphones", "startUpdates"):
            startUpdates(request.params, replyHandler)
        case ("headphones", "stopUpdates"):
            adapter.stopUpdates()
            active = false
            dispatchStatus()
            reply(NSNull(), replyHandler)
        case ("headphones", "calibrateNeutral"):
            switch adapter.calibrateNeutral() {
            case .success(let neutral): reply(["ok": true, "neutral": neutral], replyHandler)
            case .failure(let error): reply(error, replyHandler)
            }
        case ("app", "haptic"):
            haptic(request.params)
            reply(NSNull(), replyHandler)
        case ("app", "speak"):
            speak(request.params)
            reply(NSNull(), replyHandler)
        case ("app", "openSettings"):
            openSettings()
            reply(NSNull(), replyHandler)
        case ("app", "log"):
            if let event = request.params["event"] { print("Upright event:", event) }
            reply(NSNull(), replyHandler)
        default:
            reply(BridgeError.invalidRequest("Unknown bridge method \(request.module).\(request.method)"), replyHandler)
        }
    }

    private func requestPermission(_ replyHandler: @escaping (Any?, String?) -> Void) {
        adapter.requestPermission { [weak self] status in
            guard let self else {
                replyHandler(nil, "Bridge deallocated")
                return
            }
            self.dispatchStatus()
            replyHandler(self.permissionString(for: status), nil)
        }
    }

    private func startUpdates(_ params: [String: Any], _ replyHandler: @escaping (Any?, String?) -> Void) {
        guard !active else {
            reply(BridgeError.alreadyActive, replyHandler)
            return
        }
        let sampleRate = params["sampleRateHz"] as? Int ?? 25
        adapter.startUpdates(sampleRateHz: sampleRate) { [weak self] sample in
            self?.dispatch(BridgeEvent(type: "motion", payload: sample.dictionary()))
        } onError: { [weak self] error in
            self?.active = false
            self?.dispatch(BridgeEvent(type: "error", payload: ["code": error.code, "message": error.localizedDescription ?? error.code]))
            reply(error, replyHandler)
        }
        active = true
        dispatchStatus()
        reply(NSNull(), replyHandler)
    }

    private func statusDictionary() -> [String: Any] {
        [
            "platform": "ios-native-shell",
            "apiVersion": "1",
            "supported": adapter.isDeviceMotionAvailable,
            "permission": permissionString(for: adapter.authorizationStatus),
            "connection": connectionState(),
            "deviceMotionAvailable": adapter.isDeviceMotionAvailable,
            "deviceName": deviceName(),
            "sampleRateHz": adapter.sampleRateHz ?? NSNull()
        ]
    }

    private func dispatchStatus() {
        dispatch(BridgeEvent(type: "status", payload: statusDictionary()))
    }

    private func dispatch(_ event: BridgeEvent) {
        guard let typeJSON = try? JSONSerialization.data(withJSONObject: event.type),
              let typeString = String(data: typeJSON, encoding: .utf8),
              let payloadJSON = try? JSONSerialization.data(withJSONObject: event.payload),
              let payloadString = String(data: payloadJSON, encoding: .utf8) else {
            return
        }
        webView?.evaluateJavaScript("window.__dispatchNativeEvent(\(typeString), \(payloadString))", completionHandler: nil)
    }

    private func reply(_ value: Any?, _ replyHandler: @escaping (Any?, String?) -> Void) {
        replyHandler(value, nil)
    }

    private func reply(_ error: BridgeError, _ replyHandler: @escaping (Any?, String?) -> Void) {
        replyHandler(nil, error.localizedDescription ?? error.code)
    }

    private func permissionString(for status: CMAuthorizationStatus) -> String {
        switch status {
        case .notDetermined: return "unknown"
        case .authorized: return "granted"
        case .denied: return "denied"
        case .restricted: return "restricted"
        @unknown default: return "unknown"
        }
    }

    private func connectionState() -> String {
        let hasBluetoothOutput = AVAudioSession.sharedInstance().currentRoute.outputs.contains { output in
            output.portType == .bluetoothA2DP || output.portType == .bluetoothLE
        }
        if active && adapter.isDeviceMotionActive && (hasBluetoothOutput || managerIsConnectionActive()) { return "active" }
        if hasBluetoothOutput || managerIsConnectionActive() { return "connected" }
        return "disconnected"
    }

    private func managerIsConnectionActive() -> Bool {
        if #available(iOS 15.0, *) {
            return adapter.isConnectionStatusActive
        }
        return false
    }

    private func deviceName() -> String? {
        let outputs = AVAudioSession.sharedInstance().currentRoute.outputs
        if let airPods = outputs.first(where: { $0.portName.lowercased().contains("airpods") }) {
            return airPods.portName
        }
        if let bluetooth = outputs.first(where: { $0.portType == .bluetoothA2DP || $0.portType == .bluetoothLE }) {
            return bluetooth.portName.isEmpty ? bluetooth.portType.rawValue : bluetooth.portName
        }
        return nil
    }

    private func haptic(_ params: [String: Any]) {
        let kind = params["kind"] as? String ?? "subtle"
        let style: UIImpactFeedbackGenerator.FeedbackStyle = kind == "alert" ? .heavy : .light
        UIImpactFeedbackGenerator(style: style).impactOccurred()
    }

    private func speak(_ params: [String: Any]) {
        guard let text = params["text"] as? String, !text.isEmpty else { return }
        let synthesizer = AVSpeechSynthesizer()
        let utterance = AVSpeechUtterance(string: text)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        synthesizer.speak(utterance)
    }

    private func openSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }

    private func installObservers() {
        observers.append(NotificationCenter.default.addObserver(forName: AVAudioSession.routeChangeNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self else { return }
            if self.connectionState() == "disconnected" && self.active {
                self.adapter.stopUpdates()
                self.active = false
                self.dispatch(BridgeEvent(type: "interruption", payload: ["reason": "airpods_disconnected"]))
            }
            self.dispatchStatus()
        })
        observers.append(NotificationCenter.default.addObserver(forName: UIApplication.willResignActiveNotification, object: nil, queue: .main) { [weak self] _ in
            guard let self, self.active else { return }
            self.adapter.stopUpdates()
            self.active = false
            self.dispatch(BridgeEvent(type: "interruption", payload: ["reason": "app_backgrounded"]))
            self.dispatchStatus()
        })
        observers.append(NotificationCenter.default.addObserver(forName: UIApplication.didBecomeActiveNotification, object: nil, queue: .main) { [weak self] _ in
            self?.dispatchStatus()
        })
    }
}

extension NativeBridge: WKScriptMessageHandlerWithReply {
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let request = BridgeRequest(body: message.body) else {
            replyHandlerForLegacy(message)
            return
        }
        handle(request) { value, error in
            if let error {
                self.dispatch(BridgeEvent(type: "error", payload: ["code": "native_error", "message": error]))
            }
        }
    }

    @available(iOS 14.0, *)
    func userContentController(
        _ userContentController: WKUserContentController,
        didReceive message: WKScriptMessage,
        replyHandler: @escaping (Any?, String?) -> Void
    ) {
        guard let request = BridgeRequest(body: message.body) else {
            replyHandler(nil, "Invalid bridge request")
            return
        }
        handle(request, replyHandler: replyHandler)
    }

    private func replyHandlerForLegacy(_ message: WKScriptMessage) {
        dispatch(BridgeEvent(type: "error", payload: ["code": "invalid_request", "message": "Invalid bridge request"]))
    }
}
''')

write("ios/Upright/RootViewController.swift", r'''
import UIKit
import WebKit

final class RootViewController: UIViewController, WKNavigationDelegate {
    private let adapter = HeadphoneMotionAdapter()
    private let bridge: NativeBridge
    private var webView: WKWebView!

    override init(nibName nibNameOrNil: String?, bundle nibBundleOrNil: Bundle?) {
        self.bridge = NativeBridge(adapter: adapter)
        super.init(nibName: nibNameOrNil, bundle: nibBundleOrNil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black

        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        bridge.install(in: configuration)

        webView = WKWebView(frame: view.bounds, configuration: configuration)
        webView.navigationDelegate = self
        webView.allowsBackForwardNavigationGestures = false
        webView.scrollView.bounces = false
        webView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(webView)
        bridge.webView = webView

        loadLocalWebApp()
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        webView.frame = view.bounds
    }

    private func loadLocalWebApp() {
        if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "web") {
            webView.loadFileURL(url, allowingReadAccessTo: Bundle.main.bundleURL)
        } else {
            webView.loadHTMLString("<html><body><h1>Unable to load Upright web app.</h1></body></html>", baseURL: Bundle.main.bundleURL)
        }
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.allow)
            return
        }
        if url.scheme == "file" {
            decisionHandler(.allow)
        } else {
            UIApplication.shared.open(url)
            decisionHandler(.cancel)
        }
    }
}
''')

png_icon(ROOT / "ios/Upright/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png")
write_json("ios/Upright/Assets.xcassets/AppIcon.appiconset/Contents.json", {
    "images": [
        {
            "filename": "AppIcon-1024.png",
            "idiom": "universal",
            "platform": "ios",
            "size": "1024x1024"
        }
    ],
    "info": {"author": "xcode", "version": 1}
})
write_json("ios/Upright/Assets.xcassets/Contents.json", {"info": {"author": "xcode", "version": 1}})

write("ios/Upright.xcodeproj/project.pbxproj", pbxproj())
project_target_id = id_for("Upright target")
write("ios/Upright.xcodeproj/xcshareddata/xcschemes/Upright.xcscheme", scheme(project_target_id))

print(f"Wrote Upright repo to {ROOT}")
