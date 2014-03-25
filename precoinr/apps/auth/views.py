from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext




def login_user(request):
    username = password = ''

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/account')
            else:
                return redirect('/login')#TODO:
        else:
            return redirect('/login')#TODO:

    return render_to_response('login.html',
                              {'username': username},
                              context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return redirect('/login')