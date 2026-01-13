# Sample Data for GreenTrust AI

This directory contains sample PDF invoices for testing the ESG audit system.

## Sample Invoices

### sample_invoice_1.txt
- **Supplier**: SUP-MH-2024-089 (Global Logistics Co.)
- **Route**: Mumbai Port → Delhi Warehouse
- **Transport Mode**: Road (Truck)
- **Weight**: 2,500 kg
- **Distance**: 1,450 km
- **Claimed CO2e**: 245.5 kg
- **Expected Benchmark**: ~230 kg (6.7% deviation - acceptable)

### sample_invoice_2.txt
- **Supplier**: SUP-KA-2024-112 (Express Freight Services)
- **Route**: Bangalore → Chennai (International Port)
- **Transport Mode**: Road + Sea
- **Weight**: 5,000 kg
- **Distance**: 350 km (road) + 2,000 km (sea)
- **Claimed CO2e**: 180.0 kg
- **Expected Benchmark**: ~190 kg (5.3% deviation - acceptable)

## Testing Notes

These samples are designed to test:
1. **Extraction accuracy**: Messy formatting, varying field positions
2. **Verification logic**: Realistic deviations from benchmarks
3. **Compliance evaluation**: Different transport modes and routes

## Creating Real PDFs

To convert these text files to actual PDFs for testing:

```bash
# Using Python
python -c "from fpdf import FPDF; pdf = FPDF(); pdf.add_page(); pdf.set_font('Arial', size=12); pdf.multi_cell(0, 10, open('sample_invoice_1.txt').read()); pdf.output('sample_invoice_1.pdf')"
```

Or use any text-to-PDF converter tool.
