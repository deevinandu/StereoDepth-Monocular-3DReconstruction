from src import config
from src.core import StereoPipeline
from src.utils import (
    load_image, 
    save_point_cloud, 
    visualize_results_interactive,
    view_interactive_pointcloud
)
import cv2

# Hardcoded image paths (project root directory)
# Hardcoded image paths (project root directory)
LEFT_IMAGE_PATH = r"inputs/left_15.jpeg"
RIGHT_IMAGE_PATH = r"inputs/right.jpeg"
OUTPUT_PLY_PATH = r"outputs/output.ply"


def main():
    # Initialize Pipeline
    pipeline = StereoPipeline(
        focal_length_mm=config.FOCAL_LENGTH_MM,
        sensor_width_mm=config.SENSOR_WIDTH_MM,
        baseline_cm=config.BASELINE_CM,
        target_width=config.TARGET_WIDTH
    )

    # Load Images
    imgL = load_image(LEFT_IMAGE_PATH, config.TARGET_WIDTH)
    imgR = load_image(RIGHT_IMAGE_PATH, config.TARGET_WIDTH)

    # Rectify (skip if images are already properly aligned)
    if config.SKIP_RECTIFICATION:
        print("[INFO] Skipping rectification (images assumed to be pre-aligned)")
    else:
        imgL, imgR = pipeline.rectify_images(imgL, imgR)

    # Compute Disparity
    disparity = pipeline.compute_disparity(
        imgL, imgR, 
        num_disp=config.SGBM_NUM_DISPARITIES, 
        block_size=config.SGBM_BLOCK_SIZE,
        wls_lambda=config.WLS_LAMBDA,
        wls_sigma=config.WLS_SIGMA
    )

    # Compute Depth
    depth_map = pipeline.calculate_depth(disparity)

    # Save Point Cloud to PLY file
    save_point_cloud(
        depth_map, 
        cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB), 
        pipeline.f_pixel, 
        OUTPUT_PLY_PATH
    )

    # Visualize with interactive depth hover
    visualize_results_interactive(imgL, disparity, depth_map)

    # Open interactive 3D point cloud viewer (zoom, pan, tilt)
    view_interactive_pointcloud(
        depth_map, 
        cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB), 
        pipeline.f_pixel
    )


if __name__ == "__main__":
    main()