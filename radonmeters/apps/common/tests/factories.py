import factory

from common.models import DosimeterPDFReportTheme


class DosimeterPDFReportThemeFactory(factory.DjangoModelFactory):
    body = factory.Faker('text')

    class Meta:
        model = DosimeterPDFReportTheme
