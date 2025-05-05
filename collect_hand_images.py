import cv2
import os

# Set your labels here
labels = ["Hello", "I Love You", "No", "Ok", "Please", "Yes"]
images_per_label = 300

# Directory to save the dataset
dataset_dir = "SignLanguageDataset"
os.makedirs(dataset_dir, exist_ok=True)

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not accessible")
    exit()

for label in labels:
    count = 0
    label_dir = os.path.join(dataset_dir, label)
    os.makedirs(label_dir, exist_ok=True)
    
    print(f"\nCollecting images for label: {label}")
    print("Press 's' to start capturing, 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, f'Label: {label} | Images: {count}/{images_per_label}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow("Capture Images", frame)

        key = cv2.waitKey(1)

        if key == ord('s') and count < images_per_label:
            # Save image
            img_path = os.path.join(label_dir, f"{label}_{count}.jpg")
            cv2.imwrite(img_path, frame)
            count += 1

        elif key == ord('q') or count >= images_per_label:
            print(f"Finished capturing for label: {label}")
            break

print("Dataset collection completed.")
cap.release()
cv2.destroyAllWindows()
