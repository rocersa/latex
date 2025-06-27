# Takes arguments returns pdf

class GenerateInvoice:
    def __init__(self, data):
        self.data = data

    def generate_pdf(self):
        # Logic to generate PDF from the provided data
        return self.data

    def generate_latex_string(self):
        # Logic to generate LaTeX string from the provided data
        pass

def generate_invoice(data):
    invoice = GenerateInvoice(data)
    return invoice.generate_pdf()
