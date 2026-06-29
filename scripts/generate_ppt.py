import sys
import subprocess

# Auto-install reportlab if missing
try:
    import reportlab
except ImportError:
    print("Installing reportlab for PDF generation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Check if it's the title page (page 1)
        if self._pageNumber == 1:
            # Draw premium dark theme header for title slide
            self.setFillColor(colors.HexColor("#0a0f1a"))
            self.rect(0, 0, 792, 612, fill=True, stroke=False)
            
            # Subtle accent highlights
            self.setFillColor(colors.HexColor("#06b6d4"))
            self.rect(0, 0, 792, 12, fill=True, stroke=False)
            self.restoreState()
            return

        # Slide Background (Dark Blue theme)
        self.setFillColor(colors.HexColor("#090d16"))
        self.rect(0, 0, 792, 612, fill=True, stroke=False)

        # Header bar
        self.setFillColor(colors.HexColor("#0e1626"))
        self.rect(0, 532, 792, 80, fill=True, stroke=False)

        # Widescreen Cyan accent line
        self.setFillColor(colors.HexColor("#06b6d4"))
        self.rect(0, 530, 792, 2, fill=True, stroke=False)

        # Footer
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(36, 24, "GUARDIAN-AI  |  SAFETY IN TRANSIT")
        self.drawRightString(756, 24, f"Slide {self._pageNumber} of {page_count}")
        self.restoreState()

def create_presentation_pdf(output_filename="guardian_ai_presentation.pdf"):
    # Landscape letter is 792 x 612 pt
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles matching GuardianAI color palette
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=38,
        leading=44,
        textColor=colors.HexColor("#ffffff"),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#06b6d4"),
        alignment=1,
        spaceAfter=30
    )

    slide_header_style = ParagraphStyle(
        'SlideHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#ffffff"),
        spaceAfter=30
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=19,
        textColor=colors.HexColor("#94a3b8"),
        spaceAfter=12
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=8
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#f8fafc")
    )

    story = []

    # ================= Slide 1: Title Slide =================
    story.append(Spacer(1, 150))
    story.append(Paragraph("GUARDIAN-AI 🛡️", title_style))
    story.append(Paragraph("Smart ADAS and Real-Time Driver Safety Copilot", subtitle_style))
    story.append(Spacer(1, 50))
    
    metadata_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    story.append(Paragraph("Hack2Skill Data & AI Challenge Submission  |  Built by Jatin", metadata_style))
    story.append(PageBreak())

    # ================= Slide 2: The Problem =================
    story.append(Paragraph("The Problem: Cognitive Distractions & Road Hazards", slide_header_style))
    story.append(Paragraph("<b>1.3 Million Annual Road Deaths</b>: Global statistics show that the vast majority of severe vehicular accidents are caused by human error, primarily micro-sleeps or distractions.", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("• <b>Silent Fatigue (Micro-sleeps)</b>: Drivers fall asleep for small intervals, leading to immediate lane drift and high-speed crashes.", bullet_style))
    story.append(Paragraph("• <b>Visual Distractions (Phone Usage)</b>: Looking away to interact with devices blocks response times for obstacle avoidance.", bullet_style))
    story.append(Paragraph("• <b>Missing Immediate Closed-Loop Warnings</b>: Existing dashboard cameras only record feeds, lacking edge-computer vision models that calculate risk scores and warning signals locally in real-time.", bullet_style))
    story.append(PageBreak())

    # ================= Slide 3: What We Built =================
    story.append(Paragraph("What We Built: Closed-Loop AI Safety System", slide_header_style))
    story.append(Paragraph("An end-to-end multi-agent AI framework executing real-time client-side computer vision and backend sequence projections to forecast accidents 3-5 seconds before impact.", body_style))
    
    # 2-column details table
    col_data = [
        [
            Paragraph("<b>🛡️ Browser AI Skeleton Tracking</b><br/>MediaPipe Holistic tracks 3D face mesh targets, arm segments, and 21-joint finger skeletons in real-time.", body_style),
            Paragraph("<b>🧠 4 Collaborating Backend Agents</b><br/>FastAPI agents (Driver, Vehicle, Prediction, Intervention) exchange async state metrics.", body_style)
        ],
        [
            Paragraph("<b>🔊 Synth Siren Audio Alerting</b><br/>Web Audio synthesizer oscillates warning alerts directly through speakers when danger increases.", body_style),
            Paragraph("<b>🎛️ Interactive Cockpit controls</b><br/>Speed, steering, and lane alignment sliders allow manual overrides to test risk predictions.", body_style)
        ]
    ]
    t = Table(col_data, colWidths=[350, 350])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ================= Slide 4: Why We Built It This Way =================
    story.append(Paragraph("Why We Built It That Way: Architecture Choices", slide_header_style))
    
    why_data = [
        [
            Paragraph("<b>Edge-CV + Cloud Fusion</b>", bold_body_style),
            Paragraph("MediaPipe Holistic runs client-side in the browser. This eliminates server GPU cloud costs and ensures zero latency overhead for frame capture processing (<30ms).", body_style)
        ],
        [
            Paragraph("<b>Asynchronous Event Bus</b>", bold_body_style),
            Paragraph("Decouples agent loops (e.g. vehicle updates at 10Hz, camera updates at 30Hz). If the camera is inactive, backend falls back to physics-simulations instantly.", body_style)
        ],
        [
            Paragraph("<b>Direct DOM Telemetry Updates</b>", bold_body_style),
            Paragraph("Rendering 30 FPS landmarks in React state causes browser lag. We update calibration elements directly in the DOM by ID, saving significant CPU cycles.", body_style)
        ]
    ]
    t_why = Table(why_data, colWidths=[200, 500])
    t_why.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#1e293b")),
    ]))
    story.append(t_why)
    story.append(PageBreak())

    # ================= Slide 5: How It Works (Data Flow) =================
    story.append(Paragraph("How It Works: Technical Data Flow", slide_header_style))
    
    flow_steps = [
        Paragraph("<b>1. Sensation</b>: Webcam captures video. MediaPipe tracks Eye Aspect Ratio (EAR), Mouth aspect (MAR), and Hand-to-Cheek distance vectors.", bullet_style),
        Paragraph("<b>2. Transmission</b>: WebSockets stream coordinates to FastAPI's async event bus, throttled to 150ms to prevent buffer overflow.", bullet_style),
        Paragraph("<b>3. Sequence Modeling</b>: Vehicle telemetry sequence (50, 10) passes through a BiGRU network; driver parameters are fused through a Transformer cross-attention encoder.", bullet_style),
        Paragraph("<b>4. Forecast</b>: LSTM forecaster outputs collision probability and type (e.g. rear-end) 3-5 seconds ahead.", bullet_style),
        Paragraph("<b>5. Actuation</b>: Intervention Agent triggers wailing sirens in the browser and logs safety event audits into SQLite WAL database.", bullet_style)
    ]
    for step in flow_steps:
        story.append(step)
    story.append(PageBreak())

    # ================= Slide 6: Model Training & Verification =================
    story.append(Paragraph("Trained Models & System Verification", slide_header_style))
    story.append(Paragraph("<b>1. Generated PyTorch Checkpoints</b>:<br/>All models are fully trained in the backend using custom Tensor Dataset loaders. Saved weights are stored in the <code>checkpoints/</code> directory.", body_style))
    
    stats_data = [
        ["Model Name", "Architecture", "Saved Output File"],
        ["Driver Monitor", "MobileNetV2 CNN Classifier", "driver_monitor.pt"],
        ["Vehicle Dynamics", "Bi-GRU with Attention", "vehicle_behavior.pt"],
        ["Sensor Fusion", "Transformer Cross-Attention", "sensor_fusion.pt"],
        ["Accident Predictor", "LSTM Sequence Forecaster", "accident_predictor.pt"]
    ]
    t_stats = Table(stats_data, colWidths=[180, 260, 260])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#06b6d4")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor("#94a3b8")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#1e293b")),
    ]))
    story.append(t_stats)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>2. Test Suite</b>: 10/10 tests passed via <code>pytest</code>, verifying event loop timings and sequence predictions (<10ms).", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    create_presentation_pdf()
    print("PDF Presentation successfully generated: guardian_ai_presentation.pdf")
