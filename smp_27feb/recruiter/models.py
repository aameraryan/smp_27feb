from django.db import models
from django.contrib.auth.models import User
from portal.models import EXPERIENCE_CHOICES
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from portal.models import Proposal


RECRUITER_TYPES = (('Individual', 'Individual'), ('Company', 'Company'))


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=200, blank=True, verbose_name="full name",
                                 help_text='as appears in documents')
    email = models.EmailField(blank=True, null=True, verbose_name='email')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='mobile number')

    recruiter_type = models.CharField(max_length=20, choices=RECRUITER_TYPES, blank=True)

    details = models.TextField(blank=True, help_text='anything extra about yourself')
    email_confirmed = models.BooleanField(default=False)

    last_recharge = models.DateTimeField(blank=True, null=True)
    recharge_validity = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.full_name

    def check_job_posted_by(self, job_id):
        try:
            job = self.job_set.get(id=job_id)
            return job
        except ObjectDoesNotExist:
            return False

    def check_candidate_liked(self, candidate_id):
        try:
            like = self.candidatelike_set.get(candidate__id=candidate_id)
            return True
        except ObjectDoesNotExist:
            return False

    def add_recharge(self, package_validity_days):
        validity_days = timezone.timedelta(days=package_validity_days)
        self.last_recharge = timezone.now()
        if not self.recharge_validity or self.recharge_validity < timezone.now():
            self.recharge_validity = (timezone.now() + validity_days)
        elif self.recharge_validity > timezone.now():
            self.recharge_validity += validity_days
        self.save()

    def has_subscription(self):
        return self.recharge_validity is not None and self.recharge_validity > timezone.now()

    @property
    def get_proposal_count(self):
        return Proposal.objects.filter(job__posted_by=self).count()


JOB_TYPE_CHOICES = (('Full Time', 'Full Time'), ('Part Time', "Part Time"),
                    ('Home Based', 'Home Base'), ('Contract', 'Contract'), ('Other', 'Other'))


class Job(models.Model):
    role = models.ForeignKey('portal.Role', on_delete=models.PROTECT, blank=True, null=True,
                             verbose_name='job role')
    headline = models.CharField(max_length=200, blank=True, help_text='ex.(required teacher for 5th standard)')
    industry = models.ForeignKey('portal.Industry', on_delete=models.PROTECT, blank=True, null=True,
                                 help_text='industry type of job')
    experience = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES, blank=True,
                                  help_text='required experience')
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default='Full Time')
    qualifications = models.ManyToManyField('portal.Qualification', blank=True, help_text='exact qualification required')
    skills = models.ManyToManyField('portal.Skill', blank=True, help_text='key skills')
    company_name = models.CharField(max_length=200, blank=True, help_text='vacancy in company or college')
    address = models.TextField(blank=True, help_text='address of working company or college')
    city = models.ForeignKey('portal.City', on_delete=models.PROTECT, blank=True, null=True,
                             help_text='city of work')
    salary_from = models.PositiveIntegerField(default=0)
    salary_upto = models.PositiveIntegerField(default=0)
    description = models.TextField( blank=True, help_text='job description')
    phone = models.CharField(max_length=15, blank=True, verbose_name='contact number',
                             help_text='contact number to apply')
    email = models.EmailField(blank=True, null=True,
                              help_text='email to send resumes')
    requirements = models.TextField(blank=True, help_text='requirements for job applicant')
    posted_by = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.headline)

    @property
    def get_salary_range(self):
        return "{} to {}".format(self.salary_from, self.salary_upto)


def default_headline(instance, sender, *args, **kwargs):
    if not instance.headline:
        instance.headline = 'required ' + instance.role.name + ' for ' + instance.company_name
        instance.save()


post_save.connect(default_headline, sender=Job)


class CandidateLike(models.Model):
    candidate = models.ForeignKey('portal.Candidate', on_delete=models.CASCADE)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.candidate, self.recruiter)

    class Meta:
        unique_together = ['candidate', 'recruiter']
