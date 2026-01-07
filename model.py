from ultralytics import YOLO
from config import MODEL_PATH

class DefectDetector:
    # Defect class mapping
    DEFECT_NAMES = {
        0: 'missing_hole',
        1: 'mouse_bite',
        2: 'open_circuit',
        3: 'short',
        4: 'spur',
        5: 'spurious_copper'
    }
    
    def __init__(self):
        self.model = YOLO(MODEL_PATH)
    
    def detect(self, image_path):
        """
        Run defect detection on an image.
        
        Returns:
            tuple: (has_defect: bool, confidence: float, defect_type: str or None)
        """
        results = self.model(str(image_path))
        
        has_defect = len(results[0].boxes) > 0
        confidence = float(results[0].boxes.conf[0]) if has_defect else 0.0
        defect_type = None
        
        if has_defect:
            # Get the class of the first detected defect
            class_id = int(results[0].boxes.cls[0])
            defect_type = self.DEFECT_NAMES.get(class_id, 'unknown')
        
        return has_defect, confidence, defect_type

# Initialize detector instance
detector = DefectDetector()
