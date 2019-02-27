import django_filters
from portal.models import Candidate


class CandidateFilter(django_filters.FilterSet):
    paginate_by = 1

    class Meta:
        model = Candidate
        fields = ['qualification', 'industry', 'experience', 'roles', 'city', 'skills']
