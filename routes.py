from fasthtml.common import *
from model import detector
from config import UPLOAD_DIR
from database import save_detection, get_recent_defects, get_all_detections, clear_all_detections
from datetime import datetime
import base64
import json

def dashboard_button():
    """Reusable dashboard button component"""
    return Div(
        A(
            I(**{"data-lucide": "layout-dashboard"}, style="width: 20px; height: 20px; margin-right: 8px;"),
            "Dashboard",
            href="/dashboard",
            cls="dashboard-button"
        ),
        cls="dashboard-container"
    )

def home_page():
    return Title("AI Defect Detection"), Main(
        dashboard_button(),
        Div(
            H1("AI Defect Detection", cls="page-title"),
            cls="header-container"
        ),
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
        dashboard_button(),
        Div(
            H1("AI Defect Detection", cls="page-title"),
            cls="header-container"
        ),
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
    has_defect, confidence, defect_type = detector.detect(file_path)
    
    # Save detection result to database
    save_detection(filename, has_defect, confidence, defect_type)
    
    # Format results
    if has_defect:
        result_text = "DEFECT DETECTED"
        result_icon = I(**{"data-lucide": "alert-triangle"}, cls="result-icon-svg")
        result_color = "hsl(var(--destructive))"
        result_class = "result-defect"
        # Format defect type for display
        defect_display = defect_type.replace('_', ' ').title() if defect_type else "Unknown"
        detail = f"Type: {defect_display} | Confidence: {confidence:.2%}"
    else:
        result_text = "NO DEFECT"
        result_icon = I(**{"data-lucide": "check-circle"}, cls="result-icon-svg")
        result_color = "hsl(var(--success))"
        result_class = "result-success"
        defect_display = None
        detail = "Product appears normal"
    
    return Title("Detection Results"), Main(
        dashboard_button(),
        Div(
            H1("AI Defect Detection", cls="page-title"),
            cls="header-container"
        ),
        Div(
            Div(
                Div(result_icon, cls="result-icon"),
                H2(result_text, style=f"color: {result_color};", cls="result-title"),
                Div(
                    Span(defect_display, cls="defect-type-badge") if defect_display else None,
                    cls="defect-badges-container"
                ) if has_defect else None,
                P(detail, cls="result-detail"),
                P(f"File: {filename}", cls="result-filename"),
                cls=f"result-container {result_class}"
            ),
            A("Analyze Another Image", href="/", role="button", cls="new-analysis-btn"),
            cls="container"
        ),
        Script("lucide.createIcons();")
    )

def dashboard_page():
    """Show dashboard of recent detections"""
    all_recent = get_all_detections(hours=1)
    
    # Calculate statistics
    total_scans = len(all_recent)
    total_defects = len([d for d in all_recent if d["has_defect"]])
    total_clean = total_scans - total_defects
    
    # Calculate defect type distribution
    defect_counts = {}
    for d in all_recent:
        if d["has_defect"] and d.get("defect_type"):
            defect_type = d["defect_type"]
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
    
    # Create detection cards with expandable details
    if all_recent:
        detection_cards = []
        for idx, detection in enumerate(all_recent):
            is_defect = detection["has_defect"]
            timestamp = datetime.fromisoformat(detection["timestamp"])
            defect_type = detection.get("defect_type")
            defect_display = defect_type.replace('_', ' ').title() if defect_type else "Unknown"
            
            # Read image for thumbnail
            img_path = UPLOAD_DIR / detection["filename"]
            img_data = ""
            if img_path.exists():
                img_data = base64.b64encode(img_path.read_bytes()).decode()
            
            card = Div(
                Div(
                    # Thumbnail
                    Div(
                        Img(src=f"data:image/jpeg;base64,{img_data}", cls="detection-thumbnail") if img_data else Div(cls="detection-thumbnail-placeholder"),
                        cls="thumbnail-container"
                    ),
                    # Info
                    Div(
                        Div(
                            I(**{"data-lucide": "alert-triangle" if is_defect else "check-circle"}),
                            Span(detection["filename"], cls="detection-filename"),
                            cls="detection-name"
                        ),
                        Div(
                            I(**{"data-lucide": "clock"}, style="width: 14px; height: 14px; margin-right: 4px;"),
                            Span(timestamp.strftime("%d %b at %H:%M"), cls="detection-time"),
                            cls="detection-timestamp"
                        ),
                        cls="detection-info"
                    ),
                    # Badge and expand button
                    Div(
                        Div(
                            Span(defect_display, cls="detection-badge badge-defect") if is_defect and defect_type else Span("Clean", cls="detection-badge badge-clean"),
                            cls="badge-group"
                        ),
                        Button(
                            I(**{"data-lucide": "chevron-down"}, cls="expand-icon"),
                            cls="expand-button",
                            onclick=f"document.getElementById('details-{idx}').classList.toggle('hidden'); this.querySelector('.expand-icon').style.transform = document.getElementById('details-{idx}').classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(180deg)';"
                        ),
                        cls="detection-actions"
                    ),
                    cls="detection-card-header"
                ),
                # Expandable details
                Div(
                    Div(
                        Img(src=f"data:image/jpeg;base64,{img_data}", cls="detection-full-image") if img_data else Div(),
                        cls="detection-image-container"
                    ),
                    Div(
                        Div(
                            Span("Confidence", cls="detail-label"),
                            Span(f"{detection['confidence']:.0%}", cls="detail-value"),
                            cls="detail-row"
                        ),
                        Div(
                            Span("Defect Type", cls="detail-label"),
                            Span(defect_display if defect_type else "N/A", cls="detail-value"),
                            cls="detail-row"
                        ) if is_defect else None,
                        Div(
                            Span("Analysis", cls="detail-label"),
                            P(
                                "The image appears to be free of visible defects." if not is_defect else f"{defect_display} defect detected with {detection['confidence']:.0%} confidence. Please review the image for quality control.",
                                cls="detail-analysis"
                            ),
                            cls="detail-row detail-analysis-row"
                        ),
                        cls="detection-details-content"
                    ),
                    id=f"details-{idx}",
                    cls="detection-details hidden"
                ),
                cls=f"detection-card {'detection-card-defect' if is_defect else ''}"
            )
            detection_cards.append(card)
    else:
        detection_cards = [
            Div(
                I(**{"data-lucide": "inbox"}, style="width: 48px; height: 48px; color: hsl(var(--muted-foreground)); margin-bottom: 16px;"),
                P("No detections in the last hour", style="color: hsl(var(--muted-foreground)); font-size: 1.1rem;"),
                style="text-align: center; padding: 60px 20px;"
            )
        ]
    
    return Title("Analysis Dashboard"), Main(
        Div(
            # Header
            Div(
                Button(
                    I(**{"data-lucide": "arrow-left"}, style="width: 20px; height: 20px;"),
                    onclick="window.location.href='/'",
                    cls="icon-button back-button"
                ),
                Div(
                    Div(
                        I(**{"data-lucide": "layout-dashboard"}, style="width: 24px; height: 24px; margin-right: 12px;"),
                        H1("Analysis Dashboard", cls="dashboard-title-new"),
                        cls="dashboard-title-row"
                    ),
                    P("Last hour activity", cls="dashboard-subtitle"),
                    cls="dashboard-title-container"
                ),
                Form(
                    Button(
                        I(**{"data-lucide": "trash-2"}, style="width: 16px; height: 16px; margin-right: 8px;"),
                        "Clear History",
                        type="submit",
                        cls="clear-history-button"
                    ),
                    method="post",
                    action="/clear-history"
                ),
                cls="dashboard-header-new"
            ),
            
            # Statistics Cards
            Div(
                Div(
                    P(str(total_scans), cls="stat-value-new"),
                    P("Total Scans", cls="stat-label-new"),
                    cls="stat-card-new"
                ),
                Div(
                    Div(
                        I(**{"data-lucide": "alert-triangle"}, style="width: 20px; height: 20px; margin-right: 8px; color: hsl(var(--destructive));"),
                        P(str(total_defects), style="color: hsl(var(--destructive)); font-size: 2.0rem; font-weight: 700;"),
                        cls="stat-value-row"
                    ),
                    P("Defects Found", cls="stat-label-new"),
                    cls="stat-card-new stat-card-defect"
                ),
                Div(
                    Div(
                        I(**{"data-lucide": "check-circle"}, style="width: 20px; height: 20px; margin-right: 8px; color: hsl(var(--success));"),
                        P(str(total_clean), style="color: hsl(var(--success)); font-size: 2.0rem; font-weight: 700;"),
                        cls="stat-value-row"
                    ),
                    P("Clean", cls="stat-label-new"),
                    cls="stat-card-new stat-card-clean"
                ),
                cls="stats-container-new"
            ),
            
            # Defect Distribution Pie Chart
            Div(
                H3("Defect Type Distribution", cls="chart-title"),
                Canvas(id="defectChart", style="max-height: 300px;"),
                cls="chart-container"
            ) if defect_counts else None,
            
            # Detections List
            Div(*detection_cards, cls="detections-list"),
            
            cls="dashboard-wrapper"
        ),
        Script(src="https://cdn.jsdelivr.net/npm/chart.js"),
        Script(f"""
            lucide.createIcons();
            
            // Defect distribution pie chart
            const defectData = {json.dumps(defect_counts) if defect_counts else '{}'};
            
            if (Object.keys(defectData).length > 0) {{
                const ctx = document.getElementById('defectChart');
                
                // Color palette for different defect types
                const colors = {{
                    'missing_hole': '#ef4444',
                    'mouse_bite': '#f97316',
                    'open_circuit': '#eab308',
                    'short': '#8b5cf6',
                    'spur': '#06b6d4',
                    'spurious_copper': '#ec4899'
                }};
                
                const labels = Object.keys(defectData).map(key => key.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '));
                const data = Object.values(defectData);
                const bgColors = Object.keys(defectData).map(key => colors[key] || '#6b7280');
                
                new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: labels,
                        datasets: [{{
                            data: data,
                            backgroundColor: bgColors,
                            borderWidth: 2,
                            borderColor: '#fff'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    padding: 15,
                                    font: {{
                                        size: 12,
                                        family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
                                    }},
                                    usePointStyle: true,
                                    pointStyle: 'circle'
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return label + ': ' + value + ' (' + percentage + '%)';
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        """)
    )
