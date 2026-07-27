---
name: ue58-import-png-ui-texture-2026-06-24
description: UE 5.8 批量导入 PNG 为 UTexture2D 做 UI 看板的最短路径 + 必须设的 4 字段
metadata: 
 node_type: memory
 type: reference
 originSessionId: 70e1adbc-2968-4029-9b07-073968d8d3d8
---

# UE 5.8 批量导入 PNG → UTexture2D (UI 看板)

## 最短路径

1. **物理文件先到位**：`cp` 把 png 复制到 `Content/<path>/` 下
2. **写一次性 ability**（用完即焚）调 `unreal.AssetToolsHelpers`:
 ```python
 import unreal
 asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
 tasks = []
 for name in PNG_NAMES:
 task = unreal.AssetImportTask()
 task.filename = os.path.join(SRC, name + ".png")
 task.destination_path = "/Game/<path>"
 task.destination_name = name
 task.automated = True
 task.replace_existing = True
 task.save = True
 tasks.append(task)
 asset_tools.import_asset_tasks(tasks) # 批处理,单次即可
 ```
3. **设置 UI 4 字段**（不设就用默认 World 压缩 + 生成 mip,UI 上糊):
 ```python
 tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
 tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
 tex.set_editor_property("never_stream", True)
 tex.set_editor_property("srgb", True)
 unreal.EditorAssetLibrary.save_loaded_asset(tex)
 ```
4. **`python reload`** 重新扫 abilities,然后 `python <name>` 调用
5. **用完即焚**：删 ability 文件 + 再 `python reload`,否则污染 `python` 命令清单

## 验证

- `find /Game *<Name>*` → 资产在 AssetRegistry
- `ls /Assets/<path>` → Content Browser 能看到

## 踩坑

- **`destination_name` 别加后缀**（UE 已自动处理 .png → .uasset）;加后缀路径会出现 `name.name` 重复
- **能力文件名别加下划线前缀**（除非想隐藏）:`import_foo.py` 是公开命令,`_import_foo.py` 才私有
- **导入后没看到资产**？99% 是没设 `task.automated=True` 或 `task.save=True`
- **没 reload 就调用** → "Unknown subcommand" 报错,新 ability 没被注册

## ponytail: 用完即焚

一次性 ability 不该留下来。保留会污染命令清单 + 增加 reload 扫描成本。需要时按上面模板重写。
