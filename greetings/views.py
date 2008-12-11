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
import math
from random import random
import datetime
from django.conf import settings
import hashlib

def card_from_hash(request, hash):
    json_response = dict()
    try:
        card = Card.objects.get(short_hash=hash)
        return get_greeting(request, card)
    except Exception, e:
        json_response['success'] = False
        json_response['error'] = str(e)
        return HttpResponse(simplejson.dumps(json_response))

def card_from_id(request, greeting_id):
    json_response = dict()
    try:
        card = Card.objects.get(pk=greeting_id)
        return get_greeting(request, card)
    except ObjectDoesNotExist, e:
        json_response['success'] = False
        json_response['error'] = str(e)
        return HttpResponse(simplejson.dumps(json_response))

def make_hash_list_from_objects(objects, field):
    hash_list = list()
    for entry in objects:
        m = hashlib.md5()
        m.update( eval("entry."+field) )
        hash_list.append(m.hexdigest())
    return hash_list


def all_cards_for_id(request, person_id, since_id=0):
    json_list = list()
    for card in Card.objects.filter(to_people=person_id, pk__gt=since_id).order_by("-id"):
        json_list.append(json_from_card(card))
    return HttpResponse( simplejson.dumps(json_list) )

def more_info_for_person(request, person_id):
    json_response = dict()
    try:
        person = Person.objects.get(pk=person_id)
        json_response['name'] = person.name
        hash_list = list()
        for phone in person.phones.all() :
            m = hashlib.md5()
            m.update(phone.number)
            hash_list.append(m.hexdigest())
        json_response['phone_list'] = make_hash_list_from_objects(person.phones.all(), "number")
        json_response['email_list'] = make_hash_list_from_objects(person.emails.all(), "address")        
        json_response['success'] = True
    except Exception, e:
        json_response['success'] = False
        json_response['error'] = str(e)
    return HttpResponse( simplejson.dumps(json_response) )

def json_from_card(card):
    greeting = card
    json = dict()
    json['from'] = greeting.from_person.name
    json['from_id'] = greeting.from_person.id
    json['to'] = [str(person) for person in greeting.to_people.all() ]
    json['hash'] = greeting.short_hash
    json['text'] = greeting.text_content
    if greeting.image_file:
        json['image_url'] = greeting.image_file.url
    json['template'] = greeting.template
    if greeting.audio_file:
        print greeting.audio_file.name
        print greeting.audio_file.url
        json['audio_url'] = greeting.audio_file.url
    json['card_id'] = greeting.id
    return json

def get_greeting(request, card):
    json = dict()
    try:
        json = json_from_card(card)
        json['success'] = True
    except Exception, e:
        json['success'] = False
        json['error'] = str(e)
    return HttpResponse(simplejson.dumps(json))
    
def check_request_parameters(request, param_list):   
    for elem in param_list:
        if elem not in request.REQUEST:
            return False
    return True

def find_person_from_lists(email_list=None, phone_list=None):
    person = None
    if email_list:
        for el in email_list:
            if len(el) > 0:
                try:                
                    email = Email.objects.get(address=el.strip())
                    print "Email is", email.address
                    person = Person.objects.get(emails=email)
                    return person
                except Exception, e:
                    pass
    if phone_list:
        for el in phone_list:
            if len(el) > 0:
                try:
                    phone = Phone.objects.get(number=el.strip())
                    print "Phone is", phone.number
                    person = Person.objects.get(phones=phone)
                    return person
                except Exception, e:
                    print e
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
                    if len(email) > 0:
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
                    if len(phone) > 0:                    
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
        
def random_lowercase_list(length=4):
    return_list = list()
    for el in range(0, length):
        return_list.append("%c" % (math.floor(random()*26)+97))
    return return_list

def make_greeting(request):
    print request.POST
    json_response = dict()
    try:
        if check_request_parameters(request, ("from_user_id", "to_people_phones") ):
            new_card = Card()
            new_card.from_person = Person.objects.get(pk=request.REQUEST['from_user_id'])            
            card_hash = None
            while( card_hash == None ):
                new_hash = "".join([str(x) for x in random_lowercase_list()])
                if len(Card.objects.filter(short_hash=new_hash)) == 0:
                    card_hash = new_hash
            new_card.short_hash = card_hash
            
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
            json_response['hash'] = new_card.short_hash
        else:
            json_response['success'] = False
            json_response['error'] = "missing people ids"
            
    except Exception, e:
        json_response['success'] = False
        json_response['error'] = str(e) 
    return HttpResponse( simplejson.dumps(json_response) )

def check_or_make_dir(dirname):
    import errno
    import os

    try:
        # os.makedirs will also create all the parent directories
        os.makedirs(dirname)
    except OSError, err:
        if err.errno == errno.EEXIST:
            if os.path.isdir(dirname):
                print "directory already exists"
            else:
                print "file already exists, but not a directory"
                raise # re-raise the exception
        else:
            raise
    
    
def open_from_hash(request,hash):
    return HttpResponseRedirect("greet://%s" % hash)    

def add_attachment(request):
    print "Attaching..."
    json_response = dict()
    if check_request_parameters(request, ('card_id', 'hash', 'type')) and request.FILES:
        try:
            card = get_object_or_404(Card, pk=request.REQUEST['card_id'])
            

            date_string = datetime.datetime.now().strftime('%m-%d')
            short_name = ""
            image = False
            sound = False
            if request.REQUEST['type'] == 'image':
                image = True
                short_name = "image_uploads/%s/" % (date_string)
                dir_name = settings.MEDIA_ROOT + (short_name)
                check_or_make_dir(dir_name)
                out_url = dir_name + "%s.caf"%card.short_hash
            elif request.REQUEST['type'] == 'sound':
                sound = True
                short_name = "audio_uploads/%s/" % (date_string)
                dir_name = settings.MEDIA_ROOT + (short_name)
                check_or_make_dir(dir_name)
                out_url = dir_name + "%s.caf"%card.short_hash
            print "Out to ", out_url
            out_fl = open(out_url, 'w')
            for eachfile in request.FILES:
                out_fl.write(request.FILES[eachfile].read())
            if image:
                card.image_file = out_url
            elif sound:
                card.audio_file = out_url
            card.save()
            json_response['success'] = True
        except Exception, e:
            json_response['success'] = False
            json_response['error'] = str(e)
    else:
        json_response['success'] = False
        json_response['error'] = "missing params"
    print simplejson.dumps(json_response)
    return HttpResponse(simplejson.dumps(json_response))
            
            
            
            
            
            
            