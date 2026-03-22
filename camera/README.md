# 摄像头绑定与监控应用

一个功能完整的摄像头绑定与实时监控网页应用，支持USB摄像头和网络摄像头（RTSP）。

## 功能特性

### 摄像头绑定
- 支持USB摄像头和网络摄像头（RTSP）两种类型
- 动态表单：根据选择的摄像头类型显示对应的输入字段
- 实时表单验证
- 摄像头品牌和型号选择（网络摄像头）

### 实时监控
- 全屏监控画面显示
- 500ms自动刷新频率
- 摄像头名称显示
- 错误处理和重试机制

### 会话管理
- LocalStorage存储会话信息
- 自动会话过期处理（24小时）
- 页面刷新后自动恢复监控状态
- 浏览器标签页切换时保持连接

## 技术栈

### 后端
- Flask：Web框架
- Flask-SQLAlchemy：数据库ORM
- OpenCV：视频处理
- SQLite：数据存储

### 前端
- 原生HTML/CSS/JavaScript
- Fetch API：HTTP请求
- LocalStorage：会话存储

## 项目结构

```
fire/
├── backend/
│   ├── app.py              # Flask应用主文件
│   ├── models.py           # 数据库模型
│   └── camera.py           # 摄像头捕获器
├── templates/
│   ├── bind.html           # 绑定页面
│   └── monitor.html        # 监控页面
├── static/
│   ├── css/
│   │   ├── bind.css        # 绑定页面样式
│   │   └── monitor.css     # 监控页面样式
│   └── js/
│       ├── bind.js         # 绑定页面脚本
│       └── monitor.js      # 监控页面脚本
├── requirements.txt        # Python依赖
└── start.bat              # Windows启动脚本
```

## 安装和运行

### 环境要求
- Python 3.8+
- pip

### 快速启动（Windows）

1. 双击运行 `start.bat`
2. 等待依赖安装完成
3. 浏览器访问 `http://localhost:5000`

### 手动启动

1. 创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 启动应用：
```bash
cd backend
python app.py
```

5. 访问应用：
打开浏览器访问 `http://localhost:5000`

## 使用说明

### 绑定摄像头

1. 选择摄像头类型（USB摄像头/网络摄像头）
2. 填写摄像头信息：
   - **USB摄像头**：名称、设备索引
   - **网络摄像头**：名称、IP地址、端口、用户名、密码、品牌、型号
3. 点击"绑定摄像头"按钮
4. 绑定成功后自动跳转到监控页面

### 监控画面

- 监控页面会自动刷新摄像头画面（500ms间隔）
- 摄像头名称显示在顶部
- 如果出现连接错误，会显示错误信息和"重试"按钮
- 点击"重试"按钮会清除会话并返回绑定页面

### 会话管理

- 会话信息存储在浏览器LocalStorage中
- 会话有效期：24小时
- 刷新页面后自动恢复监控状态
- 切换浏览器标签页时保持连接

## API接口

### POST /api/camera/bind
绑定摄像头

**请求体：**
```json
{
  "cameraType": "usb|rtsp",
  "name": "摄像头名称",
  "deviceIndex": 0,
  "ip": "192.168.1.100",
  "port": 554,
  "username": "用户名",
  "password": "密码",
  "brand": "品牌",
  "model": "型号"
}
```

**响应：**
```json
{
  "success": true,
  "sessionId": "会话ID"
}
```

### GET /api/camera/snapshot/<session_id>
获取摄像头快照

**响应：** JPEG图片数据流

### GET /api/camera/info/<session_id>
获取摄像头信息

**响应：**
```json
{
  "session_id": "会话ID",
  "source_type": "usb|rtsp",
  "name": "摄像头名称",
  "status": "active|error",
  "error": "错误信息",
  "timestamp": 时间戳
}
```

### DELETE /api/camera/unbind/<session_id>
解绑摄像头

**响应：**
```json
{
  "success": true
}
```

## 数据库结构

### stream表
- `id`：主键
- `session_id`：会话ID（唯一标识）
- `source_type`：摄像头类型（'usb'|'rtsp'）
- `source_url`：摄像头地址
- `name`：摄像头名称
- `status`：状态（'connecting'|'connected'|'error'）
- `error_info`：错误信息
- `created_at`：创建时间
- `updated_at`：更新时间

## 注意事项

1. 确保摄像头设备正常连接
2. 网络摄像头需要正确的RTSP地址格式
3. 防火墙可能需要开放5000端口
4. 长时间不活动会话会自动清理
5. 建议使用Chrome或Edge浏览器以获得最佳体验

## 故障排除

### 摄像头无法连接
- 检查摄像头是否正常工作
- 验证网络摄像头的IP地址和端口
- 确认用户名和密码正确
- 检查防火墙设置

### 画面无法加载
- 检查网络连接
- 确认服务器正在运行
- 查看浏览器控制台错误信息

### 会话过期
- 重新绑定摄像头
- 检查系统时间是否正确

## 许可证

MIT License
