# -*- coding: utf-8 -*-

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from rest_framework.authtoken.admin import TokenAdmin as BaseTokenAdmin
from rest_framework.authtoken.models import Token

from .models import User


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'is_partner',
        'is_laboratory', 'groups')
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'is_laboratory', 'is_partner')
    fieldsets = None


class TokenAdmin(BaseTokenAdmin):
    list_display = ('key', 'user', 'created',)
    list_filter = (
        'user__is_active',
        'user__is_staff',
        'user__is_laboratory',
        'user__is_partner')
    fields = ('user',)
    ordering = ('-created',)


admin.site.unregister(Token)
admin.site.register(Token, TokenAdmin)


