from django.shortcuts import redirect
from django.urls import reverse
from oscar.apps.dashboard.views import IndexView as CoreIndexView

from common.utils import is_radosure


class IndexView(CoreIndexView):
    """
    An overview view which displays several reports about the shop.

    Supports the permission-based dashboard. It is recommended to add a
    index_nonstaff.html template because Oscar's default template will
    display potentially sensitive store information.
    """

    def get(self, request, *args, **kwargs):
        if is_radosure():
            # for radosure redirect to orders page.
            url = reverse('dashboard:order-list')
            return redirect(url)
        return super().get(request, *args, **kwargs)
