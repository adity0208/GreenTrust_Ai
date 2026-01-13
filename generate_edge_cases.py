"""
Extended PDF generator for edge case invoices.
Creates 5 edge case scenarios for competition testing.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from pathlib import Path


def create_edge_case_missing_date():
    """Edge Case 1: Invoice with missing date field."""
    
    pdf_path = Path("data_samples/edge_case_missing_date.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("SWIFT CARGO SERVICES", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Invoice header - NO DATE
    story.append(Paragraph("SHIPPING INVOICE", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    invoice_data = [
        ["Invoice No:", "SC-2024-00892"],
        ["Supplier ID:", "SUP-KA-2024-234"],
        ["PO Ref:", "PO/2024/0234"]
        # DATE MISSING!
    ]
    
    t = Table(invoice_data, colWidths=[2*inch, 3*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Shipment info
    story.append(Paragraph("SHIPMENT DETAILS", styles['Heading3']))
    shipment_data = [
        ["Origin:", "Bangalore Tech Park"],
        ["Destination:", "Chennai Port"],
        ["Transport Mode:", "Road - Container Truck"],
        ["Weight:", "1,800 kg"],
        ["Distance:", "350 kilometers"],
    ]
    
    t2 = Table(shipment_data, colWidths=[2*inch, 3.5*inch])
    t2.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica')]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))
    
    # Environmental data
    story.append(Paragraph("CARBON FOOTPRINT", styles['Heading3']))
    env_data = [
        ["Total CO2e Emissions:", "60.5 kg CO2e"],
        ["Emission Factor:", "0.096 kg/ton-km"],
        ["Calculation Method:", "GHG Protocol"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E3F2FD'))
    ]))
    story.append(t3)
    
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


def create_edge_case_eur_currency():
    """Edge Case 2: Invoice in EUR currency."""
    
    pdf_path = Path("data_samples/edge_case_eur_currency.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("EUROFREIGHT LOGISTICS GmbH", title_style))
    story.append(Paragraph("International Shipping Solutions", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("SHIPPING INVOICE", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    invoice_data = [
        ["Invoice No:", "EFL-2024-DE-1156"],
        ["Supplier ID:", "SUP-EU-2024-445"],
        ["Date:", "January 11, 2026"],
        ["Currency:", "EUR €"]
    ]
    
    t = Table(invoice_data, colWidths=[2*inch, 3*inch])
    t.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica')]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Shipment info
    story.append(Paragraph("SHIPMENT INFORMATION", styles['Heading3']))
    shipment_data = [
        ["Origin:", "Hamburg Port, Germany"],
        ["Destination:", "Mumbai Port, India"],
        ["Transport Mode:", "Sea Freight - Container Ship"],
        ["Weight:", "12.5 metric tons"],  # In tons, not kg!
        ["Distance:", "6,850 nautical miles"],
        ["Freight Cost:", "€2,450.00"]
    ]
    
    t2 = Table(shipment_data, colWidths=[2*inch, 3.5*inch])
    t2.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica')]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))
    
    # Environmental data
    story.append(Paragraph("ENVIRONMENTAL IMPACT (SEBI BRSR)", styles['Heading3']))
    env_data = [
        ["Total CO2e Emissions:", "202.8 kg CO2e"],
        ["Emission Intensity:", "0.016 kg CO2e per ton-km"],
        ["Methodology:", "ISO 14064-1:2018"],
        ["Carbon Offset:", "€45.00 (voluntary)"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E8F5E9'))
    ]))
    story.append(t3)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<i>Note: All amounts in EUR. Convert to INR at current exchange rate for reporting.</i>", 
                          ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
    
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


def create_edge_case_high_risk_region():
    """Edge Case 3: Invoice from high-risk region."""
    
    pdf_path = Path("data_samples/edge_case_high_risk_region.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#C62828'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("BORDER LOGISTICS LLC", title_style))
    story.append(Paragraph("Cross-Border Transport Services", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("SHIPPING INVOICE", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    invoice_data = [
        ["Invoice No:", "BL-2024-AF-0089"],
        ["Supplier ID:", "SUP-AF-2024-089"],
        ["Date:", "January 9, 2026"],
        ["Route Classification:", "HIGH RISK ZONE"]
    ]
    
    t = Table(invoice_data, colWidths=[2*inch, 3*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFEBEE'))
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Shipment info
    story.append(Paragraph("SHIPMENT INFORMATION", styles['Heading3']))
    shipment_data = [
        ["Origin:", "Kabul Distribution Center, Afghanistan"],
        ["Destination:", "Islamabad Warehouse, Pakistan"],
        ["Transport Mode:", "Road - Armored Truck (Security Escort)"],
        ["Weight:", "950 kg"],
        ["Distance:", "680 kilometers"],
        ["Security Level:", "HIGH - Armed escort required"]
    ]
    
    t2 = Table(shipment_data, colWidths=[2*inch, 3.5*inch])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.red)
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))
    
    # Environmental data
    story.append(Paragraph("CARBON FOOTPRINT ASSESSMENT", styles['Heading3']))
    env_data = [
        ["Total CO2e Emissions:", "62.6 kg CO2e"],
        ["Emission Factor:", "0.096 kg CO2e per ton-km"],
        ["Verification:", "Self-reported (Third-party unavailable)"],
        ["Risk Assessment:", "MANDATORY HUMAN REVIEW"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFEBEE')),
        ('TEXTCOLOR', (0,3), (-1,3), colors.red)
    ]))
    story.append(t3)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>WARNING:</b> Shipment from conflict zone. Enhanced due diligence required.", 
                          ParagraphStyle('Warning', parent=styles['Normal'], fontSize=9, textColor=colors.red)))
    
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


def create_edge_case_multimodal():
    """Edge Case 4: Multimodal transport (air + road + sea)."""
    
    pdf_path = Path("data_samples/edge_case_multimodal.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#F57C00'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("GLOBAL MULTIMODAL LOGISTICS", title_style))
    story.append(Paragraph("Integrated Transport Solutions", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("SHIPPING INVOICE - MULTIMODAL", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    invoice_data = [
        ["Invoice No:", "GML-2024-MM-0567"],
        ["Supplier ID:", "SUP-SG-2024-567"],
        ["Date:", "January 10, 2026"],
        ["Service Type:", "Multimodal (Air + Sea + Road)"]
    ]
    
    t = Table(invoice_data, colWidths=[2*inch, 3*inch])
    t.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica')]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Multi-leg journey
    story.append(Paragraph("MULTI-LEG JOURNEY DETAILS", styles['Heading3']))
    
    leg_data = [
        ["Leg", "Mode", "Route", "Distance", "Weight", "CO2e"],
        ["1", "Air Freight", "Singapore → Mumbai", "4,100 km", "800 kg", "1,970.4 kg"],
        ["2", "Road", "Mumbai Port → Delhi", "1,450 km", "800 kg", "110.9 kg"],
        ["3", "Road", "Delhi → Chandigarh", "250 km", "800 kg", "19.2 kg"],
    ]
    
    t2 = Table(leg_data, colWidths=[0.6*inch, 1.2*inch, 1.8*inch, 1*inch, 0.9*inch, 0.9*inch])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFF3E0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))
    
    # Total emissions
    story.append(Paragraph("TOTAL ENVIRONMENTAL IMPACT", styles['Heading3']))
    env_data = [
        ["Total CO2e Emissions:", "2,100.5 kg CO2e"],
        ["Breakdown:", "Air: 93.7% | Road: 6.3%"],
        ["Methodology:", "Mode-specific emission factors (GHG Protocol)"],
        ["Complexity:", "HIGH - Multi-leg calculation"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFF3E0'))
    ]))
    story.append(t3)
    
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


def create_edge_case_zero_emissions():
    """Edge Case 5: Supplier claims 100% carbon-neutral (greenwashing test)."""
    
    pdf_path = Path("data_samples/edge_case_zero_emissions.pdf")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#4CAF50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("🌿 GREENWAY ECO-LOGISTICS 🌿", title_style))
    story.append(Paragraph("100% Carbon Neutral Shipping - Certified Green", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("CARBON-NEUTRAL SHIPPING INVOICE", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    invoice_data = [
        ["Invoice No:", "GEL-2024-CN-0123"],
        ["Supplier ID:", "SUP-GR-2024-123"],
        ["Date:", "January 12, 2026"],
        ["Certification:", "ISO 14001 Certified"]
    ]
    
    t = Table(invoice_data, colWidths=[2*inch, 3*inch])
    t.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica')]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Shipment info
    story.append(Paragraph("SHIPMENT INFORMATION", styles['Heading3']))
    shipment_data = [
        ["Origin:", "Pune Green Hub"],
        ["Destination:", "Mumbai Eco-Port"],
        ["Transport Mode:", "Electric Truck (100% Renewable Energy)"],
        ["Weight:", "3,500 kg"],
        ["Distance:", "150 kilometers"],
    ]
    
    t2 = Table(shipment_data, colWidths=[2*inch, 3.5*inch])
    t2.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica')]))
    story.append(t2)
    story.append(Spacer(1, 0.2*inch))
    
    # Environmental data - ZERO EMISSIONS CLAIM
    story.append(Paragraph("CARBON FOOTPRINT - NET ZERO", styles['Heading3']))
    env_data = [
        ["Gross CO2e Emissions:", "50.4 kg CO2e (calculated)"],
        ["Carbon Offsets Purchased:", "50.4 kg CO2e"],
        ["Net CO2e Emissions:", "0.0 kg CO2e ✓"],
        ["Offset Provider:", "GreenCarbon Solutions Ltd."],
        ["Offset Verification:", "Voluntary (not third-party verified)"],
        ["Renewable Energy %:", "100% (company claim)"]
    ]
    
    t3 = Table(env_data, colWidths=[2.5*inch, 3*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#C8E6C9')),
        ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold')
    ]))
    story.append(t3)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Note:</b> Carbon offsets are voluntary and not independently verified. " +
                          "Actual emissions calculated at 50.4 kg CO2e before offsets.", 
                          ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
    
    doc.build(story)
    print(f"Created: {pdf_path}")
    return str(pdf_path)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("GENERATING EDGE CASE INVOICES")
    print("="*60 + "\n")
    
    create_edge_case_missing_date()
    create_edge_case_eur_currency()
    create_edge_case_high_risk_region()
    create_edge_case_multimodal()
    create_edge_case_zero_emissions()
    
    print("\n" + "="*60)
    print("ALL EDGE CASE INVOICES GENERATED!")
    print("="*60)
