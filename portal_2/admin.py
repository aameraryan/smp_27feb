from django.contrib import admin
from .models import City, Qualification, Role, Candidate, Industry, Skill, Proposal, Recharge, Package

admin.site.register(City)
admin.site.register(Qualification)
admin.site.register(Industry)
admin.site.register(Candidate)
admin.site.register(Role)
admin.site.register(Skill)
admin.site.register(Proposal)
admin.site.register(Package)
admin.site.register(Recharge)
