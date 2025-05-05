import os
import json
dataset_path = 'SignLanguageDataset'
class_names = sorted(os.listdir(dataset_path))

label_map = {str(i): name for i, name in enumerate(class_names)}

with open("label_map.json", "w") as f:
    json.dump(label_map, f, indent=4)

print('Success')