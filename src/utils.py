import cv2
import numpy as np
import matplotlib.pyplot as plt

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

def visualize_results(img_l, disparity, depth_map):
    """Visualizes the rectification, disparity, and depth."""
    plt.figure(figsize=(14, 5))
    
    plt.subplot(131)
    plt.imshow(cv2.cvtColor(img_l, cv2.COLOR_BGR2RGB))
    plt.title("Rectified Left View")
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