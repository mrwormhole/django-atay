from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.core.mail import EmailMessage

from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def send_invoice_to_email(invoice_link, customer_name, customer_email, subject):
    template = render_to_string("email.html", {"customer_name": customer_name, "invoice_link": invoice_link})
    email = EmailMessage(
        subject,
        template,
        settings.EMAIL_HOST_USER,
        [customer_email],
    )
    email.fail_silentyly = False
    email.send()
