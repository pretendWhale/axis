from .models import *


def char_length_filter(explanation_list):
	filtered_explanations = [explanation for explanation in explanation_list if len(explanation["text"]) > 18]
	print("filtered explanations")
	print(filtered_explanations)
	return filtered_explanations
	#more than x chars and check some number of values in mooclet engine. if something has been flagged, always add 
	#char filtering set a var and then separately have functionality which adds stuff

