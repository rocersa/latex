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
    nz_time = utc_now.astimezone(pytz.timezone('Pacific/Auckland'))
    au_time = utc_now.astimezone(pytz.timezone('Australia/Sydney'))
    # Generate LaTeX source code
    if country == 'UK':
        latex_source = generate_latex_invoice_uk(invoice, uk_time)
    elif country == 'US':
        latex_source = generate_latex_invoice_us(invoice, us_time)
    elif country == 'NZ':
        latex_source = generate_latex_invoice_nz(invoice, nz_time)
    elif country == 'AU':
        latex_source = generate_latex_invoice_au(invoice, au_time)
    
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
    \\usepackage{{booktabs}}
    \\usepackage{{ragged2e}}
    \\pagestyle{{empty}}

    %% Define new column types:
    \\newcolumntype{{L}}[1]{{>{{\\RaggedRight}}p{{#1\\linewidth}}}}
    \\newcolumntype{{R}}[1]{{>{{\\RaggedLeft}}p{{#1\\linewidth}}}}
    \\newcolumntype{{C}}[1]{{>{{\\Centering}}p{{#1\\linewidth}}}}

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
        \\noindent
        \\texttt{{{invoice['customers']['first_name']}}} \\texttt{{{invoice['customers']['last_name']}}} \\\\""" 
    if invoice['customers']['company']:
        latex_source += f"""
        \\texttt{{{invoice['customers']['company']}}} \\\\""" 
    if invoice['customer_order_number']:
        latex_source += f"""
        \\texttt{{{invoice['customer_order_number']}}} \\\\""" 
    latex_source += f"""
        \\texttt{{{invoice['customers']['email']}}} \\\\
        \\texttt{{{invoice['customers']['phone']}}} \\\\
    """
    if invoice['customers']['second_phone']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['second_phone']}}} \\\\
    """
    if invoice['addresses']['building_name']:
        latex_source += f"""
        \\texttt{{{invoice['addresses']['building_name']}}} \\\\""" 
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
    \\begingroup % limit the scope of the next two instructions
    \\footnotesize % switch to 10pt font
    \\setlength\\tabcolsep{{3pt}} % default: 6pt
    \\begin{{longtable}}{{@{{}} L{{0.4}} C{{0.05}} R{{0.1}} R{{0.1}} R{{0.1}} R{{0.1}} @{{}}}}
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. VAT}} & \\textbf{{VAT (20\%)}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endfirsthead

        \\multicolumn{{6}}{{@{{}}l}}{{{{\\bfseries\\tablename\\ \\thetable}}, continued from previous page}} \\\\
        \\addlinespace
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. VAT}} & \\textbf{{VAT (20\%)}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endhead

        \\midrule
        \\multicolumn{{6}}{{r@{{}}}}{{(Continued on next page)}} \\\\
        \\endfoot

        \\endlastfoot

        {invoice_table_rows_uk(invoice)}
        \\hline
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{£{((invoice['Price']) * (5/6)):.2f}}}}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{£{(invoice['Price']*(1/6)):.2f}}}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{£{invoice['Price']:.2f}}}}} \\\\
        \\cline{{4-6}}"""
    if invoice['amount_paid']:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Amount Paid}} & \\multicolumn{{1}}{{r|}}{{\\texttt{{£{invoice['amount_paid']:.2f}}}}} \\\\
        \\cline{{4-6}}
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. VAT}} & \\multicolumn{{1}}{{r}}{{\\textbf{{£{(invoice['Price'] - invoice['amount_paid']):.2f}}}}} \\\\
        """
    else:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. VAT}} & \\multicolumn{{1}}{{r}}{{\\textbf{{£{(invoice['Price']):.2f}}}}} \\\\"""
    latex_source += f"""
    \\end{{longtable}}
    \\endgroup
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
        table_rows += f"\\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{£{(product['price'] * (5/6)):.2f}}} & \\texttt{{£{(product['price'] * product['Quantity'] * (5/6)):.2f}}} & \\texttt{{£{(product['price'] * product['Quantity'] * (1/6)):.2f}}} & \\texttt{{£{(product['price'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    if invoice['freight_charged'] != 0:
        table_rows += f"\\texttt{{Freight: {invoice['freight_carrier']}}} & \\texttt{{1}} & \\texttt{{£{(invoice['freight_charged'] * (5/6)):.2f}}} & \\texttt{{£{(invoice['freight_charged'] * (5/6)):.2f}}} & \\texttt{{£{(invoice['freight_charged'] * (1/6)):.2f}}} & \\texttt{{£{(invoice['freight_charged']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

def generate_latex_invoice_nz(invoice, nz_time):
    # Generate LaTeX content here (similar to the LaTeX source in your Node.js example)
    tax = 0.15
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\usepackage{{booktabs}}
    \\usepackage{{ragged2e}}
    \\pagestyle{{empty}}

    %% Define new column types:
    \\newcolumntype{{L}}[1]{{>{{\\RaggedRight}}p{{#1\\linewidth}}}}
    \\newcolumntype{{R}}[1]{{>{{\\RaggedLeft}}p{{#1\\linewidth}}}}
    \\newcolumntype{{C}}[1]{{>{{\\Centering}}p{{#1\\linewidth}}}}

    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{COR-TEN-STEEL NZ}}}}
    \\end{{center}}
    \\vspace{{0.5cm}}
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        14 Riverbank Road \\\\
        Otaki \\\\
        5512 \\\\
        04 886 5801 \\\\
        nz@cor-ten-steel.co.nz \\\\
        www.cor-ten-steel.co.nz \\\\
        \\vspace{{0.5cm}}
        \\noindent
        \\texttt{{{invoice['customers']['first_name']}}} \\texttt{{{invoice['customers']['last_name']}}} \\\\""" 
    if invoice['customers']['company']:
        latex_source += f"""
        \\texttt{{{invoice['customers']['company']}}} \\\\""" 
    if invoice['customer_order_number']:
        latex_source += f"""
        \\texttt{{{invoice['customer_order_number']}}} \\\\""" 
    latex_source += f"""
        \\texttt{{{invoice['customers']['email']}}} \\\\
        \\texttt{{{invoice['customers']['phone']}}} \\\\
    """
    if invoice['customers']['second_phone']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['second_phone']}}} \\\\
    """
    if invoice['addresses']['building_name']:
        latex_source += f"""
        \\texttt{{{invoice['addresses']['building_name']}}} \\\\""" 
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
        GST Number: 66 558 215 \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{nz_time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    \\begingroup % limit the scope of the next two instructions
    \\footnotesize % switch to 10pt font
    \\setlength\\tabcolsep{{3pt}} % default: 6pt
    \\begin{{longtable}}{{@{{}} L{{0.4}} C{{0.05}} R{{0.1}} R{{0.1}} R{{0.1}} R{{0.1}} @{{}}}}
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. GST}} & \\textbf{{GST (15\%)}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endfirsthead

        \\multicolumn{{6}}{{@{{}}l}}{{{{\\bfseries\\tablename\\ \\thetable}}, continued from previous page}} \\\\
        \\addlinespace
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. GST}} & \\textbf{{GST (15\%)}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endhead

        \\midrule
        \\multicolumn{{6}}{{r@{{}}}}{{(Continued on next page)}} \\\\
        \\endfoot

        \\endlastfoot

        {invoice_table_rows_nz(invoice, tax)}
        \\hline
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{\${((invoice['Price']) * (1/(1 + tax))):.2f}}}}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{\${(invoice['Price']*(tax/ (1 + tax))):.2f}}}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{\${invoice['Price']:.2f}}}}} \\\\
        \\cline{{4-6}}"""
    if invoice['amount_paid']:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Amount Paid}} & \\multicolumn{{1}}{{r|}}{{\\texttt{{\${invoice['amount_paid']:.2f}}}}} \\\\
        \\cline{{4-6}}
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. GST}} & \\multicolumn{{1}}{{r}}{{\\textbf{{\${(invoice['Price'] - invoice['amount_paid']):.2f}}}}} \\\\
        """
    else:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. GST}} & \\multicolumn{{1}}{{r}}{{\\textbf{{\${(invoice['Price']):.2f}}}}} \\\\"""
    latex_source += f"""
    \\end{{longtable}}
    \\endgroup
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    \\texttt{{Account/Business Name: Rocersa Limited}} \\\\
    \\texttt{{Account Number: 02-0506-0143690-002}} \\\\
    \\texttt{{Reference: {str(invoice['InvoiceID']).zfill(5)}}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source
def invoice_table_rows_nz(invoice, tax):
    table_rows = ""
    for product in invoice["InvoiceComponentsT"]:
        table_rows += f"\\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{\${(product['price'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(product['price'] * product['Quantity'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(product['price'] * product['Quantity'] * (tax/ (1 + tax))):.2f}}} & \\texttt{{\${(product['price'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    if invoice['freight_charged'] != 0:
        table_rows += f"\\texttt{{Freight: {invoice['freight_carrier']}}} & \\texttt{{1}} & \\texttt{{\${(invoice['freight_charged'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(invoice['freight_charged'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(invoice['freight_charged'] * (tax/ (1 + tax))):.2f}}} & \\texttt{{\${(invoice['freight_charged']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows

def generate_latex_invoice_au(invoice, au_time):
    tax = 0.1
    latex_source = f"""
    \\documentclass[a4paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a4paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\usepackage{{booktabs}}
    \\usepackage{{ragged2e}}
    \\pagestyle{{empty}}

    %% Define new column types:
    \\newcolumntype{{L}}[1]{{>{{\\RaggedRight}}p{{#1\\linewidth}}}}
    \\newcolumntype{{R}}[1]{{>{{\\RaggedLeft}}p{{#1\\linewidth}}}}
    \\newcolumntype{{C}}[1]{{>{{\\Centering}}p{{#1\\linewidth}}}}

    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{COR-TEN-STEEL AU}}}}
    \\end{{center}}
    \\vspace{{0.5cm}}
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        53 Hobart St \\\\
        Riverstone 2765 \\\\
        NSW \\\\
        02 8007 3949 \\\\
        aus@cor-ten-steel.com.au \\\\
        www.cor-ten-steel.com.au \\\\
        \\vspace{{0.5cm}}
        \\noindent
        \\texttt{{{invoice['customers']['first_name']}}} \\texttt{{{invoice['customers']['last_name']}}} \\\\""" 
    if invoice['customers']['company']:
        latex_source += f"""
        \\texttt{{{invoice['customers']['company']}}} \\\\""" 
    if invoice['customer_order_number']:
        latex_source += f"""
        \\texttt{{{invoice['customer_order_number']}}} \\\\""" 
    latex_source += f"""
        \\texttt{{{invoice['customers']['email']}}} \\\\
        \\texttt{{{invoice['customers']['phone']}}} \\\\
    """
    if invoice['customers']['second_phone']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['second_phone']}}} \\\\
    """
    if invoice['addresses']['building_name']:
        latex_source += f"""
        \\texttt{{{invoice['addresses']['building_name']}}} \\\\""" 
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
        GST/ABN Number: 35 671 639 843 \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{au_time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    \\begingroup % limit the scope of the next two instructions
    \\footnotesize % switch to 10pt font
    \\setlength\\tabcolsep{{3pt}} % default: 6pt
    \\begin{{longtable}}{{@{{}} L{{0.4}} C{{0.05}} R{{0.1}} R{{0.1}} R{{0.1}} R{{0.1}} @{{}}}}
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. GST}} & \\textbf{{GST (10\%)}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endfirsthead

        \\multicolumn{{6}}{{@{{}}l}}{{{{\\bfseries\\tablename\\ \\thetable}}, continued from previous page}} \\\\
        \\addlinespace
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. GST}} & \\textbf{{GST (10\%)}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endhead

        \\midrule
        \\multicolumn{{6}}{{r@{{}}}}{{(Continued on next page)}} \\\\
        \\endfoot

        \\endlastfoot

        {invoice_table_rows_au(invoice, tax)}
        \\hline
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{\${((invoice['Price']) * (1/(1 + tax))):.2f}}}}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{\${(invoice['Price']*(tax/ (1 + tax))):.2f}}}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{\${invoice['Price']:.2f}}}}} \\\\
        \\cline{{4-6}}"""
    if invoice['amount_paid']:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Amount Paid}} & \\multicolumn{{1}}{{r|}}{{\\texttt{{\${invoice['amount_paid']:.2f}}}}} \\\\
        \\cline{{4-6}}
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. GST}} & \\multicolumn{{1}}{{r}}{{\\textbf{{\${(invoice['Price'] - invoice['amount_paid']):.2f}}}}} \\\\
        """
    else:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. GST}} & \\multicolumn{{1}}{{r}}{{\\textbf{{\${(invoice['Price']):.2f}}}}} \\\\"""
    latex_source += f"""
    \\end{{longtable}}
    \\endgroup
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    \\texttt{{Account/Business Name: Rocersa Limited}} \\\\
    \\texttt{{BSB: 06 2000}} \\\\
    \\texttt{{ACC: 14651089}} \\\\
    \\texttt{{Reference: {str(invoice['InvoiceID']).zfill(5)}}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source
def invoice_table_rows_au(invoice, tax):
    table_rows = ""
    for product in invoice["InvoiceComponentsT"]:
        table_rows += f"\\texttt{{{product['ProductsT']['NameMetric']}}} & \\texttt{{{product['Quantity']}}} & \\texttt{{\${(product['price'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(product['price'] * product['Quantity'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(product['price'] * product['Quantity'] * (tax/ (1 + tax))):.2f}}} & \\texttt{{\${(product['price'] * product['Quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    if invoice['freight_charged'] != 0:
        table_rows += f"\\texttt{{Freight: {invoice['freight_carrier']}}} & \\texttt{{1}} & \\texttt{{\${(invoice['freight_charged'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(invoice['freight_charged'] * (1/(1 + tax))):.2f}}} & \\texttt{{\${(invoice['freight_charged'] * (tax/ (1 + tax))):.2f}}} & \\texttt{{\${(invoice['freight_charged']):.2f}}} \\\\ \n"
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
    \\vspace{{0.5cm}}
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
        \\texttt{{{invoice['customers']['first_name']}}} \\texttt{{{invoice['customers']['last_name']}}} \\\\
    """
    if invoice['customers']['company']:
        latex_source += f"""
    \\texttt{{{invoice['customers']['company']}}} \\\\
    """
    if invoice['addresses']['street_address']:
        latex_source += f"""
    \\texttt{{{invoice['addresses']['street_address']}}} \\\\
    """
    if invoice['addresses']['postal_code']:
        latex_source += f"""
    \\texttt{{{invoice['addresses']['postal_code']}}} \\\\
    """
    if invoice['addresses']['city']:
        latex_source += f"""
    \\texttt{{{invoice['addresses']['city']}}} \\\\
    """
    if invoice['addresses']['state_province']:
        latex_source += f"""
    \\texttt{{{invoice['addresses']['state_province']}}} \\\\
    """
    latex_source += f"""
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        EIN: 47-3791745 \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{us_time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    \\begin{{longtable}}{{|p{{0.4\\textwidth}}|>{{\\centering\\arraybackslash}}p{{0.1\\textwidth}}|p{{0.2\\textwidth}}|p{{0.2\\textwidth}}|}}
        \\hline
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total}} \\\\
        \\hline
        \\endhead
        {invoice_table_rows_us(invoice)}
        """
    if invoice['us_tax_rate'] != 0:
        latex_source += f"""
        \\multicolumn{{2}}{{c|}}{{}} & Subtotal & \\$\\texttt{{{(invoice['Price'] * (100/(100 + invoice['us_tax_rate'])) - invoice['freight_charged']):.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Freight & \\$\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Tax & \\$\\texttt{{{(invoice['Price'] * (invoice['us_tax_rate'] / (100 + invoice['us_tax_rate']))):.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Balance Due & \\$\\texttt{{{(invoice['Price'] ):.2f}}} \\\\
        \\cline{{3-4}}
        \\endfoot
    \\end{{longtable}}
    """
    else:
        latex_source += f"""
        \\multicolumn{{2}}{{c|}}{{}} & Subtotal & \\$\\texttt{{{(invoice['Price'] - invoice['freight_charged']):.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Freight & \\$\\texttt{{{invoice['freight_charged']:.2f}}} \\\\
        \\cline{{3-4}}
        \\multicolumn{{2}}{{c|}}{{}} & Balance due & \\$\\texttt{{{invoice['Price']:.2f}}} \\\\
        \\cline{{3-4}}
        \\endfoot
    \\end{{longtable}}
    """
    latex_source += f"""
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
    us_time = utc_now.astimezone(pytz.timezone('Pacific/Auckland'))
    # Generate LaTeX source code
    if country == 'UK':
        latex_source = generate_latex_picklist_uk(invoice, info, components, uk_time)
    elif country == 'US':
        latex_source = generate_latex_picklist_us(invoice, info, components, us_time)
    elif country == 'NZ':
        latex_source = generate_latex_picklist_nz(invoice, info, components, nz_time)
    
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
    \\textsf{{\\Large {invoice['customers']['email']}}} \\\\
    \\textsf{{\\Large {invoice['customers']['phone']}}} \\\\
    """
    if invoice['customers']['second_phone']:
        latex_source += f"""\\textsf{{\\Large {invoice['customers']['second_phone']}}} \\\\"""
    latex_source += f"""
    \\noindent
    \\textsf{{\\Large {invoice['delivery_instructions']}}} \\\\

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
        \\textbf{{\\fontsize{{20}}{{24}}\\selectfont Picklist}} \\\\
        \\vspace{{1cm}}
        \\small
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

def generate_latex_picklist_nz(invoice, info, components, nz_time):
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
    \\textsf{{\\Large {invoice['customers']['email']}}} \\\\
    \\textsf{{\\Large {invoice['customers']['phone']}}} \\\\
    """
    if invoice['customers']['second_phone']:
        latex_source += f"""\\textsf{{\\Large {invoice['customers']['second_phone']}}} \\\\"""
    latex_source += f"""
    \\noindent
    \\textsf{{\\Large {invoice['delivery_instructions']}}} \\\\

    \\vspace{{0.5cm}}
    
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        COR-TEN-STEEL NZ \\\\
        14 Riverbank Road \\\\
        Otaki 5512 \\\\
        Tel: 04 886 5801 \\\\
        Email: nz@cor-ten-steel.co.nz \\\\
 
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\textbf{{\\fontsize{{20}}{{24}}\\selectfont Picklist}} \\\\
        \\vspace{{1cm}}
        \\small
        Invoice Number: \\texttt{{{str(invoice['InvoiceID']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{nz_time.strftime("%d-%b-%Y %H:%M")}}} 
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
        {picklist_table_rows_nz(invoice, components)}
    \\end{{longtable}}
    


    \\end{{document}}
    """
    return latex_source
def picklist_table_rows_nz(invoice, components):
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
    if invoice['freight_carrier'] == 'Collect':
        latex_source += f"""
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {invoice['addresses']['street_address']}}} \\\\
    """
    else: 
        latex_source += f"""
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {invoice['addresses']['street_address']}}} \\\\
 
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {invoice['addresses']['city']}}} \\\\

    \\textbf{{\\fontsize{{70}}{{84}}\\selectfont {invoice['addresses']['postal_code']} {invoice['addresses']['state_province']}}} \\\\
    """
    latex_source += f"""
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
        \\textbf{{\\fontsize{{20}}{{24}}\\selectfont Picklist}} \\\\
        \\vspace{{1cm}}
        \\small
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