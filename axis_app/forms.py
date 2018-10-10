from django import forms
from .models import *


class ExplanationForm(forms.ModelForm):
	add_to_version_set = forms.BooleanField(initial=True)

	class Meta:
		model = Explanation
		fields = ('text', 'add_to_version_set', 'rating')

