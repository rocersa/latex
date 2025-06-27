
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