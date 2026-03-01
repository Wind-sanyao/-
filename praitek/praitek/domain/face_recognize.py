# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import face_recognition
import numpy as np

from praitek.app import get_app_conf_value, get_config_path
from praitek.domain.typedef import Box

__face_yml = os.path.join(get_config_path(), "face.yml")

face_root_path = get_app_conf_value('IMAGE_FACE_FOLDER', None, None)
scan_names = []
scan_face_samples = []
update_image = False


def get_images_and_labels(path):
    path_names = os.listdir(path)
    # 新建连个list用于存放
    face_samples = []
    names = []
    global scan_names
    global scan_face_samples

    # 遍历图片路径，导入图片和id添加到list中
    for path_name in path_names:
        # print(path_name)
        image_dir = os.path.join(path, path_name)
        if os.path.isdir(image_dir):
            image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir)]
            for image_path in image_paths:
                face = face_recognition.load_image_file(image_path)
                face_bounding_boxes = face_recognition.face_locations(face)

                # If training image contains exactly one face
                if len(face_bounding_boxes) == 1:
                    face_enc = face_recognition.face_encodings(face)[0]
                    # Add face encoding for current image with corresponding label (name) to the training data
                    face_samples.append(face_enc)
                    names.append(path_name)
                    break
    scan_names = names.copy()
    scan_face_samples = face_samples.copy()
    return


def face_predict(frame) -> list[Box]:
    global clf
    global scan_names
    global update_image
    boxes = []
    if update_image is True:
        get_images_and_labels(face_root_path)
        update_image = False

    # Find all the faces in the test image using the default HOG-based model
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        tolerance = 0.45
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(scan_face_samples, face_encoding, tolerance)

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(scan_face_samples, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = scan_names[best_match_index]

            confidence = 1 - face_distances[best_match_index]

            box = Box(class_id=0, confidence=confidence, xyxy=[left, top, right, bottom],
                      cls_name_map=dict({0: name}))

            boxes.append(box)
    return boxes  # 全部过一遍还没识别出说明无法识别


def re_init_image():
    global update_image
    update_image = True


get_images_and_labels(face_root_path)
