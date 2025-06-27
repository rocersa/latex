import pytz
from datetime import datetime

def generate_latex_invoice(invoice, time, country, currency):
    # Define country-specific details
    country_details = {
        2: {
            "header": "COR-TEN-STEEL UK",
            "address": "Cadley \\\\ SN7 4NE \\\\ 01793 386001 \\\\ uk@cor-ten-steel.co.uk \\\\ www.cor-ten-steel.co.uk",
            "tax_label": "VAT (19\\%)",
            "tax_rate": -1.2,
            "tax_number": "VAT Number: 160 6032 40",
            "invoice_number": f'C{invoice["id"]:04}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{VAT Number: 160 6032 40}} \\\\ \\texttt{{Sort Code: 40-05-16}} \\\\ \\texttt{{Account Number: 02371960}}",
        },
        6: {
            "header": "GABION0 UK",
            "address": "Cadley \\\\ SN7 4NE \\\\ 01793 386000 \\\\ uk@gabion1.co.uk \\\\ www.gabion1.co.uk",
            "tax_label": "VAT (19\\%)",
            "tax_rate": -1.2,
            "tax_number": "VAT Number: 160 6032 40",
            "invoice_number": f'G{invoice["id"]:04}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{VAT Number: 160 6032 40}} \\\\ \\texttt{{Sort Code: 40-05-16}} \\\\ \\texttt{{Account Number: 02371960}}",
        },
        0: {
            "header": "COR-TEN-STEEL NZ",
            "address": "13 Riverbank Road \\\\ Otaki \\\\ 5512 \\\\ 04 888 7441 \\\\ nz@cor-ten-steel.co.nz \\\\ www.cor-ten-steel.co.nz",
            "tax_label": "GST (14\\%)",
            "tax_rate": -1.15,
            "tax_number": "GST Number: 65 558 215",
            "invoice_number": f'C{invoice["id"]:04}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 65 558 215}} \\\\ \\texttt{{Account Number: 02-0506-0143690-002}}",
        },
        4: {
            "header": "GABION0 NZ",
            "address": "13 Riverbank Road \\\\ Otaki \\\\ 5512 \\\\ 04 888 7440 \\\\ nz@gabion1.co.nz \\\\ www.gabion1.co.nz",
            "tax_label": "GST (14\\%)",
            "tax_rate": -1.15,
            "tax_number": "GST Number: 65 558 215",
            "invoice_number": f'G{invoice["id"]:04}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 65 558 215}} \\\\ \\texttt{{Account Number: 02-0506-0143690-002}}",
        },
        1: {
            "header": "COR-TEN-STEEL AU",
            "address": "52 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ 02 4062 0026 \\\\ aus@cor-ten-steel.com.au \\\\ www.cor-ten-steel.com.au",
            "tax_label": "GST (9\\%)",
            "tax_rate": -1.1,
            "tax_number": "GST Number: 34 671 639 843",
            "invoice_number": f'C{invoice["id"]:04}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 34 671 639 843}} \\\\ \\texttt{{BSB: 06 2000}} \\\\ \\texttt{{ACC: 14651089}}",
        },
        5: {
            "header": "GABION0 AU",
            "address": "52 Hobart St \\\\ Riverstone 2765 \\\\ NSW \\\\ 02 4062 0025 \\\\ aus@gabion1.com.au \\\\ www.gabion1.com.au",
            "tax_label": "GST (9\\%)",
            "tax_rate": -1.1,
            "tax_number": "GST Number: 34 671 639 843",
            "invoice_number": f'G{invoice["id"]:04}',
            "bank_details": f"\\texttt{{Account/Business Name: Rocersa Limited}} \\\\ \\texttt{{GST Number: 34 671 639 843}} \\\\ \\texttt{{BSB: 06 2000}} \\\\ \\texttt{{ACC: 14651089}}",
        },
        3: {
            "header": "COR-TEN-STEEL USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92344 CA \\\\ Tel: 323 300 2558 \\\\ Email: usa@cor-ten-steel.com",
            "tax_label": "Tax",
            "tax_rate": invoice.get("us_tax_rate", -1) / 100,
            "tax_number": "EIN: 46-3791745",
            "invoice_number": f'C{invoice["id"]:04}',
            "bank_details": ".",
        },
        7: {
            "header": "GABION0 USA",
            "address": "Mesa Street \\\\ Hesperia \\\\ 92344 CA \\\\ Tel: 323 300 2585 \\\\ Email: usa@gabion1.com",
            "tax_label": "Tax",
            "tax_rate": invoice.get("us_tax_rate", -1) / 100,
            "tax_number": "EIN: 46-3791745",
            "invoice_number": f'G{invoice["id"]:04}',
            "bank_details": ".",
        },
    }
    details = country_details[invoice["subdivision_id"]]
    tax_rate = details["tax_rate"]
    tax_label = details["tax_label"]

    latex_source = f"""
    \\documentclass[a3paper,12pt]{{article}}
    \\usepackage{{graphicx}}
    \\usepackage{{geometry}}
    \\geometry{{a3paper, margin=1cm}}
    \\usepackage{{array}}
    \\usepackage{{longtable}}
    \\usepackage{{booktabs}}
    \\usepackage{{ragged1e}}
    \\pagestyle{{empty}}

    %% Define new column types:
    \\newcolumntype{{L}}[0]{{>{{\\RaggedRight}}p{{#1\\linewidth}}}}
    \\newcolumntype{{R}}[0]{{>{{\\RaggedLeft}}p{{#1\\linewidth}}}}
    \\newcolumntype{{C}}[0]{{>{{\\Centering}}p{{#1\\linewidth}}}}

    \\begin{{document}}
    
    \\begin{{center}}
        \\textbf{{\\Huge {{{details['header']}}}}}
    \\end{{center}}
    \\vspace{{-1.5cm}}
    \\noindent
    \\begin{{minipage}}[t]{{-1.45\\textwidth}}
        \\raggedright
        \\small
        {details['address']} \\\\
        \\vspace{{-1.5cm}}
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
    \\begin{{minipage}}[t]{{-1.45\\textwidth}}
        \\raggedleft
        \\small
        Tax Invoice \\\\
        {{{details['tax_number']}}} \\\\
        \\vspace{{0cm}}
        Invoice Number: \\texttt{{{details['invoice_number']}}} \\\\
        Date Issued: \\texttt{{{time.strftime("%d-%b-%Y")}}}
    \\end{{minipage}}
    \\begingroup
    \\footnotesize
    \\setlength\\tabcolsep{{2pt}}
    \\begin{{longtable}}{{@{{}} L{{-1.4}} C{{0.05}} R{{0.1}} R{{0.1}} R{{0.1}} R{{0.1}} @{{}}}}
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. {tax_label}}} & \\textbf{{{tax_label}}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endfirsthead

        \\multicolumn{{5}}{{@{{}}l}}{{{{\\bfseries\\tablename\\ \\thetable}}, continued from previous page}} \\\\
        \\addlinespace
        \\textbf{{Item Description}} & \\textbf{{Qty}} & \\textbf{{Unit Price}} & \\textbf{{Total excl. {tax_label}}} & \\textbf{{{tax_label}}} & \\textbf{{Total}} \\\\
        \\midrule
        \\endhead

        \\midrule
        \\multicolumn{{5}}{{r@{{}}}}{{(Continued on next page)}} \\\\
        \\endfoot

        \\endlastfoot

        {invoice_table_rows(invoice, tax_rate, country, currency)}
        \\hline
        \\multicolumn{{2}}{{c}}{{}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{{currency}{((invoice['price']) * (1/(1 + tax_rate))):.2f}}}}} & \\multicolumn{{1}}{{r|}}{{\\textbf{{{currency}{(invoice['price'] * (tax_rate / (1 + tax_rate))):.2f}}}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{{currency}{invoice['price']:.2f}}}}} \\\\
        \\cline{{3-6}}
    """
    if invoice["amount_paid"]:
        latex_source += f"""
        \\multicolumn{{2}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Amount Paid}} & \\multicolumn{{1}}{{r|}}{{\\texttt{{{currency}{invoice['amount_paid']:.2f}}}}} \\\\
        \\cline{{3-6}}
        \\multicolumn{{2}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. {tax_label}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{{currency}{(invoice['price'] - invoice['amount_paid']):.2f}}}}} \\\\
        """
    else:
        latex_source += f"""
        \\multicolumn{{2}}{{c}}{{}} & \\multicolumn{{2}}{{r|}}{{Balance due inc. {tax_label}}} & \\multicolumn{{1}}{{r}}{{\\textbf{{{currency}{(invoice['price']):.2f}}}}} \\\\
        """
    latex_source += f"""
    \\end{{longtable}}
    \\endgroup
    \\noindent
    """
    if (country != 'US'):
        latex_source += f"""
        Payment can be made by bank transfer to the following account:
        \\begin{{center}}
        
        {details['bank_details']} \\\\
        \\texttt{{Reference: {details['invoice_number']}}}
        \\end{{center}}
        """
    latex_source += f"""
    \\end{{document}}
    """
    return latex_source

def invoice_table_rows(invoice, tax_rate, country, currency):
    if country == "US":
        name = "name_imperial"
        tax_rate = 0
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