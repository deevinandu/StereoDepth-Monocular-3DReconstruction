import cv2
import numpy as np
import matplotlib
try:
    matplotlib.use('TkAgg')
except Exception:
    pass
import matplotlib.pyplot as plt
import open3d as o3d

def load_image(path, target_width=None):
    """Loads an image and optionally resizes it."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {path}")
    
    if target_width:
        h, w = img.shape[:2]
        scale = target_width / w
        new_dim = (target_width, int(h * scale))
        img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)
        
    return img

def save_point_cloud(depth_map, img_rgb, focal_length_px, filename):
    """Generates a PLY 3D point cloud file."""
    print(f"[INFO] Generating 3D Point Cloud -> {filename}")
    h, w = depth_map.shape
    i, j = np.meshgrid(np.arange(w), np.arange(h))
    
    # Mask valid points (exclude infinite/zero depth and extremely far points)
    mask = (depth_map > 0) & (depth_map < 1000) 
    
    z = depth_map[mask]
    x = (i[mask] - w/2) * z / focal_length_px
    y = (j[mask] - h/2) * z / focal_length_px
    
    colors = img_rgb[mask]
    
    header = f"""ply
format ascii 1.0
element vertex {len(z)}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""
    with open(filename, 'w') as f:
        f.write(header)
        for xi, yi, zi, c in zip(x, y, z, colors):
            f.write(f"{xi:.2f} {yi:.2f} {zi:.2f} {c[0]} {c[1]} {c[2]}\n")


def create_point_cloud_data(depth_map, img_rgb, focal_length_px):
    """Creates point cloud data arrays for visualization."""
    h, w = depth_map.shape
    i, j = np.meshgrid(np.arange(w), np.arange(h))
    
    # Mask valid points
    mask = (depth_map > 0) & (depth_map < 1000)
    
    z = depth_map[mask]
    x = (i[mask] - w/2) * z / focal_length_px
    y = (j[mask] - h/2) * z / focal_length_px
    
    # Stack coordinates
    points = np.vstack((x, y, z)).T
    
    # Normalize colors to 0-1 range for Open3D
    colors = img_rgb[mask].astype(np.float64) / 255.0
    
    return points, colors


def view_interactive_pointcloud(depth_map, img_rgb, focal_length_px):
    """
    Opens an interactive 3D point cloud viewer using Open3D.
    Controls:
    - Left mouse: Rotate
    - Scroll: Zoom
    - Middle mouse / Shift+Left: Pan
    - R: Reset view
    - Q: Quit
    """
    print("[INFO] Opening interactive 3D point cloud viewer...")
    print("       Controls: Left-drag=Rotate, Scroll=Zoom, Middle-drag=Pan, R=Reset, Q=Quit")
    
    points, colors = create_point_cloud_data(depth_map, img_rgb, focal_length_px)
    
    # Create Open3D point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    
    # Flip Y axis for correct orientation (image coordinates to 3D)
    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
    
    # Visualize
    o3d.visualization.draw_geometries(
        [pcd],
        window_name="Interactive 3D Point Cloud",
        width=1280,
        height=720,
        point_show_normal=False
    )


def visualize_results_interactive(img_l, disparity, depth_map):
    """
    Visualizes the results with interactive depth hover display.
    Hover over the depth map to see depth values.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    
    # Left image
    ax1 = axes[0]
    ax1.imshow(cv2.cvtColor(img_l, cv2.COLOR_BGR2RGB))
    ax1.set_title("Left View")
    ax1.axis('off')
    
    # Disparity map
    ax2 = axes[1]
    ax2.imshow(disparity, cmap='plasma')
    ax2.set_title("Disparity Map (WLS Filtered)")
    ax2.axis('off')
    
    # Depth map with hover
    ax3 = axes[2]
    depth_img = ax3.imshow(depth_map, cmap='magma_r', vmin=0, vmax=300)
    plt.colorbar(depth_img, ax=ax3, label='Depth (cm)')
    ax3.set_title("Estimated Depth (hover for values)")
    ax3.axis('off')
    
    # Create annotation for depth display
    annot = ax3.annotate(
        "", xy=(0, 0), xytext=(20, 20),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.9),
        fontsize=10,
        fontweight='bold'
    )
    annot.set_visible(False)
    
    def on_hover(event):
        """Handle mouse hover to display depth values."""
        if event.inaxes == ax3:
            x, y = int(event.xdata), int(event.ydata)
            if 0 <= x < depth_map.shape[1] and 0 <= y < depth_map.shape[0]:
                depth_val = depth_map[y, x]
                if depth_val > 0 and depth_val < 1000:
                    annot.xy = (x, y)
                    annot.set_text(f"Depth: {depth_val:.1f} cm")
                    annot.set_visible(True)
                else:
                    annot.set_text("Depth: Invalid")
                    annot.set_visible(True)
                fig.canvas.draw_idle()
        else:
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()
    
    # Connect hover event
    fig.canvas.mpl_connect("motion_notify_event", on_hover)
    
    plt.tight_layout()
    plt.show()


def visualize_results(img_l, disparity, depth_map):
    """Visualizes the rectification, disparity, and depth (legacy non-interactive)."""
    plt.figure(figsize=(14, 5))
    
    plt.subplot(131)
    plt.imshow(cv2.cvtColor(img_l, cv2.COLOR_BGR2RGB))
    plt.title("Left View")
    plt.axis('off')

    plt.subplot(132)
    plt.imshow(disparity, cmap='plasma')
    plt.title("Disparity Map (WLS Filtered)")
    plt.axis('off')

    plt.subplot(133)
    plt.imshow(depth_map, cmap='magma_r', vmin=0, vmax=300)
    plt.colorbar(label='Depth (cm)')
    plt.title("Estimated Depth")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()