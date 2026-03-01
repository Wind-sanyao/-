# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import shutil
import threading

from werkzeug.utils import secure_filename

from praitek.app import get_app_conf_value
from praitek.domain.face import Face as Face_domain
from praitek.infra.face_image import FaceImage as Fi_infra

from praitek.domain.face_recognize import re_init_image

FACE_IMAGE_FOLDER = get_app_conf_value('IMAGE_FACE_FOLDER', None, None)


class Face:
    @staticmethod
    def get_face_group_list():
        return [g.__dict__ for g in Face_domain.get_face_group_list()]

    @staticmethod
    def add_face_group_info(group):
        group_id = Face_domain.add_face_group(group)
        return group_id

    @staticmethod
    def delete_face_group_info(gid):
        return Face_domain.delete_face_group(gid)

    @staticmethod
    def update_face_group_info(gid, group_info):
        return Face_domain.update_face_group(gid, group_info)

    @staticmethod
    def get_face_list():
        return [f.__dict__ for f in Face_domain.get_face_list()]

    @staticmethod
    def get_face_info(fid):
        return Face_domain.get_face_info(fid)

    @staticmethod
    def add_face_info(face, files):
        images = []
        for f in files:
            images.append(secure_filename(f.filename))
        face_id = Face_domain.add_face(face, images)
        for f in files:
            file_path = os.path.join(FACE_IMAGE_FOLDER, str(face_id))
            if not os.path.exists(file_path):
                os.makedirs(file_path, exist_ok=True)
            f.save(os.path.join(file_path, secure_filename(f.filename)))
            time.sleep(0.5)
        threading.Thread(target=re_init_image).start()
        return face_id

    @staticmethod
    def delete_face_info(fid):
        Face_domain.delete_face(fid)
        file_path = os.path.join(FACE_IMAGE_FOLDER, str(fid))
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
        threading.Thread(target=re_init_image).start()
        return

    @staticmethod
    def update_face_info(fid, face):
        return Face_domain.update_face(fid, face)

    @staticmethod
    def add_face_to_group(gid, fids):
        return Face_domain.add_face_to_group(gid, fids)

    @staticmethod
    def remove_face_from_group(gid, fids):
        return Face_domain.remove_face_from_group(gid, fids)

    @staticmethod
    def update_face_image(fid, files, img_ids):
        fis = Fi_infra.get_image_list_of_face(face_id=fid, image_ids=img_ids)
        images = []
        for f in files:
            images.append(secure_filename(f.filename))
        if len(images) != 0:
            Face_domain.add_image_to_face(fid, images)
            for f in files:
                file_path = os.path.join(FACE_IMAGE_FOLDER, str(fid))
                if not os.path.exists(file_path):
                    os.makedirs(file_path, exist_ok=True)
                f.save(os.path.join(file_path, secure_filename(f.filename)))
        Face_domain.remove_image_from_face(fid, img_ids)
        for fi in fis:
            file_name = os.path.join(FACE_IMAGE_FOLDER, str(fid), fi.image)
            if os.path.exists(file_name):
                os.remove(file_name)
        threading.Thread(target=re_init_image).start()
        return

    @staticmethod
    def add_image_to_face(fid, files):
        images = []
        for f in files:
            images.append(secure_filename(f.filename))
        if len(images) != 0:
            Face_domain.add_image_to_face(fid, images)
            for f in files:
                file_path = os.path.join(FACE_IMAGE_FOLDER, str(fid))
                if not os.path.exists(file_path):
                    os.makedirs(file_path, exist_ok=True)
                f.save(os.path.join(file_path, secure_filename(f.filename)))
            threading.Thread(target=re_init_image).start()
        return

    @staticmethod
    def remove_image_from_face(fid, img_ids):
        fis = Fi_infra.get_image_list_of_face(face_id=fid, image_ids=img_ids)
        Face_domain.remove_image_from_face(fid, img_ids)
        for fi in fis:
            file_name = os.path.join(FACE_IMAGE_FOLDER, str(fid), fi.image)
            if os.path.exists(file_name):
                os.remove(file_name)
        threading.Thread(target=re_init_image).start()
        return

    @staticmethod
    def get_face_image(img_id):
        fi = Fi_infra(id=img_id).get_face_image_info()
        file_path = os.path.join(FACE_IMAGE_FOLDER, str(fi.face_id), fi.image)
        with open(file_path, 'rb') as f:
            img = f.read()
            return img
