from django.views.generic.detail import DetailView

from zinnia.models.entry import Entry
from zinnia.views.mixins.entry_preview import EntryPreviewMixin
from zinnia.views.mixins.entry_protection import EntryProtectionMixin


class EntryDetailView(
        EntryPreviewMixin,
        EntryProtectionMixin,
        DetailView):
    template_name_field = 'template'

    def get_queryset(self):
        return Entry.published.on_site()
