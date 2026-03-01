# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from praitek.app import app, get_app_conf_value
from praitek.domain.event import Event as Event_domain
from praitek.domain.typedef import Box
from praitek.infra.event import Event as Event_infra
from praitek.infra.face import FaceImage as Fi_infra


class EventService:
    @staticmethod
    def get_event_list(biz_type, filter_str, order_by, page, size):
        events, cnt = Event_domain().get_event_list(biz_type, filter_str, order_by, page, size)
        return [e.__dict__ for e in events], cnt

    @classmethod
    def get_event_image(cls, event_id, with_bbox):
        event = Event_infra(id=event_id).get_event_info()
        return cls.draw_image(event, with_bbox)

    @staticmethod
    def draw_image(event, with_bbox):
        # 1. 获取截图
        file = str(os.path.join(app.config["IMAGE_FOLDER"], event.image + ".png"))
        img = cv2.imread(filename=file)

        # 2. 画框, 获取裁剪图像
        face_image_map_dic = {}
        cropped_img_map = {}
        face_ids = []
        img_ext = None
        if with_bbox == 1 or with_bbox == 2:
            boxes = str.split(event.od_data_str, ';')
            for box_str in boxes:
                box = Box.load(box_str)
                cropped_img = img[box.xyxy[1]:box.xyxy[3], box.xyxy[0]:box.xyxy[2]]
                if box.class_id not in cropped_img_map.keys():
                    cropped_img_map[box.class_id] = cropped_img
                face_ids.append(box.class_id)
                img = cv2.rectangle(img, box.xyxy[:2], box.xyxy[2:], color=(0, 255, 0), thickness=2)
                # 2.1 添加人脸姓名
                if with_bbox == 2:
                    font_size = int(img.shape[0] / 32)
                    text = '{name} {:.2f}'.format(box.confidence, name=box.class_name)
                    img = cv2_img_put_chn_text(img, text, box.xyxy[0], box.xyxy[1] - font_size - 5,
                                               color=(0, 255, 0), font_size=font_size)

            # 3. 获取人脸照片
            if with_bbox == 2:
                images = Fi_infra.get_image_list_by_face_list(face_ids)
                for img_con in images:
                    if img_con.face_id not in face_image_map_dic.keys():
                        file_path = os.path.join(get_app_conf_value('IMAGE_FACE_FOLDER', None, None),
                                                 str(img_con.face_id), img_con.image)
                        face_image_map_dic[img_con.face_id] = cv2.imread(filename=file_path)

                # 4. 拼接人脸头像
                for box_str in boxes:
                    box = Box.load(box_str)
                    img_f = cv2.resize(face_image_map_dic.get(box.class_id), (80, 60))
                    img_c = cv2.resize(cropped_img_map.get(box.class_id), (80, 60))
                    img_con = np.concatenate([img_f, img_c], axis=1)
                    if img_ext is not None:
                        img_ext = np.concatenate([img_ext, img_con], axis=1)
                    else:
                        img_ext = img_con
                # 4.1 横向补充拼接长度
                if img_ext is not None:
                    img_default = np.full((60, img.shape[1] - img_ext.shape[1], 3), 0, dtype=np.uint8)
                    img_ext = np.concatenate([img_ext, img_default], axis=1)

        # 4.2 纵向照片拼接
        if img_ext is not None:
            img = np.vstack((img, img_ext))
        data = cv2.imencode('.png', img)[1]
        return data.tobytes()


def cv2_img_put_chn_text(img, text, left, top, color=(0, 255, 0), font_size=20):
    if isinstance(img, np.ndarray):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    style = ImageFont.truetype(
        "C:/windows/fonts/STKAITI.TTF", font_size, encoding="utf-8")
    # 绘制文本
    draw.text((left, top), text, color, font=style)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
