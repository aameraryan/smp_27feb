import django_filters
from recruiter.models import Job
from portal.models import Qualification


class JobFilter(django_filters.FilterSet):

    paginate_by = 1
    salary_from = django_filters.NumberFilter(label='salary from', field_name='salary_from', lookup_expr='gte')
    salary_upto = django_filters.NumberFilter(label='salary upto', field_name='salary_upto', lookup_expr='lte')

    class Meta:
        model = Job
        fields = ['role', 'industry', 'city', 'experience', 'salary_from', 'salary_upto']
        paginate_by = 1
