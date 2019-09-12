from django.db import models
from zinnia.models_bases.entry import AbstractEntry


class Entry(AbstractEntry):
    """
    Entry with '/blog/<id>/' URL
    """

    class Meta(AbstractEntry.Meta):
        abstract = True

    @models.permalink
    def get_absolute_url(self):
        return ['blog_entry_detail', (), {'pk': self.id}]
