from django.conf.urls import url
from oscar.apps.dashboard.users.app import UserManagementApplication

from oscar.core.loading import get_class


class UserManagementApplicationCustom(UserManagementApplication):
    default_permissions = ['is_staff', ]

    user_create_view = get_class('dashboard.users.views', 'UserCreateView')
    user_detail_view = get_class('dashboard.users.views', 'UserUpdateView')

    address_create_view = get_class('dashboard.users.views', 'DashboardAddressCreateView')
    address_update_view = get_class('dashboard.users.views', 'DashboardAddressUpdateView')
    address_delete_view = get_class('dashboard.users.views', 'DashboardAddressDeleteView')
    address_change_status_view = get_class('dashboard.users.views', 'DashboardAddressChangeStatusView')

    def get_urls(self):
        urls = super().get_urls()
        urls = [
            url(r'^create/$',
                self.user_create_view.as_view(), name='user-create'),

           # Address book
           url(r'^(?P<user_pk>\d+)/addresses/add/$',
               self.address_create_view.as_view(),
               name='address-create'),
           url(r'^(?P<user_pk>\d+)/addresses/(?P<pk>\d+)/$',
               self.address_update_view.as_view(),
               name='address-detail'),
           url(r'^(?P<user_pk>\d+)/addresses/(?P<pk>\d+)/delete/$',
               self.address_delete_view.as_view(),
               name='address-delete'),
           url(r'^(?P<user_pk>\d+)/addresses/(?P<pk>\d+)/'
               r'(?P<action>default_for_(billing|shipping))/$',
               self.address_change_status_view.as_view(),
               name='address-change-status'),
        ] + urls
        return self.post_process_urls(urls)


application = UserManagementApplicationCustom()
