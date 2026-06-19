# Complete Examples

## Simple Color Material

```json
{
  "version": "1.0",
  "name": "RedMaterial",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": { "Constant": [1.0, 0.0, 0.0] }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" }
  }
}
```

## Texture Material

```json
{
  "version": "1.0",
  "name": "TextureMaterial",
  "nodes": [
    {
      "id": "tex",
      "type": "TextureSample",
      "properties": { "Texture": "/Game/Textures/MyTexture" }
    }
  ],
  "output": {
    "baseColor": { "node": "tex", "pin": "RGB" }
  }
}
```

## Metal Material

```json
{
  "version": "1.0",
  "name": "MetalMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": { "Constant": [0.8, 0.8, 0.9] }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" },
    "metallic": 1.0,
    "roughness": 0.3
  }
}
```

## Transparent Glass Material

```json
{
  "version": "1.0",
  "name": "GlassMaterial",
  "domain": "Surface",
  "blendMode": "Translucent",
  "shadingModel": "DefaultLit",
  "nodes": [
    {
      "id": "color",
      "type": "Constant3Vector",
      "properties": { "Constant": [0.9, 0.95, 1.0] }
    }
  ],
  "output": {
    "baseColor": { "node": "color", "pin": "Result" },
    "metallic": 0.0,
    "roughness": 0.1,
    "opacity": 0.5
  }
}
```

## Color + Texture Blend

```json
{
  "version": "1.0",
  "name": "TintedTexture",
  "nodes": [
    { "id": "tex", "type": "TextureSample", "properties": { "Texture": "/Game/Textures/BaseColor" } },
    { "id": "tint", "type": "Constant3Vector", "properties": { "Constant": [1.0, 0.8, 0.6] } },
    { "id": "multiply", "type": "Multiply" }
  ],
  "connections": [
    { "from": "tex", "fromPin": "RGB", "to": "multiply", "toPin": "A" },
    { "from": "tint", "fromPin": "Result", "to": "multiply", "toPin": "B" }
  ],
  "output": {
    "baseColor": { "node": "multiply", "pin": "Result" }
  }
}
```

## Emissive Material

```json
{
  "version": "1.0",
  "name": "EmissiveMaterial",
  "nodes": [
    {
      "id": "emissiveColor",
      "type": "Constant3Vector",
      "properties": { "Constant": [2.0, 0.5, 0.0] }
    }
  ],
  "output": {
    "emissive": { "node": "emissiveColor", "pin": "Result" }
  }
}
```

## Normal Map Material

```json
{
  "version": "1.0",
  "name": "NormalMapMaterial",
  "nodes": [
    { "id": "baseColor", "type": "Constant3Vector", "properties": { "Constant": [0.5, 0.5, 0.5] } },
    { "id": "normalTex", "type": "TextureSample", "properties": { "Texture": "/Game/Textures/Normal" } }
  ],
  "output": {
    "baseColor": { "node": "baseColor", "pin": "Result" },
    "normal": { "node": "normalTex", "pin": "RGB" }
  }
}
```

## Substrate Silicone Material

```json
{
  "version": "1.0",
  "name": "SiliconeMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [
      {
        "id": "silicone_surface",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.95, 0.92, 0.88],
          "Roughness": 0.15,
          "F0": [0.04, 0.04, 0.04]
        }
      },
      {
        "id": "silicone_base",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.85, 0.82, 0.78],
          "Roughness": 0.4
        }
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "silicone_surface",
      "bottom": "silicone_base",
      "topThickness": 0.005
    }
  }
}
```

## Material with Parameters

```json
{
  "version": "1.0",
  "name": "ParametricMaterial",
  "nodes": [
    {
      "id": "baseColorParam",
      "type": "VectorParameter",
      "properties": {
        "ParameterName": "BaseColor",
        "DefaultValue": [1.0, 1.0, 1.0, 1.0]
      }
    },
    {
      "id": "roughnessParam",
      "type": "ScalarParameter",
      "properties": {
        "ParameterName": "Roughness",
        "DefaultValue": 0.5
      }
    }
  ],
  "output": {
    "baseColor": { "node": "baseColorParam", "pin": "Result" },
    "roughness": { "node": "roughnessParam", "pin": "Result" }
  }
}
```
