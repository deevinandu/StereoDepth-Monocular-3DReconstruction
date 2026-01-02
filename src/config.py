# Camera Intrinsic Parameters
# Adjust these based on the specific sensor used for capture.
FOCAL_LENGTH_MM = 4.76
SENSOR_WIDTH_MM = 6.40
BASELINE_CM = 15.0  # Distance between the two camera positions

# Image Processing Parameters
TARGET_WIDTH = 1000  # Resized width for processing speed
SGBM_NUM_DISPARITIES = 256  # Increased for larger baseline (must be divisible by 16)
SGBM_BLOCK_SIZE = 7  # Slightly larger block for better matching

# Rectification Settings
# Set to True if images are already properly aligned (tripod with horizontal movement only)
# Set to False for handheld/uncalibrated stereo pairs
SKIP_RECTIFICATION = True

# WLS Filter Parameters (for disparity smoothing)
WLS_LAMBDA = 8000.0  # Regularization strength
WLS_SIGMA = 1.5  # Edge sensitivity