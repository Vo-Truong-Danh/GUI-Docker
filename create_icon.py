"""
Auto-generate icon for Spark Runner GUI
Creates a professional-looking icon with Spark theme
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_spark_icon():
    """Create Spark Runner GUI icon"""
    size = 256
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))  # Transparent
    draw = ImageDraw.Draw(img)
    
    # Draw circular background with gradient effect
    center = size // 2
    
    # Outer glow (dark blue)
    for i in range(10):
        alpha = int(50 * (1 - i/10))
        radius = center - 10 + i * 2
        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill=(9, 105, 218, alpha)
        )
    
    # Main circle (dark background)
    main_radius = center - 20
    draw.ellipse(
        [center - main_radius, center - main_radius, center + main_radius, center + main_radius],
        fill=(15, 23, 42, 255)
    )
    
    # Inner gradient circle (Spark color)
    for i in range(main_radius - 30, 0, -3):
        ratio = i / (main_radius - 30)
        r = int(255 * ratio)
        g = int(107 * ratio)
        b = 0
        alpha = int(255 * (1 - ratio * 0.5))
        draw.ellipse(
            [center - i, center - i, center + i, center + i],
            fill=(r, g, b, alpha)
        )
    
    # Draw "S" letter for Spark
    try:
        # Try multiple font options
        font_options = [
            "C:\\Windows\\Fonts\\arialbd.ttf",  # Arial Bold
            "C:\\Windows\\Fonts\\calibrib.ttf",  # Calibri Bold
            "C:\\Windows\\Fonts\\seguisb.ttf",  # Segoe UI Semibold
            "arial.ttf",
            "calibri.ttf"
        ]
        font = None
        for font_path in font_options:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 140)
                break
        if font is None:
            font = ImageFont.load_default()
    except Exception as e:
        print(f"⚠️ Font loading warning: {e}")
        font = ImageFont.load_default()
    
    # Draw "S"
    text = "S"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 15
    
    # Draw shadow (multiple layers for depth)
    for offset in range(5, 0, -1):
        alpha = int(100 * (offset / 5))
        draw.text((text_x + offset, text_y + offset), text, font=font, fill=(0, 0, 0, alpha))
    
    # Draw main text (white with slight gradient)
    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
    
    # Add small spark/lightning effect
    spark_points = [
        (center + 60, center - 50),
        (center + 50, center - 30),
        (center + 65, center - 30),
        (center + 55, center - 10)
    ]
    draw.polygon(spark_points, fill=(255, 215, 0, 255))  # Gold
    
    # Save as ICO with multiple sizes
    icon_path = 'icon.ico'
    img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"✅ Icon created: {icon_path}")
    
    # Save preview as PNG
    preview_path = 'icon_preview.png'
    img.save(preview_path)
    print(f"✅ Preview saved: {preview_path}")
    
    # Create smaller preview for documentation
    small_preview = img.resize((64, 64), Image.Resampling.LANCZOS)
    small_preview.save('icon_small.png')
    print(f"✅ Small preview saved: icon_small.png")
    
    return icon_path

def main():
    """Main entry point"""
    print("🎨 Creating Spark Runner GUI Icon...")
    print("-" * 50)
    
    try:
        icon_path = create_spark_icon()
        print("-" * 50)
        print("✨ Icon creation complete!")
        print(f"\n📁 Files created:")
        print(f"   - {icon_path} (Main icon file)")
        print(f"   - icon_preview.png (Full size preview)")
        print(f"   - icon_small.png (Small preview)")
        print(f"\n📝 Next steps:")
        print(f"   1. Check icon_preview.png to see the icon")
        print(f"   2. Run: .\\build.bat (icon will be included automatically)")
        print(f"   3. Check dist\\SparkRunnerGUI.exe for the icon")
        
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
