from fasthtml.common import *
from model import detector
from config import UPLOAD_DIR
import base64

def home_page():
    return Title("AI Defect Detection"), Main(
        H1("AI Defect Detection", cls="page-title"),
        Div(
            Form(
                Label(
                    Div(
                        I(**{"data-lucide": "upload"}, cls="upload-icon"),
                        P(" Click to upload or drag and drop", cls="upload-text"),
                        P("PNG, JPG, JPEG up to 10MB", cls="upload-subtext"),
                        cls="drop-zone"
                    ),
                    Input(
                        type="file",
                        name="image",
                        accept="image/*",
                        required=True,
                        id="fileInput",
                        onchange="this.form.submit()",
                        style="display:none"
                    )
                ),
                method="post",
                action="/preview",
                enctype="multipart/form-data",
                id="uploadForm"
            ),
            cls="container"
        ),
        Script("lucide.createIcons();")
    )


async def preview_handler(image: UploadFile):
    """Handle image upload and show preview"""
    if not image:
        return Div(P("Please upload an image", style="color: red;"))
    
    # Save uploaded file
    file_path = UPLOAD_DIR / image.filename
    content = await image.read()
    file_path.write_bytes(content)
    
    # Create base64 image for preview
    img_data = base64.b64encode(content).decode()
    
    return Title("AI Defect Detection"), Main(
        H1("AI Defect Detection", cls="page-title"),
        Div(
            Div(
                Img(src=f"data:image/jpeg;base64,{img_data}", cls="preview-image"),
                cls="preview-container"
            ),
            Form(
                Button(" Analyze Image", type="submit", cls="analyze-btn"),
                Input(type="hidden", name="filename", value=image.filename),
                method="post",
                action="/analyze",
                cls="analyze-form"
            ),
            A("← Upload Different Image", href="/", cls="back-link"),
            cls="container"
        ),
        Script("lucide.createIcons();")
    )

async def analyze_handler(filename: str):
    """Handle analysis of uploaded image"""
    file_path = UPLOAD_DIR / filename
    
    # Run detection
    has_defect, confidence = detector.detect(file_path)
    
    # Format results
    if has_defect:
        result_text = "DEFECT DETECTED"
        result_icon = I(**{"data-lucide": "alert-triangle"}, cls="result-icon-svg")
        result_color = "hsl(var(--destructive))"
        result_class = "result-defect"
        detail = f"Confidence: {confidence:.2%}"
    else:
        result_text = "NO DEFECT"
        result_icon = I(**{"data-lucide": "check-circle"}, cls="result-icon-svg")
        result_color = "hsl(var(--success))"
        result_class = "result-success"
        detail = "Product appears normal"
    
    return Title("Detection Results"), Main(
        H1("AI Defect Detection", cls="page-title"),
        Div(
            Div(
                Div(result_icon, cls="result-icon"),
                H2(result_text, style=f"color: {result_color};", cls="result-title"),
                P(detail, cls="result-detail"),
                P(f"File: {filename}", cls="result-filename"),
                cls=f"result-container {result_class}"
            ),
            A("Analyze Another Image", href="/", role="button", cls="new-analysis-btn"),
            cls="container"
        ),
        Script("lucide.createIcons();")
    )
