import cv2

print("测试摄像头访问...")

# 尝试打开摄像头（索引0）
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("无法打开摄像头")
else:
    print("摄像头打开成功")
    
    # 尝试读取一帧
    ret, frame = cap.read()
    if ret:
        print(f"成功读取帧，大小: {frame.shape}")
        
        # 尝试编码为JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            print(f"成功编码为JPEG，大小: {len(jpeg.tobytes())} 字节")
        else:
            print("编码JPEG失败")
    else:
        print("读取帧失败")
    
    # 释放摄像头
    cap.release()

print("测试完成")