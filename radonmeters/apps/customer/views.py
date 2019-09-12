from django.contrib.auth import update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from oscar.apps.customer.utils import get_password_reset_url
from oscar.core.loading import get_class, get_model

CommunicationEventType = get_model('customer', 'CommunicationEventType')
Dispatcher = get_class('customer.utils', 'Dispatcher')

CoreProfileView = get_class('oscar.apps.customer.views', 'ProfileView')
CoreProfileUpdateView = get_class('oscar.apps.customer.views', 'ProfileUpdateView')
CoreChangePasswordView = get_class('oscar.apps.customer.views', 'ChangePasswordView')

PasswordChangeForm = get_class('customer.forms', 'PasswordChangeForm')
ProfileForm = get_class('customer.forms', 'ProfileForm')


class ProfileView(CoreProfileView):
    """
    Overridden default behavior for providing redirect to profile update page.
    """

    def dispatch(self, request, *args, **kwargs):
        return redirect('customer:profile-update')


class ProfileUpdateView(CoreProfileUpdateView):
    """
    Overridden for adding new form in the current view.

    Now it represents ProfileForm and PasswordChangeForm on one page:
    - ProfileForm: handled by this view (look at parent Class);
    - PasswordChangeForm: handled by `ChangePasswordView` (look at Class below);
    """

    template_name = 'customer/profile/profile_change_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = self.get_form(ProfileForm)
        context['password_form'] = self.get_form(PasswordChangeForm)
        return context


class ChangePasswordView(CoreChangePasswordView):
    """
    Overridden for handling of Ajax requests in:
    - form_valid
    - form_invalid
    """

    def form_valid(self, form):
        """
        Overridden for handling of Ajax requests.
        """

        if self.request.is_ajax():
            # `super` cannot be used here, because it creates
            # a message in messages, and user will be notified
            # about password changing twice.

            # Next strings from root realisation (except creating a message).
            form.save()
            update_session_auth_hash(self.request, self.request.user)
            ctx = {
                'user': self.request.user,
                'site': get_current_site(self.request),
                'reset_url': get_password_reset_url(self.request.user)}
            msgs = CommunicationEventType.objects.get_and_render(
                code=self.communication_type_code, context=ctx)
            Dispatcher().dispatch_user_messages(self.request.user, msgs)

            return JsonResponse({
                'message': _('Password has been successfully updated.')})
        else:
            return super().form_valid(form)

    def form_invalid(self, form):
        """
        Overridden for handling of Ajax requests.
        """

        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return super().form_invalid(form)
