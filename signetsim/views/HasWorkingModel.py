#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014-2017 Vincent Noel (vincent.noel@butantan.gov.br)
#
# This file is part of libSigNetSim.
#
# libSigNetSim is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libSigNetSim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libSigNetSim.  If not, see <http://www.gnu.org/licenses/>.

""" HasWorkingModel.py

	This file ...

"""

from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied

from signetsim.models import SbmlModel
from libsignetsim import SbmlDocument
from signetsim.views.HasWorkingProject import HasWorkingProject
from signetsim.views.HasVariablesInSession import HasVariablesInSession
import os
from libsbml import Date
import datetime

class HasWorkingModel(HasWorkingProject, HasVariablesInSession):

	def __init__(self):

		HasWorkingProject.__init__(self)
		HasVariablesInSession.__init__(self)
		self.list_of_models = None

		self.model = None
		self.modelInstance = None
		self.model_id = None
		self.model_name = None
		self.model_filename = None
		self.model_list_of_submodels = []
		self.model_list_of_submodels_names = []
		self.model_list_of_submodels_types = []
		self.model_submodel = None

		self.__request = None

	def get_context_data(self, **kwargs):

		kwargs = HasWorkingProject.get_context_data(self, **kwargs)

		kwargs['sbml_models'] = self.list_of_models
		kwargs['model_id'] = self.model_id
		kwargs['model_name'] = self.model_name
		kwargs['model_has_submodels'] = (self.model is not None and self.model.parentDoc.isCompEnabled() and len(self.model.listOfSubmodels) > 0)
		kwargs['model_submodels'] = ["Model definition"] + [model.getName() for model in self.model.parentDoc.listOfModelDefinitions]
		kwargs['model_submodel'] = self.model_submodel
		return kwargs


	def load(self, request, recompute=True, *args, **kwargs):

		# print("> Model loading")
		HasWorkingProject.load(self, request, *args, **kwargs)
		HasVariablesInSession.load(self, request, *args, **kwargs)

		self.__request = request

		self.__loadModels(request)
		self.__loadModel(request, *args)

	def isChooseModel(self, request):

		if HasWorkingProject.isChooseProject(self, request):

			self.list_of_models = None
			self.__clearModelVariables()
			self.__clearPickledModel(request)
			return True

		elif request.POST['action'] == "choose_model":
			self.__setModel(request)
			return True

		elif request.POST['action'] == "choose_submodel":
			self.__setSubmodel(request)
			return True

		else:
			return False

	def getModelInstance(self):
		if self.modelInstance is None:
			if self.model.parentDoc.modelInstance is not None:
				self.modelInstance = self.model.parentDoc.modelInstance

			elif self.model is not None:
				self.modelInstance = self.model.parentDoc.getModelInstance()
				self.saveModelInSession(self.model, self.model_id)

		return self.modelInstance


	def getModel(self):

		if self.model_submodel is None or self.model_submodel == 0:
			return self.model

		elif self.model_submodel == -1:
			return self.getModelInstance()

		else:
			t_list_submodels = self.model.parentDoc.listOfModelDefinitions
			return t_list_submodels[self.model_submodel-1]

	def getSbmlModel(self):
		return SbmlModel.objects.get(id=self.model_id)

	def saveModel(self, request):
		if self.model is not None and self.isProjectOwner(request):

			self.savePickledModel(request)

			# We need to reset the instance
			self.modelInstance = None
			self.model.parentDoc.modelInstance = None

			if self.model_filename is not None:
				self.saveModelHistory(request)
				self.model.parentDoc.writeSbmlToFile(self.model_filename)



	def reloadModel(self):
		self.__loadModelVariables()

	def isModelLoaded(self):
		return self.model is not None

	def isFlattenModel(self):
		return self.model_submodel is not None and self.model_submodel == -1

	def isCompModelDefinition(self):
		return self.model_submodel is not None and self.model_submodel == 0

	def isCompInternalSubmodel(self):
		return self.model_submodel is not None and self.model_submodel > 0

	def saveModelName(self, request, name):

		if (self.model_submodel == 0 or self.model_submodel is None) and self.isProjectOwner(request):
			db_model = SbmlModel.objects.get(project=self.project_id, id=self.model_id)
			db_model.name = name
			db_model.save()


	def setModel(self, request, model_id):

		if model_id is not None:
			self.model_id = model_id
			self.model_submodel = None
			self.modelInstance = None

		self.__loadModelVariables()
		self.savePickledModel(request)
		self.deleteSubmodelFromSession()


	def __setModel(self, request):

		self.model_id = self.list_of_models[int(request.POST['model_id'])].id
		self.model_submodel = 0
		self.modelInstance = None
		self.__loadModelVariables()
		self.savePickledModel(request)
		self.saveSubmodelInSession(self.model_submodel)

	def __setSubmodel(self, request):

		t_id = str(request.POST['submodel_id'])

		if t_id != "":
			self.model_submodel = int(t_id)
			if (self.model_submodel) > len(self.model.parentDoc.listOfModelDefinitions):
				self.model_submodel = -1

		else:
			self.model_submodel = 0

		self.saveSubmodelInSession(self.model_submodel)

	def __loadModels(self, request):
		if self.isProjectLoaded():
			self.list_of_models = SbmlModel.objects.filter(project=self.project_id)

	def __loadModel(self, request, *args):
		""" Load the model for this view
			Here the model_id is the indice of the model in the list
			and model.id is the database model's id

		"""

		if self.hasModelInSession():
				self.model_id = self.getModelIdFromSession()
				self.__loadPickledModel(request)

		# Otherwise we just load the first one on the list, if there is a lists
		elif self.list_of_models is not None and len(self.list_of_models) > 0:
				self.model_id = self.list_of_models[0].id
				self.__loadModelVariables()
				self.savePickledModel(request)

		else:
			raise PermissionDenied

	def __loadModelVariables(self):

		if self.model_id is not None and SbmlModel.objects.filter(id=self.model_id).exists():

			t_model = SbmlModel.objects.get(id=self.model_id)

			if self.isProjectOwner(self.__request) or t_model.project.access == "PU":
				self.model_filename = os.path.join(settings.MEDIA_ROOT, str(t_model.sbml_file))

				t_doc = SbmlDocument()
				t_doc.readSbmlFromFile(self.model_filename)
				self.model = t_doc.model
				self.model_name = self.model.getName()

				self.model_list_of_submodels = self.model.listOfSubmodels
				self.model_list_of_submodels_names = []
				self.model_list_of_submodels_types = []
				for submodel in self.model.listOfSubmodels:
					if submodel.getModelRef() in self.model.parentDoc.listOfModelDefinitions.sbmlIds():
						self.model_list_of_submodels_names.append(self.model.parentDoc.listOfModelDefinitions.getBySbmlId(submodel.getModelRef()).getNameOrSbmlId())
						self.model_list_of_submodels_types.append(0)
					if submodel.getModelRef() in self.model.parentDoc.listOfExternalModelDefinitions.sbmlIds():
						self.model_list_of_submodels_names.append(self.model.parentDoc.listOfExternalModelDefinitions.getBySbmlId(submodel.getModelRef()).getNameOrSbmlId())
						self.model_list_of_submodels_types.append(1)
			else:
				raise PermissionDenied

		else:
			raise Http404("The model doesn't exist !")

	def __clearModelVariables(self):

		self.model_id = None
		self.model = None
		self.model_name = None
		self.model_submodel = None
		self.modelInstance = None

	def savePickledModel(self, request):

		if self.model_id is not None and self.isProjectOwner(request):
			self.saveModelInSession(self.model, self.model_id)
			self.saveSubmodelInSession(self.model_submodel)

	def __loadPickledModel(self, request):

		self.model = self.getModelFromSession()
		self.model_filename = self.getModelFilenameFromSession()

		if self.hasSubmodelInSession():
			self.model_submodel = self.getSubmodelIdFromSession()

		self.model_name = self.model.getName()

	def __clearPickledModel(self, request):

		self.deleteModelFromSession()
		self.deleteSubmodelFromSession()

	def getModelSubmodels(self, request, model_id):
		""" Returning the submodels of a model available within the project
		"""
		if self.isUserLoggedIn(request) and self.project is not None:
			t_models = [pm for pm in self.getProjectModels(request) if pm.id != self.model_id]
			t_filename = os.path.join(settings.MEDIA_ROOT, str(t_models[model_id].sbml_file))
			doc = SbmlDocument()
			doc.readSbmlFromFile(t_filename)
			if doc.useCompPackage:
				return [doc.model.getSbmlId()] + doc.listOfModelDefinitions.sbmlIds()+doc.listOfExternalModelDefinitions.sbmlIds()
			else:
				return [doc.model.getSbmlId()]

	def getModelSBMLSubmodels(self, request):
		""" Returning the submodels of a model available within the project
		"""
		if self.isUserLoggedIn(request) and self.project is not None and self.model_id is not None:
			t_filename = os.path.join(settings.MEDIA_ROOT, str(self.model_filename))
			doc = SbmlDocument()
			doc.readSbmlFromFile(t_filename)
			if doc.useCompPackage:
				return (doc.listOfModelDefinitions.getListOfModelDefinitions()
						+ doc.listOfExternalModelDefinitions.getListOfModelDefinitions())

	def saveModelHistory(self, request):
		if self.model.sbmlLevel >= 2:

			creator = self.model.modelHistory.createCreator()
			if str(request.user.email) not in self.model.modelHistory.getListOfCreatorsEmails():
				creator = self.model.modelHistory.createCreator()
				if request.user.first_name is not None:
					creator.setGivenName(request.user.first_name.encode('utf-8'))
				else:
					creator.setGivenName("")

				if request.user.last_name is not None:
					creator.setFamilyName(request.user.last_name.encode('utf-8'))
				else:
					creator.setFamilyName("")

				if request.user.email is not None:
					creator.setEmail(request.user.email.encode('utf-8'))
				else:
					creator.setEmail("")

				if request.user.organization is not None:
					creator.setOrganization(request.user.organization.encode('utf-8'))
				else:
					creator.setOrganization("")

			date = Date()
			now = datetime.datetime.now()
			date.setYear(now.year)
			date.setMonth(now.month)
			date.setDay(now.day)
			date.setHour(now.hour)
			date.setMinute(now.minute)
			date.setSecond(now.second)
			if self.model.modelHistory.getDateCreated() is None:
				self.model.modelHistory.setDateCreated(date)

			self.model.modelHistory.addModifiedDate(date)
