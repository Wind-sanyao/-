# 重建开发环境

## 1. Yolov8

根据具体的软硬件环境配置 Yolov8 环境（略）

## 2. Python

```sh
# Python的版本可以根据情况调整
conda create -n praitek python=3.9
conda activate praitek
pip install dlib
# 注释掉 requirements.txt 中的 dlib 行
pip install -r requirements.txt
```

## 3. MariaDB

- 安装 MariaDB
- 运行命令 `praitek-demo-ui.exe setup` 初始化数据库和表。 _`praitek-demo-ui.exe`在另一个项目中。_

## 4. 运行项目

```sh
python -m praitek.main
```
