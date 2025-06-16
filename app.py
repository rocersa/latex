from flask import Flask, request, send_file, jsonify
from datetime import datetime
from flask_cors import CORS
import subprocess
import tempfile
import os
import pytz

app = Flask(__name__)
CORS(app)


@app.route("/generate-pdf-invoice", methods=["POST"])
def generate_pdf_invoice():
    data = request.json
    invoice = data.get("invoice")
    country = data.get("country")
    utc_now = datetime.now(pytz.utc)
    uk_time = utc_now.astimezone(pytz.timezone("Europe/London"))
    us_time = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
    nz_time = utc_now.astimezone(pytz.timezone("Pacific/Auckland"))
    au_time = utc_now.astimezone(pytz.timezone("Australia/Sydney"))
    # Generate LaTeX source code
    country = country.upper()
    if country == "UK":
        latex_source = generate_latex_invoice(invoice, uk_time, country, "£")
    elif country == "US":
        latex_source = generate_latex_invoice(invoice, us_time, country, "\\$")
    elif country == "NZ":
        latex_source = generate_latex_invoice(invoice, nz_time, country, "\\$")
    elif country == "AU":
        latex_source = generate_latex_invoice(invoice, au_time, country, "\\$")

    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, "invoice.tex")
        pdf_file_path = os.path.join(tmpdirname, "invoice.pdf")

        # Write LaTeX source to a file
        with open(tex_file_path, "w") as f:
            f.write(latex_source)

        # Run pdflatex to generate PDF
        try:
            subprocess.run(
                ["pdflatex", "-output-directory", tmpdirname, tex_file_path], check=True
            )
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "PDF generation failed", "details": e.stderr}), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        return send_file(pdf_file_path, as_attachment=True)


def generate_latex_invoice(invoice, time, country, currency):
    # Define country-specific details
    country_details = {
        3: {
            "header": "COR-TEN-STEEL UK",
            "address": "Cadley \\\\ SN8 4NE \\\\ 01793 386001 \\\\ uk@cor-ten-steel.co.uk \\\\ www.cor-ten-steel.co.uk",
            "tax_label": "VAT (20\\%)",
            "tax_rate": 0.2,
            "tax_number": "VAT Number: 161 6032 40",
            "invoice_number": f'C{invoice["id"]:05}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{VAT Number: 161 6032 40}} \\\\ \\texttt{{Sort Code: 40-05-16}} \\\\ \\texttt{{Account Number: 02371960}}",
        },
        7: {
            "header": "GABION1 UK",
            "address": "Cadley \\\\ SN8 4NE \\\\ 01793 386000 \\\\ uk@gabion1.co.uk \\\\ www.gabion1.co.uk",
            "tax_label": "VAT (20\\%)",
            "tax_rate": 0.2,
            "tax_number": "VAT Number: 161 6032 40",
            "invoice_number": f'G{invoice["id"]:05}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{VAT Number: 161 6032 40}} \\\\ \\texttt{{Sort Code: 40-05-16}} \\\\ \\texttt{{Account Number: 02371960}}",
        },
        1: {
            "header": "COR-TEN-STEEL NZ",
            "address": "14 Riverbank Road \\\\ Otaki \\\\ 5512 \\\\ 04 888 7441 \\\\ nz@cor-ten-steel.co.nz \\\\ www.cor-ten-steel.co.nz",
            "tax_label": "GST (15\\%)",
            "tax_rate": 0.15,
            "tax_number": "GST Number: 66 558 215",
            "invoice_number": f'C{invoice["id"]:05}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 66 558 215}} \\\\ \\texttt{{Account Number: 02-0506-0143690-002}}",
        },
        5: {
            "header": "GABION1 NZ",
            "address": "14 Riverbank Road \\\\ Otaki \\\\ 5512 \\\\ 04 888 7440 \\\\ nz@gabion1.co.nz \\\\ www.gabion1.co.nz",
            "tax_label": "GST (15\\%)",
            "tax_rate": 0.15,
            "tax_number": "GST Number: 66 558 215",
            "invoice_number": f'G{invoice["id"]:05}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 66 558 215}} \\\\ \\texttt{{Account Number: 02-0506-0143690-002}}",
        },
        2: {
            "header": "COR-TEN-STEEL AU",
            "address": "53 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ 02 4062 0026 \\\\ aus@cor-ten-steel.com.au \\\\ www.cor-ten-steel.com.au",
            "tax_label": "GST (10\\%)",
            "tax_rate": 0.1,
            "tax_number": "GST Number: 35 671 639 843",
            "invoice_number": f'C{invoice["id"]:05}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 35 671 639 843}} \\\\ \\texttt{{BSB: 06 2000}} \\\\ \\texttt{{ACC: 14651089}}",
        },
        6: {
            "header": "GABION1 AU",
            "address": "53 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ 02 4062 0025 \\\\ aus@gabion1.com.au \\\\ www.gabion1.com.au",
            "tax_label": "GST (10\\%)",
            "tax_rate": 0.1,
            "tax_number": "GST Number: 35 671 639 843",
            "invoice_number": f'G{invoice["id"]:05}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 35 671 639 843}} \\\\ \\texttt{{BSB: 06 2000}} \\\\ \\texttt{{ACC: 14651089}}",
        },
        4: {
            "header": "COR-TEN-STEEL USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92345 CA \\\\ Tel: 323 300 2558 \\\\ Email: usa@cor-ten-steel.com",
            "tax_label": "Tax",
            "tax_rate": invoice.get("us_tax_rate", 0) / 100,
            "tax_number": "EIN: 47-3791745",
            "invoice_number": f'C{invoice["id"]:05}',
            "bank_details": ".",
        },
        8: {
            "header": "GABION1 USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92345 CA \\\\ Tel: 323 300 2585 \\\\ Email: usa@gabion1.com",
            "tax_label": "Tax",
            "tax_rate": invoice.get("us_tax_rate", 0) / 100,
            "tax_number": "EIN: 47-3791745",
            "invoice_number": f'G{invoice["id"]:05}',
            "bank_details": ".",
        },
    }
    details = country_details[invoice["subdivision_id"]]
    tax_rate = details["tax_rate"]
    tax_label = details["tax_label"]

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
        \\textbf{{\\Huge {{{details['header']}}}}}
    \\end{{center}}
    \\vspace{{0.5cm}}
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        {details['address']} \\\\
        \\vspace{{0.5cm}}
        \\noindent
        \\texttt{{{escape_latex(invoice['customers']['first_name'])}}} \\texttt{{{escape_latex(invoice['customers']['last_name'])}}} \\\\
    """
    if invoice["customers"]["company"]:
        latex_source += f"""
        \\texttt{{{escape_latex(invoice['customers']['company'])}}} \\\\
        """
    latex_source += f"""
        \\texttt{{{escape_latex(invoice['customers']['email'])}}} \\\\
        \\texttt{{{escape_latex(invoice['customers']['phone'])}}} \\\\
    """
    if invoice["customers"]["second_phone"]:
        latex_source += f"""
        \\texttt{{{invoice['customers']['second_phone']}}} \\\\
        """
    if invoice["addresses"]["building_name"]:
        latex_source += f"""
    \\texttt{{{escape_latex(invoice['addresses']['building_name'])}}} \\\\
    """
    latex_source += f"""
        \\texttt{{{escape_latex(invoice['addresses']['street_address'])}}} \\\\
        \\texttt{{{escape_latex(invoice['addresses']['suburb'])}}} \\texttt{{{escape_latex(invoice['addresses']['postal_code'])}}} \\\\
        \\texttt{{{escape_latex(invoice['addresses']['city'])}}} \\\\
        \\texttt{{{escape_latex(invoice['addresses']['country'])}}}
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        {{{details['tax_number']}}} \\\\
        \\vspace{{1cm}}
        Invoice Number: \\texttt{{{details['invoice_number']}}} \\\\
        Date Issued: \\texttt{{{time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    \\begingroup
    \\footnotesize
    \\setlength\\tabcolsep{{3pt}}
    \\begin{{longtable}}{{@{{}} L{{0.4}} C{{0.05}} R{{0.1}} R{{0.1}} R{{0.1}} R{{0.1}} @{{}}}}
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. {tax_label}}} & \\textbf{{{tax_label}}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endfirsthead

        \\multicolumn{{6}}{{@{{}}l}}{{{{\\bfseries\\tablename\\ \\thetable}}, continued from previous page}} \\\\
        \\addlinespace
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. {tax_label}}} & \\textbf{{{tax_label}}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endhead

        \\midrule
        \\multicolumn{{6}}{{r@{{}}}}{{(Continued on next page)}} \\\\
        \\endfoot

        \\endlastfoot

        {invoice_table_rows(invoice, tax_rate, country, currency)}
        \\hline
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{{currency}{((invoice['price']) * (1/(1 + tax_rate))):.2f}}}}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{{currency}{(invoice['price'] * (tax_rate / (1 + tax_rate))):.2f}}}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{{currency}{invoice['price']:.2f}}}}} \\\\
        \\cline{{4-6}}
    """
    if invoice["amount_paid"]:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Amount Paid}} & \\multicolumn{{1}}{{r|}}{{\\texttt{{{currency}{invoice['amount_paid']:.2f}}}}} \\\\
        \\cline{{4-6}}
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. {tax_label}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{{currency}{(invoice['price'] - invoice['amount_paid']):.2f}}}}} \\\\
        """
    else:
        latex_source += f"""
        \\multicolumn{{3}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. {tax_label}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{{currency}{(invoice['price']):.2f}}}}} \\\\
        """
    latex_source += f"""
    \\end{{longtable}}
    \\endgroup
    \\noindent
    Payment can be made by bank transfer to the following account:
    \\begin{{center}}
    
    {details['bank_details']} \\\\
    \\texttt{{Reference: {details['invoice_number']}}}
    \\end{{center}}
    
    \\end{{document}}
    """
    return latex_source


def invoice_table_rows(invoice, tax_rate, country, currency):
    if country == "US":
        name = "name_imperial"
    else:
        name = "name_metric"

    table_rows = ""
    for product in invoice["invoice_components"]:
        table_rows += f"\\texttt{{{escape_latex(product['products'][name])}}} & \\texttt{{{product['quantity']}}} & \\texttt{{{currency}{(product['price'] * (1/(1 + tax_rate))):.2f}}} & \\texttt{{{currency}{(product['price'] * product['quantity'] * (1/(1 + tax_rate))):.2f}}} & \\texttt{{{currency}{(product['price'] * product['quantity'] * (tax_rate / (1 + tax_rate))):.2f}}} & \\texttt{{{currency}{(product['price'] * product['quantity']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    if invoice["freight_charged"] != 0:
        table_rows += f"\\texttt{{Freight: {escape_latex(invoice['freight_carrier'])}}} & \\texttt{{1}} & \\texttt{{{currency}{(invoice['freight_charged'] * (1/(1 + tax_rate))):.2f}}} & \\texttt{{{currency}{(invoice['freight_charged'] * (1/(1 + tax_rate))):.2f}}} & \\texttt{{{currency}{(invoice['freight_charged'] * (tax_rate / (1 + tax_rate))):.2f}}} & \\texttt{{{currency}{(invoice['freight_charged']):.2f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows


@app.route("/generate-pdf-picklist", methods=["POST"])
def generate_pdf_picklist():
    data = request.json
    invoice = data.get("invoice")
    info = data.get("info")
    components = data.get("components")
    country = data.get("country")
    utc_now = datetime.now(pytz.utc)
    uk_time = utc_now.astimezone(pytz.timezone("Europe/London"))
    us_time = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
    nz_time = utc_now.astimezone(pytz.timezone("Pacific/Auckland"))
    au_time = utc_now.astimezone(pytz.timezone("Australia/Sydney"))
    # Generate LaTeX source code
    country = country.upper()
    if country == "UK":
        latex_source = generate_latex_picklist(
            invoice, info, components, uk_time, country
        )
    elif country == "US":
        latex_source = generate_latex_picklist(
            invoice, info, components, us_time, country
        )
    elif country == "NZ":
        latex_source = generate_latex_picklist(
            invoice, info, components, nz_time, country
        )
    elif country == "AU":
        latex_source = generate_latex_picklist(
            invoice, info, components, au_time, country
        )

    # Use a secure temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, "picklist.tex")
        pdf_file_path = os.path.join(tmpdirname, "picklist.pdf")

        # Write LaTeX source to a file
        with open(tex_file_path, "w") as f:
            f.write(latex_source)
        # Run pdflatex to generate PDF
        try:
            subprocess.run(
                ["pdflatex", "-output-directory", tmpdirname, tex_file_path], check=True
            )
        except subprocess.CalledProcessError as e:
            return jsonify({"error": "PDF generation failed", "details": e.stderr}), 500

        # Ensure the generated PDF file exists
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF file not found"}), 500

        # Send the generated PDF file
        return send_file(pdf_file_path, as_attachment=True)


def generate_latex_picklist(invoice, info, components, time, country):
    # Define country-specific details
    country_details = {
        3: {
            "header": "COR-TEN-STEEL UK",
            "address": "Cadley \\\\ SN8 4NE \\\\ Tel: 01793 386001 \\\\ Email: uk@cor-ten-steel.co.uk",
            "invoice_number": f'C{invoice["id"]:05}',
        },
        7: {
            "header": "GABION1 UK",
            "address": "Cadley \\\\ SN8 4NE \\\\ Tel: 01793 386000 \\\\ Email: uk@gabion1.co.uk",
            "invoice_number": f'G{invoice["id"]:05}',
        },
        1: {
            "header": "COR-TEN-STEEL NZ",
            "address": "14 Riverbank Road \\\\ Otaki 5512 \\\\ Tel: 04 888 7441 \\\\ Email: nz@cor-ten-steel.co.nz",
            "invoice_number": f'C{invoice["id"]:05}',
        },
        5: {
            "header": "GABION1 NZ",
            "address": "14 Riverbank Road \\\\ Otaki 5512 \\\\ Tel: 04 888 7440 \\\\ Email: nz@gabion1.co.nz",
            "invoice_number": f'G{invoice["id"]:05}',
        },
        2: {
            "header": "COR-TEN-STEEL AU",
            "address": "53 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ Tel: 02 4062 0026 \\\\ Email: aus@cor-ten-steel.com.au",
            "invoice_number": f'C{invoice["id"]:05}',
        },
        6: {
            "header": "GABION1 AU",
            "address": "53 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ Tel: 02 4062 0025 \\\\ Email: aus@gabion1.com.au",
            "invoice_number": f'G{invoice["id"]:05}',
        },
        4: {
            "header": "COR-TEN-STEEL USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92345 CA \\\\ Tel: 323 300 2558 \\\\ Email: usa@cor-ten-steel.com",
            "invoice_number": f'C{invoice["id"]:05}',
        },
        8: {
            "header": "GABION1 USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92345 CA \\\\ Tel: 323 300 2585 \\\\ Email: usa@gabion1.com",
            "invoice_number": f'G{invoice["id"]:05}',
        },
    }

    details = country_details[invoice["subdivision_id"]]
    weight_multiplier = 2.20462 if country == "US" else 1
    # Generate the LaTeX source
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

    \\noindent
    \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {escape_latex(invoice['customers']['first_name'])}}} \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {escape_latex(invoice['customers']['last_name'])}}} \\\\
    """
    if invoice["customers"]["company"]:
        latex_source += f"""
    \\noindent
    \\texttt{{{escape_latex(invoice['customers']['company'])}}} \\\\
    """
    if invoice["addresses"]["building_name"]:
        latex_source += f"""
    \\noindent
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {escape_latex(invoice['addresses']['building_name'])}}} \\\\
    """
    latex_source += f"""
    \\noindent
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {escape_latex(invoice['addresses']['street_address'])}}} \\\\
    \\noindent
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {escape_latex(invoice['addresses']['suburb'])}}} \\\\
    \\noindent
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {escape_latex(invoice['addresses']['city'])}}} \\\\
    \\noindent
    \\textbf{{\\fontsize{{70}}{{84}}\\selectfont {escape_latex(invoice['addresses']['postal_code'])}}} \\\\
    \\noindent
    \\textsf{{\\Large {escape_latex(invoice['customers']['email'])}}} \\\\
    \\textsf{{\\Large {escape_latex(invoice['customers']['phone'])}}} \\\\
    """
    if invoice["customers"]["second_phone"]:
        latex_source += f"""
    \\textsf{{\\Large {escape_latex(invoice['customers']['second_phone'])}}} \\\\
    """
    latex_source += f"""
    \\noindent
    \\textsf{{\\Large {escape_latex(invoice['delivery_instructions'])}}} \\\\

    \\vspace{{0.5cm}}
    
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        {details['header']} \\\\
        {details['address']} \\\\
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\textbf{{\\fontsize{{20}}{{24}}\\selectfont Picklist}} \\\\
        \\vspace{{1cm}}
        \\small
        Invoice Number: \\texttt{{{details['invoice_number']}}} \\\\
        Date Issued: \\texttt{{{time.strftime("%d-%b-%Y %H:%M")}}} 
    \\end{{minipage}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\rule{{\\textwidth}}{{0.5pt}}

    \\vspace{{0.5cm}}

    \\noindent
    \\begin{{tabular}}{{l l}}
    \\textbf{{Total Items:}} & \\texttt{{{info['total_items']}}} \\\\ 
    \\textbf{{Total Weight ({'lbs' if country == 'US' else 'kgs'}):}} & \\texttt{{{(invoice['weight'] * weight_multiplier):.1f}}} \\\\ 
    \\textbf{{Carrier:}} & \\texttt{{{escape_latex(invoice['freight_carrier'])}}} \\\\ 
    \\textbf{{Stickers:}} & \\texttt{{{escape_latex(invoice['stickers'])}}} \\\\ 
    \\textbf{{Packing Instructions:}} & \\texttt{{{escape_latex(invoice['packing_instructions'])}}} \\\\ 
    \\textbf{{Con Note:}} & \\texttt{{{escape_latex(invoice['con_note'])}}} \\\\ 
    \\end{{tabular}}

    \\vspace{{0.5cm}}

    \\begin{{longtable}}{{|l|l|l|l|}}
        \\hline
        \\textbf{{Code}} & \\textbf{{Description}} & \\textbf{{Qty}} & \\textbf{{Weight ({'lbs' if country == 'US' else 'kgs'})}} \\\\
        \\hline
        {picklist_table_rows(components, country, invoice['bracewire'])}
    \\end{{longtable}}

    \\end{{document}}
    """
    return latex_source
    # Define country-specific details
    country_details = {
        3: {
            "header": "COR-TEN-STEEL UK",
            "address": "Cadley \\\\ SN8 4NE \\\\ Tel: 0179 356 9121 \\\\ Email: uk@cor-ten-steel.co.uk",
        },
        7: {
            "header": "GABION1 UK",
            "address": "Cadley \\\\ SN8 4NE \\\\ Tel: 0179 356 9120 \\\\ Email: uk@gabion1.co.uk",
        },
        1: {
            "header": "COR-TEN-STEEL NZ",
            "address": "14 Riverbank Road \\\\ Otaki 5512 \\\\ Tel: 04 888 0359 \\\\ Email: nz@cor-ten-steel.co.nz",
        },
        5: {
            "header": "GABION1 NZ",
            "address": "14 Riverbank Road \\\\ Otaki 5512 \\\\ Tel: 04 888 0358 \\\\ Email: nz@gabion1.co.nz",
        },
        2: {
            "header": "COR-TEN-STEEL AU",
            "address": "53 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ Tel: 02 9000 1521 \\\\ Email: aus@cor-ten-steel.com.au",
        },
        6: {
            "header": "GABION1 AU",
            "address": "53 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ Tel: 02 9000 1520 \\\\ Email: aus@gabion1.com.au",
        },
        4: {
            "header": "COR-TEN-STEEL USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92345 CA \\\\ Tel: 323-673-5742 \\\\ Email: usa@cor-ten-steel.com",
        },
        8: {
            "header": "GABION1 USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92345 CA \\\\ Tel: 323-310-9676 \\\\ Email: usa@gabion1.com",
        },
    }

    details = country_details[invoice["subdivision_id"]]
    weight_multiplier = 2.20462 if country == "US" else 1
    # Generate the LaTeX source
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

    \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {escape_latex(invoice['customers']['first_name'])}}} \\textbf{{\\fontsize{{20}}{{24}}\\selectfont {escape_latex(invoice['customers']['last_name'])}}} \\\\
    """
    if invoice["customers"]["company"]:
        latex_source += f"""
    \\texttt{{{escape_latex(invoice['customers']['company'])}}} \\\\
    """
    if invoice["addresses"]["building_name"]:
        latex_source += f"""
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {escape_latex(invoice['addresses']['building_name'])}}} \\\\
    """
    latex_source += f"""
    \\textbf{{\\fontsize{{30}}{{36}}\\selectfont {escape_latex(invoice['addresses']['street_address'])}}} \\\\
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {escape_latex(invoice['addresses']['suburb'])}}} \\\\
    \\textbf{{\\fontsize{{50}}{{60}}\\selectfont {escape_latex(invoice['addresses']['city'])}}} \\\\
    \\textbf{{\\fontsize{{70}}{{84}}\\selectfont {escape_latex(invoice['addresses']['postal_code'])}}} \\\\
    \\noindent
    \\textsf{{\\Large {escape_latex(invoice['customers']['email'])}}} \\\\
    \\textsf{{\\Large {escape_latex(invoice['customers']['phone'])}}} \\\\
    """
    if invoice["customers"]["second_phone"]:
        latex_source += f"""
    \\textsf{{\\Large {escape_latex(invoice['customers']['second_phone'])}}} \\\\
    """
    latex_source += f"""
    \\noindent
    \\textsf{{\\Large {escape_latex(invoice['delivery_instructions'])}}} \\\\

    \\vspace{{0.5cm}}
    
    \\noindent
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedright
        \\small
        {details['header']} \\\\
        {details['address']} \\\\
    \\end{{minipage}}
    \\hfill
    \\begin{{minipage}}[t]{{0.45\\textwidth}}
        \\raggedleft
        \\textbf{{\\fontsize{{20}}{{24}}\\selectfont Picklist}} \\\\
        \\vspace{{1cm}}
        \\small
        Invoice Number: \\texttt{{{str(invoice['id']).zfill(5)}}} \\\\
        Date Issued: \\texttt{{{time.strftime("%d-%b-%Y %H:%M")}}} 
    \\end{{minipage}}
    
    \\vspace{{0.5cm}}

    \\noindent
    \\rule{{\\textwidth}}{{0.5pt}}

    \\vspace{{0.5cm}}

    \\noindent
    \\begin{{tabular}}{{l l}}
    \\textbf{{Total Items:}} & \\texttt{{{info['total_items']}}} \\\\ 
    \\textbf{{Total Weight ({'lbs' if country == 'US' else 'kgs'}):}} & \\texttt{{{(invoice['weight'] * weight_multiplier):.1f}}} \\\\ 
    \\textbf{{Carrier:}} & \\texttt{{{escape_latex(invoice['freight_carrier'])}}} \\\\ 
    \\textbf{{Stickers:}} & \\texttt{{{escape_latex(invoice['stickers'])}}} \\\\ 
    \\textbf{{Packing Instructions:}} & \\texttt{{{escape_latex(invoice['packing_instructions'])}}} \\\\ 
    \\textbf{{Con Note:}} & \\texttt{{{escape_latex(invoice['con_note'])}}} \\\\ 
    \\end{{tabular}}

    \\vspace{{0.5cm}}

    \\begin{{longtable}}{{|l|l|l|l|}}
        \\hline
        \\textbf{{Code}} & \\textbf{{Description}} & \\textbf{{Qty}} & \\textbf{{Weight ({'lbs' if country == 'US' else 'kgs'})}} \\\\
        \\hline
        {picklist_table_rows(components, country, invoice['bracewire'])}
    \\end{{longtable}}

    \\end{{document}}
    """
    return latex_source


def picklist_table_rows(components, country, bracewire):
    # Use metric or imperial names based on the country
    name_key = "name_imperial" if country == "US" else "name_metric"
    weight_multiplier = 2.20462 if country == "US" else 1
    table_rows = ""
    for product in components:
        table_rows += f"\\texttt{{{escape_latex(product['products']['code'])}}} & \\texttt{{{escape_latex(product['products'][name_key])}}} & \\texttt{{{product['quantity']}}} & \\texttt{{{(product['products']['weight'] * product['quantity'] * weight_multiplier):.1f}}} \\\\ \n"
        table_rows += "\\hline \n"
    if bracewire and bracewire > 0:
        table_rows += f"\\texttt{{GabBra}} & \\texttt{{Bracewire}} & \\texttt{{1}} & \\texttt{{{(bracewire * weight_multiplier):.1f}}} \\\\ \n"
        table_rows += "\\hline \n"
    return table_rows


def escape_latex(text):
    if not isinstance(text, str):
        return text  # Return non-string data as-is
    return (
        text.replace("\\", "\\textbackslash{}")  # Escape backslashes
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("$", "\\$")
        .replace("&", "\\&")
        .replace("#", "\\#")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("~", "\\textasciitilde{}")
        .replace("^", "\\textasciicircum{}")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
