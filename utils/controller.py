# controller.py
from PyQt5.QtWidgets import QFileDialog
from utils.model import ImageAnalyzer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore
import cv2
import os

class MainController:
    def __init__(self, ui):
        self.ui = ui
        self.analyzer = ImageAnalyzer()
        self.test_images = []       # 存圖像資料
        self.test_image_paths = [] # 存圖像路徑
        self.current_index = 0     # 目前顯示的索引
        self.bind_events()

    def bind_events(self):
        self.ui.pushButton_select_training_folder.clicked.connect(self.select_folder_and_analyze)
        self.ui.pushButton_select_test_folder.clicked.connect(self.select_test_folder)
        self.ui.pushButton_previous.clicked.connect(self.show_previous_image)
        self.ui.pushButton_next.clicked.connect(self.show_next_image)

    def select_folder_and_analyze(self):
        folder = QFileDialog.getExistingDirectory(None, "選擇圖片資料夾", "")
        if not folder:
            print("❌ 使用者取消選擇")
            return

        print(f"📂 選擇資料夾：{folder}")
        images = self.analyzer.load_images_from_folder(folder)
        if not images:
            print("⚠️ 沒有讀到圖片")
            return

        # 計算平均黑色佔比並儲存成實例變數
        self.avg_black_ratio = self.analyzer.compute_average_black_area(images)

        # 顯示於終端機
        print(f"✅ 平均黑色面積佔比：{self.avg_black_ratio * 100:.2f}%")

    def select_test_folder(self):
        folder = QFileDialog.getExistingDirectory(None, "選擇測試圖片資料夾", "")
        if not folder:
            print("❌ 使用者取消選擇")
            return

        print(f"📂 測試資料夾：{folder}")
        self.test_images = self.analyzer.load_images_from_folder(folder)
        self.test_image_paths = [os.path.join(folder, f) for f in os.listdir(folder)
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]

        if not self.test_images:
            print("⚠️ 沒有讀到圖片")
            return

        self.current_index = 0
        self.show_current_image()
        # 準備統計變數
        TP = TN = FP = FN = 0

        for img, path in zip(self.test_images, self.test_image_paths):
            _, black_ratio = self.analyzer.detect_black_area(img)
            predicted = "NG" if black_ratio < self.avg_black_ratio else "OK"
            gt = "good" if "good" in path.lower() else "NG"

            if gt == "good":
                if predicted == "OK":
                    TP += 1  # 正常預測正確
                else:
                    FP += 1  # overkill
            else:
                if predicted == "NG":
                    TN += 1  # 瑕疵預測正確
                else:
                    FN += 1  # underkill

        total = TP + TN + FP + FN
        acc = (TP + TN) / total if total > 0 else 0.0
        overkill = FP / (TP + FP) if (TP + FP) > 0 else 0.0
        underkill = FN / (TN + FN) if (TN + FN) > 0 else 0.0

        # 顯示到 GUI
        self.ui.label_accuracy.setText(f"{acc * 100:.2f}%")
        self.ui.label_overkill_rate.setText(f"{overkill * 100:.2f}%")
        self.ui.label_underkill_rate.setText(f"{underkill * 100:.2f}%")

    def show_current_image(self):
        if not self.test_images:
            return

        img = self.test_images[self.current_index]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(
            self.ui.label_org_img.width(),
            self.ui.label_org_img.height(),
            aspectRatioMode=QtCore.Qt.KeepAspectRatio
        )
        self.ui.label_org_img.setPixmap(pixmap)

        # 顯示圖片檔名
        current_file = os.path.basename(self.test_image_paths[self.current_index])
        self.ui.label_file_name.setText(current_file)

        # ➤ Ground Truth 判斷：根據路徑是否包含 "good"
        current_path = self.test_image_paths[self.current_index]
        if "good" in current_path.lower():
            self.ui.label_GT_result.setText("good")
            self.ui.label_GT_result.setStyleSheet("color: green;")
        else:
            self.ui.label_GT_result.setText("NG")
            self.ui.label_GT_result.setStyleSheet("color: red;")

        # 計算黑色佔比
        _, black_ratio = self.analyzer.detect_black_area(img)

        # 與訓練平均值比較，顯示判斷結果
        if hasattr(self, "avg_black_ratio"):
            if black_ratio < self.avg_black_ratio:
                self.ui.label_detect_result.setStyleSheet("color: red;")
                self.ui.label_detect_result.setText(f"{black_ratio * 100:.2f}% (NG)")
            else:
                self.ui.label_detect_result.setStyleSheet("color: green;")
                self.ui.label_detect_result.setText(f"{black_ratio * 100:.2f}% (OK)")
        else:
            self.ui.label_detect_result.setStyleSheet("color: black;")
            self.ui.label_detect_result.setText(f"{black_ratio * 100:.2f}%")


    def show_previous_image(self):
        if self.test_images and self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

    def show_next_image(self):
        if self.test_images and self.current_index < len(self.test_images) - 1:
            self.current_index += 1
            self.show_current_image()