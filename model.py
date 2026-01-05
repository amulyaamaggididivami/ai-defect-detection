from ultralytics import YOLO
from config import MODEL_PATH

class DefectDetector:
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
    
    def detect(self, image_path):
        """
        Run defect detection on an image.
        
        Returns:
            tuple: (has_defect: bool, confidence: float)
        """
        results = self.model(str(image_path))
        
        has_defect = len(results[0].boxes) > 0
        confidence = float(results[0].boxes.conf[0]) if has_defect else 0.0
        
        return has_defect, confidence

# Initialize detector instance
detector = DefectDetector()
