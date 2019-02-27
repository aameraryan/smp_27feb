from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.http import Http404
from django.utils import timezone
from django.conf import settings
User._meta.get_field('email')._unique = True


class Role(models.Model):
    name = models.CharField(max_length=200)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=200)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Industries'


class Qualification(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Qualifications'


class City(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Cities'


EXPERIENCE_CHOICES = (('', 'Any'),
                      ('0-1', '0-1 years'),
                      ('1-2', '1-2 years'),
                      ('2-4', '2-4 years'),
                      ('4-6', '4-6 years'),
                      ('6-8', '6-8 years'),
                      ('8-10', '8-10 years'),
                      ('10+', '10+ years'),)


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=50, blank=True, verbose_name='first name')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='last name')
    full_name = models.CharField(max_length=200, blank=True, verbose_name="full name",
                                 help_text='as appears in documents')
    email = models.EmailField(blank=True, null=True, verbose_name='email')
    phone = models.CharField(max_length=15, blank=True, verbose_name='mobile number',
                             help_text='HR will call on this contact number')

    roles = models.ManyToManyField(Role, verbose_name='roles', help_text='roles able to work')
    skills = models.ManyToManyField(Skill, verbose_name='skill', help_text='key skill')
    qualification = models.ForeignKey(Qualification, on_delete=models.PROTECT, blank=True, null=True,
                                      verbose_name='qualification', help_text='highest qualification')
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name='industry', help_text='industry of work and experience')
    experience = models.CharField(max_length=150, choices=EXPERIENCE_CHOICES, blank=True,
                                  verbose_name='experience', help_text='total experience')

    address = models.TextField(blank=True, verbose_name='current address',
                               help_text='address ex.(flat no./building name/street name/locality)')
    city = models.ForeignKey(City, on_delete=models.PROTECT, blank=True, null=True,
                             verbose_name='current city')

    resume = models.FileField(null=True, blank=True, upload_to='resumes/')
    details = models.TextField(blank=True, help_text='anything extra about yourself')
    email_confirmed = models.BooleanField(default=False)

    last_recharge = models.DateTimeField(blank=True, null=True)
    recharge_validity = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def check_job_proposal_posted_by(self, proposal_id):
        try:
            proposal = self.proposal_set.get(id=proposal_id)
            return proposal
        except ObjectDoesNotExist:
            return False

    def check_job_proposal_exist(self, job_id):
        try:
            proposal = self.proposal_set.get(job__id=job_id)
            return proposal
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
    def get_resume_link(self):
        if self.resume:
            print(self.resume)
            return self.resume.url
        else:
            return ''


class Proposal(models.Model):
    job = models.ForeignKey('recruiter.Job', on_delete=models.CASCADE)
    posted_by = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    message = models.TextField(blank=True, help_text='proposal message')
    on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} for {}".format(self.posted_by, self.job.headline)

    class Meta:
        unique_together = ('job', 'posted_by')


class Package(models.Model):
    name = models.CharField(max_length=50)
    available = models.BooleanField(default=True)
    user_type = models.CharField(max_length=20, choices=(('Recruiter', 'Recruiter'), ('Candidate', 'Candidate')))
    price = models.IntegerField()
    validity_days = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return "{} - {} - {}".format(self.name, self.price, self.validity_days)


class Recharge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    on = models.DateTimeField(auto_now_add=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    package_details = models.TextField()

    def __str__(self):
        return "{} - {} - {}".format(self.user, self.package, self.on)


def add_recharge_to_user(instance, created, sender, *args, **kwargs):
    if created:
        package = instance.package
        user_type = package.user_type
        if user_type == 'Candidate':
            instance.user.candidate.add_recharge(package_validity_days=package.validity_days)
        elif user_type == 'Recruiter':
            instance.user.recruiter.add_recharge(package_validity_days=package.validity_days)
        else:
            raise Http404


post_save.connect(add_recharge_to_user, sender=Recharge)


def save_package_details(instance, sender, *args, **kwargs):
    if instance.package:
        package = instance.package
        correct_package_details = "Name : {} \nPrice : {} \nValidity Days : {}\nDescription : {}".format(
            package.name, package.price, package.validity_days, package.description)
        if instance.package_details != correct_package_details:
            instance.package_details = correct_package_details
            instance.save()


post_save.connect(save_package_details, sender=Recharge)
