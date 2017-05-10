#!/usr/bin/env python
""" GetSpecies.py


	This file...

	Copyright (C) 2016 Vincent Noel (vincent.noel@butantan.gov.br)

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as published
	by the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

from django.conf import settings
from os.path import join

from signetsim.views.json.JsonView import JsonView
from signetsim.views.HasWorkingModel import HasWorkingModel
from libsignetsim.model.SbmlDocument import SbmlDocument
from libsignetsim.model.Model import Model
from libsignetsim.model.sbml.KineticLaw import KineticLaw
from libsignetsim.model.ModelException import ModelException

class GetReaction(JsonView, HasWorkingModel):

	def __init__(self):
		JsonView.__init__(self)
		HasWorkingModel.__init__(self)


	def post(self, request, *args, **kwargs):
		self.load(request, *args, **kwargs)

		reaction = self.getModel().listOfReactions.getBySbmlId(str(request.POST['sbml_id']))

		list_of_parameters = []
		for parameter in self.getModel().listOfParameters.values():
			list_of_parameters.append(parameter)

		for parameter in reaction.listOfLocalParameters.values():
			list_of_parameters.append(parameter)

		self.data.update({
			'id': self.getModel().listOfReactions.values().index(reaction),
			'name': "" if reaction.getName() is None else reaction.getName(),
			'sbml_id': reaction.getSbmlId(),
			'list_of_reactants': [
				(
					self.getModel().listOfSpecies.index(reactant.getSpecies()),
					reactant.stoichiometry.getPrettyPrintMathFormula()
				)
				for reactant in reaction.listOfReactants.values()
			],
			'list_of_modifiers': [
				(
					self.getModel().listOfSpecies.index(modifier.getSpecies()),
					modifier.stoichiometry.getPrettyPrintMathFormula()
				)
				for modifier in reaction.listOfModifiers.values()
			],
			'list_of_products': [
				(
					self.getModel().listOfSpecies.index(product.getSpecies()),
					product.stoichiometry.getPrettyPrintMathFormula()
				)
				for product in reaction.listOfProducts.values()
			],
			'kinetic_law': reaction.kineticLaw.getPrettyPrintMathFormula(),
			'reaction_type': reaction.getReactionType(),
			'reaction_type_name': KineticLaw.reactionTypes[reaction.getReactionType()],
			'reversible': 1 if reaction.reversible else 0,
			'list_of_parameters': [
				list_of_parameters.index(t_param) for t_param in reaction.getReactionParameters()
			],
			'notes': "" if reaction.getNotes() is None else reaction.getNotes(),

		})
		return JsonView.post(self, request, *args, **kwargs)


	def load(self, request, *args, **kwargs):
		HasWorkingModel.load(self, request, *args, **kwargs)

