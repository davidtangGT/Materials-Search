import torch 
import os
from torch_geometric.data import Data
from pymatgen.io.cif import CifParser
import pandas as pd
import numpy as np
import torch_geometric.utils
import networkx as nx
from multiprocessing import Pool

class MOFDataset():
	"""docstring for MOFDataset"""
	def __init__(self, 
		train = True):
		super(MOFDataset, self).__init__()

		if train:
			self.data_dir = "/data/training/"
		else:
			self.data_dir = "/data/test/"

	def get_data(self):
		""" returns a list of Data objects """
		# print(type(directory)) 
		# files = glob.glob(self.data_dir+"*.cif")
		directory = os.getcwd() + self.data_dir

		labels = pd.read_csv(directory+"properties.csv")
		# counter = 1


		dataset = []

		counter = 0

		# print(feature_matrix)
		size = len(labels['filename'])
		steps = int(size / 20)
		
		arr = [x for x in range(0,size, steps)]

		with Pool(processes=20) as pool:
			resuls = [pool.apply_async(self.get_data_helper, args=(labels,arr[i],arr[i] + steps, size, )) for i in range(len(arr))]

			dataset = []

			for vals in resuls:
				vals = vals.get()
				for each in vals:
					dataset.append(each)
		# print(dataset)
		# for file in labels['filename']:
		# 	if(os.path.exists(directory+file+".cif")):
				# file  = labels['filename'][counter]
				# structure = self.cif_structure(directory+file+".cif")
				# distance_matrix = structure.distance_matrix

				# graph = nx.from_numpy_matrix(distance_matrix.astype(np.double))
				# num_nodes = distance_matrix.shape[0]
				# # print(num_nodes)
				# feature_matrix = self.get_feature_matrix(structure)
				
				# data = torch_geometric.utils.from_networkx(graph)
				# # data.x = torch.tensor(feature_matrix, dtype=torch.double)
				# data.x = torch.zeros(num_nodes,11)
				# data.y = labels['LCD'][counter]
				# if counter == 100:
				# 	break	
				# dataset.append(data)
				# counter +=1
		# 	else:
		# 		print("Not ok skipping: ", file)
		return dataset

	def cif_structure(self,file_name):
		parser = CifParser(file_name)
		structure = parser.get_structures()[0]
		return structure	

	def one_hot_encode(self, element):
		elements = ["H","N","C","O","Co","P","Zn","Ag","Cd","Cu","Fe"]

		one_hot_vector = np.zeros(len(elements))
		one_hot_vector[elements.index(element)] = 1
		return one_hot_vector

	def one_hot_test(self, val = 0, element="H"):
		one_hot = self.one_hot_encode(element)
		print(one_hot)

		true_val = np.zeros(11)
		true_val[val] = 1
		print(true_val)
		print(true_val == self.one_hot_encode(element))
	def get_feature_matrix(self, structure):
		arr = []
		for each in structure.sites:
			vec = self.one_hot_encode(str(each.specie))
			arr.append(vec)
		return np.array(arr)

	def get_data_helper(self, labels, counter_start, counter_end, size):
		dataset = []
		for x in range(counter_start,counter_end):
			if (x == size):
				break
			directory = os.getcwd() + self.data_dir

			file  = labels['filename'][x]
			structure = self.cif_structure(directory+file+".cif")
			distance_matrix = structure.distance_matrix

			graph = nx.from_numpy_matrix(distance_matrix.astype(np.double))
			num_nodes = distance_matrix.shape[0]
			# print(num_nodes)
			feature_matrix = self.get_feature_matrix(structure)
			
			data = torch_geometric.utils.from_networkx(graph)
			# data.x = torch.tensor(feature_matrix, dtype=torch.double)
			data.x = torch.zeros(num_nodes,11)
			data.y = labels['LCD'][x]
			dataset.append(data)
			# dataset.append(x)

		return dataset



