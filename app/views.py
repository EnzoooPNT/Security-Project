from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from .token import generatorToken
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Security_Project import settings
from django.core.mail import send_mail, EmailMessage

# Create your views here.

# Page principale

def home(request):
    return render(request, 'app/index.html')

#Créer un compte

def register(request):
    if request.method == "POST" :
        
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        if User.objects.filter(username=username):
            messages.error(request, "Ce nom d'utilisateur est déja pris")
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request, "Cette adresse mail est deja prise")
            return redirect('register') 
        if password != password1:
            messages.error(request, "Les deux mots de passe ne sont pas identiques")
            return redirect('register')
        my_user = User.objects.create_user(username, email, password)
        my_user.first_name= firstname
        my_user.last_name= lastname
        my_user.is_active = False
        my_user.save()
        messages.success(request, "Votre compte a été créé avec succès")
        
        #email de bienvenu 
        
        subject = "Bienvenu sur le projet authentification"
        message = "Bienvenu " + my_user.first_name + " " + my_user.last_name + "\n Nous sommes heureux de vous compter parmi nous. \n\n\n Merci \n Le groupe de Nicolas, Nathy, Florian et Enzo."
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        
        #email de confirmation
        
        current_site = get_current_site(request)
        email_subject = "Confirmation de l'adresse mail sur le projet authentification"
        messageConfirm = render_to_string("emailconfirm.html", {
            "name" : my_user.first_name,
            "domain" : current_site.domain,
            "id" : urlsafe_base64_encode(force_bytes(my_user.pk)), 
            "token" : generatorToken.make_token(my_user)
        })
        
        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [my_user.email]
        )
    
        email.fail_silently = True
        email.send()
        return redirect('login') 
            
    return render(request, 'app/register.html')

# Se connecter

def Login(request):
    if request.method == "POST" :
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        my_user = User.objects.get(username=username)
        
        if user is not None :
            login(request, user)
            firstname = user.first_name
            return render(request, 'app/index.html', {'firstname':firstname})
        
        # Quand l'utilisateur essaye de se connecter alors qu'il n'a pas confirmé son email
        
        elif my_user.is_active == False:
            messages.error(request, "Votre adresse mail n'a pas été confirmé")
        else: 
            messages.error(request, "Mauvaise authentification")
            return redirect('login')
    return render(request, 'app/login.html')

# Déconnexion

def Logout(request):
    logout(request)
    messages.success(request, '')
    return redirect('home') 

# Verification si on a faire au bon utilisateur

def activate(request, uidb64, token) : 
    try:
        id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=id)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # On reconnait l'utilisateur
    
    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a été confirmé")
        return redirect('login')
    else:
        messages.error(request, "La confirmation de votre email a échoué")
        return redirect('home')