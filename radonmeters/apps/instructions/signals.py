from django.db.models.signals import pre_save
from django.dispatch import receiver

from instructions.models import InstructionTemplate


@receiver(pre_save, sender=InstructionTemplate, dispatch_uid="instruction_pre_save")
def instruction_pre_save(sender, instance, *args, **kwargs):
    """
    Update is_active field
    """
    if instance.is_active:
        qs = sender.objects.filter(is_active=True)
        if instance.id:
            qs = qs.exclude(id=instance.id)
        qs.update(is_active=False)
