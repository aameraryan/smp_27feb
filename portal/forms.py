from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Candidate, Proposal, Skill, Role, Industry, City, Qualification


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class UpdateProfileForm(forms.ModelForm):

    skills = forms.ModelMultipleChoiceField(required=False, queryset=Skill.objects.all())
    roles = forms.ModelMultipleChoiceField(required=False, queryset=Role.objects.all())
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    details = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    resume = forms.FileField(required=False, widget=forms.FileInput(), label='Upload New')

    # address = forms.CharField(widget=forms.Textarea(attrs={'row': 4, 'col': 10}))

    # roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, candidate=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if candidate is not None:
            self.fields["first_name"].initial = candidate.first_name
            self.fields["last_name"].initial = candidate.last_name
            self.fields["full_name"].initial = candidate.full_name
            self.fields["qualification"].initial = candidate.qualification
            self.fields["skills"].initial = candidate.skills.all()
            self.fields["roles"].initial = candidate.roles.all()
            self.fields["industry"].initial = candidate.industry
            self.fields["phone"].initial = candidate.phone
            self.fields["experience"].initial = candidate.experience
            self.fields["city"].initial = candidate.city
            self.fields["details"].initial = candidate.details
            self.fields["address"].initial = candidate.address
            if candidate.resume:
                self.fields["resume"].initial = candidate.resume.file

    class Meta:
        model = Candidate
        exclude = ['email', 'user', 'email_confirmed', 'last_recharge', 'recharge_validity']


class ProposalForm(forms.ModelForm):

    class Meta:
        model = Proposal
        exclude = ('on', 'job', 'posted_by')


class ProposalUpdateForm(forms.ModelForm):
    def __init__(self, proposal=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if proposal is not None:
            self.fields["message"].initial = proposal.message

    class Meta:
        model = Proposal
        exclude = ('on', 'posted_by', 'job')

