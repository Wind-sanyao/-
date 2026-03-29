## test cuda driver
import torch

print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))
print(torch.backends.cudnn.version())
print(torch.version.cuda)