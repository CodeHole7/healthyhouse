from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import (
    CreateView)
from django.views.generic.edit import BaseUpdateView
from oscar.apps.dashboard.users.views import UserDetailView
from oscar.core.compat import get_user_model
from oscar.core.loading import (
    get_class, get_classes, get_model)

PageTitleMixin, RegisterUserMixin = get_classes(
    'customer.mixins', ['PageTitleMixin', 'RegisterUserMixin'])
DashboardUserAddressForm = get_class('address.forms', 'UserAddressForm')
UserAddress = get_model('address', 'UserAddress')
UserUpdateForm = get_class('dashboard.users.forms', 'UserUpdateForm')
User = get_user_model()


# ------------
# User managing
# ------------

class UserUpdateView(UserDetailView, BaseUpdateView):
    template_name = 'dashboard/users/detail.html'
    model = User
    form_class = UserUpdateForm
    context_object_name = 'customer'

    def get_success_url(self):
        messages.success(self.request, _("User was saved."))
        return reverse('dashboard:user-detail', args=(self.object.id, ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_edit_user'] = context['form']
        return context


class UserCreateView(CreateView):
    template_name = 'dashboard/users/create.html'
    model = User
    form_class = UserUpdateForm

    def get_success_url(self):
        messages.success(self.request, _("User was created."))
        return reverse('dashboard:users-index')


# ------------
# Address book
# ------------
# Override from oscar/apps/customer/views.py
# for dashboard address managing

class DashboardAddressMixin:
    model = UserAddress
    user = None

    def get_success_url(self):
        return reverse('dashboard:user-detail', args=(self.user.id, ))

    def get_redirect_url(self, *args, **kwargs):
        return self.get_success_url()

    def get(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs['user_pk'])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs['user_pk'])
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DashboardAddressMixin, self).get_context_data(**kwargs)
        ctx['user_address'] = self.user
        return ctx


class DashboardAddressCreateView(
        DashboardAddressMixin, PageTitleMixin, generic.CreateView):
    form_class = DashboardUserAddressForm
    template_name = 'dashboard/users/address/address_form.html'

    def get_form_kwargs(self):
        kwargs = super(DashboardAddressCreateView, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' created") % self.object.summary)
        return super(DashboardAddressCreateView, self).get_success_url()


class DashboardAddressUpdateView(
        DashboardAddressMixin, PageTitleMixin, generic.UpdateView):
    form_class = DashboardUserAddressForm
    template_name = 'dashboard/users/address/address_form.html'

    def get_form_kwargs(self):
        kwargs = super(DashboardAddressUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' updated") % self.object.summary)
        return super(DashboardAddressUpdateView, self).get_success_url()


class DashboardAddressDeleteView(
        DashboardAddressMixin, PageTitleMixin, generic.DeleteView):
    template_name = 'dashboard/users/address/address_delete.html'
    context_object_name = 'address'

    def get_success_url(self):
        messages.success(self.request,
                         _("Address '%s' deleted") % self.object.summary)
        return super(DashboardAddressDeleteView, self).get_success_url()


class DashboardAddressChangeStatusView(
        DashboardAddressMixin, generic.RedirectView):
    """
    Sets an address as default_for_(billing|shipping)
    """
    permanent = False

    def get(self, request, pk=None, action=None, *args, **kwargs):
        address = self.object = get_object_or_404(UserAddress, pk=pk)

        #  We don't want the user to set an address as the default shipping
        #  address, though they should be able to set it as their billing
        #  address.
        if address.country.is_shipping_country:
            setattr(address, 'is_%s' % action, True)
        elif action == 'default_for_billing':
            setattr(address, 'is_default_for_billing', True)
        else:
            messages.error(request, _('We do not ship to this country'))
        address.save()
        return super(DashboardAddressChangeStatusView, self).get(request, *args, **kwargs)
