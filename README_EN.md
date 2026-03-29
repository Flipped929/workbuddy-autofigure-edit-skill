# WorkBuddy Skill — AutoFigure-Edit Inline Editor

> **AutoFigure-Edit** × **WorkBuddy** — Convert paper method descriptions into editable SVG figures with one click, featuring a full-featured browser-based visual editor (no additional software required).

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![AutoFigure-Edit](https://img.shields.io/badge/upstream-ResearAI%2FAutoFigure--Edit-brightgreen)](https://github.com/ResearAI/AutoFigure-Edit)
[![ICLR 2026](https://img.shields.io/badge/paper-ICLR%202026-orange)](https://arxiv.org/abs/2603.06674)

[中文](README.md) | English

---

## Preview

![Preview](assets/preview_banner.png)

---

## Features

### 🤖 AI Figure Generation Pipeline
- **4-step pipeline**: Paper method text → Image generation → SAM3 segmentation → Background removal → SVG assembly
- **Multi-LLM support**: OpenRouter, Bianxie AI (China), Google Gemini, local Ollama
- **Multi SAM3 backends**: Roboflow, fal.ai, local deployment

### 🎨 Browser-based Inline Editor (draw.io style)

Simply open [`assets/editor-demo.html`](assets/editor-demo.html) in your browser — **zero dependencies, no server needed**.

#### Basic Editing
| Feature | Description |
|---------|-------------|
| ✏️ Edit Mode | Click "Enable Editing" in the toolbar to enter interactive mode |
| 🖱️ Drag to Move | Drag any element; SVG viewBox coordinates are auto-converted |
| ⬛ Resize Handles | 8-direction handles appear on selection for precise resizing (Visio-style) |
| 🎨 Fill Color | One-click color picker in toolbar to change fill color |
| 📝 Property Popup | Click element to open edit panel: text / font-size / color / radius / stroke / opacity |
| ＋ Add Elements | Insert rectangles, text, circles, arrows (lines), and styled icons |

#### Multi-select & Alignment
| Feature | Description |
|---------|-------------|
| 🔲 Multi-select | Ctrl+Click to add to selection; drag on empty area for rubber-band selection |
| ⬜ Group | Ctrl+G — wraps selected elements into a `<g>` group for unified movement |
| ⬛ Ungroup | Ctrl+Shift+G — dissolves the group; offset is automatically applied to children |
| 📐 Smart Guides | Yellow magnetic snap guides while dragging; 8px threshold, snaps to edge/center |
| ◀▶▲▼ Align Toolbar | 6 alignment modes (left/center-h/right/top/center-v/bottom) + 2 distribute modes |
| Tab | Cycle through elements (draw.io style) |

#### Connectors (Visio Core)
| Feature | Description |
|---------|-------------|
| 🔗 Connector Tool | Click "Connector", then click source → target; arrow line is drawn automatically |
| 🔵 Endpoint Handles | Blue endpoint handles appear on selection; drag to rebind source/target (60px snap) |
| 🔄 Dynamic Follow | Connectors automatically recalculate endpoints when elements are moved |
| ✏️ Edit Properties | Popup to change color, stroke width, and dash style (solid/dashed/dotted) |

#### Icon Panel
| Feature | Description |
|---------|-------------|
| ⬡ 18 Icons | CPU / DB / Cloud / Code / Brain / Lightning / Eye / Lock / Gear / Network and more |
| One-click Insert | Click "⬡ Icons" in toolbar to open a 6×3 grid panel; click to insert |
| Full Editing | Supports color, size, opacity; participates in alignment, z-order, undo/redo |

#### Canvas Zoom & Pan
| Feature | Shortcut |
|---------|----------|
| Wheel zoom (centered on cursor) | Mouse wheel |
| Step zoom (preset levels 10%–800%) | Ctrl+`-` / Ctrl+`=` |
| Reset to 100% | Ctrl+`0` |
| Fit to canvas | Toolbar "Fit" / bottom HUD |
| Pan (space + drag) | Space + drag |
| Pinch-to-zoom (touch) | Two-finger gesture |

#### Undo / Redo (History System)
- **Ctrl+Z / Ctrl+Y**, up to **60 steps**
- Covers all operation types: move, resize, style, add, delete, group/ungroup, z-order, lock, connector

#### Layers Panel & Context Menu
| Feature | Description |
|---------|-------------|
| Layers Panel | F7 or toolbar button opens a right-side drawer listing all elements; supports click/visibility/lock |
| Context Menu | Right-click: select / edit / z-order / group / ungroup / delete |
| Overlap Picker | Right-click → "Elements here" — a floating picker to resolve stacked-element selection |
| Property Bar | Shows element type / x / y / w / h / uid below the toolbar when an element is selected |

#### Z-Order
| Shortcut | Action |
|----------|--------|
| `]` | Move forward one layer |
| `Ctrl+]` | Bring to front |
| `[` | Move back one layer |
| `Ctrl+[` | Send to back |

#### Complete Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+S` | Export SVG |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste (+20 unit offset) |
| `Ctrl+D` | Duplicate in place |
| `Ctrl+A` | Select all |
| `Ctrl+G` | Group selected elements |
| `Ctrl+Shift+G` | Ungroup |
| `Ctrl+-` | Zoom out |
| `Ctrl+=` | Zoom in |
| `Ctrl+0` | Reset zoom to 100% |
| `Delete` | Delete selected element |
| `Esc` | Deselect / exit connector mode |
| `↑ ↓ ← →` | Nudge (1 unit) |
| `Shift+Arrow` | Large nudge (10 units) |
| `Tab` | Select next element (cycle) |
| `G` | Toggle grid display |
| `L` | Lock / unlock element |
| `F7` | Open / close Layers panel |

---

## Directory Structure

```
workbuddy-autofigure-edit-skill/
├── SKILL.md                  # WorkBuddy Skill entry file
├── scripts/
│   ├── setup_env.py          # Interactive environment setup wizard
│   ├── run_autofigure.py     # CLI wrapper for AutoFigure-Edit
│   ├── launch_editor.py      # Inline editor launcher script
│   └── check_update.py       # GitHub update checker
├── references/
│   ├── providers.md          # LLM provider configuration guide
│   ├── sam3-backends.md      # SAM3 backend configuration guide
│   ├── local-llm.md          # Local LLM configuration
│   ├── inline-editor.md      # Inline editor full documentation
│   └── changelog.md          # Changelog
└── assets/
    ├── editor-demo.html      # Inline editor demo (open directly in browser)
    ├── preview_banner.png
    └── preview_fullpage.png
```

---

## Quick Installation

### Install this Skill in WorkBuddy

1. Clone the repository:
   ```bash
   git clone https://github.com/Flipped929/workbuddy-autofigure-edit-skill.git
   ```

2. Copy the folder to your WorkBuddy Skills directory:
   - **Windows**: `%USERPROFILE%\.workbuddy\skills\autofigure-edit\`
   - **macOS/Linux**: `~/.workbuddy/skills/autofigure-edit/`

3. Start a conversation in WorkBuddy with a trigger phrase, for example:
   - `Use AutoFigure-Edit to generate a paper figure`
   - `Open the inline editor to edit my SVG`
   - `Check if AutoFigure-Edit has updates`

---

## Usage Examples

### Generate a paper figure (CLI)

```bash
python scripts/run_autofigure.py \
  --project-dir /path/to/AutoFigure-Edit-main \
  --method-file paper.txt
```

### Configure environment (interactive)

```bash
python scripts/setup_env.py --project-dir /path/to/AutoFigure-Edit-main
```

### Launch the inline editor

```bash
# Open a generated SVG for visual editing
python scripts/launch_editor.py --svg /path/to/final.svg

# Generate a standalone HTML (offline-capable, shareable)
python scripts/launch_editor.py --svg /path/to/final.svg --standalone
```

### Live demo editor

Open `assets/editor-demo.html` directly in your browser — no server needed. Full editing features available immediately.

---

## Upstream Project

This Skill is a WorkBuddy integration wrapper for [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit) by Westlake University / ResearAI (ICLR 2026).

- **Upstream repository**: https://github.com/ResearAI/AutoFigure-Edit
- **Paper**: https://arxiv.org/abs/2603.06674
- **License**: Apache 2.0 (same as upstream)

---

## License

Apache License 2.0 — see [LICENSE](LICENSE)
