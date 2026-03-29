#!/usr/bin/env python3
"""
launch_editor.py — AutoFigure-Edit 网页内联编辑器启动脚本

用法：
    python scripts/launch_editor.py --svg /path/to/final.svg
    python scripts/launch_editor.py --svg /path/to/final.svg --port 9900
    python scripts/launch_editor.py --svg /path/to/final.svg --standalone
    python scripts/launch_editor.py --svg /path/to/final.svg --no-open
"""

import argparse
import os
import sys
import shutil
import webbrowser
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler


# ──────────────────────────────────────────────────────────────
# 内联编辑器 HTML 模板（纯前端，零外部依赖）
# ──────────────────────────────────────────────────────────────
EDITOR_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>SVG 内联编辑器 — AutoFigure-Edit</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--blue:#00aaff;--purple:#a060ff;--teal:#00e0c0;--white:#fff;--bg:#080812}}
html,body{{width:100%;min-height:100vh;background:var(--bg);font-family:-apple-system,'SF Pro Display','Inter',sans-serif;color:#fff;overflow-x:hidden}}

/* toolbar */
#editor-toolbar{{
  display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
  border-radius:16px;padding:12px 20px;margin:16px 20px 12px;
  position:sticky;top:12px;z-index:100;backdrop-filter:blur(20px);
}}
.tb-label{{font-size:12px;font-weight:600;color:rgba(255,255,255,.4);letter-spacing:.08em;text-transform:uppercase;margin-right:4px}}
.tb-btn{{
  display:inline-flex;align-items:center;gap:6px;
  background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);
  border-radius:8px;padding:7px 14px;font-size:13px;font-weight:500;color:rgba(255,255,255,.8);
  cursor:pointer;transition:all .2s;white-space:nowrap
}}
.tb-btn:hover{{background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.25);color:#fff}}
.tb-btn.active{{background:rgba(0,170,255,.2);border-color:rgba(0,170,255,.5);color:var(--blue)}}
.tb-btn:disabled{{opacity:.35;cursor:not-allowed}}
.tb-sep{{width:1px;height:28px;background:rgba(255,255,255,.1);flex-shrink:0}}
.tb-color-wrap{{position:relative;width:28px;height:28px;border-radius:6px;border:2px solid rgba(255,255,255,.2);overflow:hidden;cursor:pointer;flex-shrink:0}}
.tb-color-wrap input[type=color]{{position:absolute;inset:-4px;width:calc(100%+8px);height:calc(100%+8px);cursor:pointer;border:none;padding:0}}
.tb-color-preview{{position:absolute;inset:0;pointer-events:none;border-radius:4px}}
#edit-hint{{font-size:12px;color:rgba(255,255,255,.3);margin-left:auto}}

/* svg container */
#svg-wrap{{
  margin:0 20px 40px;border-radius:20px;overflow:hidden;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
  box-shadow:0 20px 60px rgba(0,0,0,.5);
  min-height:200px;display:flex;align-items:center;justify-content:center;
  padding:20px;
}}
#svg-wrap svg{{max-width:100%;height:auto;display:block;margin:auto}}

/* edit mode highlights */
#svg-wrap.edit-mode [data-editable]{{cursor:pointer;transition:filter .2s,outline .1s}}
#svg-wrap.edit-mode [data-editable]:hover{{filter:brightness(1.4) drop-shadow(0 0 6px rgba(0,170,255,.8))}}
#svg-wrap.edit-mode [data-editable].selected{{filter:brightness(1.5) drop-shadow(0 0 10px rgba(0,170,255,1))}}

/* popup */
#edit-popup{{
  display:none;position:fixed;z-index:999;
  background:rgba(14,14,28,.95);border:1px solid rgba(0,170,255,.4);
  border-radius:14px;padding:16px 20px;min-width:260px;
  box-shadow:0 20px 60px rgba(0,0,0,.6),0 0 30px rgba(0,170,255,.15);
  backdrop-filter:blur(20px);
}}
#edit-popup.visible{{display:block}}
.popup-title{{font-size:12px;font-weight:600;color:var(--blue);letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px}}
.popup-row{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.popup-row label{{font-size:12px;color:rgba(255,255,255,.5);width:52px;flex-shrink:0}}
.popup-row input[type=text],.popup-row textarea{{
  flex:1;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.15);
  border-radius:8px;padding:7px 10px;font-size:13px;color:#fff;font-family:inherit;
  outline:none;resize:none;
}}
.popup-row input[type=text]:focus,.popup-row textarea:focus{{border-color:rgba(0,170,255,.6)}}
.popup-row input[type=color]{{width:36px;height:30px;border:none;border-radius:6px;cursor:pointer;background:none;padding:0}}
.popup-row input[type=range]{{flex:1;accent-color:var(--blue)}}
.popup-row span{{font-size:12px;color:rgba(255,255,255,.4);width:36px;text-align:right}}
.popup-btns{{display:flex;gap:8px;margin-top:14px}}
.popup-btn{{flex:1;padding:8px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .2s}}
.popup-btn.ok{{background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff}}
.popup-btn.ok:hover{{opacity:.85}}
.popup-btn.cancel{{background:rgba(255,255,255,.08);color:rgba(255,255,255,.6);border:1px solid rgba(255,255,255,.1)}}
.popup-btn.cancel:hover{{background:rgba(255,255,255,.12);color:#fff}}

/* toast */
#toast{{position:fixed;bottom:30px;left:50%;transform:translateX(-50%) translateY(80px);background:rgba(0,170,255,.9);color:#fff;padding:12px 28px;border-radius:99px;font-size:14px;font-weight:600;z-index:9999;transition:transform .4s ease,opacity .4s ease;opacity:0;pointer-events:none}}
#toast.show{{transform:translateX(-50%) translateY(0);opacity:1}}

.page-title{{padding:20px 20px 0;font-size:15px;font-weight:600;color:rgba(255,255,255,.5)}}
.page-title span{{color:rgba(255,255,255,.9)}}
</style>
</head>
<body>

<p class="page-title">AutoFigure-Edit · 网页内联编辑器 &nbsp;›&nbsp; <span>{svg_filename}</span></p>

<div id="editor-toolbar">
  <span class="tb-label">编辑器</span>
  <button class="tb-btn" id="btn-edit-mode" onclick="toggleEditMode()">✏️ 开启编辑</button>
  <div class="tb-sep"></div>
  <button class="tb-btn" id="btn-add-text" onclick="addText()" disabled>＋ 添加文字</button>
  <button class="tb-btn" id="btn-add-rect" onclick="addRect()" disabled>▭ 添加方块</button>
  <div class="tb-sep"></div>
  <span class="tb-label" style="font-size:11px">填充色</span>
  <div class="tb-color-wrap" title="修改选中元素填充色">
    <div class="tb-color-preview" id="fill-preview" style="background:#00aaff"></div>
    <input type="color" id="fill-color" value="#00aaff" oninput="applyFill(this.value)"/>
  </div>
  <span class="tb-label" style="font-size:11px">文字色</span>
  <div class="tb-color-wrap" title="修改选中文字颜色">
    <div class="tb-color-preview" id="text-preview" style="background:#ffffff"></div>
    <input type="color" id="text-color" value="#ffffff" oninput="applyTextColor(this.value)"/>
  </div>
  <div class="tb-sep"></div>
  <button class="tb-btn" onclick="undoAction()" title="撤销 Ctrl+Z">↩ 撤销</button>
  <button class="tb-btn" onclick="redoAction()" title="重做 Ctrl+Y">↪ 重做</button>
  <div class="tb-sep"></div>
  <button class="tb-btn" onclick="exportSVG()">⬇ 导出 SVG</button>
  <button class="tb-btn" onclick="exportPNG()">🖼 导出 PNG</button>
  <span id="edit-hint">点击「开启编辑」以激活元素点击</span>
</div>

<div id="svg-wrap">
  {svg_content}
</div>

<!-- Edit Popup -->
<div id="edit-popup">
  <div class="popup-title">✦ 元素属性</div>
  <div class="popup-row" id="row-content">
    <label>内容</label>
    <textarea id="popup-text" rows="2"></textarea>
  </div>
  <div class="popup-row" id="row-fontsize">
    <label>字号</label>
    <input type="range" id="popup-fontsize" min="8" max="72" value="14" oninput="document.getElementById('popup-fontsize-val').textContent=this.value+'px'"/>
    <span id="popup-fontsize-val">14px</span>
  </div>
  <div class="popup-row" id="row-fill">
    <label>填充色</label>
    <input type="color" id="popup-fill" value="#00aaff"/>
  </div>
  <div class="popup-row" id="row-opacity">
    <label>透明度</label>
    <input type="range" id="popup-opacity" min="0" max="100" value="100" oninput="document.getElementById('popup-opacity-val').textContent=this.value+'%'"/>
    <span id="popup-opacity-val">100%</span>
  </div>
  <div class="popup-btns">
    <button class="popup-btn cancel" onclick="closePopup()">取消</button>
    <button class="popup-btn ok" onclick="applyPopup()">✓ 确认</button>
  </div>
</div>

<div id="toast"></div>

<script>
// ── State ──────────────────────────────────────────────────────────────
let editMode = false;
let selectedEl = null;
const history = [];
let historyIdx = -1;
const svgWrap = document.getElementById('svg-wrap');
const svgEl = svgWrap.querySelector('svg');
const popup = document.getElementById('edit-popup');

// ── History ────────────────────────────────────────────────────────────
function snapshot() {{
  const s = svgEl.innerHTML;
  history.splice(historyIdx + 1);
  history.push(s);
  historyIdx = history.length - 1;
}}
function undoAction() {{
  if (historyIdx <= 0) return;
  historyIdx--;
  svgEl.innerHTML = history[historyIdx];
  bindEditables();
  showToast('↩ 已撤销');
}}
function redoAction() {{
  if (historyIdx >= history.length - 1) return;
  historyIdx++;
  svgEl.innerHTML = history[historyIdx];
  bindEditables();
  showToast('↪ 已重做');
}}

// ── Edit Mode ──────────────────────────────────────────────────────────
function toggleEditMode() {{
  editMode = !editMode;
  svgWrap.classList.toggle('edit-mode', editMode);
  const btn = document.getElementById('btn-edit-mode');
  btn.classList.toggle('active', editMode);
  btn.textContent = editMode ? '🔒 退出编辑' : '✏️ 开启编辑';
  document.getElementById('btn-add-text').disabled = !editMode;
  document.getElementById('btn-add-rect').disabled = !editMode;
  document.getElementById('edit-hint').textContent = editMode ? '点击 SVG 元素以编辑属性' : '点击「开启编辑」以激活元素点击';
  if (!editMode) {{ deselect(); closePopup(); }}
  if (editMode && history.length === 0) snapshot();
}}

// ── Editable binding ───────────────────────────────────────────────────
function bindEditables() {{
  svgEl.querySelectorAll('[data-editable]').forEach(el => {{
    el.addEventListener('click', onElClick);
  }});
}}
function onElClick(e) {{
  if (!editMode) return;
  e.stopPropagation();
  deselect();
  selectedEl = e.currentTarget;
  selectedEl.classList.add('selected');
  openPopup(selectedEl, e.clientX, e.clientY);
}}
svgWrap.addEventListener('click', () => {{ if (editMode) {{ deselect(); closePopup(); }} }});
function deselect() {{
  if (selectedEl) {{ selectedEl.classList.remove('selected'); selectedEl = null; }}
}}
bindEditables();

// ── Popup ──────────────────────────────────────────────────────────────
function openPopup(el, cx, cy) {{
  const tag = el.tagName.toLowerCase();
  const isText = tag === 'text' || tag === 'tspan';
  document.getElementById('row-content').style.display = isText ? 'flex' : 'none';
  document.getElementById('row-fontsize').style.display = isText ? 'flex' : 'none';
  if (isText) {{
    document.getElementById('popup-text').value = el.textContent;
    const fs = parseFloat(el.getAttribute('font-size') || el.style.fontSize || '14');
    document.getElementById('popup-fontsize').value = fs;
    document.getElementById('popup-fontsize-val').textContent = fs + 'px';
  }}
  const fill = el.getAttribute('fill') || '#00aaff';
  if (fill && fill !== 'none') document.getElementById('popup-fill').value = toHex(fill);
  const op = Math.round((parseFloat(el.getAttribute('opacity') || 1)) * 100);
  document.getElementById('popup-opacity').value = op;
  document.getElementById('popup-opacity-val').textContent = op + '%';

  popup.classList.add('visible');
  const pw = 280, ph = 240;
  let left = Math.min(cx + 12, window.innerWidth - pw - 10);
  let top = Math.min(cy + 12, window.innerHeight - ph - 10);
  popup.style.left = left + 'px';
  popup.style.top = top + 'px';
}}
function closePopup() {{ popup.classList.remove('visible'); }}
function applyPopup() {{
  if (!selectedEl) {{ closePopup(); return; }}
  snapshot();
  const tag = selectedEl.tagName.toLowerCase();
  const isText = tag === 'text' || tag === 'tspan';
  if (isText) {{
    selectedEl.textContent = document.getElementById('popup-text').value;
    selectedEl.setAttribute('font-size', document.getElementById('popup-fontsize').value);
  }}
  const fill = document.getElementById('popup-fill').value;
  if (fill) selectedEl.setAttribute('fill', fill);
  const op = parseInt(document.getElementById('popup-opacity').value) / 100;
  selectedEl.setAttribute('opacity', op);
  closePopup();
  showToast('✓ 已应用');
}}

// ── Apply colors from toolbar ──────────────────────────────────────────
function applyFill(val) {{
  document.getElementById('fill-preview').style.background = val;
  if (selectedEl) {{ snapshot(); selectedEl.setAttribute('fill', val); }}
}}
function applyTextColor(val) {{
  document.getElementById('text-preview').style.background = val;
  if (selectedEl) {{ snapshot(); selectedEl.setAttribute('fill', val); }}
}}

// ── Add elements ───────────────────────────────────────────────────────
function addText() {{
  if (!editMode) return;
  const text = prompt('输入文字内容：', '新文字');
  if (!text) return;
  snapshot();
  const vb = (svgEl.getAttribute('viewBox') || '0 0 800 400').split(' ').map(Number);
  const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  t.setAttribute('x', vb[0] + vb[2] / 2);
  t.setAttribute('y', vb[1] + vb[3] / 2);
  t.setAttribute('text-anchor', 'middle');
  t.setAttribute('font-size', '16');
  t.setAttribute('fill', '#ffffff');
  t.setAttribute('data-editable', 'text');
  t.textContent = text;
  svgEl.appendChild(t);
  t.addEventListener('click', onElClick);
  showToast('✓ 文字已添加');
}}
function addRect() {{
  if (!editMode) return;
  snapshot();
  const vb = (svgEl.getAttribute('viewBox') || '0 0 800 400').split(' ').map(Number);
  const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  r.setAttribute('x', vb[0] + vb[2] / 2 - 60);
  r.setAttribute('y', vb[1] + vb[3] / 2 - 30);
  r.setAttribute('width', '120');
  r.setAttribute('height', '60');
  r.setAttribute('rx', '8');
  r.setAttribute('fill', '#00aaff');
  r.setAttribute('opacity', '0.8');
  r.setAttribute('data-editable', 'shape');
  svgEl.appendChild(r);
  r.addEventListener('click', onElClick);
  showToast('✓ 方块已添加');
}}

// ── Export ─────────────────────────────────────────────────────────────
function exportSVG() {{
  const blob = new Blob([svgEl.outerHTML], {{type:'image/svg+xml'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'edited_figure.svg'; a.click();
  URL.revokeObjectURL(url);
  showToast('✓ SVG 已导出');
}}
function exportPNG() {{
  const scale = parseFloat(prompt('分辨率倍率（1、2 或 3）：', '2') || '2');
  const w = svgEl.viewBox?.baseVal?.width || svgEl.getBoundingClientRect().width;
  const h = svgEl.viewBox?.baseVal?.height || svgEl.getBoundingClientRect().height;
  const canvas = document.createElement('canvas');
  canvas.width = w * scale; canvas.height = h * scale;
  const ctx = canvas.getContext('2d');
  const img = new Image();
  const svgData = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgEl.outerHTML);
  img.onload = () => {{
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {{
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'edited_figure.png'; a.click();
      URL.revokeObjectURL(url);
      showToast('✓ PNG 已导出（' + scale + '×）');
    }});
  }};
  img.src = svgData;
}}

// ── Keyboard shortcuts ─────────────────────────────────────────────────
document.addEventListener('keydown', e => {{
  if (e.ctrlKey && e.key === 'z') {{ e.preventDefault(); undoAction(); }}
  if (e.ctrlKey && (e.key === 'y' || (e.shiftKey && e.key === 'Z'))) {{ e.preventDefault(); redoAction(); }}
  if (e.ctrlKey && e.key === 's') {{ e.preventDefault(); exportSVG(); }}
  if (e.ctrlKey && e.shiftKey && e.key === 'S') {{ e.preventDefault(); exportPNG(); }}
  if ((e.key === 'Delete' || e.key === 'Backspace') && selectedEl && editMode) {{
    e.preventDefault(); snapshot(); selectedEl.remove(); deselect(); closePopup();
  }}
  if (e.key === 'Escape') {{ deselect(); closePopup(); }}
}});

// ── Toast ──────────────────────────────────────────────────────────────
let toastTimer;
function showToast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2000);
}}

// helper: convert any color to hex
function toHex(c) {{
  if (!c || c === 'none') return '#000000';
  if (/^#[0-9a-f]{{3,6}}$/i.test(c)) return c.length === 4 ? '#'+[...c.slice(1)].map(x=>x+x).join('') : c;
  return '#000000';
}}
</script>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────────────────────

def find_project_dir(project_dir: str | None) -> Path | None:
    """自动查找 AutoFigure-Edit 项目目录"""
    if project_dir:
        p = Path(project_dir)
        if p.exists():
            return p
    # 常见位置
    candidates = [
        Path.cwd(),
        Path.cwd().parent,
        Path.home() / "AutoFigure-Edit-main",
        Path("D:/4-Workspace/AutoFigure-Edit/AutoFigure-Edit-main"),
    ]
    for c in candidates:
        if (c / "autofigure2.py").exists() or (c / "server.py").exists():
            return c
    return None


def make_standalone_html(svg_path: Path) -> Path:
    """将 SVG 内联到 HTML，生成独立可离线使用的 HTML 文件"""
    svg_content = svg_path.read_text(encoding="utf-8")
    svg_filename = svg_path.name

    html = EDITOR_HTML_TEMPLATE.format(
        svg_content=svg_content,
        svg_filename=svg_filename,
    )
    out_path = svg_path.parent / (svg_path.stem + "_editor.html")
    out_path.write_text(html, encoding="utf-8")
    return out_path


def serve_and_open(svg_path: Path, port: int, auto_open: bool):
    """启动本地服务器，将 SVG 内联后在浏览器中打开"""
    # 生成临时 HTML 到 svg 同目录
    html_path = make_standalone_html(svg_path)
    serve_dir = html_path.parent

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def log_message(self, format, *args):
            pass  # 静默日志

    try:
        httpd = HTTPServer(("127.0.0.1", port), Handler)
    except OSError:
        print(f"[launch_editor] 端口 {port} 被占用，尝试 {port + 1}")
        port += 1
        httpd = HTTPServer(("127.0.0.1", port), Handler)

    url = f"http://127.0.0.1:{port}/{html_path.name}"
    print(f"\n✅ 内联编辑器已启动")
    print(f"   SVG  : {svg_path}")
    print(f"   URL  : {url}")
    print(f"   按 Ctrl+C 停止服务器\n")

    if auto_open:
        def open_later():
            time.sleep(0.8)
            webbrowser.open(url)
        threading.Thread(target=open_later, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[launch_editor] 服务器已停止")
        httpd.shutdown()


# ──────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AutoFigure-Edit 网页内联编辑器启动工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--svg", required=True, help="SVG 文件路径（绝对或相对）")
    parser.add_argument("--port", type=int, default=9900, help="本地服务器端口（默认 9900）")
    parser.add_argument("--standalone", action="store_true",
                        help="仅生成独立 HTML 文件，不启动服务器")
    parser.add_argument("--no-open", action="store_true",
                        help="不自动打开浏览器")
    parser.add_argument("--project-dir", default=None,
                        help="AutoFigure-Edit 项目根目录（可选，用于自动检测）")
    args = parser.parse_args()

    svg_path = Path(args.svg).resolve()
    if not svg_path.exists():
        print(f"[ERROR] 找不到 SVG 文件：{svg_path}", file=sys.stderr)
        sys.exit(1)
    if svg_path.suffix.lower() != ".svg":
        print(f"[ERROR] 指定文件不是 SVG 格式：{svg_path}", file=sys.stderr)
        sys.exit(1)

    if args.standalone:
        out = make_standalone_html(svg_path)
        print(f"\n✅ 独立 HTML 已生成：{out}")
        if not args.no_open:
            webbrowser.open(out.as_uri())
    else:
        serve_and_open(svg_path, args.port, not args.no_open)


if __name__ == "__main__":
    main()
