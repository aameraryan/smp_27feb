from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

from .tokens import account_activation_token
from .forms import SignUpForm, UpdateProfileForm, ProposalForm, ProposalUpdateForm
from django.conf import settings
from .models import Candidate, City, Industry, Role, Qualification, Proposal, Package, Recharge
from recruiter.models import Job
from .filters import JobFilter
from .my_messages import no_subscription_message


def first_page(request):
    return render(request, 'portal/first_page.html')


def subscription_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        candidate = request.user.candidate
        if candidate.has_subscription():
            return function(request, *args, **kwargs)
        else:
            messages.error(request, no_subscription_message)
            return redirect('portal:account')
    return wrap


class SubscriptionRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.candidate.has_subscription():
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.warning(request, no_subscription_message)
            return redirect('portal:account')


def home(request):
    return render(request, 'portal/home.html', {'user': request.user})


@login_required
def account(request):
    return render(request, 'portal/account.html',
                  {'candidate': request.user.candidate,
                   'packages': Package.objects.filter(available=True, user_type='Candidate')})


@login_required
def recharge_make(request, package_id):
    if hasattr(request.user, 'candidate'):
        package = get_object_or_404(Package, id=package_id, user_type='Candidate')
        # payment process
        # payment process
        recharge = Recharge.objects.create(user=request.user, package=package)
        messages.success(request, 'Recharge of {} rupees has been successful. Your validity is till {}'.format(
            recharge.package.price, request.user.candidate.recharge_validity
        ))
        return redirect('portal:account')
    else:
        raise Http404


@login_required
def profile(request):
        return render(request, 'portal/profile.html', {'candidate': request.user.candidate})


@login_required
def update_profile(request):
    candidate = request.user.candidate
    if request.method == "POST":
        form = UpdateProfileForm(data=request.POST, files=request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Suucessfully Updated')
            return redirect('portal:profile')
        else:
            form = UpdateProfileForm(candidate=candidate)
            return render(request, 'portal/update_profile.html', {'form': form, 'form_invalid': "form is invalid !"})
    else:
        form = UpdateProfileForm(candidate=candidate)
        return render(request, 'portal/update_profile.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'portal/dashboard.html', {'candidate': request.user.candidate})


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Candidate.objects.create(user=user, email=user.email)
            current_site = get_current_site(request)
            subject = 'Activate Your Shadab Manpowers Account'
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8')
            token = account_activation_token.make_token(user)
            domain = current_site.domain
            activation_link = '{0}/activate/{1}/{2}'.format(domain, uid, token)
            email_message = "Email Verification from Shadab Manpowers\n" \
                            "Activate your account for {0} \n\n" \
                            "{1}".format(domain, activation_link)
            send_mail(from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email], subject=subject, message=email_message)
            return redirect('portal:account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'portal/register.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'portal/email_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.candidate.email_confirmed = True
        user.candidate.email = user.email
        user.candidate.save()
        user.save()
        login(request, user)
        messages.success(request, 'Succfully confirmed your email address')
        return redirect('portal:profile')
    else:
        return render(request, 'portal/email_activation_invalid.html')




from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


# JOB SEARCH VIEW
@login_required
@subscription_required
def job_search(request):
    jobs = Job.objects.all()
    j_filter = JobFilter(request.GET, queryset=jobs)
    return render(request, 'portal/job_search.html', {'filter': j_filter})


# JOB DETAIL VIEW
class JobDetailView(LoginRequiredMixin, SubscriptionRequiredMixin, DetailView):

    model = Job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['have_proposal'] = self.request.user.candidate.check_job_proposal_exist(context['object'].id)
        return context

    template_name = 'portal/job_details.html'


# PROPOSAL ADD VIEW
@login_required
@subscription_required
def proposal_add(request, job_id):
    if not request.user.candidate.check_job_proposal_exist(job_id):
        job = get_object_or_404(Job, id=job_id)
        if request.method == "POST":
            form = ProposalForm(data=request.POST)
            if form.is_valid():
                temp_form = form.save(commit=False)
                temp_form.posted_by = request.user.candidate
                temp_form.job = job
                temp_form.save()
                messages.success(request, 'succesfully added a proposal to job ({0})'.format(job.headline))
                return redirect("portal:job_search")
            else:
                form = ProposalForm()
        else:
            form = ProposalForm()
        return render(request, 'portal/proposal_add.html', {'form': form, 'job': job})
    else:
        return HttpResponse('proposal already exist')


# PROPOSAL DETAIL VIEW
class ProposalDetailView(LoginRequiredMixin, DetailView):

    model = Proposal

    def get_object(self, queryset=None):
        proposal = super().get_object(queryset=queryset)
        if proposal.posted_by != self.request.user.candidate:
            raise Http404()
        else:
            return proposal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        return context

    template_name = 'portal/proposal_details.html'


# PROPOSAL LIST VIEW
class ProposalListView(LoginRequiredMixin, ListView):
    template_name = 'portal/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 10
    ordering = ['-created']

    def get_queryset(self):
        return self.request.user.candidate.proposal_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'candidate': self.request.user.candidate})
        return context


# PROPOSAL UPDATE VIEW
@login_required
@subscription_required
def proposal_update(request, proposal_id):
    proposal = request.user.candidate.check_job_proposal_posted_by(proposal_id)
    if proposal:
        if request.method == "POST":
            form = ProposalUpdateForm(data=request.POST, instance=proposal)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile Suucessfully Updated')
                return redirect('portal:proposal_list')
            else:
                form = ProposalUpdateForm(proposal=proposal)
                return render(request, 'portal/proposal_update.html', {'form': form, 'form_invalid': "form is invalid !",
                                                                       'proposal': proposal})
        else:
            form = ProposalUpdateForm(proposal=proposal)
            return render(request, 'portal/proposal_update.html', {'form': form, 'proposal': proposal})
    else:
        return HttpResponse("you dont have such proposal")


# PROPOSAL DELETE VIEW
@login_required
def proposal_delete(request, proposal_id):
    proposal = request.user.candidate.check_job_proposal_posted_by(proposal_id)
    if proposal:
        if request.method == "POST":
            proposal.delete()
            messages.success(request, "Proposal Deleted Succesfully. ({0})".format(proposal.job.headline))
            return redirect('portal:proposal_list')
        else:
            return render(request, 'portal/proposal_delete.html', {'proposal': proposal})
    else:
        return HttpResponse("you dont have such Proposal")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('portal:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'portal/password_change.html', {'form': form})


# def password_reset_complete(request):
#     if hasattr(request.user, 'candidate'):
#         return redirect('portal:home')
#     elif hasattr(request.user, 'recruiter'):
#         return redirect('recruiter:home')
#     else:
#         raise Http404
