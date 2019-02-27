from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, reverse, get_list_or_404, get_object_or_404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist

from .tokens import account_activation_token
from .forms import SignUpForm, UpdateProfileForm, JobPostForm, JobUpdateForm
from django.conf import settings
from .models import Recruiter, Job, CandidateLike
from portal.models import Candidate, Proposal, Package, Recharge
from .filters import CandidateFilter
from portal.my_messages import no_subscription_message

recruiter_login_url = '/recruiter/login/'


def subscription_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        recruiter = request.user.recruiter
        if recruiter.has_subscription():
            return function(request, *args, **kwargs)
        else:
            messages.error(request, no_subscription_message)
            return redirect('recruiter:account')
    return wrap


class SubscriptionRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.recruiter.has_subscription():
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.warning(request, no_subscription_message)
            return redirect('recruiter:account')


@login_required
def account(request):
    return render(request, 'recruiter/account.html',
                  {'recruiter': request.user.recruiter,
                   'packages': Package.objects.filter(available=True, user_type='Recruiter')})


@login_required
def recharge_make(request, package_id):
    if hasattr(request.user, 'recruiter'):
        package = get_object_or_404(Package, id=package_id, user_type='Recruiter')
        # payment process
        # payment process
        recharge = Recharge.objects.create(user=request.user, package=package)
        messages.success(request, 'Recharge of {} rupees has been successful. Your validity is till {}'.format(
            recharge.package.price, request.user.recruiter.recharge_validity
        ))
        return redirect('recruiter:account')
    else:
        raise Http404


def home(request):
    return render(request, 'recruiter/home.html', {'user': request.user})


@login_required(login_url=recruiter_login_url)
def profile(request):
        return render(request, 'recruiter/profile.html', {'recruiter': request.user.recruiter})


@login_required(login_url=recruiter_login_url)
@subscription_required
def update_profile(request):
    recruiter = request.user.recruiter
    if request.method == "POST":
        form = UpdateProfileForm(data=request.POST, files=request.FILES, instance=recruiter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile Suucessfully Updated')
            return redirect('recruiter:profile')
        else:
            form = UpdateProfileForm(recruiter=recruiter)
            return render(request, 'recruiter/update_profile.html', {'form': form, 'form_invalid': "form is invalid !"})
    else:
        form = UpdateProfileForm(recruiter=recruiter)
        return render(request, 'recruiter/update_profile.html', {'form': form})


@login_required(login_url=recruiter_login_url)
def dashboard(request):
    return render(request, 'recruiter/dashboard.html', {'recruiter': request.user.recruiter})


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Recruiter.objects.create(user=user, email=user.email)
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8')
            token = account_activation_token.make_token(user)
            domain = current_site.domain
            activation_link = '{0}/recruiter/activate/{1}/{2}'.format(domain, uid, token)
            email_message = "\t Activate your account for {0} \n" \
                            "{1}".format(domain,     activation_link)
            send_mail(from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email], subject=subject, message=email_message)
            print(activation_link)
            return redirect('recruiter:account_activation_sent')
        else:
            form = SignUpForm()
    else:
        form = SignUpForm()
    return render(request, 'recruiter/register.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'recruiter/email_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.recruiter.email_confirmed = True
        user.recruiter.email = user.email
        user.recruiter.save()
        user.save()
        login(request, user)
        messages.success(request, 'Succfully confirmed your email address')
        return redirect('recruiter:profile')
    else:
        return render(request, 'recruiter/email_activation_invalid.html')



from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm



@login_required(login_url=recruiter_login_url)
@subscription_required
def job_post(request):
    if request.method == "POST":
        form = JobPostForm(data=request.POST, files=request.POST)
        if form.is_valid():
            temp_form = form.save(commit=False)
            temp_form.posted_by = request.user.recruiter
            temp_form.save()
            messages.success(request, 'succesfully posted a job')
            return redirect("recruiter:home")
        else:
            form = JobPostForm()
    else:
        form = JobPostForm()
    return render(request, 'recruiter/job_post.html', {'form': form})


class JobListView(LoginRequiredMixin, ListView):
    login_url = recruiter_login_url
    template_name = 'recruiter/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    # ordering = ['-id']

    def get_queryset(self):
        return self.request.user.recruiter.job_set.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'recruiter': self.request.user.recruiter})
        return context


class JobDetailView(LoginRequiredMixin, DetailView):
    login_url = recruiter_login_url

    model = Job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        job = super().get_object(queryset=queryset)
        if job.posted_by != self.request.user.recruiter:
            raise Http404
        else:
            return job


@login_required(login_url=recruiter_login_url)
@subscription_required
def job_update(request, job_id):
    job = request.user.recruiter.check_job_posted_by(job_id)
    if job:
        if request.method == "POST":
            form = JobUpdateForm(data=request.POST, files=request.FILES, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, 'Job Suucessfully Updated')
                return redirect('recruiter:job_list')
            else:
                form = JobUpdateForm(job=job)
                return render(request, 'recruiter/job_update.html', {'form': form, 'form_invalid': "form is invalid !"})
        else:
            form = JobUpdateForm(job=job)
            return render(request, 'recruiter/job_update.html', {'form': form})
    else:
        return HttpResponse("you dont have such job")


@login_required(login_url=recruiter_login_url)
def job_delete(request, job_id):
    job = request.user.recruiter.check_job_posted_by(job_id)
    if job:
        if request.method == "POST":
            job.delete()
            messages.success(request, "Job Deleted Succesfully. ({0})".format(job.headline))
            return redirect('recruiter:job_list')
        else:
            return render(request, 'recruiter/job_delete.html', {'job': job})
    else:
        return HttpResponse("you dont have such job")


class ProposalListView(LoginRequiredMixin, ListView):
    login_url = recruiter_login_url
    template_name = 'recruiter/proposal_list.html'
    context_object_name = 'proposals'
    paginate_by = 10

    def get_queryset(self):
        return Proposal.objects.filter(job__posted_by=self.request.user.recruiter)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'recruiter': self.request.user.recruiter})
        return context


class ProposalDetailView(LoginRequiredMixin, SubscriptionRequiredMixin, DetailView):

    model = Proposal
    template_name = 'recruiter/proposal_details.html'
    login_url = recruiter_login_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        proposal = super().get_object(queryset=queryset)
        if proposal.job.posted_by != self.request.user.recruiter:
            raise Http404
        else:
            return proposal


@login_required(login_url=recruiter_login_url)
@subscription_required
def candidate_search(request):
    candidates = Candidate.objects.all()
    ca_filter = CandidateFilter(request.GET, queryset=candidates)
    return render(request, 'recruiter/candidate_search.html', {'filter': ca_filter})


class CandidateDetailView(LoginRequiredMixin, SubscriptionRequiredMixin, DetailView):

    login_url = recruiter_login_url
    model = Candidate
    template_name = 'recruiter/candidate_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'candidate_liked': self.request.user.recruiter.check_candidate_liked(context['object'].id)})
        return context


@login_required(login_url=recruiter_login_url)
@subscription_required
def candidate_like(request, candidate_id):
    try:
        CandidateLike.objects.create(candidate=Candidate.objects.get(id=candidate_id), recruiter=request.user.recruiter)
        messages.success(request, 'Liked')
        return redirect('recruiter:candidate_details', pk=candidate_id)
    except:
        raise Http404


@login_required(login_url=recruiter_login_url)
def candidate_unlike(request, candidate_id):
    try:
        like = CandidateLike.objects.get(candidate__id=candidate_id, recruiter=request.user.recruiter)
        like.delete()
        messages.success(request, 'Unliked')
        return redirect('recruiter:candidate_details', pk=candidate_id)
    except:
        raise Http404


class CandidateLikeListView(LoginRequiredMixin, ListView):

    login_url = recruiter_login_url
    template_name = 'recruiter/candidate_like_list.html'
    context_object_name = 'candidate_likes'
    paginate_by = 1
    ordering = ['-created']

    def get_queryset(self):
        candidates = [cdlike.candidate for cdlike in self.request.user.recruiter.candidatelike_set.all()]
        return candidates

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'recruiter': self.request.user.recruiter})
        return context



@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('recruiter:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'recruiter/password_change.html', {'form': form})
