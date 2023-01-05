from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template

def make_pdf_preview(template_src, context, as_preview=False):
	template = get_template(template_src)
	html  = template.render(context)
	result = BytesIO()
	try:
		pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), dest=result)
		pdf_file=result
		print(type(pdf_file))
		if as_preview:
			return pdf_file.getvalue()
		else:
			return pdf_file
	except Exception as e:
		print(e)
