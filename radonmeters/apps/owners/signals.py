from django.db.models.signals import pre_save
from django.dispatch import receiver

from owners.models import Owner


@receiver(pre_save, sender=Owner, dispatch_uid="owner_pre_save")
def application_post_save(sender, instance, *args, **kwargs):
    """
    Update is_default field
    """
    if instance.is_default:
        qs = sender.objects.filter(is_default=True)
        if instance.id:
            qs = qs.exclude(id=instance.id)
        qs.update(is_default=False)
