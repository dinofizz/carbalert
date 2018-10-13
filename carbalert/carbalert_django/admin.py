from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy

from .models import Thread, SearchPhrase


class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        self.fields["email"].required = True


class MyUserCreationForm(EmailRequiredMixin, UserCreationForm):
    pass


class MyUserChangeForm(EmailRequiredMixin, UserChangeForm):
    pass


class EmailRequiredUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "fields": ("username", "email", "password1", "password2"),
                "classes": ("wide",),
            },
        ),
    )


class CarbAlertAdminSite(AdminSite):
    carb_alert = "CarbAert"
    site_title = ugettext_lazy(carb_alert)
    site_header = ugettext_lazy(carb_alert)
    index_title = ugettext_lazy(carb_alert)


admin_site = CarbAlertAdminSite()
admin.site.unregister(User)
admin.site.register(User, EmailRequiredUserAdmin)
admin.site.register(Thread)
admin.site.register(SearchPhrase)
