from flask import Flask, request, send_file, jsonify
from datetime import datetime
from flask_cors import CORS
import subprocess
import tempfile
import os
import pytz

app = Flask(__name__)
CORS(app)

@app.route('/generate-pdf-invoice', methods=['POST'])
def generate_pdf_invoice():
    data = request.json
    invoice = data.get('invoice')
    country = data.get('country')
    utc_now = datetime.now(pytz.utc)
    uk_time = utc_now.astimezone(pytz.timezone('Europe/London'))
    us_time = utc_now.astimezone(pytz.timezone('America/Los_Angeles'))
    # Generate LaTeX source code
    if country == 'UK':
        latex_source = generate_latex_invoice_uk(invoice, uk_time)
    elif country == 'US':
        latex_source = generate_latex_invoice_us(invoice, us_time)
    
    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, 'invoice.tex')
        pdf_file_path = os.path.join(tmpdirname, 'invoice.pdf')

        # Write LaTeX source to a file
        with open(tex_file_path, 'w') as f:
            f.write(latex_source)

        # Run pdflatex to generate PDF
        try:
            subprocess.run(['pdflatex', '-output-directory', tmpdirname, tex_file_path], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": "PDF generation failed",
                "details": e.stderr
            }), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        return send_file(pdf_file_path, as_attachment=True)

def generate_latex_invoice_uk(invoice, uk_time):
    # Generate LaTeX content here (similar to the LaTeX source in your Node.js example)
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\pagestyle{{empty}}

    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{COR-TEN-STEEL UK}}}}
    \\end{{center}}
    \\vspace{{0.5cm}}
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        Cadley \\\\
        SN8 4NE \\\\
        0118 234 9909 \\\\
        uk@cor-ten-steel.co.uk \\\\
        www.cor-ten-steel.co.uk \\\\
        \\vspace{{0.5cm}}
        \\textbf{{\\large Customer Details:}} \\\\
        \\texttt{{{invoice['customers']['first_name']}}} \\texttt{{{invoice['customers']['last_name']}}} \\\\
    """
    if invoice['customers']['company']:
        latex_source += f"""
        \\texttt{{{invoice['customers']['company']}}} \\\\
    """
    latex_source += f"""
        \\texttt{{{invoice['customers']['email']}}} \\\\
        \\texttt{{{invoice['customers']['phone']}}} \\\\
    """
    if invoice['addresses']['building_name']:
        latex_source += f"""
        \\texttt{{{invoice['addresses']['building_name']}}} \\\\
    """
    latex_source += f"""
        \\texttt{{{invoice['addresses']['street_address']}}} \\\\
        \\texttt{{{invoice['addresses']['suburb']}}} \\texttt{{{invoice['addresses']['postal_code']}}} \\\\
        \\texttt{{{invoice['addresses']['city']}}} \\\\
        \\texttt{{{invoice['addresses']['country']}}}
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        VAT Number: 161 6032 40 \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{uk_time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    \\begin{{longtable}}{{|p{{0.5\\textwidth}}|>{{\\centering\\arraybackslash}}p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|p{{0.1\\textwidth}}|}}
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        {invoice_table_rows_uk(invoice)}
        \\hline
        \\multicolumn{{2}}{{c|}}{{}} & Subtotal & £\\texttt{{{(invoice['Price'] - invoice['freight_charged']):.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Freight & £\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Balance due inc VAT & £\\texttt{{{invoice['Price']:.2f}}} \\\\
        \\cline{{3-4}}
    \\end{{longtable}}
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    \\texttt{{Account/Business Name: Rocersa Limited}} \\\\
    \\texttt{{Sort Code: 40-05-16}} \\\\
    \\texttt{{Account Number: 02371960}} \\\\
    \\texttt{{Reference: {str(invoice['InvoiceID']).zfill(5)}}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source

def invoice_table_rows_uk(invoice):
    table_rows = ""
    for product in invoice["InvoiceComponentsT"]:
        table_rows += f"\\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{£{product['price']:.2f}}} & \\texttt{{£{(product['price'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

def generate_latex_invoice_us(invoice, us_time):
    # Generate LaTeX content here (similar to the LaTeX source in your Node.js example)
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\pagestyle{{empty}}

    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{COR-TEN-STEEL USA}}}}
    \\end{{center}}
    
    \\vspace{{1cm}}
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        Mesa Street \\\\
        Hesperia \\\\
        92345 CA \\\\
        Tel: 760-995-2555 \\\\
        Email: usa@cor-ten-steel.com \\\\
        \\vspace{{0.5cm}}
        \\textbf{{\\large Customer Details:}} \\\\
        \\texttt{{{invoice['customers']['first_name']}}} \\texttt{{{invoice['customers']['last_name']}}} \\\\
    """
    if invoice['customers']['company']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['company']}}} \\\\
    """
    latex_source += f"""
        \\texttt{{{invoice['addresses']['street_address']}}} \\\\
        \\texttt{{{invoice['addresses']['suburb']}}} \\texttt{{{invoice['addresses']['postal_code']}}} \\\\
        \\texttt{{{invoice['addresses']['city']}}} \\\\
        \\texttt{{{invoice['addresses']['country']}}}
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        Tax Number: XXX XXX XXX (California Only) \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{us_time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    
    \\vspace{{1cm}}
    
    \\begin{{longtable}}{{|p{{0.4\\textwidth}}|>{{\\centering\\arraybackslash}}p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|p{{0.2\\textwidth}}|}}
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        \\endhead
        {invoice_table_rows_us(invoice)}
        \\multicolumn{{2}}{{c|}}{{}} & Subtotal & \\$\\texttt{{{(invoice['Price'] - invoice['freight_charged']):.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Freight & \\$\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Balance due & \\$\\texttt{{{invoice['Price']:.2f}}} \\\\
        \\cline{{3-4}}
        \\endfoot
    \\end{{longtable}}
    \\vspace{{1cm}}
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    \\texttt{{Account/Business Name: Rocersa Limited}} \\\\
    \\texttt{{ACH Routing Number: 121000358}} \\\\
    \\texttt{{Account Number: 325056815335}} \\\\
    \\texttt{{Reference: {str(invoice['InvoiceID']).zfill(5)}}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source

def invoice_table_rows_us(invoice):
    table_rows = ""
    for product in invoice["InvoiceComponentsT"]:
        table_rows += f"\\texttt{{{product['ProductsT']['NameImperial']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{\\${product['price']:.2f}}} & \\texttt{{\\${(product['price'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

@app.route('/generate-pdf-picklist', methods=['POST'])
def generate_pdf_picklist():
    data = request.json
    invoice = data.get('invoice')
    info = data.get('info')
    components = data.get('components')
    country = data.get('country')
    utc_now = datetime.now(pytz.utc)
    uk_time = utc_now.astimezone(pytz.timezone('Europe/London'))
    us_time = utc_now.astimezone(pytz.timezone('America/Los_Angeles'))
    # Generate LaTeX source code
    if country == 'UK':
        latex_source = generate_latex_picklist_uk(invoice, info, components, uk_time)
    elif country == 'US':
        latex_source = generate_latex_picklist_us(invoice, info, components, us_time)
    
    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, 'picklist.tex')
        pdf_file_path = os.path.join(tmpdirname, 'picklist.pdf')

        # Write LaTeX source to a file
        with open(tex_file_path, 'w') as f:
            f.write(latex_source)

        # Run pdflatex to generate PDF
        try:
            subprocess.run(['pdflatex', '-output-directory', tmpdirname, tex_file_path], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": "PDF generation failed",
                "details": e.stderr
            }), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        return send_file(pdf_file_path, as_attachment=True)

def generate_latex_picklist_uk(invoice, info, components, uk_time):
    # Generate LaTeX content here (similar to the LaTeX source in your Node.js example)
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\usepackage{{anyfontsize}}
    \\pagestyle{{empty}}

    \\begin{{document}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\texttt{{Deliver to:}} \\\\

    \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {invoice['customers']['first_name']}}} \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {invoice['customers']['last_name']}}} \\\\
    """
    if invoice['customers']['company']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['company']}}} \\\\
    """
    latex_source += f"""
    """
    if invoice['addresses']['building_name']:
        latex_source += f"""

    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {invoice['addresses']['building_name']}}} \\\\

    """
    latex_source += f"""
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {invoice['addresses']['street_address']}}} \\\\
 
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {invoice['addresses']['suburb']}}} \\\\

    \\textbf{{\\fontsize{{70}}{{84}}\\selectfont {invoice['addresses']['postal_code']}}} \\\\

    \\noindent
    \\textsf{{\\Large {{Email: }}}} \\textsf{{\\Large {invoice['customers']['email']}}} \\\\
    \\textsf{{\\Large {{Phone: }}}} \\textsf{{\\Large {invoice['customers']['phone']}}} \\\\

    \\vspace{{0.5cm}}
    
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        COR-TEN-STEEL UK \\\\
        Cadley \\\\
        SN8 4NE \\\\
        Tel: 0118 234 9909 \\\\
        Email: uk@cor-ten-steel.co.uk \\\\
 
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Picklist \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{uk_time.strftime("%d-%b-%Y %H:%M")}}} 
    \\end{{minipage}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\rule{{\\textwidth}}{{0.5pt}}

    \\vspace{{0.5cm}}

    \\noindent
    \\begin{{tabular}}{{l l}}
    \\textbf{{Total Items:}} & \\texttt{{{info['total_items']}}} \\\\ 
    \\textbf{{Total Weight:}} & \\texttt{{{info['total_weight']}}} \\\\ 
    \\textbf{{Carrier:}} & \\texttt{{{invoice['freight_carrier']}}} \\\\ 
    \\textbf{{Stickers:}} & \\texttt{{{invoice['stickers']}}} \\\\ 
    \\textbf{{Packing Instructions:}} & \\texttt{{{invoice['packing_instructions']}}} \\\\ 
    \\textbf{{Con Note:}} & \\texttt{{{invoice['con_note']}}} \\\\ 
    \\end{{tabular}}

    \\vspace{{0.5cm}}

    \\begin{{longtable}}{{|l|l|l|l|}}
        \\hline
        \\textbf{{Code}} & \\textbf{{Description}} & \\textbf{{Qty}} & \\textbf{{Weight (kgs)}} \\\\
        \\hline
        {picklist_table_rows_uk(invoice, components)}
    \\end{{longtable}}
    


    \\end{{document}}
    """
    return latex_source

def picklist_table_rows_uk(invoice, components):
    table_rows = ""
    for product in components:
        table_rows += f"\\texttt{{{product['ProductsT']['ProductCode']}}} & \\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{{(product['ProductsT']['Weight'] * product['Quantity']):.1f}}}  \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

def generate_latex_picklist_us(invoice, info, components, us_time):
    # Generate LaTeX content here (similar to the LaTeX source in your Node.js example)
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\usepackage{{anyfontsize}}
    \\pagestyle{{empty}}

    \\begin{{document}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\texttt{{Deliver to:}} \\\\

    \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {invoice['customers']['first_name']}}} \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {invoice['customers']['last_name']}}} \\\\
    """
    if invoice['customers']['company']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['company']}}} \\\\
    """
    latex_source += f"""
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {invoice['addresses']['street_address']}}} \\\\
 
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {invoice['addresses']['suburb']}}} \\\\

    \\textbf{{\\fontsize{{70}}{{84}}\\selectfont {invoice['addresses']['postal_code']}}} \\\\

    \\noindent
    \\textsf{{\\Large {{Email: }}}} \\textsf{{\\Large {invoice['customers']['email']}}} \\\\
    \\textsf{{\\Large {{Phone: }}}} \\textsf{{\\Large {invoice['customers']['phone']}}} \\\\

    \\vspace{{0.5cm}}
    
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        COR-TEN-STEEL USA \\\\
        Mesa Street \\\\
        Hesperia \\\\
        92345 CA \\\\
        Tel: 760-995-2555 \\\\
        Email: usa@cor-ten-steel.com \\\\
 
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Picklist \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{us_time.strftime("%d-%b-%Y %H:%M")}}} 
    \\end{{minipage}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\rule{{\\textwidth}}{{0.5pt}}

    \\vspace{{0.5cm}}

    \\noindent
    \\begin{{tabular}}{{l l}}
    \\textbf{{Total Items:}} & \\texttt{{{info['total_items']}}} \\\\ 
    \\textbf{{Total Weight:}} & \\texttt{{{info['total_weight']}}} \\\\ 
    \\textbf{{Carrier:}} & \\texttt{{{invoice['freight_carrier']}}} \\\\ 
    \\textbf{{Stickers:}} & \\texttt{{{invoice['stickers']}}} \\\\ 
    \\textbf{{Packing Instructions:}} & \\texttt{{{invoice['packing_instructions']}}} \\\\ 
    \\textbf{{Con Note:}} & \\texttt{{{invoice['con_note']}}} \\\\ 
    \\end{{tabular}}

    \\vspace{{0.5cm}}

    \\begin{{longtable}}{{|l|l|l|l|}}
        \\hline
        \\textbf{{Code}} & \\textbf{{Description}} & \\textbf{{Qty}} & \\textbf{{Weight (kgs)}} \\\\
        \\hline
        {picklist_table_rows_us(invoice, components)}
    \\end{{longtable}}
    


    \\end{{document}}
    """
    return latex_source

def picklist_table_rows_us(invoice, components):
    table_rows = ""
    for product in components:
        table_rows += f"\\texttt{{{product['ProductsT']['ProductCode']}}} & \\texttt{{{product['ProductsT']['NameImperial']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{{(product['ProductsT']['Weight'] * product['Quantity']):.1f}}}  \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)