from core import forms
from core import models
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.contrib import auth

@login_required
def account_index(request):
    """
    The 'startpage' for logged in users
    """
    return direct_to_template(request, 'core/account/index.html', {'request': request})

@login_required
def account_edit(request):
    """
    Edit account settings
    """
    message = ""
    account = models.Account.objects.get(id = request.user.id)
    
    if request.method == 'POST':
        form = forms.AccountForm(request.POST, instance = account)
        if form.is_valid():
            form.save()
            message = 'Your profile has been updated'
    else:
        form = forms.AccountForm(instance = account)
    
    return direct_to_template(  request,
                                'core/account/edit.html',
                                {   'request': request, 
                                    'form': form,
                                    'message': message})

@login_required
def account_delete(request, account_id):
    """
    Delete an account given the ID
    """
    account = models.Account.objects.get(id = account_id)
    account.delete()
    auth.logout(request)
    return redirect('/')

def account_login(request):
    """
    Method for logging in to Jeeves
    """
    error = False
    error_message = None

    if request.method == 'POST':
        account = auth.authenticate(username = request.POST['email'],
                                    password = request.POST['password'])
        
        if account:
            if account.is_active:
                auth.login(request, account)
                return redirect("/account")
            else:
                error = True
                error_message = "Your account has been disabled!"
        else:
            error = True
            error_message = "Your username and password were incorrect."
    
    return direct_to_template(  request,
                                'core/account/login.html',
                                {'form': forms.AuthenticationForm(),
                                'error': error,
                                'error_message': error_message,
                                'request': request})

def account_logout(request):
    """
    Logout an Account
    """
    auth.logout(request)
    return direct_to_template(request, 'core/account/logout.html', {'request': request})

def account_register(request):
    """
    Registration form for a new Jeeves account
    """
    if request.method == 'POST':
        form = forms.AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/account/register/complete')
    else:
        form = forms.AccountForm()

    return direct_to_template(  request,
                                'core/account/register.html',
                                {   'request': request,
                                    'form': form, })

def account_register_complete(request):
    """
    This is the page users are redirected to after
    a successful account registration
    """
    return direct_to_template(request, 'core/account/register_complete.html', {'request': request})

def index(request):
    """
    The very index
    """
    return direct_to_template(request, 'core/index.html', {'request': request})
