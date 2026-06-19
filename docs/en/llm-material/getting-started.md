# Getting Started

## Installation

1. Copy the `LLMMaterial` plugin folder to your project's `Plugins/` directory
2. Enable the plugin in UE Editor (Edit → Plugins → AI → LLMMaterial)
3. Restart the editor

## Creating Your First Material

### Step 1: Write a JSON File

Create a `MyRedMaterial.llmmat` file:

```json
{
  "version": "1.0",
  "name": "MyRedMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": {
        "Constant": [1.0, 0.0, 0.0]
      }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" }
  }
}
```

### Step 2: Generate Material Asset

Open the LLMMaterial panel in the editor (Window → LLMMaterial), or use the command line:

```bash
material generate /Game/Materials/MyRedMaterial --from MyRedMaterial.llmmat
```

### Step 3: View Results

The generated Material asset opens automatically, where you can make further adjustments in the Material Editor.

## File Format Details

### Basic Structure

```json
{
  "version": "1.0",           // Version number
  "name": "MaterialName",     // Material name
  "domain": "Surface",        // Material domain
  "blendMode": "Opaque",      // Blend mode
  "shadingModel": "DefaultLit", // Shading model
  "nodes": [...],             // Node array
  "connections": [...],       // Connection array (optional)
  "output": {...}            // Output configuration
}
```

### Node Definition

```json
{
  "id": "uniqueNodeId",       // Unique node identifier
  "type": "Constant3Vector",   // Node type
  "displayName": "My Color",   // Display name (optional)
  "properties": {              // Node properties
    "PropertyName": "value"
  }
}
```

### Output Configuration

```json
"output": {
  "baseColor": { "node": "color", "pin": "Result" },
  "metallic": 1.0,
  "roughness": 0.5,
  "normal": { "node": "normalTex", "pin": "RGB" },
  "emissive": { "node": "emissive", "pin": "Result" }
}
```

## Using the Editor Panel

LLMMaterial provides a three-column editor panel:

- **File List** (left): Manage .llmmat files
- **Node Tree** (center): View material structure
- **Properties Panel** (right): Edit node properties

### Toolbar Buttons

- **Generate**: Generate material from selected .llmmat file
- **Export Material**: Export existing material to JSON
- **Export Schema**: Export expression schema reference
