# 网页内联编辑器 — 完整使用指南

AutoFigure-Edit 内置了一套**纯前端网页内联编辑器**，让你在浏览器中直接对生成的 SVG 插图进行可视化编辑，无需安装 Inkscape 或 Illustrator 等额外软件。

---

## 架构说明

内联编辑器由三部分构成：

```
autofigure-edit-keynote.html   ← 主宿主页面（含完整编辑器 JS/CSS）
  ├── #editor-toolbar          ← 浮动工具栏（sticky 定位）
  ├── #svg-container           ← SVG 展示容器（支持内联编辑）
  └── #edit-popup              ← 元素属性弹窗
```

编辑器采用**纯原生 JS + SVG DOM 操作**，零依赖，兼容所有现代浏览器。

---

## 工具栏按钮详解

### 基础操作区
| 按钮 | ID | 说明 |
|------|----|------|
| ✏️ 开启编辑 / 🔒 退出编辑 | `btn-edit-mode` | 切换编辑模式；编辑模式下所有 `data-editable` 元素可点击 |
| ＋ 添加文字 | `btn-add-text` | 在 SVG 中插入新 `<text>` 节点（仅编辑模式下可用） |
| ▭ 添加方块 | `btn-add-rect` | 在 SVG 中插入新 `<rect>` 节点（仅编辑模式下可用） |

### 颜色区
| 控件 | 说明 |
|------|------|
| 填充色拾取器 | 修改选中元素的 `fill` 属性 |
| 文字色拾取器 | 修改选中 `<text>` 元素的 `fill` 属性 |

### 历史记录区
| 按钮 | 快捷键 | 说明 |
|------|--------|------|
| ↩ 撤销 | Ctrl+Z | 回退最近一步操作 |
| ↪ 重做 | Ctrl+Y | 前进一步（撤销后可用） |

### 导出区
| 按钮 | 说明 |
|------|------|
| ⬇ 导出 SVG | 下载当前 SVG 内容为 `.svg` 文件 |
| 🖼 导出 PNG | 通过内联 `<canvas>` 渲染，下载为 `.png`（支持 1×/2×/3× 分辨率） |

---

## 元素属性弹窗

点击任意 `data-editable` 元素后，屏幕上会出现浮动属性面板：

```
┌──────────────────────────────┐
│  ELEMENT PROPERTIES          │
│  内容  [___________________] │
│  字号  [range slider]   14px │
│  填充色 [color picker]       │
│  透明度 [range slider]  100% │
│  [  取消  ]  [  确认  ]      │
└──────────────────────────────┘
```

- **内容**：文字元素的文本内容（`<text>` 节点）
- **字号**：`font-size` 属性，范围 8–72px
- **填充色**：`fill` 颜色值
- **透明度**：`opacity` 属性，范围 0–100%

---

## 使 SVG 元素可编辑

AutoFigure-Edit 生成的 `final.svg` 中，关键元素已自动添加 `data-editable` 属性。若需手动标记其他元素，在 SVG 源码中添加：

```xml
<!-- 文字元素 -->
<text data-editable="text" x="100" y="200" font-size="16">标签内容</text>

<!-- 矩形/形状 -->
<rect data-editable="shape" x="50" y="50" width="120" height="60" fill="#00aaff"/>

<!-- 图标/图片 -->
<image data-editable="icon" href="icon.png" width="48" height="48"/>
```

---

## 导出说明

### 导出 SVG

```javascript
// 内部实现逻辑
const svgContent = svgElement.outerHTML;
const blob = new Blob([svgContent], { type: 'image/svg+xml' });
// 触发浏览器下载
```

导出的 SVG 保留所有编辑，可直接用于论文投稿（矢量格式）。

### 导出 PNG

```javascript
// 内部实现逻辑（简化）
const canvas = document.createElement('canvas');
canvas.width = svgWidth * scale;  // scale = 1/2/3
canvas.height = svgHeight * scale;
const ctx = canvas.getContext('2d');
const img = new Image();
img.src = 'data:image/svg+xml,' + encodeURIComponent(svgContent);
img.onload = () => {
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(blob => saveAs(blob, 'figure.png'));
};
```

推荐使用 **2× 或 3×** 分辨率以满足期刊/会议的图片清晰度要求（通常要求 300 DPI 以上）。

---

## 启动脚本使用方式

### `scripts/launch_editor.py`

```bash
# 基本用法：打开指定 SVG 的编辑器
python scripts/launch_editor.py --svg outputs/job_001/final.svg

# 自定义端口
python scripts/launch_editor.py --svg outputs/job_001/final.svg --port 9900

# 生成独立 HTML（将 SVG 内联进 HTML，可离线使用）
python scripts/launch_editor.py --svg outputs/job_001/final.svg --standalone
# 输出：outputs/job_001/final_editor.html

# 仅生成 HTML，不自动打开浏览器
python scripts/launch_editor.py --svg outputs/job_001/final.svg --no-open
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--svg` | 必填 | SVG 文件路径 |
| `--port` | `9900` | 本地服务器端口 |
| `--standalone` | False | 是否生成独立 HTML（内联 SVG） |
| `--no-open` | False | 不自动打开浏览器 |
| `--project-dir` | 自动检测 | AutoFigure-Edit 项目根目录 |

---

## 常见问题

### Q：编辑后关闭页面，修改会丢失吗？
A：会。请在关闭前点击「⬇ 导出 SVG」保存修改。浏览器本地存储可配置自动保存（高级功能）。

### Q：PNG 导出后图片模糊？
A：选择 3× 分辨率倍率再导出，或直接使用 SVG 格式提交（矢量无损）。

### Q：点击元素没有弹出属性面板？
A：确认已点击「✏️ 开启编辑」进入编辑模式，且元素带有 `data-editable` 属性。

### Q：添加的文字/方块如何精确定位？
A：在属性弹窗中输入 `x`、`y` 坐标值，或在编辑模式下拖拽（需启用拖拽功能）。

### Q：如何批量修改同类元素的颜色？
A：目前需逐一选中修改。批量操作可通过直接编辑 SVG 源码（Ctrl+U 查看）中的 `fill` 属性实现。

---

## 与 svg-edit 的关系

AutoFigure-Edit 同时集成了开源的 [svg-edit](https://github.com/SVG-Edit/svgedit) 作为高级编辑器，位于项目的 `svg-edit/` 子目录。

| | 内联编辑器 | svg-edit |
|-|-----------|---------|
| 启动方式 | 直接在结果页面 | 单独访问 `/svg-edit/` |
| 学习曲线 | 极低，所见即所得 | 较高，功能完整 |
| 适合场景 | 快速微调文字和颜色 | 复杂形状编辑、路径操作 |
| 依赖 | 无 | svg-edit 库 |
