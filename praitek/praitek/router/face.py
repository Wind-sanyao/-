# !/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, request, make_response
from flask_jwt_extended import jwt_required

from praitek.router.base import Resp
from praitek.service.face import Face
from praitek.domain.face import FaceGroupInfo, FaceInfo

face_bp = Blueprint('face', __name__)


# 获取人脸分组列表
@face_bp.route('/face/group/list', methods=['GET'])
@jwt_required()
def get_face_group_list():
    return Resp(data={'list': Face.get_face_group_list()}).to_dict()


# 创建人脸分组信息
@face_bp.route('/face/group/info', methods=['POST'])
@jwt_required()
def add_face_group_info():
    g = FaceGroupInfo(gid=0, name=request.json.get('name'))
    group_id = Face.add_face_group_info(g)
    return Resp(data={'id': group_id}).to_dict()


# 删除人脸分组信息
@face_bp.route('/face/group/info', methods=['DELETE'])
@jwt_required()
def delete_face_group_info():
    group_id = request.args.get('id')
    Face.delete_face_group_info(group_id)
    return Resp().to_dict()


# 修改人脸分组信息
@face_bp.route('/face/group/info', methods=['PUT'])
@jwt_required()
def update_face_group_info():
    group_id = request.json.get('id')
    name = request.json.get('name')
    group_info = FaceGroupInfo(gid=group_id, name=name)
    Face.update_face_group_info(group_id, group_info)
    return Resp().to_dict()


# 获取人脸列表
@face_bp.route('/face/list', methods=['GET'])
@jwt_required()
def get_face_list():
    return Resp(data={'list': Face.get_face_list()}).to_dict()


# 获取人脸信息
@face_bp.route('/face/info', methods=['GET'])
@jwt_required()
def get_face_info():
    face_id = request.args.get('id')
    return Resp(data=Face.get_face_info(face_id)).to_dict()


# 添加人脸信息
@face_bp.route('/face/info', methods=['POST'])
@jwt_required()
def add_face_info():
    name = request.form.get('name')
    files = request.files.getlist('files')
    f = FaceInfo(fid=0, name=name)
    fid = Face.add_face_info(f, files)
    return Resp(data={'id': fid}).to_dict()


# 删除人脸信息
@face_bp.route('/face/info', methods=['DELETE'])
@jwt_required()
def delete_face_info():
    face_id = request.args.get('id')
    Face.delete_face_info(face_id)
    return Resp().to_dict()


# 修改人脸信息
@face_bp.route('/face/info', methods=['PUT'])
@jwt_required()
def update_face_info():
    face_id = request.json.get('id')
    name = request.json.get('name')
    face_info = FaceInfo(fid=face_id, name=name)
    Face.update_face_info(face_id, face_info)
    return Resp().to_dict()


# 向人脸分组中添加人脸
@face_bp.route('/face/group/add_face', methods=['POST'])
@jwt_required()
def add_face_to_group():
    g_id = request.json.get('group_id')
    f_ids = request.json.get('face_ids')
    Face.add_face_to_group(g_id, f_ids)
    return Resp().to_dict()


# 从人脸分组中移除人脸
@face_bp.route('/face/group/remove_face', methods=['POST'])
@jwt_required()
def remove_face_from_group():
    g_id = request.json.get('group_id')
    f_ids = request.json.get('face_ids')
    Face.remove_face_from_group(g_id, f_ids)
    return Resp().to_dict()


# 为人脸增减照片
@face_bp.route('/face/update_image', methods=['POST'])
@jwt_required()
def update_face_image():
    f_id = request.form.get('face_id')
    files = request.files.getlist('files')
    del_img_ids = request.form.getlist('deleted_image_ids')
    Face.update_face_image(f_id, files, del_img_ids)
    return Resp().to_dict()


# 为人脸添加照片
@face_bp.route('/face/add_image', methods=['POST'])
@jwt_required()
def add_image_to_face():
    f_id = request.form.get('face_id')
    files = request.files.getlist('files')
    Face.add_image_to_face(f_id, files)
    return Resp().to_dict()


# 为人脸移除照片
@face_bp.route('/face/remove_image', methods=['POST'])
@jwt_required()
def remove_image_from_face():
    f_id = request.json.get('face_id')
    img_ids = request.json.getlist('image_ids')
    Face.remove_image_from_face(f_id, img_ids)
    return Resp().to_dict()


# 获取人脸照片
@face_bp.route('/face/image', methods=['GET'])
@jwt_required()
def get_face_image():
    image_id = int(request.args.get('id'))
    img = Face.get_face_image(image_id)
    res = make_response(img)
    res.headers["Content-Type"] = "image/png"
    return res
