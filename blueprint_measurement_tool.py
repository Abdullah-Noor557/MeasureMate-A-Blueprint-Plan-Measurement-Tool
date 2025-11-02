import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import math
import json
import os
import csv
from datetime import datetime
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class BlueprintMeasurementTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Blueprint Measurement Tool")
        self.root.geometry("1200x800")
        self.dnd_available = DND_AVAILABLE
        
        # Variables
        self.image = None
        self.photo = None
        self.canvas_image = None
        self.scale_factor = None  # pixels per unit at current zoom
        self.base_scale_factor = None  # pixels per unit at zoom level 1.0
        self.calibration_zoom_level = 1.0  # zoom level when calibration was done
        self.calibration_points = []
        self.current_line_points = []
        self.measurements = []  # Store all measurements
        self.mode = "calibrate"  # "calibrate" or "measure"
        self.unit = "meters"  # default unit
        
        # Zoom variables
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.zoom_step = 0.1
        
        # Canvas offset for centering
        self.offset_x = 0
        self.offset_y = 0
        
        # Store original image size
        self.original_image = None
        self.base_scale = 1.0  # Base scale to fit canvas
        
        # Default settings
        self.settings = {
            'calibration_line_color': '#FF0000',  # Red
            'calibration_point_color': '#FF0000',
            'calibration_line_width': 2,
            'measurement_line_color': '#0000FF',  # Blue
            'measurement_point_color': '#0000FF',
            'measurement_line_width': 2,
            'measurement_text_color': '#0000FF',
            'measurement_text_size': 10,
            'measurement_text_font': 'Arial',
            'canvas_bg_color': '#808080',  # Gray
            'point_size': 4,
            'show_measurement_labels': True,
            'label_background': True,
            'label_bg_color': '#FFFFFF',
            'grid_enabled': False,
            'grid_color': '#CCCCCC',
            'grid_spacing': 50,
            'show_crosshair': True,
            'crosshair_color': '#00FF00',  # Green
            'crosshair_width': 1,
            'show_rulers': True,
            'ruler_color': '#000000',
            'ruler_bg_color': '#E0E0E0',
            'ruler_size': 30
        }
        
        self.load_settings()
        self.setup_ui()
        self.setup_menu()
        self.setup_keyboard_shortcuts()
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export Labelled Image", command=self.export_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Export Measurements (CSV)", command=self.export_measurements_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Measurements", command=self.clear_measurements, accelerator="Ctrl+C")
        edit_menu.add_command(label="Reset Calibration", command=self.reset_calibration, accelerator="Ctrl+R")
        edit_menu.add_command(label="Undo Last", command=self.undo_last_measurement, accelerator="Ctrl+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Customize Measurement", command=self.customize_selected_measurement)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in_keyboard, accelerator="+")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out_keyboard, accelerator="-")
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        view_menu.add_separator()
        self.show_crosshair_var = tk.BooleanVar(value=self.settings['show_crosshair'])
        view_menu.add_checkbutton(label="Show Crosshair", variable=self.show_crosshair_var,
                                  command=self.toggle_crosshair)
        self.show_rulers_var = tk.BooleanVar(value=self.settings['show_rulers'])
        view_menu.add_checkbutton(label="Show Rulers", variable=self.show_rulers_var,
                                  command=self.toggle_rulers)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self.open_settings_dialog, accelerator="Ctrl+,")
        settings_menu.add_command(label="Reset to Defaults", command=self.reset_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts, accelerator="F1")
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_ui(self):
        # Top control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Load image button
        ttk.Button(control_frame, text="Load Blueprint Image", 
                  command=self.load_image).pack(side=tk.LEFT, padx=5)
        
        # Mode indicator
        self.mode_label = ttk.Label(control_frame, 
                                    text="Mode: Calibration (Draw reference line)", 
                                    foreground="blue", font=("Arial", 10, "bold"))
        self.mode_label.pack(side=tk.LEFT, padx=20)
        
        # Zoom indicator
        self.zoom_label = ttk.Label(control_frame, 
                                    text="Zoom: 100%", 
                                    font=("Arial", 10))
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        
        # Clear measurements button
        ttk.Button(control_frame, text="Clear All Measurements", 
                  command=self.clear_measurements).pack(side=tk.LEFT, padx=5)
        
        # Reset calibration button
        ttk.Button(control_frame, text="Reset Calibration", 
                  command=self.reset_calibration).pack(side=tk.LEFT, padx=5)
        
        # Credit (top right)
        credit_label = ttk.Label(control_frame, text="Made with ❤ by Abdullah Noor", 
                                font=("Arial", 9, "italic"), foreground="gray")
        credit_label.pack(side=tk.RIGHT, padx=10)
        
        # Keyboard shortcuts button
        ttk.Button(control_frame, text="⌨ Shortcuts", 
                  command=self.show_shortcuts).pack(side=tk.RIGHT, padx=5)
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Canvas for image
        canvas_frame = ttk.Frame(main_container)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg=self.settings['canvas_bg_color'], cursor="cross")
        
        # Setup drag and drop
        if self.dnd_available:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind('<<Drop>>', self.on_drop)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, 
                                    command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                                    command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, 
                            yscrollcommand=v_scrollbar.set)
        
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_right_click)  # Right-click for measurement menu
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)  # Hide crosshair when leaving canvas
        self.canvas.bind("<Enter>", self.on_mouse_enter)  # Show crosshair when entering canvas
        # Bind mouse wheel for zoom (Windows and Linux)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        # For Linux
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        
        # Bind configure event to redraw rulers when canvas is resized/scrolled
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.selected_measurement_index = None
        self.crosshair_visible = False
        self.shift_pressed = False
        
        # Right side - Info panel
        info_frame = ttk.Frame(main_container, width=300)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        info_frame.pack_propagate(False)
        
        # Calibration section
        calib_frame = ttk.LabelFrame(info_frame, text="Calibration", padding="10")
        calib_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(calib_frame, text="Reference Distance:").pack(anchor=tk.W)
        
        distance_frame = ttk.Frame(calib_frame)
        distance_frame.pack(fill=tk.X, pady=5)
        
        self.distance_var = tk.StringVar(value="1.0")
        ttk.Entry(distance_frame, textvariable=self.distance_var, 
                 width=10).pack(side=tk.LEFT)
        
        self.unit_var = tk.StringVar(value="meters")
        unit_combo = ttk.Combobox(distance_frame, textvariable=self.unit_var, 
                                 values=["meters", "centimeters", "feet", "inches"], 
                                 width=10, state="readonly")
        unit_combo.pack(side=tk.LEFT, padx=5)
        
        self.calib_status = ttk.Label(calib_frame, text="Not calibrated", 
                                     foreground="red")
        self.calib_status.pack(anchor=tk.W, pady=5)
        
        # Measurements section
        measure_frame = ttk.LabelFrame(info_frame, text="Measurements", padding="10")
        measure_frame.pack(fill=tk.BOTH, expand=True)
        
        # Measurement display unit selector
        display_unit_frame = ttk.Frame(measure_frame)
        display_unit_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(display_unit_frame, text="Display in:").pack(side=tk.LEFT)
        self.display_unit_var = tk.StringVar(value="meters")
        display_unit_combo = ttk.Combobox(display_unit_frame, 
                                         textvariable=self.display_unit_var,
                                         values=["meters", "centimeters", "feet", "inches"],
                                         width=12, state="readonly")
        display_unit_combo.pack(side=tk.LEFT, padx=5)
        display_unit_combo.bind("<<ComboboxSelected>>", self.update_measurements_display)
        
        # Scrolled text for measurements
        text_frame = ttk.Frame(measure_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.measurements_text = tk.Text(text_frame, height=20, width=35, 
                                        yscrollcommand=scrollbar.set)
        self.measurements_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.measurements_text.yview)
        
        # Instructions
        dnd_text = "Drag & drop images here!" if self.dnd_available else ""
        instructions = f"""
Instructions:
1. Load a blueprint image {dnd_text}
2. Use mouse wheel to zoom in/out
3. Click two points to draw a reference line
4. Enter the actual distance
5. After calibration, draw lines to measure
6. Hold Shift for horizontal/vertical snap
7. All measurements auto-calculate!
        """
        ttk.Label(info_frame, text=instructions, justify=tk.LEFT, 
                 wraplength=280, font=("Arial", 9)).pack(side=tk.BOTTOM, pady=10)
    
    def load_image(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Select Blueprint Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                          ("All files", "*.*")]
            )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.image = self.original_image.copy()
                self.zoom_level = 1.0
                self.display_image()
                self.reset_calibration()
                messagebox.showinfo("Image Loaded", 
                                   "Image loaded successfully! Draw a reference line to calibrate.\n\nUse mouse wheel to zoom in/out!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def on_drop(self, event):
        """Handle drag and drop of files"""
        # Get the dropped file path
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            # Remove curly braces if present (Windows sometimes adds them)
            file_path = file_path.strip('{}')
            
            # Check if it's an image file
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif')
            if file_path.lower().endswith(valid_extensions):
                self.load_image(file_path)
            else:
                messagebox.showwarning("Invalid File", 
                                      "Please drop a valid image file (PNG, JPG, BMP, GIF, or TIFF).")
    
    def display_image(self, keep_view_position=False):
        if self.original_image:
            # Store current center position if needed
            if keep_view_position:
                old_center_x = self.canvas.canvasx(self.canvas.winfo_width() / 2)
                old_center_y = self.canvas.canvasy(self.canvas.winfo_height() / 2)
            
            # Get canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 600
            
            # Calculate base scaling to fit canvas (first time only)
            img_width, img_height = self.original_image.size
            if self.base_scale == 1.0:
                scale_w = canvas_width / img_width
                scale_h = canvas_height / img_height
                self.base_scale = min(scale_w, scale_h, 1.0)
            
            # Apply zoom to base scale
            final_scale = self.base_scale * self.zoom_level
            
            new_width = int(img_width * final_scale)
            new_height = int(img_height * final_scale)
            
            # Resize image
            display_img = self.original_image.resize((new_width, new_height), 
                                                     Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(display_img)
            
            # Store current canvas items
            saved_items = self.save_canvas_items()
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            
            # Configure scroll region
            self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
            
            # Draw rulers if enabled
            if self.settings['show_rulers']:
                self.draw_rulers()
            
            # Restore canvas items (measurements, calibration lines)
            self.restore_canvas_items(saved_items)
            
            # Update zoom label
            self.zoom_label.config(text=f"Zoom: {int(self.zoom_level * 100)}%")
            
            # Restore view position if zooming
            if keep_view_position:
                # Center on the same point
                new_center_x = old_center_x
                new_center_y = old_center_y
                
                # Calculate how to scroll to maintain position
                x_frac = new_center_x / new_width if new_width > 0 else 0.5
                y_frac = new_center_y / new_height if new_height > 0 else 0.5
                
                self.canvas.xview_moveto(max(0, x_frac - 0.5))
                self.canvas.yview_moveto(max(0, y_frac - 0.5))
    
    def draw_rulers(self):
        """Draw ruler markings on canvas edges"""
        # Clear existing rulers first
        self.canvas.delete("ruler")
        
        if not self.base_scale_factor:
            return
        
        scroll_region = self.canvas.cget("scrollregion")
        if not scroll_region:
            return
        
        x1, y1, x2, y2 = map(float, scroll_region.split())
        ruler_size = self.settings['ruler_size']
        
        # Get visible region
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        visible_x1 = self.canvas.canvasx(0)
        visible_x2 = self.canvas.canvasx(canvas_width)
        visible_y1 = self.canvas.canvasy(0)
        visible_y2 = self.canvas.canvasy(canvas_height)
        
        # Calculate tick spacing in pixels based on scale
        # Aim for ticks every 50-100 pixels
        unit_text = self.unit
        if self.base_scale_factor:
            # Calculate current scale factor based on zoom
            current_scale_factor = self.base_scale_factor * self.zoom_level
            # Try to get nice round numbers
            real_per_100px = 100 / current_scale_factor
            
            # Find nice tick spacing (1, 2, 5, 10, 20, 50, 100, etc.)
            nice_numbers = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
            tick_spacing_real = min(nice_numbers, key=lambda x: abs(x - real_per_100px))
            tick_spacing_px = tick_spacing_real * current_scale_factor
            
            # Draw horizontal ruler (top)
            x = 0
            tick_num = 0
            while x <= x2:
                if visible_x1 <= x <= visible_x2:
                    # Major tick every 5 intervals
                    is_major = (tick_num % 5 == 0)
                    tick_height = 15 if is_major else 8
                    
                    # Draw tick line on the image area
                    self.canvas.create_line(
                        x, y1, x, y1 + tick_height,
                        fill=self.settings['ruler_color'],
                        width=1,
                        tags="ruler"
                    )
                    
                    # Add label for major ticks
                    if is_major:
                        current_scale_factor = self.base_scale_factor * self.zoom_level
                        real_distance = x / current_scale_factor
                        self.canvas.create_text(
                            x, y1 + tick_height + 8,
                            text=f"{real_distance:.1f}",
                            fill=self.settings['ruler_color'],
                            font=("Arial", 7),
                            tags="ruler"
                        )
                
                x += tick_spacing_px
                tick_num += 1
            
            # Draw vertical ruler (left)
            y = 0
            tick_num = 0
            while y <= y2:
                if visible_y1 <= y <= visible_y2:
                    is_major = (tick_num % 5 == 0)
                    tick_width = 15 if is_major else 8
                    
                    # Draw tick line
                    self.canvas.create_line(
                        x1, y, x1 + tick_width, y,
                        fill=self.settings['ruler_color'],
                        width=1,
                        tags="ruler"
                    )
                    
                    # Add label for major ticks
                    if is_major:
                        current_scale_factor = self.base_scale_factor * self.zoom_level
                        real_distance = y / current_scale_factor
                        self.canvas.create_text(
                            x1 + tick_width + 12, y,
                            text=f"{real_distance:.1f}",
                            fill=self.settings['ruler_color'],
                            font=("Arial", 7),
                            angle=0,
                            tags="ruler"
                        )
                
                y += tick_spacing_px
                tick_num += 1
        
        # Keep rulers on top of image
        self.canvas.tag_raise("ruler")
    
    def save_canvas_items(self):
        """Save positions of all calibration and measurement items"""
        saved = {
            'calibration_points': self.calibration_points.copy(),
            'measurements': []
        }
        
        # Save measurement data
        for m in self.measurements:
            saved['measurements'].append({
                'points': m['points'].copy(),
                'distance': m['distance']
            })
        
        return saved
    
    def restore_canvas_items(self, saved_items):
        """Restore calibration and measurement lines after zoom"""
        if not saved_items:
            return
        
        # Restore calibration line
        if len(saved_items['calibration_points']) == 2:
            p1 = saved_items['calibration_points'][0]
            p2 = saved_items['calibration_points'][1]
            
            point_size = self.settings['point_size']
            # Draw points
            self.canvas.create_oval(p1[0]-point_size, p1[1]-point_size, 
                                   p1[0]+point_size, p1[1]+point_size, 
                                   fill=self.settings['calibration_point_color'], 
                                   outline=self.settings['calibration_point_color'], 
                                   tags="calibration")
            self.canvas.create_oval(p2[0]-point_size, p2[1]-point_size, 
                                   p2[0]+point_size, p2[1]+point_size, 
                                   fill=self.settings['calibration_point_color'], 
                                   outline=self.settings['calibration_point_color'], 
                                   tags="calibration")
            # Draw line
            self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                   fill=self.settings['calibration_line_color'], 
                                   width=self.settings['calibration_line_width'], 
                                   tags="calibration")
        
        # Restore measurements
        self.measurements = []
        for m_data in saved_items['measurements']:
            p1 = m_data['points'][0]
            p2 = m_data['points'][1]
            
            # Get custom colors if available, otherwise use defaults
            line_color = m_data.get('line_color', self.settings['measurement_line_color'])
            point_color = m_data.get('point_color', self.settings['measurement_point_color'])
            line_width = m_data.get('line_width', self.settings['measurement_line_width'])
            text_color = m_data.get('text_color', self.settings['measurement_text_color'])
            
            point_size = self.settings['point_size']
            # Draw points
            self.canvas.create_oval(p1[0]-point_size, p1[1]-point_size, 
                                   p1[0]+point_size, p1[1]+point_size,
                                   fill=point_color, outline=point_color, 
                                   tags="measurement")
            self.canvas.create_oval(p2[0]-point_size, p2[1]-point_size, 
                                   p2[0]+point_size, p2[1]+point_size,
                                   fill=point_color, outline=point_color, 
                                   tags="measurement")
            
            # Draw line
            line_id = self.canvas.create_line(p1[0], p1[1], p2[0], p2[1],
                                             fill=line_color, width=line_width, 
                                             tags="measurement")
            
            # Add measurement data
            measurement_obj = {
                'points': m_data['points'].copy(),
                'distance': m_data['distance'],
                'line_id': line_id,
                'line_color': line_color,
                'point_color': point_color,
                'line_width': line_width,
                'text_color': text_color
            }
            self.measurements.append(measurement_obj)
            
            # Draw label
            if self.settings['show_measurement_labels']:
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                display_distance = self.convert_unit(m_data['distance'], self.unit,
                                                     self.display_unit_var.get())
                text = f"{display_distance:.2f} {self.display_unit_var.get()}"
                
                if self.settings['label_background']:
                    # Create background for text
                    bbox_id = self.canvas.create_text(mid_x, mid_y - 10, text=text,
                                           fill=text_color, 
                                           font=(self.settings['measurement_text_font'], 
                                                self.settings['measurement_text_size'], "bold"),
                                           tags="measurement")
                    bbox = self.canvas.bbox(bbox_id)
                    if bbox:
                        self.canvas.create_rectangle(bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2,
                                                    fill=self.settings['label_bg_color'],
                                                    outline="", tags="measurement")
                        self.canvas.tag_raise(bbox_id)
                else:
                    self.canvas.create_text(mid_x, mid_y - 10, text=text,
                                           fill=text_color, 
                                           font=(self.settings['measurement_text_font'], 
                                                self.settings['measurement_text_size'], "bold"),
                                           tags="measurement")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom"""
        if not self.original_image:
            return
        
        # Get mouse position before zoom
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        
        # Determine zoom direction
        if event.num == 5 or event.delta < 0:  # Zoom out
            new_zoom = self.zoom_level - self.zoom_step
        else:  # Zoom in (event.num == 4 or event.delta > 0)
            new_zoom = self.zoom_level + self.zoom_step
        
        # Clamp zoom level
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if new_zoom != self.zoom_level:
            # Calculate the zoom factor
            zoom_factor = new_zoom / self.zoom_level
            
            # Update zoom level
            old_zoom = self.zoom_level
            self.zoom_level = new_zoom
            
            # Scale all canvas coordinates
            self.scale_canvas_items(zoom_factor)
            
            # Redraw the image
            self.display_image(keep_view_position=False)
            
            # Adjust scroll position to zoom towards mouse
            # Get new mouse position in canvas coordinates
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate the new position after zoom
            new_mouse_x = mouse_x * zoom_factor
            new_mouse_y = mouse_y * zoom_factor
            
            # Scroll to keep the mouse position roughly in the same place
            img_width = int(self.original_image.size[0] * self.base_scale * self.zoom_level)
            img_height = int(self.original_image.size[1] * self.base_scale * self.zoom_level)
            
            if img_width > canvas_width:
                x_pos = (new_mouse_x - event.x) / img_width
                self.canvas.xview_moveto(max(0, min(1, x_pos)))
            
            if img_height > canvas_height:
                y_pos = (new_mouse_y - event.y) / img_height
                self.canvas.yview_moveto(max(0, min(1, y_pos)))
            
            # Force redraw rulers after scroll adjustment
            if self.settings['show_rulers']:
                self.canvas.after(10, self.draw_rulers)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize/scroll events"""
        # Redraw rulers when canvas is scrolled or resized
        if self.settings['show_rulers'] and self.base_scale_factor and self.original_image:
            self.canvas.delete("ruler")
            self.draw_rulers()
    
    def scale_canvas_items(self, zoom_factor):
        """Scale all stored coordinates by zoom factor"""
        # Scale calibration points
        self.calibration_points = [
            (x * zoom_factor, y * zoom_factor) 
            for x, y in self.calibration_points
        ]
        
        # Scale current line points
        self.current_line_points = [
            (x * zoom_factor, y * zoom_factor)
            for x, y in self.current_line_points
        ]
        
        # Scale measurements
        for m in self.measurements:
            m['points'] = [
                (x * zoom_factor, y * zoom_factor)
                for x, y in m['points']
            ]
    
    def on_canvas_click(self, event):
        if not self.image:
            messagebox.showwarning("No Image", "Please load a blueprint image first!")
            return
        
        # Get canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.mode == "calibrate":
            # Apply snap if shift is pressed and we have a first point
            if self.shift_pressed and len(self.calibration_points) == 1:
                x, y = self.snap_to_axis(self.calibration_points[0], (x, y))
            
            self.calibration_points.append((x, y))
            
            point_size = self.settings['point_size']
            # Draw point
            self.canvas.create_oval(x-point_size, y-point_size, x+point_size, y+point_size, 
                                   fill=self.settings['calibration_point_color'], 
                                   outline=self.settings['calibration_point_color'], 
                                   tags="calibration")
            
            if len(self.calibration_points) == 2:
                # Draw calibration line
                self.canvas.create_line(
                    self.calibration_points[0][0], self.calibration_points[0][1],
                    self.calibration_points[1][0], self.calibration_points[1][1],
                    fill=self.settings['calibration_line_color'], 
                    width=self.settings['calibration_line_width'], 
                    tags="calibration"
                )
                
                # Show dialog to confirm distance
                self.confirm_calibration()
        
        elif self.mode == "measure":
            # Apply snap if shift is pressed and we have a first point
            if self.shift_pressed and len(self.current_line_points) == 1:
                x, y = self.snap_to_axis(self.current_line_points[0], (x, y))
            
            self.current_line_points.append((x, y))
            
            point_size = self.settings['point_size']
            # Draw point
            self.canvas.create_oval(x-point_size, y-point_size, x+point_size, y+point_size, 
                                   fill=self.settings['measurement_point_color'], 
                                   outline=self.settings['measurement_point_color'],
                                   tags="measurement")
            
            if len(self.current_line_points) == 2:
                # Draw measurement line
                line_id = self.canvas.create_line(
                    self.current_line_points[0][0], self.current_line_points[0][1],
                    self.current_line_points[1][0], self.current_line_points[1][1],
                    fill=self.settings['measurement_line_color'], 
                    width=self.settings['measurement_line_width'], 
                    tags="measurement"
                )
                
                # Calculate distance
                distance = self.calculate_distance(
                    self.current_line_points[0], 
                    self.current_line_points[1]
                )
                
                # Store measurement with custom color options
                self.measurements.append({
                    "points": self.current_line_points.copy(),
                    "distance": distance,
                    "line_id": line_id,
                    "line_color": self.settings['measurement_line_color'],
                    "point_color": self.settings['measurement_point_color'],
                    "line_width": self.settings['measurement_line_width'],
                    "text_color": self.settings['measurement_text_color']
                })
                
                # Display measurement on canvas
                if self.settings['show_measurement_labels']:
                    mid_x = (self.current_line_points[0][0] + self.current_line_points[1][0]) / 2
                    mid_y = (self.current_line_points[0][1] + self.current_line_points[1][1]) / 2
                    
                    display_distance = self.convert_unit(distance, self.unit, 
                                                         self.display_unit_var.get())
                    text = f"{display_distance:.2f} {self.display_unit_var.get()}"
                    
                    if self.settings['label_background']:
                        text_id = self.canvas.create_text(mid_x, mid_y - 10, text=text, 
                                           fill=self.settings['measurement_text_color'], 
                                           font=(self.settings['measurement_text_font'], 
                                                self.settings['measurement_text_size'], "bold"),
                                           tags="measurement")
                        bbox = self.canvas.bbox(text_id)
                        if bbox:
                            self.canvas.create_rectangle(bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2,
                                                        fill=self.settings['label_bg_color'],
                                                        outline="", tags="measurement")
                            self.canvas.tag_raise(text_id)
                    else:
                        self.canvas.create_text(mid_x, mid_y - 10, text=text, 
                                           fill=self.settings['measurement_text_color'], 
                                           font=(self.settings['measurement_text_font'], 
                                                self.settings['measurement_text_size'], "bold"),
                                           tags="measurement")
                
                # Update measurements display
                self.update_measurements_display()
                
                # Reset for next measurement
                self.current_line_points = []
    
    def on_mouse_move(self, event):
        # Update crosshair
        if self.settings['show_crosshair'] and self.crosshair_visible:
            self.draw_crosshair(event)
        
        # Update ruler coordinates display
        if self.settings['show_rulers']:
            self.update_ruler_coordinates(event)
        
        # Show preview line while drawing
        if self.mode == "calibrate" and len(self.calibration_points) == 1:
            self.canvas.delete("preview")
            self.canvas.delete("snap_indicator")
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Apply snap if shift is pressed
            if self.shift_pressed:
                x, y = self.snap_to_axis(self.calibration_points[0], (x, y))
                # Draw snap indicator
                self.draw_snap_indicator((x, y))
            
            self.canvas.create_line(
                self.calibration_points[0][0], self.calibration_points[0][1],
                x, y, fill=self.settings['calibration_line_color'], 
                width=1, dash=(4, 4), tags="preview"
            )
        
        elif self.mode == "measure" and len(self.current_line_points) == 1:
            self.canvas.delete("preview")
            self.canvas.delete("snap_indicator")
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Apply snap if shift is pressed
            if self.shift_pressed:
                x, y = self.snap_to_axis(self.current_line_points[0], (x, y))
                # Draw snap indicator
                self.draw_snap_indicator((x, y))
            
            self.canvas.create_line(
                self.current_line_points[0][0], self.current_line_points[0][1],
                x, y, fill=self.settings['measurement_line_color'], 
                width=1, dash=(4, 4), tags="preview"
            )
    
    def on_mouse_leave(self, event):
        """Hide crosshair when mouse leaves canvas"""
        self.crosshair_visible = False
        self.canvas.delete("crosshair")
        self.canvas.delete("ruler_coords")
        self.canvas.delete("snap_indicator")
    
    def on_mouse_enter(self, event):
        """Show crosshair when mouse enters canvas"""
        self.crosshair_visible = True
    
    def on_shift_press(self, event):
        """Handle Shift key press"""
        self.shift_pressed = True
    
    def on_shift_release(self, event):
        """Handle Shift key release"""
        self.shift_pressed = False
        self.canvas.delete("snap_indicator")
    
    def snap_to_axis(self, start_point, end_point):
        """Snap end point to horizontal or vertical axis relative to start point"""
        x1, y1 = start_point
        x2, y2 = end_point
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        # Snap to the axis with greater movement
        if dx > dy:
            # Snap to horizontal (keep x, set y to start y)
            return (x2, y1)
        else:
            # Snap to vertical (keep y, set x to start x)
            return (x1, y2)
    
    def draw_snap_indicator(self, point):
        """Draw a visual indicator that snapping is active"""
        x, y = point
        size = 6
        
        # Draw a small square indicator
        self.canvas.create_rectangle(
            x - size, y - size, x + size, y + size,
            outline="#FF00FF",  # Magenta
            width=2,
            tags="snap_indicator"
        )
        
        # Draw small text indicator
        self.canvas.create_text(
            x, y - 15,
            text="SNAP",
            fill="#FF00FF",
            font=("Arial", 8, "bold"),
            tags="snap_indicator"
        )
    
    def draw_crosshair(self, event):
        """Draw infinite crosshair lines"""
        self.canvas.delete("crosshair")
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Get scroll region (canvas bounds)
        scroll_region = self.canvas.cget("scrollregion")
        if scroll_region:
            x1, y1, x2, y2 = map(float, scroll_region.split())
        else:
            x1, y1 = 0, 0
            x2, y2 = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Draw horizontal line (infinite width)
        self.canvas.create_line(
            x1, y, x2, y,
            fill=self.settings['crosshair_color'],
            width=self.settings['crosshair_width'],
            tags="crosshair"
        )
        
        # Draw vertical line (infinite height)
        self.canvas.create_line(
            x, y1, x, y2,
            fill=self.settings['crosshair_color'],
            width=self.settings['crosshair_width'],
            tags="crosshair"
        )
        
        # Keep crosshair on top of image but below other elements
        self.canvas.tag_lower("crosshair")
        if self.canvas_image:
            self.canvas.tag_raise("crosshair", self.canvas_image)
    
    def update_ruler_coordinates(self, event):
        """Update coordinate display on rulers"""
        if not self.base_scale_factor or not self.settings['show_rulers']:
            return
        
        self.canvas.delete("ruler_coords")
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Calculate real-world coordinates if calibrated
        if self.base_scale_factor:
            # Calculate current scale factor based on zoom
            current_scale_factor = self.base_scale_factor * self.zoom_level
            # Distance from origin (0,0) in real units
            real_x = x / current_scale_factor
            real_y = y / current_scale_factor
            
            # Display coordinates
            coord_text_x = f"{real_x:.2f}"
            coord_text_y = f"{real_y:.2f}"
            
            # Show on rulers (in window coordinates)
            ruler_size = self.settings['ruler_size']
            
            # X coordinate on top ruler
            self.canvas.create_text(
                event.x, 10,
                text=coord_text_x,
                fill=self.settings['ruler_color'],
                font=("Arial", 8, "bold"),
                tags="ruler_coords"
            )
            
            # Y coordinate on left ruler  
            self.canvas.create_text(
                10, event.y,
                text=coord_text_y,
                fill=self.settings['ruler_color'],
                font=("Arial", 8, "bold"),
                tags="ruler_coords"
            )
    
    def on_right_click(self, event):
        """Handle right-click to select and customize measurements"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Find which measurement was clicked
        for i, measurement in enumerate(self.measurements):
            p1, p2 = measurement['points']
            # Check if click is near the line
            dist_to_line = self.point_to_line_distance((x, y), p1, p2)
            if dist_to_line < 10:  # 10 pixels threshold
                self.selected_measurement_index = i
                self.show_measurement_context_menu(event, i)
                break
    
    def point_to_line_distance(self, point, line_start, line_end):
        """Calculate perpendicular distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if line_length == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Calculate perpendicular distance
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_length ** 2)))
        projection_x = x1 + t * (x2 - x1)
        projection_y = y1 + t * (y2 - y1)
        
        return math.sqrt((px - projection_x)**2 + (py - projection_y)**2)
    
    def show_measurement_context_menu(self, event, index):
        """Show context menu for measurement customization"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"Customize Measurement #{index + 1}", 
                        command=lambda: self.customize_measurement(index))
        menu.add_command(label="Delete Measurement", 
                        command=lambda: self.delete_measurement(index))
        menu.tk_popup(event.x_root, event.y_root)
    
    def confirm_calibration(self):
        try:
            reference_distance = float(self.distance_var.get())
            if reference_distance <= 0:
                raise ValueError("Distance must be positive")
            
            # Calculate pixel distance at current zoom level
            pixel_distance = math.sqrt(
                (self.calibration_points[1][0] - self.calibration_points[0][0])**2 +
                (self.calibration_points[1][1] - self.calibration_points[0][1])**2
            )
            
            # Store the zoom level when calibration was done
            self.calibration_zoom_level = self.zoom_level
            
            # Calculate scale factor at current zoom (pixels per unit)
            self.scale_factor = pixel_distance / reference_distance
            
            # Calculate base scale factor (normalized to zoom level 1.0)
            # This is independent of zoom and represents the true pixel-to-unit ratio
            self.base_scale_factor = self.scale_factor / self.zoom_level
            
            self.unit = self.unit_var.get()
            
            # Update status
            self.calib_status.config(
                text=f"Calibrated: {reference_distance} {self.unit}",
                foreground="green"
            )
            
            # Switch to measurement mode
            self.mode = "measure"
            self.mode_label.config(
                text="Mode: Measurement (Draw lines to measure)",
                foreground="green"
            )
            
            messagebox.showinfo("Calibration Complete", 
                              "Calibration successful! Now you can draw lines to measure distances.")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter a valid positive number for distance!")
            self.reset_calibration()
    
    def calculate_distance(self, point1, point2):
        """Calculate real-world distance between two points"""
        if self.base_scale_factor is None:
            return 0
        
        # Calculate pixel distance at current zoom level
        pixel_distance = math.sqrt(
            (point2[0] - point1[0])**2 + (point2[1] - point1[1])**2
        )
        
        # Use base_scale_factor and adjust for current zoom
        # Since coordinates are scaled by zoom, we need to account for that
        current_scale_factor = self.base_scale_factor * self.zoom_level
        
        real_distance = pixel_distance / current_scale_factor
        return real_distance
    
    def convert_unit(self, value, from_unit, to_unit):
        """Convert between different units"""
        # Convert to meters first
        to_meters = {
            "meters": 1.0,
            "centimeters": 0.01,
            "feet": 0.3048,
            "inches": 0.0254
        }
        
        from_meters = {
            "meters": 1.0,
            "centimeters": 100.0,
            "feet": 3.28084,
            "inches": 39.3701
        }
        
        value_in_meters = value * to_meters.get(from_unit, 1.0)
        converted_value = value_in_meters * from_meters.get(to_unit, 1.0)
        
        return converted_value
    
    def update_measurements_display(self, event=None):
        """Update the measurements text display"""
        self.measurements_text.delete(1.0, tk.END)
        
        if not self.measurements:
            self.measurements_text.insert(tk.END, "No measurements yet.\n")
            return
        
        display_unit = self.display_unit_var.get()
        
        self.measurements_text.insert(tk.END, f"All measurements in {display_unit}:\n")
        self.measurements_text.insert(tk.END, "-" * 40 + "\n")
        
        for i, measurement in enumerate(self.measurements, 1):
            distance = self.convert_unit(measurement["distance"], self.unit, display_unit)
            self.measurements_text.insert(tk.END, f"{i}. {distance:.3f} {display_unit}\n")
        
        # Calculate total
        total = sum(m["distance"] for m in self.measurements)
        total_converted = self.convert_unit(total, self.unit, display_unit)
        
        self.measurements_text.insert(tk.END, "-" * 40 + "\n")
        self.measurements_text.insert(tk.END, f"Total: {total_converted:.3f} {display_unit}\n")
        
        # Redraw measurement labels with new unit
        self.canvas.delete("measurement_label")
        for measurement in self.measurements:
            mid_x = (measurement["points"][0][0] + measurement["points"][1][0]) / 2
            mid_y = (measurement["points"][0][1] + measurement["points"][1][1]) / 2
            
            display_distance = self.convert_unit(measurement["distance"], self.unit, display_unit)
            text = f"{display_distance:.2f} {display_unit}"
            
            # Remove old text tags and add new ones
            # Note: this is a simplified approach
    
    def clear_measurements(self):
        """Clear all measurements but keep calibration"""
        if messagebox.askyesno("Clear Measurements", 
                              "Are you sure you want to clear all measurements?"):
            self.measurements = []
            self.current_line_points = []
            self.canvas.delete("measurement")
            self.canvas.delete("preview")
            self.update_measurements_display()
    
    def reset_calibration(self):
        """Reset calibration and all measurements"""
        self.scale_factor = None
        self.base_scale_factor = None
        self.calibration_zoom_level = 1.0
        self.calibration_points = []
        self.current_line_points = []
        self.measurements = []
        self.mode = "calibrate"
        
        self.calib_status.config(text="Not calibrated", foreground="red")
        self.mode_label.config(
            text="Mode: Calibration (Draw reference line)",
            foreground="blue"
        )
        
        # Clear canvas drawings
        self.canvas.delete("calibration")
        self.canvas.delete("measurement")
        self.canvas.delete("preview")
        
        self.update_measurements_display()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Shift key for line snapping
        self.root.bind('<KeyPress-Shift_L>', self.on_shift_press)
        self.root.bind('<KeyPress-Shift_R>', self.on_shift_press)
        self.root.bind('<KeyRelease-Shift_L>', self.on_shift_release)
        self.root.bind('<KeyRelease-Shift_R>', self.on_shift_release)
        
        # File operations
        self.root.bind('<Control-o>', lambda e: self.load_image())
        self.root.bind('<Control-O>', lambda e: self.load_image())
        self.root.bind('<Control-s>', lambda e: self.export_image())
        self.root.bind('<Control-S>', lambda e: self.export_image())
        
        # Edit operations
        self.root.bind('<Control-r>', lambda e: self.reset_calibration())
        self.root.bind('<Control-R>', lambda e: self.reset_calibration())
        self.root.bind('<Control-c>', lambda e: self.clear_measurements())
        self.root.bind('<Control-C>', lambda e: self.clear_measurements())
        self.root.bind('<Delete>', lambda e: self.undo_last_measurement())
        self.root.bind('<BackSpace>', lambda e: self.undo_last_measurement())
        self.root.bind('<Control-z>', lambda e: self.undo_last_measurement())
        self.root.bind('<Control-Z>', lambda e: self.undo_last_measurement())
        
        # Zoom operations
        self.root.bind('<plus>', lambda e: self.zoom_in_keyboard())
        self.root.bind('<equal>', lambda e: self.zoom_in_keyboard())  # For keyboards where + is Shift+=
        self.root.bind('<KP_Add>', lambda e: self.zoom_in_keyboard())  # Numpad +
        self.root.bind('<minus>', lambda e: self.zoom_out_keyboard())
        self.root.bind('<underscore>', lambda e: self.zoom_out_keyboard())
        self.root.bind('<KP_Subtract>', lambda e: self.zoom_out_keyboard())  # Numpad -
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        self.root.bind('<Control-Key-0>', lambda e: self.reset_zoom())
        
        # Cancel operation
        self.root.bind('<Escape>', lambda e: self.cancel_current_operation())
        
        # Help
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
        
        # Settings
        self.root.bind('<Control-comma>', lambda e: self.open_settings_dialog())
        
        # Quit
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
    
    def zoom_in_keyboard(self):
        """Zoom in using keyboard"""
        if not self.original_image:
            return
        
        new_zoom = self.zoom_level + self.zoom_step
        new_zoom = min(self.max_zoom, new_zoom)
        
        if new_zoom != self.zoom_level:
            zoom_factor = new_zoom / self.zoom_level
            self.zoom_level = new_zoom
            self.scale_canvas_items(zoom_factor)
            self.display_image(keep_view_position=False)
            # Force redraw rulers
            if self.settings['show_rulers']:
                self.canvas.after(10, self.draw_rulers)
    
    def zoom_out_keyboard(self):
        """Zoom out using keyboard"""
        if not self.original_image:
            return
        
        new_zoom = self.zoom_level - self.zoom_step
        new_zoom = max(self.min_zoom, new_zoom)
        
        if new_zoom != self.zoom_level:
            zoom_factor = new_zoom / self.zoom_level
            self.zoom_level = new_zoom
            self.scale_canvas_items(zoom_factor)
            self.display_image(keep_view_position=False)
            # Force redraw rulers
            if self.settings['show_rulers']:
                self.canvas.after(10, self.draw_rulers)
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        if not self.original_image:
            return
        
        if self.zoom_level != 1.0:
            zoom_factor = 1.0 / self.zoom_level
            self.zoom_level = 1.0
            self.scale_canvas_items(zoom_factor)
            self.display_image(keep_view_position=False)
            # Force redraw rulers
            if self.settings['show_rulers']:
                self.canvas.after(10, self.draw_rulers)
    
    def undo_last_measurement(self):
        """Remove the last measurement"""
        if self.measurements:
            self.measurements.pop()
            # Redraw canvas
            if self.original_image:
                self.display_image(keep_view_position=False)
            self.update_measurements_display()
    
    def cancel_current_operation(self):
        """Cancel current drawing operation"""
        if self.mode == "calibrate" and self.calibration_points:
            self.calibration_points = []
            self.canvas.delete("calibration")
            self.canvas.delete("preview")
            self.canvas.delete("snap_indicator")
        elif self.mode == "measure" and self.current_line_points:
            self.current_line_points = []
            self.canvas.delete("preview")
            self.canvas.delete("snap_indicator")
            # Remove the last point if one was placed
            if self.original_image:
                self.display_image(keep_view_position=False)
    
    def show_shortcuts(self):
        """Display keyboard shortcuts dialog"""
        shortcuts_text = """KEYBOARD SHORTCUTS

FILE OPERATIONS:
  Ctrl+O          Load blueprint image
  Ctrl+S          Export labelled image

MEASUREMENTS:
  Ctrl+C          Clear all measurements
  Ctrl+Z / Delete Undo last measurement
  Escape          Cancel current operation
  Shift (hold)    Snap to horizontal/vertical

CALIBRATION:
  Ctrl+R          Reset calibration

ZOOM:
  + / =           Zoom in
  -               Zoom out
  Ctrl+0          Reset zoom to 100%
  Mouse Wheel     Zoom in/out

VIEW:
  Ctrl+,          Open preferences

OTHER:
  F1              Show this help
  Ctrl+Q          Quit application

TIPS:
• Click two points to draw lines
• Hold Shift while drawing for H/V snap
• Use zoom for precise markings
• Right-click lines to customize
• All measurements update automatically
        """
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def open_settings_dialog(self):
        """Open comprehensive settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Preferences")
        settings_window.geometry("600x700")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Colors tab
        colors_frame = ttk.Frame(notebook, padding=10)
        notebook.add(colors_frame, text="Colors")
        
        # Calibration colors
        calib_group = ttk.LabelFrame(colors_frame, text="Calibration", padding=10)
        calib_group.pack(fill=tk.X, pady=5)
        
        self.create_color_setting(calib_group, "Line Color:", 'calibration_line_color', 0)
        self.create_color_setting(calib_group, "Point Color:", 'calibration_point_color', 1)
        
        # Measurement colors
        measure_group = ttk.LabelFrame(colors_frame, text="Measurements", padding=10)
        measure_group.pack(fill=tk.X, pady=5)
        
        self.create_color_setting(measure_group, "Line Color:", 'measurement_line_color', 0)
        self.create_color_setting(measure_group, "Point Color:", 'measurement_point_color', 1)
        self.create_color_setting(measure_group, "Text Color:", 'measurement_text_color', 2)
        
        # Canvas colors
        canvas_group = ttk.LabelFrame(colors_frame, text="Canvas", padding=10)
        canvas_group.pack(fill=tk.X, pady=5)
        
        self.create_color_setting(canvas_group, "Background Color:", 'canvas_bg_color', 0)
        self.create_color_setting(canvas_group, "Label Background:", 'label_bg_color', 1)
        
        # Line Settings tab
        lines_frame = ttk.Frame(notebook, padding=10)
        notebook.add(lines_frame, text="Lines & Points")
        
        # Line widths
        ttk.Label(lines_frame, text="Calibration Line Width:").grid(row=0, column=0, sticky=tk.W, pady=5)
        calib_width = ttk.Spinbox(lines_frame, from_=1, to=10, width=10)
        calib_width.set(self.settings['calibration_line_width'])
        calib_width.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(lines_frame, text="Measurement Line Width:").grid(row=1, column=0, sticky=tk.W, pady=5)
        measure_width = ttk.Spinbox(lines_frame, from_=1, to=10, width=10)
        measure_width.set(self.settings['measurement_line_width'])
        measure_width.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(lines_frame, text="Point Size:").grid(row=2, column=0, sticky=tk.W, pady=5)
        point_size = ttk.Spinbox(lines_frame, from_=2, to=10, width=10)
        point_size.set(self.settings['point_size'])
        point_size.grid(row=2, column=1, padx=5, pady=5)
        
        # Text Settings tab
        text_frame = ttk.Frame(notebook, padding=10)
        notebook.add(text_frame, text="Text")
        
        ttk.Label(text_frame, text="Font:").grid(row=0, column=0, sticky=tk.W, pady=5)
        font_combo = ttk.Combobox(text_frame, values=["Arial", "Helvetica", "Times", "Courier"], 
                                 state="readonly", width=15)
        font_combo.set(self.settings['measurement_text_font'])
        font_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(text_frame, text="Font Size:").grid(row=1, column=0, sticky=tk.W, pady=5)
        font_size = ttk.Spinbox(text_frame, from_=6, to=24, width=10)
        font_size.set(self.settings['measurement_text_size'])
        font_size.grid(row=1, column=1, padx=5, pady=5)
        
        show_labels_var = tk.BooleanVar(value=self.settings['show_measurement_labels'])
        ttk.Checkbutton(text_frame, text="Show Measurement Labels", 
                       variable=show_labels_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        label_bg_var = tk.BooleanVar(value=self.settings['label_background'])
        ttk.Checkbutton(text_frame, text="Label Background", 
                       variable=label_bg_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Display Settings tab
        display_frame = ttk.Frame(notebook, padding=10)
        notebook.add(display_frame, text="Display")
        
        # Crosshair settings
        crosshair_group = ttk.LabelFrame(display_frame, text="Crosshair", padding=10)
        crosshair_group.pack(fill=tk.X, pady=5)
        
        show_crosshair_var = tk.BooleanVar(value=self.settings['show_crosshair'])
        ttk.Checkbutton(crosshair_group, text="Show Crosshair", 
                       variable=show_crosshair_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.create_color_setting(crosshair_group, "Crosshair Color:", 'crosshair_color', 1)
        
        ttk.Label(crosshair_group, text="Crosshair Width:").grid(row=2, column=0, sticky=tk.W, pady=5)
        crosshair_width = ttk.Spinbox(crosshair_group, from_=1, to=3, width=10)
        crosshair_width.set(self.settings['crosshair_width'])
        crosshair_width.grid(row=2, column=1, padx=5, pady=5)
        
        # Ruler settings
        ruler_group = ttk.LabelFrame(display_frame, text="Rulers", padding=10)
        ruler_group.pack(fill=tk.X, pady=5)
        
        show_rulers_var = tk.BooleanVar(value=self.settings['show_rulers'])
        ttk.Checkbutton(ruler_group, text="Show Rulers", 
                       variable=show_rulers_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.create_color_setting(ruler_group, "Ruler Color:", 'ruler_color', 1)
        
        # Save function
        def save_settings():
            self.settings['calibration_line_width'] = int(calib_width.get())
            self.settings['measurement_line_width'] = int(measure_width.get())
            self.settings['point_size'] = int(point_size.get())
            self.settings['measurement_text_font'] = font_combo.get()
            self.settings['measurement_text_size'] = int(font_size.get())
            self.settings['show_measurement_labels'] = show_labels_var.get()
            self.settings['label_background'] = label_bg_var.get()
            self.settings['show_crosshair'] = show_crosshair_var.get()
            self.settings['crosshair_width'] = int(crosshair_width.get())
            self.settings['show_rulers'] = show_rulers_var.get()
            
            # Update canvas background
            self.canvas.config(bg=self.settings['canvas_bg_color'])
            
            # Update menu checkboxes
            self.show_crosshair_var.set(self.settings['show_crosshair'])
            self.show_rulers_var.set(self.settings['show_rulers'])
            
            # Save to file
            self.save_settings()
            
            # Redraw everything
            if self.original_image:
                self.display_image(keep_view_position=False)
            
            settings_window.destroy()
            messagebox.showinfo("Settings Saved", "Settings have been saved and applied!")
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def create_color_setting(self, parent, label, setting_key, row):
        """Create a color picker setting row"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        
        color_display = tk.Canvas(parent, width=30, height=20, bg=self.settings[setting_key], 
                                 relief=tk.SUNKEN, bd=1)
        color_display.grid(row=row, column=1, padx=5, pady=5)
        
        def choose_color():
            color = colorchooser.askcolor(initialcolor=self.settings[setting_key], 
                                         title=f"Choose {label}")
            if color[1]:
                self.settings[setting_key] = color[1]
                color_display.config(bg=color[1])
        
        ttk.Button(parent, text="Choose...", command=choose_color).grid(row=row, column=2, padx=5, pady=5)
    
    def customize_measurement(self, index):
        """Customize a specific measurement"""
        if index >= len(self.measurements):
            return
        
        measurement = self.measurements[index]
        
        custom_window = tk.Toplevel(self.root)
        custom_window.title(f"Customize Measurement #{index + 1}")
        custom_window.geometry("400x300")
        custom_window.transient(self.root)
        
        frame = ttk.Frame(custom_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Line color
        ttk.Label(frame, text="Line Color:").grid(row=0, column=0, sticky=tk.W, pady=10)
        line_color_canvas = tk.Canvas(frame, width=40, height=25, 
                                      bg=measurement.get('line_color', self.settings['measurement_line_color']),
                                      relief=tk.SUNKEN, bd=1)
        line_color_canvas.grid(row=0, column=1, padx=10)
        
        def choose_line_color():
            color = colorchooser.askcolor(initialcolor=measurement.get('line_color', '#0000FF'))
            if color[1]:
                measurement['line_color'] = color[1]
                line_color_canvas.config(bg=color[1])
        
        ttk.Button(frame, text="Choose", command=choose_line_color).grid(row=0, column=2)
        
        # Point color
        ttk.Label(frame, text="Point Color:").grid(row=1, column=0, sticky=tk.W, pady=10)
        point_color_canvas = tk.Canvas(frame, width=40, height=25,
                                       bg=measurement.get('point_color', self.settings['measurement_point_color']),
                                       relief=tk.SUNKEN, bd=1)
        point_color_canvas.grid(row=1, column=1, padx=10)
        
        def choose_point_color():
            color = colorchooser.askcolor(initialcolor=measurement.get('point_color', '#0000FF'))
            if color[1]:
                measurement['point_color'] = color[1]
                point_color_canvas.config(bg=color[1])
        
        ttk.Button(frame, text="Choose", command=choose_point_color).grid(row=1, column=2)
        
        # Text color
        ttk.Label(frame, text="Text Color:").grid(row=2, column=0, sticky=tk.W, pady=10)
        text_color_canvas = tk.Canvas(frame, width=40, height=25,
                                      bg=measurement.get('text_color', self.settings['measurement_text_color']),
                                      relief=tk.SUNKEN, bd=1)
        text_color_canvas.grid(row=2, column=1, padx=10)
        
        def choose_text_color():
            color = colorchooser.askcolor(initialcolor=measurement.get('text_color', '#0000FF'))
            if color[1]:
                measurement['text_color'] = color[1]
                text_color_canvas.config(bg=color[1])
        
        ttk.Button(frame, text="Choose", command=choose_text_color).grid(row=2, column=2)
        
        # Line width
        ttk.Label(frame, text="Line Width:").grid(row=3, column=0, sticky=tk.W, pady=10)
        width_spinbox = ttk.Spinbox(frame, from_=1, to=10, width=10)
        width_spinbox.set(measurement.get('line_width', 2))
        width_spinbox.grid(row=3, column=1, padx=10)
        
        # Apply button
        def apply_customization():
            measurement['line_width'] = int(width_spinbox.get())
            custom_window.destroy()
            # Redraw
            if self.original_image:
                self.display_image(keep_view_position=False)
        
        button_frame = ttk.Frame(custom_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=apply_customization).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=custom_window.destroy).pack(side=tk.RIGHT)
    
    def customize_selected_measurement(self):
        """Customize the selected measurement"""
        if self.selected_measurement_index is not None and self.selected_measurement_index < len(self.measurements):
            self.customize_measurement(self.selected_measurement_index)
        else:
            messagebox.showinfo("No Selection", 
                              "Right-click on a measurement line to select it for customization.")
    
    def delete_measurement(self, index):
        """Delete a specific measurement"""
        if index < len(self.measurements):
            del self.measurements[index]
            if self.original_image:
                self.display_image(keep_view_position=False)
            self.update_measurements_display()
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = os.path.join(os.path.dirname(__file__), 'blueprint_settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Update settings with saved values
                    self.settings.update(saved_settings)
            except Exception as e:
                print(f"Could not load settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = os.path.join(os.path.dirname(__file__), 'blueprint_settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Could not save settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to defaults?"):
            self.settings = {
                'calibration_line_color': '#FF0000',
                'calibration_point_color': '#FF0000',
                'calibration_line_width': 2,
                'measurement_line_color': '#0000FF',
                'measurement_point_color': '#0000FF',
                'measurement_line_width': 2,
                'measurement_text_color': '#0000FF',
                'measurement_text_size': 10,
                'measurement_text_font': 'Arial',
                'canvas_bg_color': '#808080',
                'point_size': 4,
                'show_measurement_labels': True,
                'label_background': True,
                'label_bg_color': '#FFFFFF',
                'grid_enabled': False,
                'grid_color': '#CCCCCC',
                'grid_spacing': 50,
                'show_crosshair': True,
                'crosshair_color': '#00FF00',
                'crosshair_width': 1,
                'show_rulers': True,
                'ruler_color': '#000000',
                'ruler_bg_color': '#E0E0E0',
                'ruler_size': 30
            }
            self.save_settings()
            self.canvas.config(bg=self.settings['canvas_bg_color'])
            self.show_crosshair_var.set(self.settings['show_crosshair'])
            self.show_rulers_var.set(self.settings['show_rulers'])
            if self.original_image:
                self.display_image(keep_view_position=False)
            messagebox.showinfo("Reset Complete", "Settings have been reset to defaults!")
    
    def toggle_crosshair(self):
        """Toggle crosshair visibility"""
        self.settings['show_crosshair'] = self.show_crosshair_var.get()
        if not self.settings['show_crosshair']:
            self.canvas.delete("crosshair")
            self.canvas.delete("ruler_coords")
        self.save_settings()
    
    def toggle_rulers(self):
        """Toggle ruler visibility"""
        self.settings['show_rulers'] = self.show_rulers_var.get()
        if self.original_image:
            self.display_image(keep_view_position=False)
        self.save_settings()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Blueprint Measurement Tool
Version 2.0

A powerful tool for measuring distances on blueprint images.

Features:
• Drag & Drop image loading
• Zoom and pan
• Custom calibration
• Multiple measurements
• Full color customization
• Per-measurement styling
• Export labelled images
• CSV export of measurements

Made with ❤ by Abdullah Noor
"""
        messagebox.showinfo("About", about_text)
    
    def export_image(self):
        """Export the current view with all measurements as an image"""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please load an image first!")
            return
        
        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            title="Export Labelled Image",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("JPEG Image", "*.jpeg"),
                ("TIFF Image", "*.tiff"),
                ("BMP Image", "*.bmp"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Create a copy of the original image at current zoom
            img_width, img_height = self.original_image.size
            final_scale = self.base_scale * self.zoom_level
            export_width = int(img_width * final_scale)
            export_height = int(img_height * final_scale)
            
            # Resize the original image to current zoom level
            export_image = self.original_image.resize((export_width, export_height), 
                                                      Image.Resampling.LANCZOS)
            
            # Create a drawing context
            draw = ImageDraw.Draw(export_image)
            
            # Try to load a font, fallback to default if not available
            try:
                font_size = self.settings['measurement_text_size']
                font = ImageFont.truetype("arial.ttf", font_size)
                small_font = ImageFont.truetype("arial.ttf", 8)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw calibration line if present
            if len(self.calibration_points) == 2:
                p1 = self.calibration_points[0]
                p2 = self.calibration_points[1]
                
                # Draw line
                draw.line([p1, p2], 
                         fill=self.settings['calibration_line_color'],
                         width=self.settings['calibration_line_width'])
                
                # Draw points
                point_size = self.settings['point_size']
                draw.ellipse([p1[0]-point_size, p1[1]-point_size, 
                             p1[0]+point_size, p1[1]+point_size],
                            fill=self.settings['calibration_point_color'])
                draw.ellipse([p2[0]-point_size, p2[1]-point_size, 
                             p2[0]+point_size, p2[1]+point_size],
                            fill=self.settings['calibration_point_color'])
            
            # Draw all measurements
            for i, measurement in enumerate(self.measurements):
                p1, p2 = measurement['points']
                
                line_color = measurement.get('line_color', self.settings['measurement_line_color'])
                point_color = measurement.get('point_color', self.settings['measurement_point_color'])
                line_width = measurement.get('line_width', self.settings['measurement_line_width'])
                text_color = measurement.get('text_color', self.settings['measurement_text_color'])
                
                # Draw line
                draw.line([p1, p2], fill=line_color, width=line_width)
                
                # Draw points
                point_size = self.settings['point_size']
                draw.ellipse([p1[0]-point_size, p1[1]-point_size, 
                             p1[0]+point_size, p1[1]+point_size],
                            fill=point_color)
                draw.ellipse([p2[0]-point_size, p2[1]-point_size, 
                             p2[0]+point_size, p2[1]+point_size],
                            fill=point_color)
                
                # Draw label if enabled
                if self.settings['show_measurement_labels']:
                    mid_x = (p1[0] + p2[0]) / 2
                    mid_y = (p1[1] + p2[1]) / 2
                    
                    display_distance = self.convert_unit(measurement['distance'], 
                                                        self.unit, 
                                                        self.display_unit_var.get())
                    text = f"{display_distance:.2f} {self.display_unit_var.get()}"
                    
                    # Get text bounding box
                    bbox = draw.textbbox((mid_x, mid_y - 10), text, font=font)
                    
                    # Draw background if enabled
                    if self.settings['label_background']:
                        padding = 2
                        draw.rectangle([bbox[0]-padding, bbox[1]-padding, 
                                      bbox[2]+padding, bbox[3]+padding],
                                     fill=self.settings['label_bg_color'])
                    
                    # Draw text
                    draw.text((mid_x, mid_y - 10), text, 
                             fill=text_color, font=font, anchor="mm")
            
            # Draw rulers if enabled
            if self.settings['show_rulers'] and self.base_scale_factor:
                self.draw_rulers_on_image(draw, export_width, export_height, small_font)
            
            # Add watermark/info
            info_text = f"Blueprint Measurement Tool | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            if self.base_scale_factor:
                info_text += f" | Unit: {self.unit} | Zoom: {int(self.zoom_level * 100)}%"
            
            # Draw info at bottom
            info_bbox = draw.textbbox((10, export_height - 20), info_text, font=small_font)
            draw.rectangle([info_bbox[0]-2, info_bbox[1]-2, 
                          info_bbox[2]+2, info_bbox[3]+2],
                         fill='white')
            draw.text((10, export_height - 20), info_text, 
                     fill='black', font=small_font)
            
            # Save the image
            export_image.save(file_path)
            messagebox.showinfo("Export Successful", 
                              f"Labelled image saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export image:\n{str(e)}")
    
    def draw_rulers_on_image(self, draw, width, height, font):
        """Draw ruler markings on the exported image"""
        if not self.base_scale_factor:
            return
        
        current_scale_factor = self.base_scale_factor * self.zoom_level
        real_per_100px = 100 / current_scale_factor
        
        # Find nice tick spacing
        nice_numbers = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
        tick_spacing_real = min(nice_numbers, key=lambda x: abs(x - real_per_100px))
        tick_spacing_px = tick_spacing_real * current_scale_factor
        
        ruler_color = self.settings['ruler_color']
        
        # Draw horizontal ruler marks (top)
        x = 0
        tick_num = 0
        while x <= width:
            is_major = (tick_num % 5 == 0)
            tick_height = 15 if is_major else 8
            
            draw.line([(x, 0), (x, tick_height)], fill=ruler_color, width=1)
            
            if is_major:
                real_distance = x / current_scale_factor
                draw.text((x, tick_height + 2), f"{real_distance:.1f}", 
                         fill=ruler_color, font=font, anchor="mt")
            
            x += tick_spacing_px
            tick_num += 1
        
        # Draw vertical ruler marks (left)
        y = 0
        tick_num = 0
        while y <= height:
            is_major = (tick_num % 5 == 0)
            tick_width = 15 if is_major else 8
            
            draw.line([(0, y), (tick_width, y)], fill=ruler_color, width=1)
            
            if is_major and y > 20:  # Avoid overlap with horizontal ruler
                real_distance = y / current_scale_factor
                draw.text((tick_width + 2, y), f"{real_distance:.1f}", 
                         fill=ruler_color, font=font, anchor="lm")
            
            y += tick_spacing_px
            tick_num += 1
    
    def export_measurements_csv(self):
        """Export measurements to a CSV file"""
        if not self.measurements:
            messagebox.showwarning("No Measurements", "No measurements to export!")
            return
        
        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            title="Export Measurements CSV",
            defaultextension=".csv",
            filetypes=[
                ("CSV File", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Measurement #',
                    f'Distance ({self.display_unit_var.get()})',
                    'Start X (px)',
                    'Start Y (px)',
                    'End X (px)',
                    'End Y (px)',
                    'Line Color',
                    'Line Width'
                ])
                
                # Write measurements
                for i, measurement in enumerate(self.measurements, 1):
                    distance = self.convert_unit(measurement['distance'], 
                                                self.unit, 
                                                self.display_unit_var.get())
                    p1, p2 = measurement['points']
                    
                    writer.writerow([
                        i,
                        f"{distance:.3f}",
                        f"{p1[0]:.1f}",
                        f"{p1[1]:.1f}",
                        f"{p2[0]:.1f}",
                        f"{p2[1]:.1f}",
                        measurement.get('line_color', self.settings['measurement_line_color']),
                        measurement.get('line_width', self.settings['measurement_line_width'])
                    ])
                
                # Write summary
                writer.writerow([])
                writer.writerow(['Summary'])
                writer.writerow(['Total Measurements', len(self.measurements)])
                
                total = sum(m['distance'] for m in self.measurements)
                total_converted = self.convert_unit(total, self.unit, self.display_unit_var.get())
                writer.writerow(['Total Distance', f"{total_converted:.3f} {self.display_unit_var.get()}"])
                
                writer.writerow(['Calibration Unit', self.unit])
                writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            
            messagebox.showinfo("Export Successful", 
                              f"Measurements saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")


def main():
    # Use TkinterDnD root if available, otherwise regular Tk
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        print("Warning: tkinterdnd2 not installed. Drag and drop will not be available.")
        print("Install it with: pip install tkinterdnd2")
    
    app = BlueprintMeasurementTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()

