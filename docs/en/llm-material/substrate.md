# Substrate Materials

LLMMaterial supports UE5 Substrate layered material system. When a .llmmat file contains the `substrate` field, the system automatically uses the Substrate routing mode.

## Routing Modes

| Mode | Condition | Description |
|------|-----------|-------------|
| Traditional | Only `nodes` | Uses traditional Material Expression construction |
| Substrate | Only `substrate.slabs` | Full Substrate pipeline |
| Hybrid | `nodes` + `substrate.slabs` | Expression + Substrate mixed |

## Basic Structure

```json
{
  "version": "1.0",
  "name": "MySubstrateMaterial",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [...],
    "compositions": [...],
    "root": {...}
  }
}
```

## Slab Types

| Type | Description | Key Inputs |
|------|-------------|------------|
| `SubstrateSlabBSDF` | Basic surface BSDF (default) | DiffuseAlbedo, Roughness, F0, Metallic, Normal |
| `SubstrateHairBSDF` | Hair BSDF | BackboneRadius, Density, DirectVectorization |
| `SubstrateUnlitBSDF` | Unlit BSDF | EmissiveRadiance |
| `SubstrateEyeBSDF` | Eye BSDF | IrisDistance, PupilRadius |
| `SubstrateSingleLayerWaterBSDF` | Single-layer water surface | Extinction, Scattering |

## Composition Types

| Type | Description | Required Fields |
|------|-------------|----------------|
| `VerticalLayering` | Vertical layering (top/bottom stack) | `top` slab ID |
| `HorizontalMixing` | Horizontal mixing (two slab blend) | `slabA`, `slabB`, `MixRatio` |
| `Add` | Add two slabs | `slabA`, `slabB` |
| `Weight` | Weight node | `slab` ID, `weight` |
| `Select` | Select node | `slabA`, `slabB`, `Threshold` |

## Slab Input Value Format

```json
"inputs": {
  "DiffuseAlbedo": [0.8, 0.8, 0.8],   // RGB array = Constant3Vector
  "Roughness": 0.3,                      // Scalar = Constant
  "F0": [0.04, 0.04, 0.04],           // RGB array (default 0.04 Fresnel)
  "Metallic": 0.0,                      // Scalar
  "Normal": "/Game/Textures/Normal",     // Texture reference
  "BaseColor": { "node": "node_id" }    // Reference Expression node (Hybrid mode)
}
```

## Example: Simple Substrate Material

```json
{
  "version": "1.0",
  "name": "SimpleSubstrate",
  "domain": "Surface",
  "blendMode": "Opaque",
  "shadingModel": "DefaultLit",
  "substrate": {
    "slabs": [
      {
        "id": "main_slab",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.8, 0.8, 0.8],
          "Roughness": 0.3,
          "F0": [0.04, 0.04, 0.04],
          "Metallic": 0.0
        }
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "main_slab"
    }
  }
}
```

## Example: Two-Layer Material

```json
{
  "version": "1.0",
  "name": "TwoLayerMaterial",
  "substrate": {
    "slabs": [
      {
        "id": "surface_layer",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.9, 0.85, 0.8],
          "Roughness": 0.15
        }
      },
      {
        "id": "base_layer",
        "type": "SubstrateSlabBSDF",
        "inputs": {
          "DiffuseAlbedo": [0.7, 0.65, 0.6],
          "Roughness": 0.6
        }
      }
    ],
    "root": {
      "type": "VerticalLayering",
      "top": "surface_layer",
      "bottom": "base_layer",
      "topThickness": 0.01
    }
  }
}
```

## Notes

- **ShadingModel Auto-Switch**: Substrate materials automatically set ShadingModel to `MSM_Strata`
- **Hybrid Mode**: Expression nodes in `nodes` can be referenced by `{ "node": "node_id" }` in `substrate.slabs[].inputs[]`
- **Texture Inputs**: Textures use asset path strings, and the system automatically creates `TextureObject` or `TextureSample` nodes
- **VerticalLayering without bottom**: When root only specifies `top`, the Top slab becomes the root directly
