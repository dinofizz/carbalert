from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Thread, SearchPhrase

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        # make user email field required
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


admin.site.unregister(User)
admin.site.register(User, EmailRequiredUserAdmin)
admin.site.register(Thread)
admin.site.register(SearchPhrase)
# Register your models here.
