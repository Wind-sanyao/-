from ultralytics import YOLO
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

# 加载你现有的 yolov8n.pt
model = YOLO("yolov8n.pt")
class_names = model.names

def detect_fire_like():
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
    )
    if not path:
        return

    img = cv2.imread(path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 定义火焰颜色范围（HSV）
    lower_fire = np.array([0, 50, 50])
    upper_fire = np.array([35, 255, 255])
    mask_fire = cv2.inRange(hsv, lower_fire, upper_fire)

    #  定义烟雾颜色范围（HSV）
    lower_smoke = np.array([0, 0, 100])
    upper_smoke = np.array([180, 50, 200])
    mask_smoke = cv2.inRange(hsv, lower_smoke, upper_smoke)

    # 合并掩码
    mask = cv2.bitwise_or(mask_fire, mask_smoke)
    res = cv2.bitwise_and(img, img, mask=mask)

    # 叠加 YOLO 通用检测
    results = model(img, conf=0.5)
    annotated = results[0].plot()

    # 把疑似火灾区域标成红色
    annotated[mask > 0] = [0, 0, 255]  # BGR 红色

    cv2.imshow("疑似火灾/烟雾区域检测", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("=====  疑似火灾检测系统（不换模型版） =====")
    detect_fire_like()