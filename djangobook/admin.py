# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.utils.translation import ugettext as _
from cargo.djangobook.models import News, Claims, ClaimStatus, CLAIM_STATUSES

class NewsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None,{'fields': ('title', 'datetime')}),
        (_(u'Contents'), {'fields': ('text',)}))
    list_display = ('title', 'datetime')
    ordered = ('-datetime')
admin.site.register(News, NewsAdmin)

#class ClaimStatusAdmin(admin.ModelAdmin):
#     list_display = ('claim', 'status')
#     ordered = ('-applied')
#admin.site.register(ClaimStatus, ClaimStatusAdmin)

class ClaimsAdminForm(forms.ModelForm):
    status = forms.ChoiceField(choices=CLAIM_STATUSES)

    def __init__(self, *args, **kwargs):
        super(ClaimsAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['status'].initial = self.instance.get_status()

    def save(self, *args, **kwargs):
        d = self.cleaned_data
        if self.instance and d.get('status'):
            self.instance.set_status(d.get('status'))
        
    class Meta:
        model = Claims

# additional field: claim status
def claim_status_field(claim):
    try:
        return ClaimStatus.objects.filter(claim=claim).order_by('-applied')[0].status
    except Exception:
        return _(u'Unknown')
claim_status_field.short_description = _(u'Claim status')
    
class ClaimsAdmin(admin.ModelAdmin):
    form = ClaimsAdminForm
    fieldsets = (
        (_(u'Meta'),
         {'fields': ('datetime', 'url', 'status')}),
        (_(u'Error'),
         {'fields': ('ctx_left', 'selected', 'ctx_right')}),
        (_(u'Comment'),
         {'fields': ('email','comment')})
        )
    list_display = ('url', 'comment', 'email', #'datetime')
                    claim_status_field, 'datetime')
    ordered = ('-datetime')

admin.site.register(Claims, ClaimsAdmin)

