"""
Quick test - Open Container Image Viewer directly
Chạy file này để mở Image Viewer ngay
"""

import sys
import os

# Add path
sys.path.insert(0, os.path.dirname(__file__))

# Import viewer
from container_image_viewer import ContainerImageViewer

# Create and show viewer
viewer = ContainerImageViewer(parent=None, log_callback=None)
viewer.container_var.set('spark-worker')
viewer.path_var.set('/tmp/demo_chart.png')
viewer.show()
