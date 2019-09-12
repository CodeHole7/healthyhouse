# -*- coding: utf-8 -*-
from modeltranslation.decorators import register
from modeltranslation.translator import TranslationOptions
from oscar.core.loading import get_model

Category = get_model('catalogue', 'Category')
ProductClass = get_model('catalogue', 'ProductClass')
Product = get_model('catalogue', 'Product')


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


# TODO: Need to think about this, can breaks down the part,
# which uses ProductClass(es) for grouping, filtering, etc.
# @register(ProductClass)
# class ProductClassTranslationOptions(TranslationOptions):
#     fields = ('name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'lead', 'description', 'specification', 'product_usage')
