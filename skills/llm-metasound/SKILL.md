---
name: llm-metasound
description: |
  LLMMetaSound 是一个 DSL 驱动的 UE5 MetaSound 音频资产生成系统。当用户需要：
  (1) 创建或设计 UE5 MetaSound 音频资产（UMetaSoundSource / UMetaSoundPatch）
  (2) 将音频图描述转换为可生成的 DSL 格式（.llmmetasound JSON）
  (3) 理解或修改现有的 MetaSound JSON 定义
  (4) 需要了解支持的节点类型（Oscillator、Filter、Envelope、Mixer 等）
  (5) 查询节点输入/输出端口、类型和默认值
  请使用此技能。
---

# LLMMetaSound - MetaSound Audio Asset DSL

## File Format

MetaSound 定义使用 `.llmmetasound` 扩展名，格式为 LLM-friendly JSON。

## Reference Files

**Node Schema**: `Plugins/LLMMetaSound/Config/Schemas/LLMMetaSoundSchema.llmmetasoundschema` — 包含所有可用 MetaSound 节点类型的完整定义（401 个节点）

**示例目录**: `Plugins/LLMMetaSound/Examples/` — 包含 `.llmmetasound` 示例文件

## Quick Start

```json
{
  "Metadata": {
    "NodeName": "MySynth",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "A simple FM synthesizer"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Sine", "Name": "Osc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 } } },
    { "NodeID": 2, "ClassName": "Envelope Follower", "Name": "Env", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 1 }
  ]
}
```

## DSL Reference

### Metadata

```json
"Metadata": {
  "NodeName": "MySound",           // 资产名称（必需）
  "NodeType": "MetasoundSource",  // 或 "MetasoundGraph"（子图/Patch）
  "MetasoundDescription": "..."    // 描述（可选）
}
```

`NodeType` 决定资产类型：
- `MetasoundSource` → UMetaSoundSource（可播放音频）
- `MetasoundGraph` → UMetaSoundPatch（纯 DSP 子图）

### Inputs / Outputs

图输入输出接口成员（可选）：

```json
"Inputs": [
  {
    "Name": "Frequency",
    "TypeName": "Primitive:Float",
    "LiteralValue": { "LiteralType": "Float", "AsFloat": 440.0 }
  }
],
"Outputs": [
  {
    "Name": "Audio",
    "TypeName": "Audio:Buffer"
  }
]
```

### LiteralValue 格式

```json
{ "LiteralType": "Float",    "AsFloat": 440.0 }
{ "LiteralType": "Integer",   "AsInteger": 2 }
{ "LiteralType": "Boolean",   "AsBool": true }
{ "LiteralType": "String",    "AsString": "Hello" }
{ "LiteralType": "FloatArray", "AsFloatArray": [1.0, 2.0, 3.0] }
```

**VertexID**：端口在节点上的索引顺序（从 0 开始），由节点定义决定。

### Nodes

```json
"Nodes": [
  {
    "NodeID": 1,
    "ClassName": "Input",         // 节点类名（必需）
    "Name": "Freq",               // 显示名称（可选）
    "TypeName": "Primitive:Float", // Input/Output 节点必须指定
    "InputDefaults": {             // 默认值（可选）
      "Frequency": { "LiteralType": "Float", "AsFloat": 440.0 }
    }
  }
]
```

**Interface 节点**（Input/Output）：
- `ClassName` 必须是 `"Input"` 或 `"Output"`
- `TypeName` 必须指定，如 `"Primitive:Float"`、`"Audio:Buffer"`

**External 节点**（Oscillator、Filter 等）：
- `ClassName` 使用注册表中的类名
- `TypeName` 对 External 节点可省略

### Edges

```json
"Edges": [
  {
    "FromNodeID": 1,     // 源节点 ID
    "FromVertexID": 0,   // 源输出端口索引
    "ToNodeID": 2,       // 目标节点 ID
    "ToVertexID": 0       // 目标输入端口索引
  }
]
```

**连接类型规则**：
- `Audio:Buffer` → `Audio:Buffer`（音频接音频）
- `Primitive:Float` → `Primitive:Float`（浮点接浮点）
- 音频不能直接接到浮点，需通过 `ConversionAudioToFloat` 转换

## Node Categories

### Generators（振荡器/声源）

| ClassName | 说明 |
|-----------|------|
| `Sine` | 正弦波振荡器 |
| `Saw` | 锯齿波振荡器 |
| `Square` | 方波振荡器 |
| `Triangle` | 三角波振荡器 |
| `Noise` | 白噪声 |
| `Perlin Noise (audio)` | Perlin 噪声（音频） |
| `Perlin Noise (float)` | Perlin 噪声（浮点） |
| `LFO` | 低频振荡器 |
| `Additive Synth` | 加法合成器 |
| `SuperOscillatorMono` | 超级振荡器（单声道） |
| `SuperOscillatorStereo` | 超级振荡器（立体声） |
| `Subharmonizer` | 次谐波合成器 |

### Filters（滤波器）

| ClassName | 说明 |
|-----------|------|
| `Ladder Filter` | Moog 风格梯形滤波器 |
| `Biquad Filter` | 双二阶滤波器 |
| `State Variable Filter` | 状态变量滤波器 |
| `DynamicFilter` | 动态滤波器 |
| `Flanger` | 镶边效果 |
| `Bitcrusher` | 采样率降低效果 |
| `WaveShaper` | 波形整形 |
| `RingMod` | 环形调制 |
| `One-Pole Low Pass Filter` | 单极低通 |
| `One-Pole High Pass Filter` | 单极高通 |

### Envelopes（包络）

| ClassName | 说明 |
|-----------|------|
| `Envelope Follower` | 包络跟随器 |
| `ADSR Envelope` | ADSR 包络 |
| `AD Envelope` | AD 包络 |
| `Fade` | 淡入淡出 |

### Math（数学运算）

| ClassName | 说明 |
|-----------|------|
| `Add` | 加法 |
| `Subtract` | 减法 |
| `Multiply` | 乘法 |
| `Divide` | 除法 |
| `Clamp` | 范围限制 |
| `MapRange` | 范围映射 |
| `Abs` | 绝对值 |
| `Max` | 最大值 |
| `Min` | 最小值 |
| `Power` | 幂运算 |
| `InterpTo` | 插值 |

### Triggers（触发器）

| ClassName | 说明 |
|-----------|------|
| `Trigger Delay` | 触发延迟 |
| `Trigger Once` | 单次触发 |
| `Trigger Select (N)` | N 路触发选择 |
| `Trigger Sequence (N)` | N 步触发序列 |
| `Trigger Route (Float, N)` | N 路浮点触发路由 |
| `Trigger Route (Audio, N)` | N 路音频触发路由 |
| `Trigger On Value Change` | 值变化触发 |
| `Trigger Toggle` | 触发开关 |
| `TriggerRepeat` | 重复触发 |

### Delays（延迟/混响）

| ClassName | 说明 |
|-----------|------|
| `Delay` | 延迟 |
| `Stereo Delay` | 立体声延迟 |
| `Delay Pitch Shift` | 音高偏移延迟 |
| `Diffuser` | 扩散器 |
| `GrainDelayNode` | 颗粒延迟 |
| `Plate Reverb` | 板式混响 |

### Mix（混音）

| ClassName | 说明 |
|-----------|------|
| `Audio Mixer (Mono, N)` | N 路单声道混音器 |
| `Audio Mixer (Stereo, N)` | N 路立体声混音器 |

### Wave Player（采样播放）

| ClassName | 说明 |
|-----------|------|
| `Wave Player` | 采样播放器 |

### External IO（外部音频）

| ClassName | 说明 |
|-----------|------|
| `Audio Bus Reader (N)` | N 声道音频总线读取 |
| `Audio Bus Writer (N)` | N 声道音频总线写入 |
| `Wave Writer` | 采样写入器 |

### Conversions（类型转换）

| ClassName | 说明 |
|-----------|------|
| `ConversionAudioToFloat` | 音频→浮点 |
| `ConversionFloatToAudio` | 浮点→音频 |
| `ConversionFloatToTime` | 浮点→时间 |
| `ConversionTimeToFloat` | 时间→浮点 |
| `BPMToSeconds` | BPM→秒 |

## Common Patterns

### 振荡器 → 滤波器 → 包络（最常用模板）

```json
{
  "Metadata": {
    "NodeName": "BasicSynth",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Basic oscillator with filter and envelope"
  },
  "Inputs": [],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Saw", "Name": "Osc", "InputDefaults": { "Frequency": { "LiteralType": "Float", "AsFloat": 110.0 } } },
    { "NodeID": 2, "ClassName": "Ladder Filter", "Name": "LPF", "InputDefaults": {} },
    { "NodeID": 3, "ClassName": "Envelope Follower", "Name": "Env", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 2, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 1 }
  ]
}
```

### 带输入接口的合成器

```json
{
  "Metadata": {
    "NodeName": "ParametricSynth",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "Synthesizer with frequency and gain inputs"
  },
  "Inputs": [
    { "Name": "Frequency", "TypeName": "Primitive:Float", "LiteralValue": { "LiteralType": "Float", "AsFloat": 440.0 } },
    { "Name": "Gain", "TypeName": "Primitive:Float", "LiteralValue": { "LiteralType": "Float", "AsFloat": 1.0 } }
  ],
  "Outputs": [],
  "Nodes": [
    { "NodeID": 1, "ClassName": "Input", "Name": "FreqIn", "TypeName": "Primitive:Float" },
    { "NodeID": 2, "ClassName": "Input", "Name": "GainIn", "TypeName": "Primitive:Float" },
    { "NodeID": 3, "ClassName": "Sine", "Name": "Osc", "InputDefaults": {} },
    { "NodeID": 4, "ClassName": "Multiply", "Name": "GainMul", "InputDefaults": {} },
    { "NodeID": 5, "ClassName": "Envelope Follower", "Name": "Env", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 0 },
    { "FromNodeID": 3, "FromVertexID": 0, "ToNodeID": 4, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 4, "ToVertexID": 1 },
    { "FromNodeID": 4, "FromVertexID": 0, "ToNodeID": 5, "ToVertexID": 1 }
  ]
}
```

### ADSR 包络模板

```json
{
  "Metadata": {
    "NodeName": "ADSRTest",
    "NodeType": "MetasoundSource",
    "MetasoundDescription": "ADSR envelope test"
  },
  "Nodes": [
    { "NodeID": 1, "ClassName": "Noise", "Name": "Noise", "InputDefaults": {} },
    { "NodeID": 2, "ClassName": "ADSR Envelope", "Name": "Env", "InputDefaults": {} },
    { "NodeID": 3, "ClassName": "Multiply", "Name": "Mul", "InputDefaults": {} },
    { "NodeID": 4, "ClassName": "Envelope Follower", "Name": "OutputEnv", "InputDefaults": { "Enable": { "LiteralType": "Boolean", "AsBool": true } } }
  ],
  "Edges": [
    { "FromNodeID": 1, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 0 },
    { "FromNodeID": 2, "FromVertexID": 0, "ToNodeID": 3, "ToVertexID": 1 },
    { "FromNodeID": 3, "FromVertexID": 0, "ToNodeID": 4, "ToVertexID": 1 }
  ]
}
```

## Examples

所有示例文件位于 `Plugins/LLMMetaSound/Examples/`：

| 文件 | 结构 | 说明 |
|------|------|------|
| `SquareBass.llmmetasound` | Square → Ladder Filter → Envelope Follower | 方波贝斯 |
| `SawDiscord.llmmetasound` | Saw → Ladder Filter → Envelope Follower | 锯齿波discord |
| `TrianglePad.llmmetasound` | Triangle → Envelope Follower | 三角波垫音 |
| `TriangleSub.llmmetasound` | Triangle → Envelope Follower | 三角波低音 |
| `NoiseBurst.llmmetasound` | Noise → Envelope Follower | 噪声突发 |
| `SquareLead.llmmetasound` | Square → Ladder Filter → Envelope Follower | 方波主音 |

## VertexID 速查

不确定端口索引时，可通过 LLMMetaSound 编辑器面板导出已有资产的 JSON 查看正确的 VertexID。

常见节点的端口索引（由注册表定义，可能因 UE 版本而异）：

**Oscillators（Sine/Saw/Square/Triangle/Noise）**：
- index 0 = Audio（输出）
- index 1 = Frequency（输入）
- index 2 = FM（输入，可选）

**Ladder Filter**：
- index 0 = Audio（输出）
- index 0 = Audio（输入）
- index 1 = Cutoff（输入）
- index 2 = Resonance（输入）

**Envelope Follower**：
- index 0 = Audio（输出）
- index 1 = Audio（输入）
- index 2 = Enable（输入，布尔）

## Troubleshooting

1. **节点类名找不到**: 使用 Schema 中的 `className` 字段值，而非 `displayName`
2. **连接失败**: 检查 TypeName 是否匹配（`Audio:Buffer` 不能直接连 `Primitive:Float`）
3. **VertexID 不确定**: 从编辑器面板导出已有资产查看，或在 Schema 中查找节点的 `inputs`/`outputs` 顺序
4. **Input/Output 节点**: 每个接口成员需要有对应 `ClassName="Input"/"Output"` 的节点
5. **默认值不生效**: `InputDefaults` 只能设置 Input 端口，Output 端口不能设置默认值

## Editor Workflow

1. 打开编辑器 → 窗口 → LLMMetaSound 面板
2. 在面板中粘贴或编写 `.llmmetasound` JSON
3. 点击 Generate 生成 MetaSound 资产
4. 可通过 Export 将已有 MetaSound 导出为 JSON 进行修改和重新生成
