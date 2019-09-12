from django.contrib import admin

from instructions.models import Instruction
from instructions.models import InstructionImage
from instructions.models import InstructionTemplate


@admin.register(InstructionImage)
class InstructionImageAdmin(admin.ModelAdmin):
    pass


@admin.register(InstructionTemplate)
class InstructionTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active']


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'orders']
    list_display = ['id', 'user', 'modified']
