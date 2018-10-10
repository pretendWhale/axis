from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.shortcuts import get_object_or_404
from .models import *
from .forms import ExplanationForm
from django.forms import formset_factory, modelformset_factory


# Create your views here.


def show_explanations(request):
	if 'mooclet' in request.GET:
		mooclet = Mooclet.objects.get_object_or_404(pk=request.GET['mooclet'])
		exps = mooclet.get_explanation_set()
		return JsonResponse(serializers.serialize('json',exps), safe=False)
	else:
		return JsonResponse({'error':'please provide MOOClet ID as a GET param'})


def show_filtered_explanations(request):
	if 'mooclet' in request.GET:
		mooclet = Mooclet.objects.get_object_or_404(pk=request.GET['mooclet'])
		exps = mooclet.filter_explanations()
		return JsonResponse(exps, safe=False)
	else:
		return JsonResponse({'error':'please provide MOOClet ID as a GET param'})


def update_explanation_set(request):
	if 'mooclet' in request.GET:
		mooclet = Mooclet.objects.get_object_or_404(pk=request.GET['mooclet'])
		exps = mooclet.filter_explanations()
		exps = [exp["text"] for exp in exps]
		versions = mooclet.get_versions()
		versions = [version["text"] for version in versions]

		exps_to_add = []
		for exp in exps:
			if exp not in versions:
				exps_to_add.append(exp)
	else:
		return JsonResponse({'error':'please provide MOOClet ID as a GET param'})


def select_versions(request):
	ExpFormSet = modelformset_factory(Explanation, form=ExplanationForm, fields=('text', 'add_to_version_set', 'rating'), extra=0)
	if request.method == 'GET':
		if 'mooclet' in request.GET:
			mooclet = Mooclet.objects.get_object_or_404(pk=request.GET['mooclet'])
			exps = mooclet.get_explanation_set()
			
			expforms = ExpFormSet(queryset=Explanation.objects.filter(mooclet=mooclet))
			print(expforms)
			# expforms = []
			# for exp in exps:
			# 	expforms.append(ExplanationForm(instance=exp))
			return render(request, 'axis_app/add_explanation.html', {'expforms': expforms})

	elif request.method == 'POST':
		print("starting post")
		expformset = ExpFormSet(request.POST)
		#print(expformset)
		exp_instances = expformset.save()
		if len(exp_instances) > 0:
			new_exps = [exp for exp in exp_instances if exp.add_to_version_set]
			mooclet = exp_instances[0].mooclet
			mooclet.add_versions(new_exps)
		return JsonResponse({"finished":"finished"})




		#compare versions to explanations and add any explanations that aren't already in the version set 
