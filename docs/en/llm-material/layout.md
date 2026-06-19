# Auto Layout

When `material generate` creates materials, nodes are automatically arranged in topological order.

## Layout Rules

- **Data flow direction**: Left to right, Source nodes (Constant/Parameter/Texture) → Operation nodes → Output
- **Column spacing**: 280px (configurable)
- **Y-axis alignment**: All columns share the same global row grid, nodes are placed according to their category
- **Isolated nodes**: Located below the leftmost column

## Global Row Grid Alignment Algorithm

1. Calculate maximum nodes per column `MaxNodesInColumn`
2. Build global row grid: `RowGrid[i] = GridOriginY - (MaxNodesInColumn - 1) * RowHeight * 0.5 + i * RowHeight`
3. Each node is placed by category row number: Source → Row 0, Operator → Row 1, Utility → Row 2, Other → Last

## Node Category Sorting

Nodes within the same column are sorted by the following order:

1. **Source** (Constant/Parameter/Texture) → Row 0 (top)
2. **Operator** (Math operations) → Row 1
3. **Utility** (Mask/Transform/Interpolation) → Row 2
4. **Other** → Subsequent rows

## Layout Algorithm

- Based on Sugiyama layered layout (BFS topological sort)
- Bidirectional barycenter sorting to reduce edge crossings
- Supports loop handling (placed in the last column)
- Global row grid ensures column alignment for all column nodes

## Modifying Layout Parameters

Layout parameters are located in: `Plugins/LLMMaterial/Source/LLMMaterial/Builder/MaterialGraphBuilder.cpp`

Constants in function `LayoutNodes()`:

- `ColumnWidth` - Column width
- `RowHeight` - Row height
- `SourceColX` - Source node column X coordinate
- `GridOriginY` - Grid origin Y coordinate

## Example

Given the following node definition:

```json
{
  "nodes": [
    { "id": "color", "type": "Constant3Vector" },
    { "id": "roughness", "type": "Constant" },
    { "id": "multiply", "type": "Multiply" }
  ],
  "connections": [
    { "from": "color", "to": "multiply" },
    { "from": "roughness", "to": "multiply" }
  ]
}
```

Auto layout result:

```
Column 0 (Source):     Column 1 (Operator):
[color]────────────→[multiply]
[roughness]────────→|
```
