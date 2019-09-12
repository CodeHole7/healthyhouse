from django import forms
from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_model
Dosimeter = get_model('catalogue', 'Dosimeter')

Order = get_model('order', 'Order')
OrderLine = get_model('order','Line')

class UpdateDosimeterStatusRequestForm(forms.Form):
    serial_number = forms.CharField(required=True)
    """
        @author: alex m
        @created: 2019.8.27
        @desc: Form for updating dosimeter's status to 'ready_for_packaging'
    """    
    user_id = None
    dosimeter = None

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)                
        super().__init__(*args, **kwargs)

    def update_dosimeter_status(self):

        self.dosimeter.status = Dosimeter.STATUS_CHOICES.ready_for_packaging
        return self.dosimeter.save()
                            

    def clean_serial_number(self):
        cleaned_data = super().clean()

        if cleaned_data['serial_number'] is not None:
            try:
                self.dosimeter = Dosimeter.objects.get( serial_number = cleaned_data['serial_number'])
                if self.dosimeter is not None:                
                    if self.dosimeter.status == 'created':
                         # get order id with 'created' status
                        orders = Order.objects.all().filter(user_id=self.user_id, status='created')
                        if len(orders) >0:                        
                            # get order_line id
                            for order in orders:
                                order_lines = OrderLine.objects.all().filter(order_id=order.id, status='created')                            
                                for order_line in order_lines:
                                    if self.dosimeter.line_id == order_line.id:                                    
                                        return cleaned_data['serial_number']
                    elif self.dosimeter.status == 'ready_for_packaging':
                        raise forms.ValidationError(_('serial number already was updated.'))                
                                    
            except Dosimeter.DoesNotExist:
                pass
            finally:
                pass     


        
        raise forms.ValidationError(_('serial number is invalid.'))


        
        





