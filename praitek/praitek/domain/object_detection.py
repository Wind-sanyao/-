# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import torch
from numpy import ndarray
from ultralytics import YOLO

import praitek.app
from praitek.domain.typedef import Box

__model: YOLO
__confidence_threshold: float


def __init_yolo_model() -> None:
    # Select .pt model file
    _pt_file = praitek.app.get_app_conf_value('MODEL', 'OD', 'yolov8n.pt')

    # Load confidence threshold
    global __confidence_threshold
    __confidence_threshold = float(
        praitek.app.get_app_conf_value(key='CONFIDENCE', section='OD', default=0.7))

    # Select device
    _device = "cuda" if torch.cuda.is_available() else "cpu"

    global __model
    __model = YOLO(_pt_file).to(_device)
    logging.info(f"Load '{_pt_file}' onto {_device}")


def od_predict(frame: ndarray) -> list[Box]:
    boxes: list[Box] = []
    verbose = praitek.app.get_app_conf_value('PREDICTION_VERBOSE', 'OD', True)
    results = __model.predict(frame, verbose=verbose)
    for result in results:
        # for i in range(len(result.boxes.cls)):
        #     d_cls_id = int(result.boxes.cls[i].item())
        #     d_cls_name = result.names[d_cls_id]
        #     d_confidence = result.boxes.conf[i].item()
        #     print(d_cls_id, d_cls_name, d_confidence)

        boxes.extend([Box(int(result.boxes.cls[i].item()), result.boxes.conf[i].item(), result.boxes.xyxy[i].tolist(),
                          result.names) for i in range(len(result.boxes.cls)) if
                      result.boxes.conf[i].item() > __confidence_threshold])
    return boxes
