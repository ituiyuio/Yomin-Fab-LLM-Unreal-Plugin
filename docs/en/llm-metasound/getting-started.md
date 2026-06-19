# Getting Started

## Prerequisites

- Unreal Engine 5.7+
- Metasound engine plugin (enabled by default in UE5)

---

## Installation

1. Copy the `LLMMetaSound` plugin folder to your project's `Plugins/` directory
2. Open your project in Unreal Editor
3. Enable the Metasound plugin if prompted
4. The plugin is ready — no additional setup needed

---

## Basic Workflow

1. **LLM generates `.llmmetasound`** — AI outputs JSON with your audio graph definition
2. **Open Panel** — Window → LLM MetaSound
3. **Generate** — One click creates the MetaSound asset
4. **Iterate** — Modify JSON, regenerate, or export existing MetaSound back to JSON

---

## File Location

Place `.llmmetasound` files in your project's `Content/` folder:

```
YourProject/
└── Content/
    └── Audio/
        ├── TriangleSub.llmmetasound
        ├── SawDiscord.llmmetasound
        └── MySound.llmmetasound
```

---

## Build Verification

Before distributing or submitting to a marketplace:

1. Delete `Intermediate/`, `Binaries/`, `Build/`, `Saved/` folders inside the plugin directory
2. Run a full rebuild from a clean Intermediate state:

   ```
   UnrealBuildTool BuildPlugin -Plugin="path/to/LLMMetaSound.uplugin" -Platform=Win64 -Configuration=Development
   ```

3. Confirm zero errors and zero consequential warnings
