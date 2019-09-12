from django.conf.urls import url
from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class OwnersDashboardApplication(DashboardApplication):
    """
    App for representation owners in the Oscar's Dashboard.
    """
    default_permissions = ['is_staff', ]

    owner_list_view = get_class(
        'dashboard.owners.views',
        'OwnerDashboardListView')
    owner_detail_view = get_class(
        'dashboard.owners.views',
        'OwnerDashboardUpdateView')
    owner_summary_view = get_class(
        'dashboard.owners.views',
        'OwnerDashboardSummaryView')
    owner_email_config_view = get_class(
        'dashboard.owners.views',
        'OwnerDashboardEmailConfigDetailView')
    owner_create_view = get_class(
        'dashboard.owners.views',
        'OwnerDashboardCreateView')
    owner_report_templates_list_view = get_class(
        'dashboard.owners.views',
        'OwnerPDFReportThemeListView')
    owner_report_templates_create_view = get_class(
        'dashboard.owners.views',
        'OwnerPDFReportThemeCreateView')
    owner_report_templates_update_view = get_class(
        'dashboard.owners.views',
        'OwnerPDFReportThemeUpdateView')

    def get_urls(self):
        urls = [
            url(r'^$',
                self.owner_list_view.as_view(),
                name='owner-list'),
            url(r'^overview$',
                self.owner_summary_view.as_view(),
                name='owner-summary'),
            url(r'^report-template/$',
                self.owner_report_templates_list_view.as_view(),
                name='owner-report-template-list'),
            url(r'^report-template/add/$',
                self.owner_report_templates_create_view.as_view(),
                name='owner-report-template-create'),
            url(r'^report-template/(?P<pk>[-\d]+)/$',
                self.owner_report_templates_update_view.as_view(),
                name='owner-report-template-detail'),
            url(r'^add/$',
                self.owner_create_view.as_view(),
                name='owner-create'),
            url(r'^(?P<pk>[-\d]+)/$',
                self.owner_detail_view.as_view(),
                name='owner-detail'),
            url(r'^(?P<pk>[-\d]+)/email-config/$',
                self.owner_email_config_view.as_view(),
                name='owner-email-config'),
        ]
        return self.post_process_urls(urls)


application = OwnersDashboardApplication()
