
# chat/forms.py

#########################################################################################################

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Room, Message

#########################################################################################################

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'is_private']
        labels = {
            'name': _("Room name"),
            'is_private': _("Make room private")
        }

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = _("Room name")
        self.fields['is_private'].label = _("Make room private")

#########################################################################################################