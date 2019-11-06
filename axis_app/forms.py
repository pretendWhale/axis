from django import forms
from .models import *


class ExplanationForm(forms.ModelForm):
	add_to_version_set = forms.BooleanField(initial=True, required=False)
	text = forms.CharField(widget=forms.Textarea(attrs={'readonly':'readonly'}))

	class Meta:
		model = Explanation
		fields = ('text', 'add_to_version_set', 'rating')

class MoocletForm(forms.ModelForm):
	#add_to_version_set = forms.BooleanField(initial=True, required=False)

	class Meta:
		model = Mooclet
		fields = ('input_engine_id', 'input_engine_name', 'output_engine_id', 'output_engine_name', 'explanation_variable','filtering_method', 'notes')

class VersionForm(forms.Form):
	version_id = forms.IntegerField()
	name = forms.CharField()
	text = forms.CharField(widget=forms.Textarea())