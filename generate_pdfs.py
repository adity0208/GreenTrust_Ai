"""
PDF Generator for GreenTrust AI sample invoices.
Creates valid and suspicious invoice PDFs for testing.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from pathlib import Path


def create_valid_invoice():
    """Create a valid invoice PDF with acceptable emissions."""
    
    pdf_path = Path("data_samples/valid_invoice.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph("GLOBAL LOGISTICS CO.", title_style))
    story.append(Paragraph("Sustainable Transportation & Supply Chain Solutions", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice header
    story.append(Paragraph("SHIPPING INVOICE", header_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Invoice details
    invoice_data = [
        ["Invoice No:", "INV-2024-00145", "Date:", "January 8, 2024"],
        ["Supplier ID:", "SUP-MH-2024-089", "PO Ref:", "PO/2024/0089"]
    ]
    
    t = Table(invoice_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Shipment information
    story.append(Paragraph("SHIPMENT INFORMATION", header_style))
    shipment_data = [
        ["Origin:", "Mumbai Port (Maharashtra)"],
        ["Destination:", "Delhi Warehouse (NCR)"],
        ["Transport Mode:", "Road Freight - Heavy Truck (20T capacity)"],
        ["Route Type:", "Domestic Interstate"],
        ["Shipment Weight:", "2,500 kg (2.5 metric tons)"],
        ["Distance:", "1,450 kilometers"],
        ["Transit Time:", "36 hours"]
    ]
    
    t2 = Table(shipment_data, colWidths=[2*inch, 4*inch])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3*inch))
    
    # Environmental impact
    story.append(Paragraph("ENVIRONMENTAL IMPACT DISCLOSURE (SEBI BRSR Compliance)", header_style))
    story.append(Paragraph("<b>Carbon Footprint Assessment:</b>", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    env_data = [
        ["Scope 3 Category 4:", "Upstream Transportation"],
        ["Emission Factor Used:", "Industry Average (Road Freight)"],
        ["Calculation Method:", "GHG Protocol"],
        ["Total CO2e Emissions:", "348.0 kg CO2e"],
        ["Emission Intensity:", "0.096 kg CO2e per ton-km"],
        ["Verification:", "Self-reported (Supplier data)"],
        ["Data Quality:", "Medium (Industry average factors)"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3.5*inch])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#2E7D32')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#E8F5E9')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    story.append(Paragraph("For queries contact: logistics@globallogistics.in | Phone: +91-22-2345-6789", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("This document is computer generated and requires no signature", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


def create_suspicious_invoice():
    """Create a suspicious invoice PDF with high emission deviation."""
    
    pdf_path = Path("data_samples/suspicious_invoice.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#C62828'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#D32F2F'),
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph("QUICK FREIGHT SERVICES", title_style))
    story.append(Paragraph("Express Delivery Solutions", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice header
    story.append(Paragraph("SHIPPING INVOICE", header_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Invoice details
    invoice_data = [
        ["Invoice No:", "QFS-2024-00892", "Date:", "January 10, 2024"],
        ["Supplier ID:", "SUP-DL-2024-156", "PO Ref:", "PO/2024/0156"]
    ]
    
    t = Table(invoice_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Shipment information
    story.append(Paragraph("SHIPMENT INFORMATION", header_style))
    shipment_data = [
        ["Origin:", "Delhi Hub"],
        ["Destination:", "Mumbai Port"],
        ["Transport Mode:", "Road Freight - Truck"],
        ["Route Type:", "Express Domestic"],
        ["Shipment Weight:", "3,200 kg (3.2 metric tons)"],
        ["Distance:", "1,420 kilometers"],
        ["Transit Time:", "24 hours (Express)"]
    ]
    
    t2 = Table(shipment_data, colWidths=[2*inch, 4*inch])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.3*inch))
    
    # Environmental impact - SUSPICIOUS VALUES
    story.append(Paragraph("ENVIRONMENTAL IMPACT DISCLOSURE", header_style))
    story.append(Paragraph("<b>Carbon Footprint Assessment:</b>", styles['Normal']))
    story.append(Spacer(1, 0.1*inch))
    
    env_data = [
        ["Scope 3 Category 4:", "Upstream Transportation"],
        ["Emission Factor Used:", "Company Proprietary Model"],
        ["Calculation Method:", "Internal Estimation"],
        ["Total CO2e Emissions:", "125.0 kg CO2e"],  # SUSPICIOUSLY LOW
        ["Emission Intensity:", "0.027 kg CO2e per ton-km"],  # Much lower than standard
        ["Verification:", "Self-reported (No third-party)"],
        ["Data Quality:", "Low (Proprietary estimation)"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3.5*inch])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#C62828')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFEBEE')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.3*inch))
    
    # Warning note
    story.append(Paragraph("<b>Note:</b> Emission values calculated using proprietary methodology. " +
                          "Third-party verification pending.", 
                          ParagraphStyle('Warning', parent=styles['Normal'], fontSize=9, textColor=colors.red)))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    story.append(Paragraph("For queries contact: info@quickfreight.com | Phone: +91-11-9876-5432", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("This document is computer generated", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


if __name__ == "__main__":
    print("Generating sample PDF invoices...")
    create_valid_invoice()
    create_suspicious_invoice()
    print("PDF generation complete!")
