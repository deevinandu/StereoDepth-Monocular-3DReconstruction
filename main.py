import argparse
from src import config
from src.core import StereoPipeline
from src.utils import load_image, visualize_results, save_point_cloud
import cv2

def main(left_path, right_path, output_ply):
    # Initialize Pipeline
    pipeline = StereoPipeline(
        focal_length_mm=config.FOCAL_LENGTH_MM,
        sensor_width_mm=config.SENSOR_WIDTH_MM,
        baseline_cm=config.BASELINE_CM,
        target_width=config.TARGET_WIDTH
    )

    # Load Images
    imgL = load_image(left_path, config.TARGET_WIDTH)
    imgR = load_image(right_path, config.TARGET_WIDTH)

    # Rectify
    imgL, imgR = pipeline.rectify_images(imgL, imgR)

    # Compute Disparity
    disparity = pipeline.compute_disparity(
        imgL, imgR, 
        num_disp=config.SGBM_NUM_DISPARITIES, 
        block_size=config.SGBM_BLOCK_SIZE
    )

    # Compute Depth
    depth_map = pipeline.calculate_depth(disparity)

    # Save Point Cloud
    save_point_cloud(
        depth_map, 
        cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB), 
        pipeline.f_pixel, 
        output_ply
    )

    # Visualize
    visualize_results(imgL, disparity, depth_map)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stereo Depth Estimation Engine")
    parser.add_argument("--left", required=True, help="Path to left image")
    parser.add_argument("--right", required=True, help="Path to right image")
    parser.add_argument("--out", default="output.ply", help="Output filename for 3D cloud")
    
    args = parser.parse_args()
    main(args.left, args.right, args.out)