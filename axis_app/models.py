from django.db import models
import requests
import uuid
import datetime
from axis.settings import MOOCLET_URL_BASE, MOOCLET_API_TOKEN
from . import explanation_filters
# Create your models here.


class Mooclet(models.Model):
	input_engine_id = models.PositiveIntegerField()#the pk of mooclet on mooclet_engine
	input_engine_name = models.CharField(blank=True, null=True, max_length=512)
	output_engine_id = models.PositiveIntegerField(default=0)#the pk of mooclet on mooclet_engine
	output_engine_name = models.CharField(blank=True, null=True, max_length=512)
	explanation_variable = models.CharField(blank=True, null=True, max_length=512)# var to get explanations from
	filtering_method = models.ForeignKey('FilteringMethod', on_delete=models.CASCADE)
	notes = models.TextField(blank=True, null=True)

	def get_explanation_set(self):
		filtering = {
		'mooclet': self.input_engine_id,
		'variable__name': self.explanation_variable
		}
		r = requests.get(MOOCLET_URL_BASE+'/value', params=filtering, headers={'Authorization': MOOCLET_API_TOKEN})
		explanations = r.json()
		print(explanations)
		axis_explanations = []
		for explanation in explanations:
			exp = Explanation.objects.get_or_create(mooclet=self, text = explanation['text'])
			axis_explanations.append(exp[0])

		return axis_explanations


	def get_engine_name(self):
		if not self.output_engine_name:
			r = requests.get(MOOCLET_URL_BASE+'/mooclet/'+str(self.output_engine_id), headers={'Authorization': MOOCLET_API_TOKEN})
			r = r.json()
			mooclet_name = r['name']
			self.output_engine_name = mooclet_name
			self.save()
		else:
			mooclet_name = self.output_engine_name
		return mooclet_name

	def filter_explanations(self):
		explanations = self.get_explanation_set()
		filtered_explanations = self.filtering_method.filter(explanations)
		return filtered_explanations

	def get_current_versions(self):
		versions = requests.get(MOOCLET_URL_BASE+'/version?mooclet='+str(self.output_engine_id), headers={'Authorization': MOOCLET_API_TOKEN})
		versions = versions.json()
		return versions

	def add_versions(self, new_versions):
		print(len(new_versions))
		curr_versions = self.get_current_versions()
		curr_versions = [version['text'] for version in curr_versions]
		mooclet_engine_name = self.get_engine_name()
		print(curr_versions)
		added_versions = []
		for version in new_versions:
			print(version.text)
			if version.text not in curr_versions:
				version_name = mooclet_engine_name+str(self.output_engine_id)+"userexplanation"+str(datetime.datetime.now(datetime.timezone.utc))
				data = {'mooclet': self.output_engine_id, 
						'name': version_name,
						'text': version.text}
				new_version = requests.post(MOOCLET_URL_BASE+'/version', data=data, headers={'Authorization':MOOCLET_API_TOKEN} )
				print(new_version)
				added_versions.append(new_version.json())
		return added_versions



class Explanation(models.Model):
	mooclet = models.ForeignKey('Mooclet', on_delete=models.CASCADE)
	text = models.TextField(null=True, blank=True)
	add_to_version_set = models.BooleanField(default=False)
	guid = models.UUIDField(default=uuid.uuid4)
	added_to_version_set = models.BooleanField(null=True, blank=True)
	rating = models.PositiveIntegerField(null=True, blank=True, choices=(
		(0, '0'),
		(1, '1'),
		(2, '2'),
		(3,'3'),
		(4,'4'),
		(5,'5'),
		(6,'6'),
		(7,'7'),
		(8,'8'),
		(9,'9'),
		(10,'10')
		))



class FilteringMethod(models.Model):
	name = models.CharField(max_length=512)

	def __str__(self):
		return self.name

	def get_filter_function(self):
		try:
			return getattr(explanation_filters, self.name)
		except:
			print("filtering method matching specified name not found")
			# TODO look through custom user-provided functions
			return None

	def filter(self, explanation_list):
	# insert all version ids here?
		filter_function = self.get_filter_function()
		filtering_parameters = None
		
		filtered_list = filter_function(explanation_list)
		return filtered_list