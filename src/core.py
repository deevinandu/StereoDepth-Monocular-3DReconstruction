import cv2
import numpy as np

class StereoPipeline:
    def __init__(self, focal_length_mm, sensor_width_mm, baseline_cm, target_width):
        self.baseline = baseline_cm
        # Calculate effective focal length in pixels for the resized image
        self.f_pixel = (focal_length_mm * target_width) / sensor_width_mm
        
    def rectify_images(self, imgL, imgR):
        """Aligns uncalibrated images using SIFT feature matching and Fundamental Matrix."""
        print("[INFO] Aligning images (Rectification)...")
        
        # SIFT Feature Detection
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(imgL, None)
        kp2, des2 = sift.detectAndCompute(imgR, None)

        # Match Features
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        
        # Lowe's Ratio Test
        good = [m for m, n in matches if m.distance < 0.75 * n.distance]

        if len(good) < 10:
            print("[WARNING] Insufficient matches for rectification. Using raw images.")
            return imgL, imgR

        pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

        # Compute Fundamental Matrix & Rectification
        F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC)
        h, w = imgL.shape[:2]
        _, H1, H2 = cv2.stereoRectifyUncalibrated(pts1, pts2, F, (w, h))

        imgL_rect = cv2.warpPerspective(imgL, H1, (w, h))
        imgR_rect = cv2.warpPerspective(imgR, H2, (w, h))
        
        return imgL_rect, imgR_rect

    def compute_disparity(self, imgL, imgR, num_disp=160, block_size=5, wls_lambda=8000.0, wls_sigma=1.5):
        """Calculates disparity using SGBM and WLS smoothing."""
        print("[INFO] Computing Disparity...")
        grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
        grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

        # SGBM Matcher - optimized for larger baseline
        left_matcher = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=num_disp,
            blockSize=block_size,
            P1=8 * 3 * block_size**2,
            P2=32 * 3 * block_size**2,
            disp12MaxDiff=1,
            uniquenessRatio=5,  # Reduced for larger baseline
            speckleWindowSize=200,  # Increased to filter more noise
            speckleRange=2,  # Reduced for stricter filtering
            preFilterCap=63,  # Added pre-filter for better texture handling
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY  # Higher quality mode
        )
        
        # WLS Filter for smoothness
        right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
        wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=left_matcher)
        wls_filter.setLambda(wls_lambda)
        wls_filter.setSigmaColor(wls_sigma)

        dispL = left_matcher.compute(grayL, grayR)
        dispR = right_matcher.compute(grayR, grayL)
        filtered_disp = wls_filter.filter(dispL, imgL, disparity_map_right=dispR)
        
        # Normalize
        return filtered_disp.astype(np.float32) / 16.0

    def calculate_depth(self, disparity):
        """Depth = (f * B) / disparity"""
        depth_map = np.zeros_like(disparity)
        mask = disparity > 0
        depth_map[mask] = (self.f_pixel * self.baseline) / disparity[mask]
        return depth_map