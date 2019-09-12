from django.conf.urls import url
from oscar.core.application import DashboardApplication
from oscar.core.loading import get_class


class DosimetersDashboardApplication(DashboardApplication):
    """
    App for representation dosimeters in the Oscar's Dashboard.
    """
    default_permissions = ['is_staff', ]

    dosimeter_list_view = get_class(
        'dashboard.dosimeters.views',
        'DosimeterDashboardListView')
    dosimeter_detail_view = get_class(
        'dashboard.dosimeters.views',
        'DosimeterDashboardUpdateView')
    dosimeter_report_download_link = get_class(
        'dashboard.dosimeters.views',
        'DownloadDosimeterReportPDF')

    dosimeter_batch_view = get_class(
    'dashboard.dosimeters.views',
    'BatchSelectDashboardView')

    def get_urls(self):
        urls = [
            url(r'^$',
                self.dosimeter_list_view.as_view(),
                name='dosimeter-list'),
            url(r'^(?P<pk>[-\w]+)/$',
                self.dosimeter_detail_view.as_view(),
                name='dosimeter-detail'),
            url(r'^download-dosimeter-reports-pdf/(\d+)$', self.dosimeter_report_download_link.as_view(), name='download_dosimeter_reports_pdf'),
            url(r'^dosimeter-batch/(?P<serial_number>[-\w]+)/(?P<owner>[-\w]+)/(?P<status>[-\w]+)/$',
                self.dosimeter_batch_view.as_view(),
                name='dosimeter-batch'),
        ]
        return self.post_process_urls(urls)


application = DosimetersDashboardApplication()
