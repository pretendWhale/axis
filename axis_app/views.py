from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.shortcuts import get_object_or_404
from .models import *
from .forms import ExplanationForm, MoocletForm, VersionForm
from django.forms import formset_factory, modelformset_factory
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, CreateView
import requests
from axis.settings import MOOCLET_URL_BASE, MOOCLET_API_TOKEN

# Create your views here.


def show_explanations(request):
	if 'mooclet' in request.GET:
		mooclet = get_object_or_404(Mooclet, pk=request.GET['mooclet'])
		exps = mooclet.get_explanation_set()
		return JsonResponse(serializers.serialize('json',exps), safe=False)
	else:
		return JsonResponse({'error':'please provide MOOClet ID as a GET param'})

def show_current_versions(request, mooclet):
	mooclet = get_object_or_404(Mooclet, pk=mooclet)
	versions = mooclet.get_current_versions()
	return render(request, 'axis_app/curr_versions.html', {'mooclet': mooclet, 'versions': versions})

def show_filtered_explanations(request):
	if 'mooclet' in request.GET:
		mooclet = Mooclet.objects.get(pk=request.GET['mooclet'])
		exps = mooclet.filter_explanations()
		return JsonResponse(exps, safe=False)
	else:
		return JsonResponse({'error':'please provide MOOClet ID as a GET param'})


def update_explanation_set(request):
	if 'mooclet' in request.GET:
		mooclet = Mooclet.objects.get(pk=request.GET['mooclet'])
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

class MoocletListView(ListView):
	model = Mooclet
	paginate_by = 100

class MoocletFormView(UpdateView):
	model = Mooclet
	template_name_suffix = '_update_form'
	fields = ('input_engine_id', 'input_engine_name', 'output_engine_id', 'output_engine_name', "explanation_variable","filtering_method", "notes")
	success_url = '/mooclet'

class MoocletCreateView(CreateView):
	model = Mooclet
	template_name_suffix = '_create_form'
	fields = ('input_engine_id', 'input_engine_name', 'output_engine_id', 'output_engine_name', "explanation_variable","filtering_method", "notes")
	success_url = '/mooclet'

def select_versions(request, mooclet):
	ExpFormSet = modelformset_factory(Explanation, form=ExplanationForm, fields=('text', 'add_to_version_set', 'rating'), extra=0)
	mooclet = get_object_or_404(Mooclet, pk=mooclet)
	if request.method == 'GET':
		exps = mooclet.get_explanation_set()
		expforms = ExpFormSet(queryset=Explanation.objects.filter(mooclet=mooclet))
		print(expforms)
		# expforms = []
		# for exp in exps:
		# 	expforms.append(ExplanationForm(instance=exp))
		return render(request, 'axis_app/add_explanation.html', {'expforms': expforms})

	elif request.method == 'POST':
		print("starting post")
		expformset = ExpFormSet(request.POST, initial=Explanation.objects.filter(mooclet=mooclet))
		print(expformset)
		exp_instances = expformset.save()
		print(len(exp_instances))
		added_versions = None
		if len(exp_instances) > 0:
			new_exps = [exp for exp in exp_instances if exp.add_to_version_set]
			print("new exps: "+str(len(new_exps)))
			mooclet = exp_instances[0].mooclet
			added_versions = mooclet.add_versions(new_exps)
		return JsonResponse({"finished":"finished", "new_versions":added_versions}, safe=False)


def edit_version(request,version):
	if request.method == 'GET':
		#instantiate form and send to template
		version_form = VersionForm(initial=version)
		return render(request, 'axis_app/edit_version.html', {'version_form':version_form})

	elif request.method == 'POST':
		version_form = VersionForm(request.POST, initial=version)
		if form.has_changed():
			req_url = MOOCLET_URL_BASE+'/version/'+str(version_form['id'])
			payload = {'name': version_form['name'], 'text': version_form['text']}
			headers = {'Authorization': MOOCLET_API_TOKEN}
			req = requests.patch(req_url, data=payload, headers=headers)
			if req.status_code < 200 or req.status_code >= 300:
				print('something went wrong!')
				print(req.json)
			else:
				return JsonResponse({"finished":"finished", "new_text":version_form['text']}, safe=False)


		#compare versions to explanations and add any explanations that aren't already in the version set 
