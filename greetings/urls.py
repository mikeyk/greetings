from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin


urlpatterns = patterns('',
    url(r'greeting/(?P<greeting_id>(\d+))', 'greetingsweb.greetings.views.get_greeting', name="get-greeting"),
    url(r'attach/', 'greetingsweb.greetings.views.add_attachment', name="add-attachment"),
    url(r'makegreeting/', 'greetingsweb.greetings.views.make_greeting', name='make-greeting'),
    url(r'newuser/', 'greetingsweb.greetings.views.new_user', name='new-user'),
)