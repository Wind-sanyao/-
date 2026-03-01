# !/usr/bin/env python
# -*- coding: utf-8 -*-
from praitek.infra.face import Face as Face_infra
from praitek.infra.face_group import FaceGroup as Fg_infra
from praitek.infra.face_group_map import FaceGroupMap as Fgm_infra
from praitek.infra.face_image import FaceImage as Fi_infra


class FaceInfo(object):
    id: int
    name: str
    groups: list[dict]
    image_ids: list[int]

    def __init__(self, fid: int = 0, name: str = '', groups: list[dict] = None, image_ids: list[int] = None):
        self.id = fid
        self.name = name
        self.groups = [] if groups is None else groups
        self.image_ids = [] if image_ids is None else image_ids


class FaceGroupInfo(object):
    id: int
    name: str
    faces: list[dict]

    def __init__(self, gid: int = 0, name: str = '', faces: list[dict] = None):
        self.id = gid
        self.name = name
        self.faces = [] if faces is None else faces


class Face:
    @staticmethod
    def get_face_group_list():
        groups = Fg_infra().get_group_list()
        faces = Face_infra.get_face_list_by_group_ids([g.id for g in groups])
        dict_map = {}
        for f in faces:
            if f.group_id in dict_map.keys():
                dict_map[f.group_id].append({'id': f.id, 'name': f.name})
            else:
                dict_map[f.group_id] = [{'id': f.id, 'name': f.name}]
        return [FaceGroupInfo(gid=g.id, name=g.name, faces=dict_map[g.id]) if g.id in dict_map.keys()
                else FaceGroupInfo(gid=g.id, name=g.name, faces=[]) for g in groups]

    @staticmethod
    def add_face_group(group: FaceGroupInfo):
        return Fg_infra(name=group.name).add_group_info()

    @staticmethod
    def delete_face_group(group_id):
        return Fg_infra(id=group_id).delete_group_info()

    @staticmethod
    def update_face_group(gid, g_info):
        map_data = {'name': g_info.name}
        return Fg_infra(id=gid).update_group_info(map_data)

    @staticmethod
    def get_face_list():
        faces = Face_infra().get_face_list()
        groups = Fg_infra.get_group_list_by_face_list([f.id for f in faces])
        images = Fi_infra.get_image_list_by_face_list([f.id for f in faces])
        face_group_map_dict = {}
        face_image_map_dic = {}
        for g in groups:
            if g.face_id in face_group_map_dict.keys():
                face_group_map_dict[g.face_id].append({'id': g.id, 'name': g.name})
            else:
                face_group_map_dict[g.face_id] = [{'id': g.id, 'name': g.name}]
        for i in images:
            if i.face_id in face_image_map_dic.keys():
                face_image_map_dic[i.face_id].append(i.id)
            else:
                face_image_map_dic[i.face_id] = [i.id]

        result = []
        for f in faces:
            f = FaceInfo(fid=f.id, name=f.name)
            if f.id in face_group_map_dict.keys():
                f.groups = face_group_map_dict[f.id]
            if f.id in face_image_map_dic.keys():
                f.image_ids = face_image_map_dic[f.id]
            result.append(f)
        return result

    @staticmethod
    def get_face_info(fid):
        fi = Face_infra(id=fid).get_face_info()
        groups = Fg_infra.get_group_list_by_face_list([fi.id])
        images = Fi_infra.get_image_list_by_face_list([fi.id])
        return FaceInfo(fid=fi.id, name=fi.name, groups=groups, image_ids=[i.id for i in images])

    @staticmethod
    def add_face(face: FaceInfo, images):
        fid = Face_infra(name=face.name).add_face_info()
        if len(images) != 0:
            Fi_infra.multi_add_face_image_info(fid, images)
        return fid

    @staticmethod
    def delete_face(fid):
        return Face_infra(id=fid).delete_face_info()

    @staticmethod
    def update_face(fid, face_info):
        map_data = {'name': face_info.name}
        return Face_infra(id=fid).update_face_info(map_data)

    @staticmethod
    def add_face_to_group(gid, fids):
        return Fgm_infra(group_id=gid).multi_add(fids)

    @staticmethod
    def remove_face_from_group(gid, fids):
        return Fgm_infra(group_id=gid).multi_delete(fids)

    @staticmethod
    def add_image_to_face(fid, images):
        Fi_infra.multi_add_face_image_info(fid, images)
        return

    @staticmethod
    def remove_image_from_face(fid, img_ids):
        Fi_infra.multi_delete_face_image_info(fid, img_ids)
        return
