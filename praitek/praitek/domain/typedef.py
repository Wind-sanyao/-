class Box:
    xyxy: list[int]
    xywh: list[int]
    class_name: str
    class_id: int
    confidence: float

    def __init__(self, class_id: int, confidence: float, xyxy: list[float], cls_name_map: dict[int, str]):
        self.class_id = class_id
        self.class_name = cls_name_map[class_id]
        self.confidence = confidence
        self.xyxy = [int(i) for i in xyxy]
        self.xywh = [self.xyxy[0], self.xyxy[1], self.xyxy[2] - self.xyxy[0], self.xyxy[3] - self.xyxy[1]]

    def __repr__(self):
        # 0,person,0.763252,30,34,432,123
        return f"{self.class_id},{self.class_name},{self.confidence},{self.xyxy[0]},{self.xyxy[1]},{self.xyxy[2]},{self.xyxy[3]}"

    @classmethod
    def load(cls, box_str):
        box = str.split(box_str, ',')
        cls.class_id = int(box[0])
        cls.class_name = str(box[1])
        cls.confidence = float(box[2])
        cls.xyxy = [int(box[3]), int(box[4]), int(box[5]), int(box[6])]
        cls.xywh = [int(box[3]), int(box[4]), int(box[5]) - int(box[3]), int(box[6]), int(box[4])]
        return cls
