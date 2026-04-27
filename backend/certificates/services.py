import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from .models import Certificate, CertificateTemplate

def generate_certificate_pdf(certificate, template_obj=None):
    """
    Generates a PDF using reportlab over an uploaded template image
    and returns the raw PDF bytes.
    """
    # If a specific template is passed, use it. Otherwise, use the one saved in the record.
    # If the record has no template, fall back to the default one.
    if not template_obj:
        template_obj = certificate.template
    if not template_obj:
        template_obj = CertificateTemplate.objects.filter(is_default=True).first()
    
    buffer = BytesIO()
    
    # Use the photo's exact resolution for standard architecture (1376x768)
    page_width, page_height = 1376.0, 768.0
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    
    if template_obj and template_obj.image:
        template_path = template_obj.image.path
        # Draw the image to fit the exact page dimensions
        c.drawImage(template_path, 0, 0, width=page_width, height=page_height)
        
    # Set up layout and colors for a dark background
    # Colors: White for standard text, Gold/Yellow for highlighted elements
    white = colors.HexColor("#FFFFFF")
    gold = colors.HexColor("#FFD700")
    
    # Center horizontally, slightly above middle vertically
    center_x = page_width / 2.0
    
    # TOP LEFT - Tournament OS Inscription with Design
    c.setFont("Helvetica-Bold", 28)
    # Shadow
    c.setFillAlpha(0.3)
    c.setFillColor(colors.HexColor("#000000"))
    c.drawString(62, page_height - 62, "TOURNAMENT OS")
    # Main text
    c.setFillAlpha(1.0)
    c.setFillColor(gold)
    c.drawString(60, page_height - 60, "TOURNAMENT OS")
    
    # CERTIFICATE TITLE - Bigger, Bolder, with drop shadow design
    title_text = "CERTIFICATE OF ACHIEVEMENT"
    c.setFont("Helvetica-Bold", 54)
    # Drop shadow
    c.setFillColor(colors.HexColor("#000000"))
    c.drawCentredString(center_x + 3, page_height - 250 - 3, title_text)
    # Main text in Gold
    c.setFillColor(gold)
    c.drawCentredString(center_x, page_height - 250, title_text)
    
    # Add a thin gold line under the title for design
    title_width = c.stringWidth(title_text, "Helvetica-Bold", 54)
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.line(center_x - title_width / 2.0, page_height - 265, center_x + title_width / 2.0, page_height - 265)
    
    # Participant Name (Highlight)
    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 64)
    c.drawCentredString(center_x, page_height - 380, certificate.full_name)
    
    y_offset = page_height - 440
    
    # Team Name (if any)
    if certificate.team_name:
        c.setFillColor(white)
        c.setFont("Helvetica", 28)
        c.drawCentredString(center_x, y_offset, f"Team: {certificate.team_name}")
        y_offset -= 50
    else:
        y_offset -= 20

    # Placement text (highlight exactly the place)
    part1 = "For achieving "
    placement_text = certificate.placement
    if "place" not in placement_text.lower() and placement_text.lower() != "participant":
        placement_text += " place"
    part3 = " in"
    
    w1 = c.stringWidth(part1, "Helvetica", 28)
    w2 = c.stringWidth(placement_text, "Helvetica-Bold", 36)
    w3 = c.stringWidth(part3, "Helvetica", 28)
    
    total_w = w1 + w2 + w3
    start_x = center_x - (total_w / 2.0)
    
    c.setFillColor(white)
    c.setFont("Helvetica", 28)
    c.drawString(start_x, y_offset, part1)
    
    # Gold Highlight and Shadow for the Placement
    c.setFillColor(colors.HexColor("#000000"))
    c.setFont("Helvetica-Bold", 36)
    c.drawString(start_x + w1 + 2, y_offset - 2, placement_text) # Shadow
    c.setFillColor(gold)
    c.drawString(start_x + w1, y_offset, placement_text)
    
    c.setFillColor(white)
    c.setFont("Helvetica", 28)
    c.drawString(start_x + w1 + w2, y_offset, part3)
    
    y_offset -= 60
    
    # Tournament Name (Highlight)
    c.setFillColor(gold)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(center_x, y_offset, certificate.tournament_name)
    y_offset -= 45
    
    # Bottom details (white, smaller)
    c.setFillColor(colors.HexColor("#E0E0E0"))
    c.setFont("Helvetica", 16)
    c.drawString(60, 60, f"Certificate No: {certificate.certificate_number}")
    c.drawString(60, 35, f"Verify Code: {certificate.unique_code}")
    
    c.save()
    
    return buffer.getvalue()
