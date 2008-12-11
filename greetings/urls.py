from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin


urlpatterns = patterns('',
    url(r'card/(?P<hash>(\w+))/', 'greetingsweb.greetings.views.card_from_hash', name="get-greeting"),
    url(r'secret/greetingbyid/(?P<greeting_id>(\d+))/', 'greetingsweb.greetings.views.card_from_id', name="get-greeting"),    
    url(r'attach/', 'greetingsweb.greetings.views.add_attachment', name="add-attachment"),
    url(r'makegreeting/', 'greetingsweb.greetings.views.make_greeting', name='make-greeting'),
    url(r'newuser/', 'greetingsweb.greetings.views.new_user', name='new-user'),
    url(r'infofor/(?P<person_id>(\d+))/', "greetingsweb.greetings.views.more_info_for_person", name='person-info'),
    url(r'allcardsfor/(?P<person_id>(\d+))/(?P<since_id>(\d+))/', "greetingsweb.greetings.views.all_cards_for_id", name='cards-for'),
)