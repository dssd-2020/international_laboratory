from django.forms import ModelForm
from app.models import *

class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'


class ProtocolForm(ModelForm):
    class Meta:
        model = Protocol
        fields = '__all__'
        # exclude = ['responsible']

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        