import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext as _
from oscar.core.loading import get_model

from deliveries.client import create_shipment_request
from deliveries.client import create_shipment_return

logger = logging.getLogger(__name__)
Shipment = get_model('deliveries', 'Shipment')
ShipmentReturn = get_model('deliveries', 'ShipmentReturn')


class ShipmentSearchForm(forms.Form):
    """
    Form for filtering instances of Shipment model in the Oscar's dashboard.
    """

    id = forms.UUIDField(
        required=False,
        label=pgettext_lazy("Shipment's ID", "ID"))
    order_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Shipment's order number", "Order number"))


class ShipmentCreateForm(forms.ModelForm):
    """
    Form for creating instances of Shipment model in the Oscar's dashboard.

    WARNINGS:
        `data` value will be replaced with result of call `get_data` method.
    """

    data = forms.CharField(required=False)

    class Meta:
        model = Shipment
        fields = ('order', 'data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget.attrs.update({'class': 'no-widget-init'})

    def create_shipment_request(self):
        """
        Method for calling 3rd-party API for creating shipment request.

        :return (dict): JSON Response of 3rd-party API.
        """

        order_id = self.cleaned_data['order']

        try:
            return create_shipment_request(order_id)
        except Exception as e:
            logger.error(
                'Next error was raised in '
                '`ShipmentCreateForm.create_shipment_request` '
                'for order: "{order_id}". '
                'Original error is: ```{error}```'.format(
                    order_id=order_id,
                    error=e))
            raise ValidationError(
                _('Something went wrong. Check order info and his products.'))

    def clean_order(self):
        """
        Checks that order doesn't has a related shipment yet.
        """

        order = self.cleaned_data['order']
        if order and getattr(order, 'shipment', None):
            raise forms.ValidationError(_('This order already has a shipment.'))
        return order

    def clean(self):
        """
        Method patched for providing value for `data` field.
        """

        cleaned_data = self.cleaned_data.copy()
        if not self.errors:
            cleaned_data['data'] = self.create_shipment_request()
        return cleaned_data


class ShipmentChangeForm(forms.ModelForm):
    """
    Form for editing instances of Shipment model in the Oscar's dashboard.
    """

    class Meta:
        model = Shipment
        readonly_fields = ('id',)
        fields = ('order', 'data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget.attrs.update({'class': 'no-widget-init'})

    def save(self, commit=True):
        """
        Overridden for updating `order.shipping_id` if value was changed.
        """

        data = self.cleaned_data.get('data', '')
        if data:
            shipment_id = data.get('id', '')
            order = self.instance.order
            if shipment_id != order.shipping_id:
                order.shipping_id = shipment_id
                order.save()

        return super().save(commit)


# new forms for ShipmentReturn
class ShipmentReturnCreateForm(forms.ModelForm):
    """
    Form for creating instances of ShipmentReturn

    WARNINGS:
        `data` value will be replaced with result of call `get_data` method.
    """

    data = forms.CharField(required=False)

    class Meta:
        model = ShipmentReturn
        fields = ('order', 'data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget.attrs.update({'class': 'no-widget-init'})

    def create_shipment_request(self):
        """
        Method for calling 3rd-party API for creating shipment request.

        :return (dict): JSON Response of 3rd-party API.
        """

        order_id = self.cleaned_data['order']

        try:
            return create_shipment_return(order_id)
        except Exception as e:
            logger.error(
                'Next error was raised in '
                '`ShipmentReturnCreateForm.create_shipment_request` '
                'for order: "{order_id}". '
                'Original error is: ```{error}```'.format(
                    order_id=order_id,
                    error=e))
            raise ValidationError(
                _('Something went wrong. Check order info and its products.'))

    def clean_order(self):
        """
        Checks that order doesn't has a related shipment yet.
        """

        order = self.cleaned_data['order']
        if order and getattr(order, 'shipment_return', None):
            raise forms.ValidationError(_('This order already has a return shipment.'))
        return order

    def clean(self):
        """
        Method patched for providing value for `data` field.
        """

        cleaned_data = self.cleaned_data.copy()
        if not self.errors:
            cleaned_data['data'] = self.create_shipment_request()
        return cleaned_data


class ShipmentReturnChangeForm(forms.ModelForm):
    """
    Form for editing instances of Shipment model in the Oscar's dashboard.
    """

    class Meta:
        model = ShipmentReturn
        readonly_fields = ('id',)
        fields = ('order', 'data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].widget.attrs.update({'class': 'no-widget-init'})

    def save(self, commit=True):
        """
        Overridden for updating `order.shipping_id` if value was changed.
        """

        data = self.cleaned_data.get('data', '')
        if data:
            shipment_id = data.get('id', '')
            order = self.instance.order
            if shipment_id != order.shipping_return_id:
                order.shipping_return_id = shipment_id
                order.save()

        return super().save(commit)
