from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from rest_framework import serializers
from .forms import CreateUserForm, ProjectUploadForm,UpdateProfileForm,ProfileForm
from .models import Profile, Projects
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import ProfileSerializer,ProjectsSerializer


# Create your views here.
def index(request):
    projects = Projects.get_projects()
    return render(request, 'index.html', {"projects":projects})

def register(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:
		form = CreateUserForm()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				user = form.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + user)

				return redirect('login')
			

		context = {'form':form}
		return render(request, 'registration/register.html', context)

def loginUser(request):
	if request.user.is_authenticated:
		return redirect('index')
	else:
		if request.method == 'POST':
			username = request.POST.get('username')
			password =request.POST.get('password')

			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('index')
			else:
				messages.info(request, 'Username or password is incorrect')

		context = {}
		return render(request, 'registration/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

def profile(request):
    '''
	returns user profile from a pool of profiles
	'''
    current_user=request.user
    profile= Profile.objects.filter(user=current_user).first()
     
    
    return render(request,'profile.html',{"profile":profile,"current_user":current_user})

def profile_update(request):
    current_user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.user = current_user
            image.save()
        return redirect('profile')

    else:
        form = ProfileForm()
        return render(request,'update_profile.html',{"form":form})

@login_required (login_url="login")
def project_post(request):
    '''
    method that post projects 
    '''
    if request.method == 'POST':
        form = ProjectUploadForm(request.POST,request.FILES)
        print(form.errors)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user.profile
            project.save()
            return redirect('index')
    else:
        form = ProjectUploadForm()
    return render(request,'project_upload.html', {"form":form})

def search_results(request):

    if 'project' in request.GET and request.GET["project"]:
        search_term = request.GET.get("project")
        searched_project = Projects.search_by_project_name(search_term)
        message = f"{search_term}"

        return render(request, 'search.html',{"message":message,"projects": searched_project})

    else:
        message = "You haven't searched for any term"
        return render(request, 'search.html',{"message":message})

class ProfileList(APIView):
    def get(self, request, format=None):
        all_profiles = Profile.objects.all()
        serializers = ProfileSerializer(all_profiles,many=True)
        return Response(serializers.data)

class ProjectsList(APIView):
    def get(self, request, format=None):
        all_projects = Projects.objects.all()
        serializers = ProjectsSerializer(all_projects, many=True)
        return Response(serializers.data)