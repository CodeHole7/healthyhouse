from oscar.apps.dashboard.catalogue.forms import ProductForm as CoreProductForm


def _generate_product_fields():
    """
    Needed for adding custom fields into base create/update form of Product.
    :return: List of fields (default + custom fields).
    """

    fields = CoreProductForm.Meta.fields
    additional_fields = [
        'lead',
        'description',
        'specification',
        'product_usage',
        'youtube_video_id',
        'min_num_for_order',
        'weight']

    key = 'description'
    if key in fields:
        fields.insert(fields.index(key), additional_fields[0])
        fields.extend(additional_fields[1:])
    else:
        fields.extend(additional_fields)
    return fields


class ProductForm(CoreProductForm):

    class Meta(CoreProductForm.Meta):
        fields = _generate_product_fields()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Next string needed for disabling `TinyMCE` widget.
        self.fields['lead'].widget.attrs['class'] = "no-widget-init"
