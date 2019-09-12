# -*- coding: utf-8 -*-
from oscar.core.loading import get_model
from rest_framework import serializers

Partner = get_model('partner', 'Partner')


class PartnerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='name')
    last_name = serializers.CharField(default='')
    email = serializers.CharField(default='')

    class Meta:
        model = Partner
        fields = ('id', 'first_name', 'last_name', 'email', 'code')
