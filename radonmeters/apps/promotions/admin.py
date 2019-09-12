from ckeditor.fields import RichTextFormField
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from modeltranslation.admin import TranslationAdmin
from oscar.core.loading import get_model

RawHTML = get_model('promotions', 'RawHTML')


@admin.register(RawHTML)
class RawHTMLAdmin(TranslationAdmin):
    model = RawHTML

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super().formfield_for_dbfield(db_field, **kwargs)
        if isinstance(getattr(field, 'widget', None), AdminTextareaWidget):
            field = RichTextFormField(required=field.required)
        self.patch_translation_field(db_field, field, **kwargs)
        return field
