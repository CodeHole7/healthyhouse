import json
import requests
from constance import config
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from accounting.models import Accounting
from common.utils import create_invoice_pdf


class AccountingSync:
    base_domain = 'https://api.dinero.dk/'
    accounting = None

    def __init__(self) -> None:
        super().__init__()
        self.accounting = Accounting.objects.first()

    def auth(self):
        response = requests.post(
            'https://authz.dinero.dk/dineroapi/oauth/token',
            data={
                'grant_type': 'password',
                'scope': 'read write',
                'username': self.accounting.username,
                'password': self.accounting.password},
            auth=(self.accounting.client_username, self.accounting.client_password)
        )
        if status.is_success(response.status_code):
            access_token = json.loads(response.text)['access_token']
        else:
            raise ValueError(_('No access to accounting'))
        return "Bearer {}".format(access_token)

    def _make_post_files(self, path, files=None):
        url = self.base_domain + path
        headers = {
            "Authorization": self.auth(),
        }

        response = requests.post(
            url,
            files=files,
            headers=headers
        )
        return response

    def _make_post_json(self, path, data=None):
        url = self.base_domain + path
        headers = {
            "Authorization": self.auth(),
            'Content-Type': 'application/json'
        }

        response = requests.post(
            url,
            json=data,
            headers=headers
        )
        return response

    def post_files(self, order, invoice=None):
        # generate_invoices_pdf
        path = 'v1/{organization_id}/files'.format(organization_id=self.accounting.organization_id)
        context = {'order': order, 'config': config}
        if not invoice:
            invoice = create_invoice_pdf(order, context, in_memory=True)
        files = {'file':  ('invoice.pdf', invoice)}
        return self._make_post_files(path, files)

    def post_invoice_metadata(self, order, invoice_file):
        # post files
        response = self.post_files(order, invoice_file)
        if not status.is_success(response.status_code):
            raise ValueError(response.text)

        path = 'v1.1/{organization_id}/ledgeritems'.format(organization_id=self.accounting.organization_id)
        data_item = self.accounting.meta_fields
        data_item.update({
                'VoucherNumber': order.number,
                'Amount': - float(order.total_incl_tax),
                'VoucherDate': order.date_placed.date().strftime('%Y-%m-%d'),
                'Description': '{number}-{partner}'.format(number=order.number, partner=order.partner_order_id),
                'FileGuid': json.loads(response.text)['FileGuid']
            }
        )
        data = [data_item]
        response = self._make_post_json(path, data)
        if not status.is_success(response.status_code):
            raise ValueError(response.text)
        return response
