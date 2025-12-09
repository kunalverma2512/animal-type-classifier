from ultralytics import YOLO

model = YOLO('cattle_model.pth') 

results = model('test_image.jpg', verbose=False)

top_class_index = results[0].probs.top1
print(results[0].names[top_class_index])
