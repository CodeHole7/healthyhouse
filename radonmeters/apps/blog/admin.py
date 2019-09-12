from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.utils.translation import ugettext as _
from modeltranslation.admin import TranslationAdmin
from zinnia.admin import CategoryAdmin as BaseCategoryAdmin
from zinnia.admin import EntryAdmin as BaseEntryAdmin
from zinnia.admin.forms import EntryAdminForm as DefaultEntryAdminForm
from zinnia.admin.widgets import MPTTFilteredSelectMultiple
from zinnia.models import Category
from zinnia.models import Entry

from blog.fields import CustomMPTTModelMultipleChoiceField


class EntryAdminForm(DefaultEntryAdminForm):
    """
    Overwritten because default realisation is not working with Django 1.11+.
    Also for replacing widget for `image_caption` field.
    """
    categories = CustomMPTTModelMultipleChoiceField(
        label=_('Categories'), required=False,
        queryset=Category.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('categories')))
    image_caption = forms.CharField(label=_('Image caption'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            field = self.fields[name]
            if (isinstance(getattr(field, 'widget', None), AdminTextareaWidget)
                    and 'lead' not in name):
                field.widget = CKEditorUploadingWidget()


# Register Custom EntryAdmin
@admin.register(Entry)
class EntryAdmin(BaseEntryAdmin, TranslationAdmin):
    """
    Overwritten because default realisation is not working with Django 1.11+.
    Also for adding TranslationAdmin logic (for rendering i18n fields).
    """
    form = EntryAdminForm

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     field = super().formfield_for_dbfield(db_field, **kwargs)
    #     if (isinstance(getattr(field, 'widget', None), AdminTextareaWidget)
    #             and 'lead' not in db_field.name):
    #         field = RichTextFormField(required=field.required)
    #     self.patch_translation_field(db_field, field, **kwargs)
    #     return field


class CategoryAdmin(BaseCategoryAdmin, TranslationAdmin):
    """
    Overwritten for adding TranslationAdmin logic (for rendering i18n fields).
    """
    pass


# Register Custom CategoryAdmin
admin.site.unregister(Category)
admin.site.register(Category, CategoryAdmin)
