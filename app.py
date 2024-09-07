from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import datetime

app = Flask(__name__)
CORS(app)

@app.route('/generate-pdf-invoice', methods=['POST'])
def generate_pdf_invoice():
    data = request.json
    invoice = data.get('invoice')
    totalPrice = data.get('totalPrice')

    # Generate LaTeX source code
    latex_source = generate_latex_invoice(invoice, totalPrice)
    
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

def generate_latex_invoice(invoice, totalPrice):
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
    
    \\vspace{{1cm}}
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        Cadley \\\\
        SN8 4NE \\\\
        Tel: 0118 234 9909 \\\\
        Email: uk@cor-ten-steel.co.uk \\\\
        \\vspace{{0.5cm}}
        \\textbf{{\\large Customer Details:}} \\\\
        Name: \\texttt{{{invoice['CustomerT']['FirstName']}}} \\texttt{{{invoice['CustomerT']['LastName']}}} \\\\
        Address: \\\\
        \\texttt{{{invoice['CustomerT']['AddressNumber']}}} \\texttt{{{invoice['CustomerT']['AddressStreet']}}} \\\\
        \\texttt{{{invoice['CustomerT']['AddressSuburb']}}} \\texttt{{{invoice['CustomerT']['AddressPostcode']}}} \\\\
        \\texttt{{{invoice['CustomerT']['AddressCity']}}} \\\\
        \\texttt{{{invoice['CustomerT']['AddressCountry']}}}
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        VAT Number: 161 6032 40 \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{datetime.date.today().strftime("%Y-%m-%d")}}}
    \\end{{minipage}}
    
    \\vspace{{1cm}}
    
    \\begin{{longtable}}{{|p{{0.4\\textwidth}}|>{{\\centering\\arraybackslash}}p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|p{{0.2\\textwidth}}|}}
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        \\endhead
        {invoice_table_rows(invoice)}
        \\multicolumn{{2}}{{c|}}{{}} & Subtotal & £\\texttt{{{totalPrice:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Freight & £\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Balance due inc VAT & £\\texttt{{{invoice['Price']:.2f}}} \\\\
        \\cline{{3-4}}
        \\endfoot
    \\end{{longtable}}
    \\vspace{{1cm}}
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    \\texttt{{Account Name: Cor-Ten-Steel}} \\\\
    \\texttt{{Sort Code: 12-34-56}} \\\\
    \\texttt{{Account Number: 12345678}} \\\\
    \\texttt{{Reference: 00003}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source

def invoice_table_rows(invoice):
    table_rows = ""
    for product in invoice["InvoiceComponentsT"]:
        table_rows += f"\\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{£{product['ProductsT']['UKRetailCost']:.2f}}} & \\texttt{{£{(product['ProductsT']['UKRetailCost'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

@app.route('/generate-pdf-picklist', methods=['POST'])
def generate_pdf_picklist():
    data = request.json
    invoice = data.get('invoice')
    totalPrice = data.get('totalPrice')
    components = data.get('components')

    # Generate LaTeX source code
    latex_source = generate_latex_picklist(invoice, totalPrice, components)
    
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

def generate_latex_picklist(invoice, totalPrice, components):
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
    
    \\begin{{center}}
        \\textbf{{\\Huge {{COR-TEN-STEEL UK}}}}
    \\end{{center}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\texttt{{Deliver to:}} \\\\

    \\noindent
    \\textbf{{\\fontsize{{20}}{{24}} {invoice['CustomerT']['FirstName']}}} \\textbf{{\\fontsize{{20}}{{24}} {invoice['CustomerT']['LastName']}}} \\\\
    \\textbf{{\\fontsize{{30}}{{36}} {invoice['CustomerT']['AddressNumber']}}} \\textbf{{\\fontsize{{30}}{{36}} {invoice['CustomerT']['AddressStreet']}}} \\\\
    \\textbf{{\\fontsize{{50}}{{60}} {invoice['CustomerT']['AddressSuburb']}}} \\\\

    \\noindent
    \\textbf{{\\fontsize{{70}}{{84}} {invoice['CustomerT']['AddressPostcode']}}} \\\\
    \\textsf{{\\Large {{Email: }}}} \\textsf{{\\Large {invoice['CustomerT']['Email']}}} \\\\
    \\textsf{{\\Large {{Phone: }}}} \\textsf{{\\Large {invoice['CustomerT']['Phone']}}} \\\\

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
        Date Issued: \\texttt{{{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}}} 
    \\end{{minipage}}
    
    \\vspace{{0.5cm}}

    \\begin{{longtable}}{{|l|>{{\\centering\\arraybackslash}}p{{0.45\\textwidth}}|p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|}}
        \\hline
        \\textbf{{Code}} & \\textbf{{Description}} & \\textbf{{Qty}} & \\textbf{{Weight (kgs)}} \\\\
        \\hline
        \\endhead
        {picklist_table_rows(invoice, components)}
    \\end{{longtable}}
    
    \\noindent
    \\begin{{tabular}}{{l l}}
    \\textbf{{Total Items:}} & \\texttt{{17}} \\\\ 
    \\textbf{{Total Weight:}} & \\texttt{{100 kgs}} \\\\ 
    \\textbf{{Carrier:}} & \\texttt{{Fastways}} \\\\ 
    \\textbf{{Stickers:}} & \\texttt{{1 Orange 1 Green}} \\\\ 
    \\textbf{{Packing Instructions:}} & \\texttt{{2 Parcels 20 kg each}} \\\\ 
    \\textbf{{Con Note:}} & \\texttt{{N/A}} \\\\ 
    \\end{{tabular}}

    \\end{{document}}
    """
    return latex_source

def picklist_table_rows(invoice, components):
    table_rows = ""
    for product in components:
        table_rows += f"\\texttt{{{product['ProductsT']['ProductCode']}}} & \\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{{(product['ProductsT']['Weight'] * product['Quantity']):.2f}}}  \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)