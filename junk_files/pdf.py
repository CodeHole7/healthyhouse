from weasyprint import HTML

# Generate and return report file.
html = HTML(
    filename='./pdf.html'
)
if as_image:
    return html.write_png()
html.write_pdf('./test.pdf')