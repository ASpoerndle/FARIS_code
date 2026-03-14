import torch
print(torch.__version__)
from ultralytics import YOLO

model = YOLO("./YOLO.pt")

