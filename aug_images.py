import os
import cv2

# Function to apply horizontal flip
def apply_horizontal_flip(image):
    return cv2.flip(image, 1)

# Function to adjust brightness
def adjust_brightness(image, alpha=1.0, beta=50):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

# Function to apply rotation
def rotate_image(image, angle=30):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h))

# Directories
input_folder = 'data_and_installs/images'  # Replace with your input folder path
output_folder = 'data_and_installs/aug_images'

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Process each image in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpeg") or filename.endswith(".jpg") or filename.endswith(".png"):
        # Read the image
        image_path = os.path.join(input_folder, filename)
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert image to RGB

        # Apply transformations
        flipped_image = apply_horizontal_flip(image_rgb)
        bright_image = adjust_brightness(image_rgb)
        rotated_image = rotate_image(image_rgb)

        # Create a folder for the current image
        base_name = os.path.splitext(filename)[0]
        image_output_folder = os.path.join(output_folder, base_name)
        if not os.path.exists(image_output_folder):
            os.makedirs(image_output_folder)

        # Save the original and augmented images
        output_image_paths = [
            os.path.join(image_output_folder, f"{base_name}1.jpeg"),
            os.path.join(image_output_folder, f"{base_name}2.jpeg"),
            os.path.join(image_output_folder, f"{base_name}3.jpeg"),
            os.path.join(image_output_folder, f"{base_name}4.jpeg")
        ]

        # Save the images
        cv2.imwrite(output_image_paths[0], cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))  # Original image
        cv2.imwrite(output_image_paths[1], cv2.cvtColor(flipped_image, cv2.COLOR_RGB2BGR))  # Flipped image
        cv2.imwrite(output_image_paths[2], cv2.cvtColor(bright_image, cv2.COLOR_RGB2BGR))  # Brightness adjusted image
        cv2.imwrite(output_image_paths[3], cv2.cvtColor(rotated_image, cv2.COLOR_RGB2BGR))  # Rotated image

print("Augmentation completed and saved in 'aug_images' folder.")
