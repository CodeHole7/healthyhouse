from django.conf.urls import url
from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class InstructionsDashboardApplication(DashboardApplication):
    """
    App for representation owners in the Oscar's Dashboard.
    """
    default_permissions = ['is_staff', ]

    instruction_template_list_view = get_class(
        'dashboard.instructions.views',
        'InstructionTemplateListView')
    instruction_template_create_view = get_class(
        'dashboard.instructions.views',
        'InstructionTemplateCreateView')
    instruction_template_update_view = get_class(
        'dashboard.instructions.views',
        'InstructionTemplateUpdateView')

    def get_urls(self):
        urls = [
            url(r'^templates/$',
                self.instruction_template_list_view.as_view(),
                name='instruction-template-list'),
            url(r'^templates/add/$',
                self.instruction_template_create_view.as_view(),
                name='instruction-template-create'),
            url(r'^templates/(?P<pk>[-\d]+)/$',
                self.instruction_template_update_view.as_view(),
                name='instruction-template-detail'),
        ]
        return self.post_process_urls(urls)


application = InstructionsDashboardApplication()
