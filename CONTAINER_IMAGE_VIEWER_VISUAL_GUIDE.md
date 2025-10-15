# 📸 Container Image Viewer v2 - Visual Guide

## 🎨 UI Layout Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 📊 Container Image Viewer                                          ─ □ ✕  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─ TOOLBAR ROW 1 ───────────────────────────────────────────────────┐   │
│  │ 🐳 Container: [spark-worker ▼] 📁 Path: [/tmp/          ▼]        │   │
│  │                                         [💡 /tmp/] [⚡ /output/]   │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─ TOOLBAR ROW 2 ───────────────────────────────────────────────────┐   │
│  │ [📂 Browse Files] [👁️ View Image] [💾 Download] [🔄 Refresh]     │   │
│  │ [🗑️ Clear]                    ┌─ Zoom ──────────┐                 │   │
│  │                                │ [➕][100%][➖][🔄]│                 │   │
│  │                                └──────────────────┘                 │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─ IMAGE DISPLAY ──────────────────────────────────────────────────┐    │
│  │╔══════════════════════════════════════════════════════════════╗ │ ▲   │
│  │║                                                              ║ │ █   │
│  │║              Dark Canvas (#2b2b2b)                           ║ │ █   │
│  │║                                                              ║ │ █   │
│  │║                  [Image Display Here]                        ║ │ █   │
│  │║                                                              ║ │ █   │
│  │║                                                              ║ │ █   │
│  │║                                                              ║ │ ▼   │
│  │╚══════════════════════════════════════════════════════════════╝ │     │
│  │◄────────────────────────────────────────────────────────────────►│     │
│  └──────────────────────────────────────────────────────────────────┘     │
│                                                                            │
│  ┌─ STATUS BAR ─────────────────────────────────────────────────────┐    │
│  │ ✅ Loaded: demo_chart.png       │ 800×600 | 45.2 KB | RGB | 100% │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 File Browser Window

```
┌──────────────────────────────────────────────────────────┐
│ 📂 Browse Images - spark-worker:/tmp/            ─ □ ✕  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📁 Images in spark-worker:/tmp/         (5 files)      │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │ 📄 Filename          │ 📏 Size                  │ ▲  │
│  ├──────────────────────┼──────────────────────────┤ █  │
│  │ demo_chart.png       │ 45.2K                    │ █  │
│  │ spark_result.png     │ 120K                     │ █  │
│  │ output_graph.jpg     │ 89K                      │ █  │
│  │ analysis_plot.png    │ 234K                     │ █  │
│  │ final_visual.png     │ 1.2M                     │ ▼  │
│  └──────────────────────┴──────────────────────────┘    │
│                                                          │
│  [👁️ View Selected]            [❌ Cancel]               │
│                                                          │
└──────────────────────────────────────────────────────────┘

💡 Tip: Double-click bất kỳ file nào để xem ngay!
```

---

## 🎯 State 1: Initial State (Empty)

```
┌────────────────────────────────────────────────────────────┐
│ 📊 Container Image Viewer                                  │
├────────────────────────────────────────────────────────────┤
│ 🐳 Container: [spark-worker ▼]  📁 Path: [/tmp/      ▼]  │
│                                        [💡 /tmp/] [⚡ /out/]│
├────────────────────────────────────────────────────────────┤
│ [📂 Browse] [👁️ View] [💾 Down] [🔄 Ref] [🗑️ Clr] [Zoom] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                    📊 No image loaded                      │
│                                                            │
│              💡 Click 'Browse Files' or                    │
│           enter path and click 'View Image'                │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ ✅ Ready - Select a container and browse images            │
└────────────────────────────────────────────────────────────┘
```

**Elements:**
- Dark canvas với placeholder text
- Status: "✅ Ready"
- Zoom: 100% (disabled)

---

## 🎯 State 2: After Browse

```
┌──────────────────────────────────────────────────────────┐
│ 📊 Container Image Viewer                                │
├──────────────────────────────────────────────────────────┤
│ 🐳 Container: [spark-worker ▼]  📁 Path: [/tmp/demo_chart.png ▼] │
│                                        [💡 /tmp/] [⚡ /out/]│
├──────────────────────────────────────────────────────────┤
│ [📂 Browse] [👁️ View] [💾 Down] [🔄 Ref] [🗑️ Clr] [Zoom] │
├──────────────────────────────────────────────────────────┤
│ File Browser window opened (see above)                   │
│ User double-clicked "demo_chart.png"                     │
└──────────────────────────────────────────────────────────┘
```

**Actions:**
1. User clicked "📂 Browse Files"
2. File browser opened
3. User double-clicked "demo_chart.png"
4. Path updated to "/tmp/demo_chart.png"
5. view_image() auto-called

---

## 🎯 State 3: Image Loaded (100% Zoom)

```
┌────────────────────────────────────────────────────────────┐
│ 📊 Container Image Viewer                                  │
├────────────────────────────────────────────────────────────┤
│ 🐳 Container: [spark-worker ▼]  📁 Path: [/tmp/demo_chart.png ▼] │
│                                        [💡 /tmp/] [⚡ /out/]│
├────────────────────────────────────────────────────────────┤
│ [📂 Browse] [👁️ View] [💾 Down] [🔄 Ref] [🗑️ Clr]         │
│                           🔍 Zoom [➕][100%][➖][🔄]        │
├────────────────────────────────────────────────────────────┤
│ ╔══════════════════════════════════════════════════════╗  │
│ ║                                                      ║  │
│ ║         📊 Spark Performance Chart                   ║  │
│ ║                                                      ║  │
│ ║  ┌────┬────┬────┬────┬────┐                         ║  │
│ ║  │    │    │    │    │    │                         ║  │
│ ║  │ ▓▓ │ ▓▓ │ ▓▓ │ ▓▓ │ ▓▓ │  Bar Chart             ║  │
│ ║  │ ▓▓ │ ▓▓ │ ▓▓ │ ▓▓ │ ▓▓ │                         ║  │
│ ║  └────┴────┴────┴────┴────┘                         ║  │
│ ║   Q1   Q2   Q3   Q4   Q5                            ║  │
│ ║                                                      ║  │
│ ╚══════════════════════════════════════════════════════╝  │
├────────────────────────────────────────────────────────────┤
│ ✅ Loaded: demo_chart.png │ 800×600 | 45.2 KB | RGB | 100%│
└────────────────────────────────────────────────────────────┘
```

**Visual Details:**
- Image displayed at original size (800×600)
- Dark canvas background contrasts with image
- Scrollbars appear if image > canvas
- Status shows: filename, dimensions, size, format, zoom
- Zoom controls enabled

---

## 🎯 State 4: Image Zoomed In (200%)

```
┌────────────────────────────────────────────────────────────┐
│ 📊 Container Image Viewer                                  │
├────────────────────────────────────────────────────────────┤
│ 🐳 Container: [spark-worker ▼]  📁 Path: [/tmp/demo_chart.png ▼] │
│                                        [💡 /tmp/] [⚡ /out/]│
├────────────────────────────────────────────────────────────┤
│ [📂 Browse] [👁️ View] [💾 Down] [🔄 Ref] [🗑️ Clr]         │
│                           🔍 Zoom [➕][200%][➖][🔄]        │
├────────────────────────────────────────────────────────────┤
│ ╔══════════════════════════════════════════════════════╗▲ │
│ ║ 📊 Spark Performance Chart (ZOOMED)                  ║█ │
│ ║                                                      ║█ │
│ ║  ┌──────────┬──────────┬──────────┐                 ║█ │
│ ║  │          │          │          │                 ║█ │
│ ║  │  ▓▓▓▓▓▓  │  ▓▓▓▓▓▓  │  ▓▓▓▓▓▓  │  Detail View   ║▼ │
│ ║  │  ▓▓▓▓▓▓  │  ▓▓▓▓▓▓  │  ▓▓▓▓▓▓  │                 ║  │
│ ║  │  ▓▓▓▓▓▓  │  ▓▓▓▓▓▓  │  ▓▓▓▓▓▓  │  Can read      ║  │
│ ║  └──────────┴──────────┴──────────┘  numbers now!  ║  │
│ ║     Q1         Q2         Q3                        ║  │
│ ╚══════════════════════════════════════════════════════╝  │
│ ◄──────────────────────────────────────────────────────►  │
├────────────────────────────────────────────────────────────┤
│ ✅ Loaded: demo_chart.png │ 1600×1200 | 45.2 KB | RGB | 200%│
└────────────────────────────────────────────────────────────┘
```

**Changes:**
- Image size: 800×600 → 1600×1200 (2x larger)
- Zoom label: 100% → 200%
- Scrollbars active (image exceeds canvas)
- Details visible (numbers on chart readable)
- Status shows new size: 1600×1200

**How to zoom:**
- Click ➕ button (2 times)
- Or Ctrl + Mouse Wheel Up

---

## 🎯 State 5: Download Dialog

```
┌────────────────────────────────────────────────────────────┐
│ 📊 Container Image Viewer                                  │
│                                                            │
│      ┌──────────────────────────────────────────┐         │
│      │ 💾 Save Image As                   ─ □ ✕│         │
│      ├──────────────────────────────────────────┤         │
│      │ Save in: [Downloads ▼]                  │         │
│      │                                          │         │
│      │ 📁 Documents                             │         │
│      │ 📁 Pictures                              │         │
│      │ 📁 Desktop                               │         │
│      │ 📁 Downloads         ◄ Selected          │         │
│      │                                          │         │
│      │ File name: [demo_chart.png________]     │         │
│      │                                          │         │
│      │ Save as type: [PNG files (*.png) ▼]     │         │
│      │                                          │         │
│      │          [Save]        [Cancel]          │         │
│      └──────────────────────────────────────────┘         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Actions:**
1. User clicked "💾 Download"
2. Save dialog opened
3. Default filename: demo_chart.png
4. Default location: Downloads folder
5. File type: PNG files (*.png)

**After save:**
```
┌─────────────────────────────────────────────┐
│ ✅ Success                            ─ □ ✕│
├─────────────────────────────────────────────┤
│                                             │
│  Downloaded successfully!                   │
│                                             │
│  Location: C:\Users\...\Downloads\demo_chart.png
│  Size: 45.2 KB                              │
│                                             │
│                 [OK]                        │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🎯 Interactive Elements - Visual States

### Buttons

**Normal State:**
```
┌──────────────────┐
│ 📂 Browse Files  │
└──────────────────┘
```

**Hover State:**
```
┌──────────────────┐
│ 📂 Browse Files  │  ← Slightly lighter
└──────────────────┘
```

**Clicked State:**
```
┌──────────────────┐
│ 📂 Browse Files  │  ← Pressed look
└──────────────────┘
```

**Disabled State:**
```
┌──────────────────┐
│ 📂 Browse Files  │  ← Grayed out
└──────────────────┘
```

---

### Zoom Control States

**Zoom In Available:**
```
🔍 Zoom: [➕] [100%] [➖] [🔄]
          ↑
       Can zoom in
```

**Max Zoom (500%):**
```
🔍 Zoom: [⊗] [500%] [➖] [🔄]
          ↑
       Disabled
```

**Min Zoom (10%):**
```
🔍 Zoom: [➕] [10%] [⊗] [🔄]
                    ↑
                Disabled
```

---

### Path Dropdown States

**Closed:**
```
📁 Path: [/tmp/                             ▼]
```

**Opened:**
```
📁 Path: [/tmp/                             ▲]
         ┌────────────────────────────────────┐
         │ /tmp/                              │ ← Current
         ├────────────────────────────────────┤
         │ /output/                           │
         │ /opt/spark/work/                   │
         │ /app/results/                      │
         │ /tmp/charts/                       │
         └────────────────────────────────────┘
```

---

## 🎨 Color Scheme

### Main UI Colors

```
┌─────────────────┬──────────┬───────────────────┐
│ Element         │ Color    │ Hex Code          │
├─────────────────┼──────────┼───────────────────┤
│ Canvas BG       │ Dark     │ #2b2b2b           │
│ Placeholder     │ Gray     │ #888888           │
│ Status (Ready)  │ Green    │ Default + ✅      │
│ Status (Error)  │ Red      │ Default + ❌      │
│ Status (Wait)   │ Yellow   │ Default + ⏳      │
│ Info Text       │ Gray     │ #666666           │
│ Window BG       │ Light    │ System default    │
│ Button BG       │ Default  │ System default    │
└─────────────────┴──────────┴───────────────────┘
```

### Status Message Colors

```
✅ Success:    [Green text or ✅ icon]
❌ Error:      [Red text or ❌ icon]
⏳ Loading:    [Yellow text or ⏳ icon]
ℹ️ Info:       [Blue text or ℹ️ icon]
⚠️ Warning:    [Orange text or ⚠️ icon]
```

---

## 📐 Layout Dimensions

### Window Size

```
Default:  1100 × 750 px
Minimum:  800 × 600 px
Maximum:  User's screen size
```

### Section Heights

```
Toolbar Row 1:  ~50 px
Toolbar Row 2:  ~60 px (includes zoom frame)
Canvas:         ~550 px (expandable)
Status Bar:     ~30 px
─────────────────────────
Total:          ~690 px (+ titlebar ~60 px = 750 px)
```

### Element Widths

```
Container dropdown:  ~150 px
Path combobox:       ~400 px (expandable)
Quick buttons:       ~80 px each
Action buttons:      ~120-160 px
Zoom controls:       ~180 px
```

---

## 🎬 Animation Flow

### Opening Viewer

```
1. [Main GUI] User clicks Tools → Container Image Viewer
   ↓
2. [0.1s] New window appears (fade in)
   ↓
3. [0.2s] UI elements load
   ↓
4. [0.3s] Placeholder text appears
   ↓
5. [0.5s] Ready! Status: "✅ Ready"
```

### Browse → View Flow

```
1. User clicks "📂 Browse Files"
   ↓
2. [0.5s] File browser window opens
   ↓
3. [1.0s] Files load into treeview
   ↓
4. User double-clicks image
   ↓
5. [0.1s] Browser closes
   ↓
6. [0.2s] Path updates
   ↓
7. [0.5s] Status: "⏳ Loading image..."
   ↓
8. [1.0s] docker cp executes
   ↓
9. [0.5s] PIL loads image
   ↓
10. [0.2s] Canvas displays image
    ↓
11. [0.1s] Status: "✅ Loaded: filename"
    ↓
12. Done! (Total: ~3-4 seconds)
```

### Zoom Flow

```
1. User clicks ➕ or Ctrl+Scroll
   ↓
2. [0.05s] zoom_level *= 1.2
   ↓
3. [0.1s] PIL resizes image (LANCZOS)
   ↓
4. [0.1s] PhotoImage created
   ↓
5. [0.05s] Canvas updated
   ↓
6. [0.05s] Zoom label: "120%"
   ↓
7. Done! (Total: ~0.35 seconds - FAST!)
```

---

## 💡 Visual Tips

### Tip 1: Contrast Improvement

**Before (Light canvas):**
```
┌────────────────────┐
│ ░░░░░░░░░░░░░░░░░░ │  ← Light gray BG
│ ░  📊 Image      ░ │  ← Hard to see
│ ░░░░░░░░░░░░░░░░░░ │
└────────────────────┘
```

**After (Dark canvas):**
```
┌────────────────────┐
│ ████████████████████│  ← Dark BG
│ █  📊 Image      █ │  ← Clear contrast!
│ ████████████████████│
└────────────────────┘
```

### Tip 2: Status Bar Split

**Single status (old):**
```
┌───────────────────────────────────────────────┐
│ Status: Loaded demo_chart.png                 │
└───────────────────────────────────────────────┘
```

**Dual status (new):**
```
┌────────────────────────────┬──────────────────┐
│ ✅ Loaded: demo_chart.png  │ 800×600 | 45.2KB│
└────────────────────────────┴──────────────────┘
 ← Action status               ← Image info →
```

### Tip 3: Visual Hierarchy

```
LEVEL 1: Window Title
   📊 Container Image Viewer
         ↓
LEVEL 2: Section Labels
   🐳 Container    📁 Path    🔍 Zoom
         ↓
LEVEL 3: Controls
   [Buttons]      [Inputs]   [➕➖]
         ↓
LEVEL 4: Content
   [Image Display Area]
         ↓
LEVEL 5: Info
   Status Bar
```

---

## 📱 Responsive Behavior

### Window Resize: Small (800×600)

```
┌─────────────────────────────────────┐
│ Container Image Viewer              │
├─────────────────────────────────────┤
│ [spark-w ▼] [/tmp/      ▼] [💡][⚡] │
├─────────────────────────────────────┤
│ [Browse][View][Down][Ref][Clr]     │
│                        [Zoom]       │
├─────────────────────────────────────┤
│ ╔═══════════════════════════════╗  │
│ ║    (Image - scrollable)       ║  │
│ ╚═══════════════════════════════╝  │
├─────────────────────────────────────┤
│ Status                 | Info       │
└─────────────────────────────────────┘
```

### Window Resize: Large (1600×1000)

```
┌───────────────────────────────────────────────────────────────────┐
│ Container Image Viewer                                            │
├───────────────────────────────────────────────────────────────────┤
│ 🐳 Container: [spark-worker     ▼] 📁 Path: [/tmp/____________▼] │
│                                       [💡 /tmp/] [⚡ /output/]     │
├───────────────────────────────────────────────────────────────────┤
│ [📂 Browse Files] [👁️ View Image] [💾 Download] [🔄 Refresh]     │
│ [🗑️ Clear]                           🔍 Zoom [➕][100%][➖][🔄]   │
├───────────────────────────────────────────────────────────────────┤
│ ╔═════════════════════════════════════════════════════════════╗  │
│ ║                                                             ║  │
│ ║                    (Large Image Display)                    ║  │
│ ║                                                             ║  │
│ ╚═════════════════════════════════════════════════════════════╝  │
├───────────────────────────────────────────────────────────────────┤
│ ✅ Loaded: demo_chart.png          │ 800×600 | 45.2 KB | RGB | 100%│
└───────────────────────────────────────────────────────────────────┘
```

---

## ✨ Final Visual Summary

### Before (v1)
```
Simple, functional, but dated
❌ No zoom
❌ Basic file list
❌ Light canvas
❌ Minimal info
```

### After (v2)
```
Modern, feature-rich, beautiful
✅ Zoom with controls
✅ File browser with size
✅ Dark canvas
✅ Comprehensive info
✅ Quick shortcuts
✅ Visual feedback
```

---

**Visual Guide Complete!** 🎨

Use this guide để hiểu layout và flow của Container Image Viewer v2.
Perfect for training users hoặc design documentation! 📚
