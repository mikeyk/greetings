# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.db.models.query import Q
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from greetingsweb.greetings.models import *
import base64


def get_greeting(request, greeting_id):
    greeting = get_object_or_404(Card, pk=greeting_id)
    json_response = dict()
    json_response['from'] = greeting.from_person.username
    json_response['to'] = str(greeting.to_people.all())
    json_response['text'] = greeting.text_content
    json_response['image_url'] = str(greeting.image_file)
    json_response['template'] = greeting.template
    json_response['audio_url'] = str(greeting.audio_file)
    
    return HttpResponse(simplejson.dumps(json_response))
    
def check_request_parameters(request, param_list):   
    for elem in param_list:
        if elem not in request.REQUEST:
            return False
    return True

def find_person_from_lists(email_list=None, phone_list=None):
    person = None
    if email_list:
        for el in email_list:
            try:                
                email = Email.objects.get(address=el.strip())
                print email
                person = Person.objects.get(emails=email)
                return person
            except Exception, e:
                pass
    if phone_list:
        for el in phone_list:
            try:
                phone = Phone.objects.get(number=el.strip())
                person = Person.objects.get(phones=phone)
                return person
            except Exception, e:
                pass
    return None
            
    


def new_user(request):
    json_response = dict()
    try:

        if check_request_parameters(request, ("email_list", "phone_list", "name") ):
            email_list = request.REQUEST['email_list'].split(',')
            phone_list = request.REQUEST['phone_list'].split(',')            
            user = find_person_from_lists(email_list=email_list, phone_list=phone_list)
            if not user:
                user = Person()            
                user.name = request.REQUEST['name']
                user.save()
            
                # true unless otherwise
            
                json_response['success'] = True            
                for email in email_list:
                    if len(Email.objects.filter(address=email)) > 0:
                        json_response['success'] = False
                        json_response['error'] = "Duplicate email"
                    else:
                        new_email = Email()
                        new_email.address = email
                        new_email.save()          
                        print "adding ", new_email.address          
                        user.emails.add(new_email)
                    
                for phone in phone_list:
                    if len(Phone.objects.filter(number=phone)) > 0:
                        json_response['success'] = False
                        json_response['error'] = "Duplicate phone"
                    else:
                        new_phone = Phone()
                        new_phone.number = phone                    
                        new_phone.save()
                        user.phones.add(new_phone)

            json_response['new_id'] = user.id
        else:
            json_response['success'] = False
            json_response['error'] = "missing parameters"
            
    except Exception, e:
        json_response['success'] = False
        json_response['error'] = str(e)
    
    return HttpResponse(simplejson.dumps(json_response))
    
def get_or_create_person_from_phone(phone):
    try:
        user = find_person_from_lists(phone_list=(phone,))
        if user:
            return user
        else:
            user = Person()
            user.save()
            user.phones.add(phone)
            return user
    except Exception, e:
        return None

def make_greeting(request):
    json_response = dict()
    try:
        if check_request_parameters(request, ("from_user_id", "to_people_phones") ):
            new_card = Card()
            new_card.from_person = Person.objects.get(pk=request.REQUEST['from_user_id'])            

            
            new_card.save()            
            for phone in request.REQUEST["to_people_phones"].split(","):
                other_person = get_or_create_person_from_phone(phone)
                if other_person:
                    new_card.to_people.add( get_or_create_person_from_phone(phone) )
            if check_request_parameters(request, ("text",) ):
                new_card.text_content = request.REQUEST["text"]


            new_card.save()
            json_response['success'] = True
            json_response['card_id'] = new_card.id
        else:
            json_response['success'] = False
            json_response['error'] = "missing people ids"
            
    except Exception, e:
        print e
        json_response['success'] = False
        json_response['error'] = str(e) 
    return HttpResponse(simplejson.dumps(json_response))
    
def add_attachment(request):
    out_fl = open('out.caf', 'w')
    for eachfile in request.FILES:
        out_fl.write(request.FILES[eachfile].read())