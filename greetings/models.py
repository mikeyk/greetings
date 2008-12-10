from django.db import models
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from greetingsweb.admin import site
# Create your models here.

class Template(models.Model):
    name = models.CharField(blank=True, max_length=255)

class Email(models.Model):
    address = models.TextField()
    def __unicode__(self):
        return self.address

class Phone(models.Model):
    number = models.TextField()
    
class Person(models.Model):
    emails = models.ManyToManyField(Email, null=True, blank=True)
    phones = models.ManyToManyField(Phone, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    def __unicode__(self):
        if self.name:
            return self.name
        elif self.phones:
            return self.phones
        elif self.emails:
            return self.emails
 
class EmailInline(admin.StackedInline):
    model = Email

class PhoneInline(admin.StackedInline):
    model = Phone

    
class Card (models.Model):
    from_person = models.ForeignKey(Person, related_name="from_person")
    to_people = models.ManyToManyField(Person, related_name="to_people", null=True, blank=True)
    audio_file = models.FileField(upload_to='audio_uploads/', null=True, blank=True)
    image_file = models.FileField(upload_to='image_uploads/', null=True, blank=True)
    template = models.ForeignKey(Template, null=True, blank=True)
    text_content = models.TextField()
    short_hash = models.CharField(max_length=10, null=True, blank=True)
    def __unicode__(self):
        return "Card from %s to %s that says %s" % (self.from_person, self.to_people, self.text_content)



class MyUserAdmin(UserAdmin):
    inlines = []
    
class ProfileAdmin(admin.ModelAdmin):
    # inlines = [EmailInline, PhoneInline]
    pass
    
site.register(Template)
site.register(Card)
site.register(Email)
site.register(Phone)
site.register(Person, ProfileAdmin)
site.register(User, MyUserAdmin)