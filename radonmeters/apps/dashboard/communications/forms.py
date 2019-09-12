from oscar.apps.dashboard.communications.forms import \
    CommunicationEventTypeForm as BaseCommunicationEventTypeForm


class CommunicationEventTypeForm(BaseCommunicationEventTypeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_body_template'].widget.attrs.update(
            {'class': 'no-widget-init'})
        self.fields['email_body_html_template'].widget.attrs.update(
            {'class': 'no-widget-init'})

    def get_preview_context(self):
        ctx = {}
        if hasattr(self, 'preview_order'):
            ctx['order'] = self.preview_order
            ctx['user'] = self.preview_order.user
        return ctx
