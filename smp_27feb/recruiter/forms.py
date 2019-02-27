from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recruiter, Job


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class UpdateProfileForm(forms.ModelForm):
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    def __init__(self, recruiter=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if recruiter is not None:
            self.fields["full_name"].initial = recruiter.full_name
            self.fields["phone"].initial = recruiter.phone
            self.fields["details"].initial = recruiter.details
            self.fields["recruiter_type"].initial = recruiter.recruiter_type

    class Meta:
        model = Recruiter
        fields = ('full_name', 'phone', 'recruiter_type', 'details')
        exclude = ('email', 'user', 'email_confirmed')


class JobPostForm(forms.ModelForm):

    class Meta:
        model = Job
        exclude = ('posted_by', 'posted_on')


class JobUpdateForm(forms.ModelForm):
    def __init__(self, job=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if job is not None:
            self.fields["role"].initial = job.role
            self.fields["headline"].initial = job.headline
            self.fields["industry"].initial = job.industry
            self.fields["experience"].initial = job.experience
            self.fields["qualifications"].initial = job.qualifications.all()
            self.fields["skills"].initial = job.skills.all()
            self.fields["company_name"].initial = job.company_name
            self.fields["address"].initial = job.address
            self.fields["city"].initial = job.city
            self.fields["salary_from"].initial = job.salary_from
            self.fields["salary_upto"].initial = job.salary_upto
            self.fields["description"].initial = job.description
            self.fields["phone"].initial = job.phone
            self.fields["email"].initial = job.email
            self.fields["requirements"].initial = job.requirements

    class Meta:
        model = Job
        exclude = ('posted_by', 'posted_on')


