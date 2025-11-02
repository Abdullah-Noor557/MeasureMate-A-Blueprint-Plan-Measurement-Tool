# Blueprint Measurement Tool 📐

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

A powerful, user-friendly desktop application for precise measurements on blueprint images and floor plans. Born from necessity at Team Swift, this tool eliminates the tedious manual process of measuring with rulers or making rough estimates.

<img width="1919" height="1031" alt="image" src="https://github.com/user-attachments/assets/9cfd64cd-923f-4c2f-884a-b2133bb503d6" />

## 📖 The Story

While working at **Team Swift**, our team regularly dealt with aeroplane blueprints, and technical drawings. The workflow was frustrating: we'd either hold physical rulers up to printed blueprints (inaccurate and time-consuming) or make rough visual estimates that often led to costly errors.

I realized we needed a better solution—one that would:
- Allow digital measurement with pixel-perfect accuracy
- Handle any image format and resolution
- Support multiple units of measurement
- Save time and eliminate human error

So I built this tool. What used to take 30 minutes of squinting at rulers now takes 2 minutes with precise, verifiable measurements. The tool has since become indispensable for our team's workflow, and I'm sharing it here hoping it helps others facing the same challenges.

## ✨ Features

### Core Functionality
- 🖼️ **Universal Image Support** - PNG, JPG, JPEG, BMP, GIF, TIFF formats
- 📏 **Smart Calibration System** - Set scale once using any known reference distance
- 🎯 **Precision Measurements** - Draw lines between any two points for instant distance calculation
- 🔄 **Multi-Unit Support** - Seamlessly convert between meters, centimeters, feet, and inches
- 🔍 **Advanced Zoom** - 10% to 1000% zoom with mouse wheel for pixel-perfect accuracy
- 📊 **Measurement History** - Track all measurements with running totals

### User Experience
- 🎨 **Customizable Interface** - Adjust colors, line widths, fonts, and visual styles
- 🖱️ **Drag & Drop** - Simply drag images into the application
- 📐 **Crosshair & Rulers** - Optional visual aids for precise alignment
- ⌨️ **Keyboard Shortcuts** - Streamlined workflow with comprehensive hotkeys
- 🎨 **Per-Measurement Styling** - Customize individual measurements with unique colors
- 📍 **Snap-to-Axis** - Hold Shift for perfect horizontal/vertical lines

### Export & Sharing
- 💾 **Export Labeled Images** - Save blueprints with measurements burned in
- 📄 **CSV Export** - Export all measurements to spreadsheet format
- 🏷️ **Watermarked Output** - Automatic timestamp and metadata on exports

### Advanced Features
- 🔴 **Multi-Color Support** - Color-coded calibration (red) and measurement (blue) lines
- 📋 **Settings Persistence** - Your preferences are saved between sessions
- ↩️ **Undo/Redo** - Quickly fix mistakes with Ctrl+Z
- 🎯 **Right-Click Context Menu** - Customize or delete individual measurements
- 📱 **Responsive Design** - Resizable interface that adapts to your screen

## 🚀 Quick Start

### For Windows Users (Easiest)

**An executable (.exe) is available in the [Releases](https://github.com/) section!**

1. Download the latest `BlueprintMeasurementTool.exe` from Releases
2. Double-click to run—no installation required
3. Start measuring!

### For Python Users

#### Installation

```bash
# Clone the repository
git clone https://github.com/
cd blueprint-measurement-tool

# Install dependencies
pip install -r requirements.txt
```

#### Running the Application

```bash
python blueprint_measurement_tool.py
```

## 📚 How to Use

### Step-by-Step Guide

#### 1. Load Your Blueprint
- Click **"Load Blueprint Image"** or drag & drop an image file
- Supported formats: PNG, JPG, JPEG, BMP, GIF, TIFF

#### 2. Calibrate the Scale
This is the most important step for accurate measurements!

1. **Find a known distance** on your blueprint (e.g., a wall marked as "10 feet" or "3 meters")
2. **Zoom in** using the mouse wheel for precision
3. **Click two points** on that known distance to draw a reference line (red)
4. Enter the **actual distance** in the "Reference Distance" field
5. Select the **unit** (meters, centimeters, feet, or inches)
6. The tool automatically calculates the scale

💡 **Tip**: The longer your reference line, the more accurate your measurements will be!

#### 3. Take Measurements
- After calibration, simply **click two points** to measure any distance
- The measurement appears instantly on the image and in the side panel
- Draw as many measurements as you need
- Hold **Shift** while drawing for perfectly horizontal/vertical lines

#### 4. Customize & Export
- Change display units anytime using the "Display in:" dropdown
- Right-click any measurement line to customize its color/width
- Export labeled image: **File → Export Labelled Image** (Ctrl+S)
- Export to CSV: **File → Export Measurements (CSV)**

### Visual Guide

```
1. CALIBRATION MODE          2. MEASUREMENT MODE         3. RESULTS
   (Red line)                   (Blue lines)                (Display panel)

   [Image]                      [Image]                     ╔════════════════╗
   Reference: 10 ft         →   Multiple measurements   →   ║ Measurements   ║
   Known distance               Automatic calculation        ║ 1. 15.3 ft     ║
                                                            ║ 2. 8.7 ft      ║
                                                            ║ 3. 22.1 ft     ║
                                                            ║ Total: 46.1 ft ║
                                                            ╚════════════════╝
```

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| **File Operations** |
| Load image | `Ctrl+O` |
| Export image | `Ctrl+S` |
| Quit | `Ctrl+Q` |
| **Measurements** |
| Clear all | `Ctrl+C` |
| Undo last | `Ctrl+Z` / `Delete` / `Backspace` |
| Cancel current | `Escape` |
| Snap to axis | Hold `Shift` while drawing |
| **Calibration** |
| Reset calibration | `Ctrl+R` |
| **Zoom** |
| Zoom in | `+` / `=` or Mouse Wheel Up |
| Zoom out | `-` or Mouse Wheel Down |
| Reset zoom | `Ctrl+0` |
| **View** |
| Preferences | `Ctrl+,` |
| **Help** |
| Show shortcuts | `F1` |

💡 **Pro Tip**: Press **F1** anytime to see all shortcuts in the app!

## 🎨 Customization

Access **Settings → Preferences** (Ctrl+,) to customize:

### Colors
- Calibration line and point colors
- Measurement line and point colors
- Text and label colors
- Canvas background
- Crosshair and ruler colors

### Line Settings
- Line widths (1-10 pixels)
- Point sizes (2-10 pixels)

### Text Settings
- Font family (Arial, Helvetica, Times, Courier)
- Font size (6-24 pt)
- Show/hide labels
- Label backgrounds

### Display
- Toggle crosshair visibility
- Toggle ruler visibility
- Adjust crosshair and ruler colors

All settings are automatically saved and restored between sessions!

## 📋 Requirements

### Minimum System Requirements
- **OS**: Windows 7+, macOS 10.12+, or Linux
- **Python**: 3.6 or higher (if running from source)
- **RAM**: 512 MB minimum
- **Display**: 1024x768 or higher recommended

### Python Dependencies
```
Pillow>=10.0.0          # Image processing
tkinterdnd2>=0.3.0      # Drag & drop support (optional)
```

**Note**: `tkinter` is included with Python installations

## 🔧 Technical Details

### How It Works

1. **Calibration Phase**
   - User draws a reference line on the image
   - Calculates pixel distance between the two points
   - Establishes a pixels-per-unit ratio based on known distance
   - Stores base scale factor independent of zoom level

2. **Measurement Phase**
   - For each measurement line:
     - Calculates pixel distance using Euclidean distance formula
     - Converts to real-world units using calibration ratio
     - Adjusts for current zoom level
     - Displays result with unit conversion

3. **Zoom System**
   - Base scale adapts image to canvas size
   - Zoom level (0.1x to 10x) multiplies base scale
   - All coordinates scale proportionally
   - Measurements remain accurate at any zoom level

4. **Export System**
   - Creates a copy of the original image at current zoom
   - Draws all measurements using PIL's ImageDraw
   - Renders text labels with customizable fonts
   - Adds metadata watermark with timestamp

### Architecture
```
blueprint_measurement_tool.py
├── BlueprintMeasurementTool (Main Class)
│   ├── UI Components (Tkinter)
│   ├── Image Processing (PIL/Pillow)
│   ├── Calibration System
│   ├── Measurement Engine
│   ├── Zoom & Pan System
│   ├── Settings Manager (JSON)
│   └── Export Module (Image & CSV)
```

## 📦 Project Structure

```
blueprint-measurement-tool/
├── blueprint_measurement_tool.py  # Main application
├── blueprint_settings.json        # User preferences (auto-generated)
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── README_BLUEPRINT_TOOL.md      # Original documentation
└── screenshot.png                 # Application screenshot
```

## 🐛 Troubleshooting

### Common Issues

**Q: Image won't load**
- Ensure the file is a valid image format
- Check file isn't corrupted (try opening in another program)
- Verify file path doesn't contain special characters

**Q: Measurements seem inaccurate**
- Double-check your calibration reference distance
- Use a longer reference line for better accuracy
- Ensure you clicked the exact start/end points of the reference
- Try re-calibrating with a different known distance

**Q: Drag & drop not working**
- The `tkinterdnd2` package is optional
- If not installed, use the "Load Blueprint Image" button instead
- Install with: `pip install tkinterdnd2`

**Q: Export image is blank or missing measurements**
- Ensure you've completed calibration first
- Check that measurements are visible on screen before exporting
- Try zooming to 100% before export

**Q: Application won't start**
- Verify Python 3.6+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check for error messages in the console

## 🤝 Contributing

Contributions are welcome! Whether it's:
- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code contributions

Please feel free to open an issue or submit a pull request.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/blueprint-measurement-tool.git
cd blueprint-measurement-tool

# Install dependencies
pip install -r requirements.txt

# Run the application
python blueprint_measurement_tool.py
```

## 📝 Use Cases

This tool is perfect for:
- 📐 **Architects & Engineers** - Verify dimensions on digital blueprints
- 🏗️ **Construction Teams** - Quick measurements from floor plans
- 🏠 **Real Estate** - Measure room dimensions from property photos
- 🎨 **Interior Designers** - Plan furniture layouts and spacing
- 🗺️ **Urban Planners** - Analyze site plans and maps
- 🏢 **Facility Managers** - Document building layouts
- 📚 **Students** - Study drawings
- 🛠️ **DIY Enthusiasts** - Home renovation planning

## 📄 License

This project is licensed under the MIT License - feel free to use, modify, and distribute as needed.

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Image processing powered by Pillow (PIL)
- Drag & drop support via tkinterdnd2
- Inspired by the daily challenges at Team Swift

## 👨‍💻 Author

**Made with ❤️ by Abdullah Noor**

*From frustration with rulers to a tool that saves hours—built at Team Swift, shared with the world.*

---

## 📞 Support

If you find this tool useful, please:
- ⭐ Star this repository
- 🐛 Report bugs via Issues
- 💬 Share feedback and suggestions
- 📢 Tell others who might benefit

**Happy Measuring! 📏✨**

