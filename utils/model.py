# model.py
import os
import cv2
import numpy as np

class ImageAnalyzer:
    def load_images_from_folder(self, folder_path, valid_exts=(".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
        images = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(valid_exts):
                full_path = os.path.join(folder_path, filename)
                img = cv2.imread(full_path)
                if img is not None:
                    images.append(img)
        return images

    def detect_black_area(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, contours, -1, 255, -1)
        black_area = cv2.countNonZero(mask)
        total_area = h * w
        return mask, black_area / total_area

    def compute_average_black_area(self, images):
        ratios = []
        for img in images:
            _, ratio = self.detect_black_area(img)
            ratios.append(ratio)
        if ratios:
            return sum(ratios) / len(ratios)
        else:
            return 0.0
