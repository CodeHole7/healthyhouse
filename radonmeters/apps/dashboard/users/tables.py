from django_tables2 import A, Column, LinkColumn, TemplateColumn
from oscar.apps.dashboard.users.tables import UserTable as UserTableCore

from oscar.core.loading import get_class

DashboardTable = get_class('dashboard.tables', 'DashboardTable')


class UserTable(UserTableCore):
    source = Column(accessor='source')
    num_orders = Column(accessor='orders.count', orderable=False, verbose_name='Num orders')

    icon = "group"

    class Meta(DashboardTable.Meta):
        template = 'dashboard/users/table.html'
