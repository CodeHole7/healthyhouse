from django import forms
from django.utils.translation import pgettext_lazy

from catalogue.models import Dosimeter, Batch, Batch_Dosimeter
from owners.models import Owner, OwnerEmailConfig

class DosimeterDashboardSearchForm(forms.Form):
    """
    Form for filtering dosimeters in Oscar's Dashboard.
    """

    id = forms.UUIDField(
        required=False,
        label=pgettext_lazy("Dosimeter's ID", "ID"))
    serial_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Dosimeter's serial number", "Serial number"))
    order_number = forms.CharField(
        required=False,
        label=pgettext_lazy("Dosimeter's order number", "Order number"))

class DosimeterDashboardChangeForm(forms.ModelForm):
    """
    Form for edit dosimeters in Oscar's Dashboard.
    """

    class Meta:
        model = Dosimeter
        fields = (
            'line', 'status', 'serial_number',
            'concentration', 'uncertainty', 'active_area', 'is_active',
            'measurement_start_date', 'measurement_end_date',
            'floor', 'location')
        widgets = {
            'line': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['line'].disabled = True

class DosimeterDashboardUpdateForm(forms.Form):
    """
    Form for updating dosimeters in Oscar's Dashboard.
    """
    serial_number = forms.CharField(
        required=True,
        label=pgettext_lazy("Dosimeter's serial number", "Serial number"))
    status = forms.ChoiceField(
        required=True,
        choices=Dosimeter.STATUS_CHOICES,
        initial=Dosimeter.STATUS_CHOICES.unknown,
        label=pgettext_lazy("Status", "Status"))


    """
        @author: alex m
        @created: 2019.2.29
        @desc: choice field to select owner of dosimeter
    """

    OWNERS_CHOICE = []


    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.OWNERS_CHOICE = [(-1,'No Select')]

        for owner in Owner.objects.all():
            self.OWNERS_CHOICE.append((owner.id, owner.first_name))

        self.fields['owner'] = forms.ChoiceField(
            required=False,
            choices = self.OWNERS_CHOICE,
            #disabled = True,
            label = pgettext_lazy("Owner", "Owner")
        )

        self.fields['owner'].widget.attrs['disabled'] = True

    def clean_owner(self):
        
        if self.cleaned_data['status'] == Dosimeter.STATUS_CHOICES.shipped_to_distributor:
            self.fields['owner'].widget.attrs['disabled'] = False
            if int(self.cleaned_data['owner']) < 0:
                raise forms.ValidationError(pgettext_lazy('You must select owner','You must select owner'))
        return self.cleaned_data['owner']
"""
    @author: alex m
    @created: 2019.2.29
    @desc: form for batch creator
"""
class BatchSelectDashboardUpdateForm(forms.Form):

    # serial_number_label = forms.CharField(
    #     disabled = True,
    #     required=False,
    #     label=pgettext_lazy("Dosimeter's serial number", "Serial number"))

    

    # status_label = forms.ChoiceField(
    #     disabled = True,
    #     required=False,
    #     choices=Dosimeter.STATUS_CHOICES,
    #     initial=Dosimeter.STATUS_CHOICES.unknown,
    #     label=pgettext_lazy("Status", "Status"))


    status = forms.CharField(widget=forms.HiddenInput())
    owner = forms.IntegerField(widget=forms.HiddenInput())
    serial_number = forms.CharField(widget=forms.HiddenInput())


    CHOICES=[('NEW','new batch'),
         ('SELECTED','existed batch')]

    like = forms.ChoiceField(
        choices=CHOICES, 
        widget=forms.RadioSelect, 
        initial = 'SELECTED', 
        label = pgettext_lazy("Included it into", "Included it into")
    )

    new_batch_name = forms.CharField(
        max_length = 255,
        required = False,
        label = pgettext_lazy("New Batch", "New Batch")
    )

    BATCHS_CHOICE = []
    # OWNERS_CHOICE = []

      
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['like'] == 'NEW':
            if not cleaned_data['new_batch_name']:
                self.add_error('new_batch_name',"You didn't enter new batch name")
            try:
                batch = Batch.objects.get(batch_owner_id = cleaned_data['owner'], batch_name = cleaned_data['new_batch_name'])
                self.add_error('new_batch_name', 'This batch name already exists')
            except Batch.DoesNotExist:
                pass
        elif cleaned_data['like'] == 'SELECTED':
            if not cleaned_data['batchs']:
                self.add_error('batchs',"You didn't select batch")

        # if not cleaned_data['batchs'] and not cleaned_data['new_batch_name']:
        #     raise forms.ValidationError("please enter new batch name or select existed batch.")
        return cleaned_data
    def save_data(self):
        
        if self.cleaned_data['like'] == 'NEW':

            batch = Batch(batch_name = self.cleaned_data['new_batch_name'], 
                batch_owner_id = self.cleaned_data['owner'])
            batch.save()
            
        elif self.cleaned_data['like'] == 'SELECTED':
            # try:
            batch = Batch.objects.get(id = self.cleaned_data['batchs'], batch_owner_id = self.cleaned_data['owner'])
            # except Batch.DoesNotExist:
            #     return False
        
        # try:

        dosimeter = Dosimeter.objects.get(serial_number = self.cleaned_data['serial_number'])
        dosimeter.status = self.cleaned_data['status']
        dosimeter.save()
        # except Dosimeter.DoesNotExist:
        #     return False
        try:
            batch_dosimeter = Batch_Dosimeter.objects.get(dosimeter_id = dosimeter.id)
            batch_dosimeter.batch_id = batch_id
            batch_dosimeter.save()
        except Batch_Dosimeter.DoesNotExist:            
            batch_dosimeter = Batch_Dosimeter(batch_id = batch.id, dosimeter_id = dosimeter.id)
            batch_dosimeter.save()

        return batch

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.BATCHS_CHOICE = []

        for batch in Batch.objects.all().filter(batch_owner_id = kwargs['initial']['owner']):
            self.BATCHS_CHOICE.append((batch.id, batch.batch_name))

        self.fields['batchs'] = forms.ChoiceField(
            required=False,
            choices = self.BATCHS_CHOICE,
            label = pgettext_lazy("Select Batch", "Select Batch")
        )  

        # self.OWNERS_CHOICE = []

        # for owner in Owner.objects.all():
        #     self.OWNERS_CHOICE.append((owner.id, owner.first_name))

        # self.fields['owner_label'] = forms.ChoiceField(
        #     required=False,
        #     disabled=True,
        #     choices = self.OWNERS_CHOICE,
        #     label = pgettext_lazy("Owner", "Owner")
        # )

        # self.fields['owner'].widget.attrs['readonly'] = True
        # self.fields['status'].widget.attrs['readonly'] = True
        # self.fields['serial_number'].widget.attrs['readonly'] = True




