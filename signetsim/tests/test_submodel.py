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

""" test_submodel.py

	This file...

"""

from django.test import TestCase, Client
from django.conf import settings

from signetsim.models import User, Project, SbmlModel, ModelsDependency
from os import mkdir
from os.path import dirname, join, isdir
from json import loads
from shutil import rmtree


class TestSubmodel(TestCase):

	fixtures = ["user_with_project.json"]

	def testCreateModel(self):

		user = User.objects.filter(username='test_user')[0]
		self.assertEqual(len(Project.objects.filter(user=user)), 1)
		project = Project.objects.filter(user=user)[0]

		if isdir(join(settings.MEDIA_ROOT, project.folder)):
			rmtree(join(settings.MEDIA_ROOT, project.folder))
			mkdir(join(settings.MEDIA_ROOT, project.folder))

		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 0)

		c = Client()
		self.assertTrue(c.login(username='test_user', password='password'))

		response_choose_project = c.get('/project/%s/' % project.folder)
		self.assertRedirects(response_choose_project, '/models/', status_code=302, target_status_code=200)

		response_choose_project = c.post('/models/', {
			'action': 'choose_project',
			'project_id': 0
		})
		self.assertEqual(response_choose_project.status_code, 200)

		files_folder = join(dirname(__file__), "files")
		comp_files_folder = join(files_folder, "comp_model")

		model_filename = join(comp_files_folder, "modelcEvRcX.xml")
		response_load_submodel_1 = c.post('/models/', {
			'action': 'load_model',
			'docfile': open(model_filename, 'rb')
		})

		self.assertEqual(response_load_submodel_1.status_code, 200)
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 1)

		model_filename = join(comp_files_folder, "modelEHfev9.xml")
		response_load_submodel_2 = c.post('/models/', {
			'action': 'load_model',
			'docfile': open(model_filename, 'rb')
		})

		self.assertEqual(response_load_submodel_2.status_code, 200)
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 2)


		model_filename = join(comp_files_folder, "modelI1vrys.xml")
		response_load_submodel_3 = c.post('/models/', {
			'action': 'load_model',
			'docfile': open(model_filename, 'rb')
		})

		self.assertEqual(response_load_submodel_3.status_code, 200)
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 3)
		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 0)

		model_filename = join(comp_files_folder, "modelz9xdww.xml")

		response_load_model = c.post('/models/', {
			'action': 'load_model',
			'docfile': open(model_filename, 'rb')
		})

		self.assertEqual(response_load_model.status_code, 200)
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 4)
		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 4)

		response_choose_model = c.post('/edit/submodels/', {
			'action': 'choose_model',
			'model_id': 3
		})

		self.assertEqual(response_choose_model.status_code, 200)
		self.assertEqual(
			[submodel for submodel in response_choose_model.context['model_submodels']],
			['Model definition', 'Test submodel']
		)

		self.assertEqual(
			[submodel.getNameOrSbmlId() for submodel in response_choose_model.context['list_of_submodels']],
			['SOS module', 'Ras module', 'MAPK module', 'Test submodel']
		)

		self.assertEqual(
			response_choose_model.context['list_of_submodel_types'],
			[1, 1, 1, 0]
		)

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_choose_model.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['sos_mod'], 'cell'),
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'sos', ['sos_mod'], 'sos'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'erkpp')
			]

		)

		response_delete_submodel = c.post('/edit/submodels/', {
			'action': 'delete',
			'submodel_id': 0
		})


		self.assertEqual(response_delete_submodel.status_code, 200)
		self.assertEqual(
			response_delete_submodel.context['getErrors'],
			['Submodel SOS module is used. Please remove the substitutions first']
		)

		self.assertEqual(len(response_delete_submodel.context['list_of_submodel_types']), 4)
		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 4)

		list_of_substitutions = response_delete_submodel.context['list_of_substitutions']
		substitution_id = [
			list_of_substitutions.index(substitution)
			for substitution in list_of_substitutions
			if substitution[1].getSbmlId() == 'compartment_0' and substitution[2] == ['sos_mod']
		][0]

		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': substitution_id
		})

		self.assertEqual(response_delete_substitution.status_code, 200)

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_delete_substitution.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'sos', ['sos_mod'], 'sos'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'erkpp')
			]
		)
		list_of_substitutions = response_delete_substitution.context['list_of_substitutions']
		substitution_id = [
			list_of_substitutions.index(substitution)
			for substitution in list_of_substitutions
			if substitution[1].getSbmlId() == 'erkpp' and substitution[2] == ['sos_mod']
		][0]

		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': substitution_id
		})
		self.assertEqual(response_delete_substitution.status_code, 200)
		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_delete_substitution.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'sos', ['sos_mod'], 'sos'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp')
			]
		)

		list_of_substitutions = response_delete_substitution.context['list_of_substitutions']
		substitution_id = [
			list_of_substitutions.index(substitution)
			for substitution in list_of_substitutions
			if substitution[1].getSbmlId() == 'sos' and substitution[2] == ['sos_mod']
		][0]
		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': substitution_id
		})
		self.assertEqual(response_delete_substitution.status_code, 200)

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_delete_substitution.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp')
			]
		)

		response_delete_submodel = c.post('/edit/submodels/', {
			'action': 'delete',
			'submodel_id': 0
		})

		self.assertEqual(response_delete_submodel.status_code, 200)
		self.assertEqual(
			response_delete_submodel.context['getErrors'],
			[]
		)
		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 3)
		self.assertEqual(len(response_delete_submodel.context['list_of_submodel_types']), 3)

		response_add_submodel = c.post('/edit/submodels/', {
			'action': 'save',
			'submodel_id': "",
			'submodel_name': "SOS module",
			'submodel_sbml_id': "sos_mod",
			'submodel_type': 1,
			'submodel_source': 0,
			'submodel_submodel': 0,
			'extent_conversion_factor': "",
			'time_conversion_factor': "",
		})

		self.assertEqual(response_add_submodel.status_code, 200)
		self.assertEqual(len(response_add_submodel.context['list_of_submodel_types']), 4)
		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 4)

		self.assertEqual(
			[submodel.getNameOrSbmlId() for submodel in response_add_submodel.context['list_of_submodels']],
			['Ras module', 'MAPK module', 'Test submodel', 'SOS module']
		)

		self.assertEqual(
			response_add_submodel.context['list_of_submodel_types'],
			[1, 1, 0, 1]
		)

		response_get_submodel = c.post('/json/get_submodel/', {
			'id': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module'),
		})

		self.assertEqual(response_get_submodel.status_code, 200)
		json_response = loads(response_get_submodel.content.decode('utf-8'))

		self.assertEqual(json_response['id'], [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module')
		)
		self.assertEqual(json_response['name'], "SOS module")
		self.assertEqual(json_response['sbml_id'], "sos_mod")
		self.assertEqual(json_response['type'], 1)
		self.assertEqual(json_response['source'], 0)
		self.assertEqual(json_response['source_name'], "SOS")
		self.assertEqual(json_response['extent_conversion_factor'], "")
		self.assertEqual(json_response['extent_conversion_factor_name'], "")
		self.assertEqual(json_response['time_conversion_factor'], "")
		self.assertEqual(json_response['time_conversion_factor_name'], "")

		response_get_list_objects_from_submodel = c.post('/json/get_list_of_objects_from_submodels/', {
			'model_id': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module'),
		})

		self.assertEqual(response_get_list_objects_from_submodel.status_code, 200)
		json_response = loads(response_get_list_objects_from_submodel.content.decode('utf-8'))

		self.assertEqual(json_response[u'list'], [
			u'cell (Compartment)',
			u'SOS activation by FGF2 (Parameter)',
			u'SOS inactivation by Mapk catalytic constant (Parameter)',
			u'SOS inactivation by Mapk michaelis constant (Parameter)',
			u'SOS (Species)',
			u'SOS_inactive (Species)',
			u'FGF2 (Species)',
			u'ERK-PP (Species)',
			u'SOS activation (Reaction)',
			u'SOS inactivation by Erk (Reaction)'
		])
		list_of_objects = json_response[u'list']
		response_add_substitution = c.post('/edit/submodels/', {

			'action': 'save_substitution',
			'substitution_id': "",
			'substitution_type': 0,
			'substitution_model_object': response_add_submodel.context['list_of_objects'].index('Compartment 0 (Compartment)'),
			'substitution_submodel': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module'),
			'substitution_submodel_object': list_of_objects.index(u'cell (Compartment)')
		})

		self.assertEqual(response_add_substitution.status_code, 200)
		self.assertEqual(response_add_substitution.context['form_subs'].getErrors(), [])

		response_add_substitution = c.post('/edit/submodels/', {

			'action': 'save_substitution',
			'substitution_id': "",
			'substitution_type': 0,
			'substitution_model_object': response_add_submodel.context['list_of_objects'].index('ERK-PP (Species)'),
			'substitution_submodel': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module'),
			'substitution_submodel_object': list_of_objects.index(u'FGF2 (Species)')
		})

		self.assertEqual(response_add_substitution.status_code, 200)
		self.assertEqual(response_add_substitution.context['form_subs'].getErrors(), [])

		response_add_substitution = c.post('/edit/submodels/', {

			'action': 'save_substitution',
			'substitution_id': "",
			'substitution_type': 0,
			'substitution_model_object': response_add_submodel.context['list_of_objects'].index('SOS (Species)'),
			'substitution_submodel': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module'),
			'substitution_submodel_object': list_of_objects.index(u'SOS (Species)')
		})

		self.assertEqual(response_add_substitution.status_code, 200)
		self.assertEqual(response_add_substitution.context['form_subs'].getErrors(), [])

		response_get_submodel = c.get('/edit/submodels/')
		self.assertEqual(response_get_submodel.status_code, 200)
		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_get_submodel.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'compartment_0', ['sos_mod'], 'cell'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'sos', ['sos_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'fgf2')
			]
		)
		list_of_substitutions = response_get_submodel.context['list_of_substitutions']
		substitution_id = [
			list_of_substitutions.index(substitution)
			for substitution in list_of_substitutions
			if substitution[1].getSbmlId() == 'erkpp' and substitution[2] == ['sos_mod']
		][0]
		response_modify_substitution = c.post('/edit/submodels/', {

			'action': 'save_substitution',
			'substitution_id': substitution_id,
			'substitution_type': 0,
			'substitution_model_object': response_add_submodel.context['list_of_objects'].index('ERK-PP (Species)'),
			'substitution_submodel': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('SOS module'),
			'substitution_submodel_object': list_of_objects.index(u'ERK-PP (Species)')
		})

		self.assertEqual(response_modify_substitution.status_code, 200)
		self.assertEqual(response_modify_substitution.context['form_subs'].getErrors(), [])
		self.assertEqual(response_modify_substitution.context['getErrors'], [])

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_modify_substitution.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'compartment_0', ['sos_mod'], 'cell'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'sos', ['sos_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'erkpp')
			]
		)

		response_get_substitution = c.post('/json/get_substitution/', {
			'id': substitution_id
		})

		self.assertEqual(response_get_substitution.status_code, 200)
		json_response = loads(response_get_substitution.content.decode('utf-8'))

		self.assertEqual(json_response['id'], substitution_id)
		self.assertEqual(json_response['object_name'], "ERK-PP")
		self.assertEqual(json_response['submodel_id'], [
				submodel.getNameOrSbmlId()
				for submodel in response_modify_substitution.context['list_of_submodels']
			].index('SOS module')
		)
		self.assertEqual(json_response['submodel_name'], "SOS module")
		self.assertEqual(json_response['submodel_object_id'], list_of_objects.index(u'ERK-PP (Species)'))
		self.assertEqual(json_response['submodel_object_name'], "ERK-PP")

		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 4)

		response_add_submodel = c.post('/edit/submodels/', {
			'action': 'save',
			'submodel_id': "",
			'submodel_name': "Internal model",
			'submodel_sbml_id': "internal",
			'submodel_type': 0,
			'extent_conversion_factor': "",
			'time_conversion_factor': ""
		})


		self.assertEqual(response_add_submodel.status_code, 200)
		self.assertEqual(
			[submodel.getNameOrSbmlId() for submodel in response_add_submodel.context['list_of_submodels']],
			['Ras module', 'MAPK module', 'Test submodel', 'SOS module', 'Internal model']
		)

		self.assertEqual(
			response_add_submodel.context['list_of_submodel_types'],
			[1, 1, 0, 1, 0]
		)

		self.assertEqual(len(ModelsDependency.objects.filter(project=project)), 5)

		response_add_submodel = c.post('/edit/submodels/', {
			'action': 'save',
			'submodel_id': 4,
			'submodel_name': "Internal model, modified",
			'submodel_sbml_id': "internal_modified",
			'submodel_type': 0,
			'extent_conversion_factor': "",
			'time_conversion_factor': ""
		})

		self.assertEqual(response_add_submodel.status_code, 200)
		self.assertEqual(
			[submodel.getNameOrSbmlId() for submodel in response_add_submodel.context['list_of_submodels']],
			['Ras module', 'MAPK module', 'Test submodel', 'SOS module', 'Internal model, modified']
		)

		self.assertEqual(
			response_add_submodel.context['list_of_submodel_types'],
			[1, 1, 0, 1, 0]
		)

		response_select_internal = c.post('/edit/compartments/', {
			'action': 'choose_submodel',
			'submodel_id': 2
		})
		self.assertEqual(response_select_internal.status_code, 200)

		response_save_compartment = c.post('/edit/compartments/', {
			'action': 'save',
			'compartment_id': "",
			'compartment_name': "Cell",
			'compartment_sbml_id': "cell",
			'compartment_size': 1,
			'compartment_unit': "",
			'compartment_constant': "on",
			'compartment_sboterm': "",
		})

		self.assertEqual(response_save_compartment.status_code, 200)
		self.assertEqual(response_save_compartment.context['getErrors'], [])

		response_select_internal = c.post('/edit/submodels/', {
			'action': 'choose_submodel',
			'submodel_id': 0
		})
		self.assertEqual(response_select_internal.status_code, 200)

		response_add_substitution = c.post('/edit/submodels/', {

			'action': 'save_substitution',
			'substitution_id': "",
			'substitution_type': 0,
			'substitution_model_object': response_add_submodel.context['list_of_objects'].index("Compartment 0 (Compartment)"),
			'substitution_submodel': [
				submodel.getNameOrSbmlId()
				for submodel in response_add_submodel.context['list_of_submodels']
			].index('Internal model, modified'),
			'substitution_submodel_object': 0
		})


		self.assertEqual(response_add_substitution.status_code, 200)
		self.assertEqual(response_add_substitution.context['form_subs'].getErrors(), [])

		response_get_submodel = c.get('/edit/submodels/')
		self.assertEqual(response_get_submodel.status_code, 200)
		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_get_submodel.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'compartment_0', ['sos_mod'], 'cell'),
				(0, 'compartment_0', ['internal_modified'], 'cell'),
				(0, 'sos', ['ras_mod'], 'sos'),
				(0, 'sos', ['sos_mod'], 'sos'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'erkpp')
			]
		)

		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': 4
		})
		self.assertEqual(response_delete_substitution.status_code, 200)
		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': 4
		})
		self.assertEqual(response_delete_substitution.status_code, 200)

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_delete_substitution.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'compartment_0', ['sos_mod'], 'cell'),
				(0, 'compartment_0', ['internal_modified'], 'cell'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'erkpp')
			]
		)
		response_add_replacedby = c.post('/edit/submodels/', {

			'action': 'save_substitution',
			'substitution_id': "",
			'substitution_type': 1,
			'substitution_model_object': response_delete_substitution.context['list_of_objects'].index("SOS (Species)"),
			'substitution_submodel': 3,
			'substitution_submodel_object': 4
		})
		self.assertEqual(response_add_replacedby.status_code, 200)
		self.assertEqual(response_add_replacedby.context['getErrors'], [])
		self.assertEqual(response_add_replacedby.context['form_subs'].getErrors(), [])

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_add_replacedby.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'compartment_0', ['sos_mod'], 'cell'),
				(0, 'compartment_0', ['internal_modified'], 'cell'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
				(0, 'erkpp', ['sos_mod'], 'erkpp'),
				(1, 'sos', ['sos_mod'], 'sos'),
			]
		)



		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': 8
		})
		self.assertEqual(response_delete_substitution.status_code, 200)

		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': 7
		})
		self.assertEqual(response_delete_substitution.status_code, 200)

		response_delete_substitution = c.post('/edit/submodels/', {
			'action': 'delete_substitution',
			'substitution_id': 2
		})
		self.assertEqual(response_delete_substitution.status_code, 200)

		self.assertEqual(
			[
				(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
				for sub_type, object_1, submodel, object_2
				in response_delete_substitution.context['list_of_substitutions']
			],
			[
				(0, 'compartment_0', ['ras_mod'], 'cell'),
				(0, 'compartment_0', ['mapk_mod'], 'cell'),
				(0, 'compartment_0', ['internal_modified'], 'cell'),
				(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
				(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
				(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
			]
		)


		response_models = c.get('/models/')
		self.assertEqual(response_models.status_code, 200)

		response_delete_model = c.post('/models/', {
			'action': 'delete_model',
			'id': [id for id, _, _ in response_models.context['sbml_models']][
				[name for _, name, _ in response_models.context['sbml_models']].index('SOS')
			]
		})

		self.assertEqual(response_delete_model.status_code, 200)
		self.assertEqual(
			response_delete_model.context['getErrors'],
			[u'This model is used as a submodel by SOS-Ras-MAPK and cannot be removed.']
		)
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 4)

		response_delete_submodel = c.post('/edit/submodels/', {
			'action': 'delete',
			'submodel_id': 3
		})

		self.assertEqual(response_delete_submodel.status_code, 200)
		self.assertEqual(
			response_delete_submodel.context['getErrors'],
			[]
		)

		self.assertEqual(
			[submodel.getNameOrSbmlId() for submodel in response_delete_submodel.context['list_of_submodels']],
			['Ras module', 'MAPK module', 'Test submodel', 'Internal model, modified']
		)


		response_delete_model = c.post('/models/', {
			'action': 'delete_model',
			'id': [id for id, _, _ in response_models.context['sbml_models']][
				[name for _, name, _ in response_models.context['sbml_models']].index('SOS')
			]
		})

		self.assertEqual(response_delete_model.status_code, 200)
		self.assertEqual(response_delete_model.context['getErrors'], [])
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 3)

		# response_get_replacedby = c.post('/json/get_substitution/', {
		# 	'id': 0
		# })
		#
		# self.assertEqual(response_get_replacedby.status_code, 200)
		# json_response = loads(response_get_replacedby.content)
		#
		# self.assertEqual(json_response[u'object_name'], u'SOS')
		# self.assertEqual(json_response[u'object_id'], 0)
		# self.assertEqual(json_response[u'submodel_name'], u'SOS module')
		# self.assertEqual(json_response[u'submodel_id'], 2)
		# self.assertEqual(json_response[u'submodel_object_name'], u'SOS')
		# self.assertEqual(json_response[u'submodel_object_id'], 4)
		#
		# response_delete_replacedby = c.post('/edit/submodels/', {
		# 	'action': 'delete_substitution',
		# 	'substitution_id': 0
		# })
		#
		# self.assertEqual(response_delete_replacedby.status_code, 200)
		# self.assertEqual(
		# 	[
		# 		(sub_type, object_1.getSbmlId(), submodel, object_2.getSbmlId())
		# 		for sub_type, object_1, submodel, object_2
		# 		in response_delete_replacedby.context['list_of_substitutions']
		# 	],
		# 	[
		# 		(0, 'compartment_0', ['ras_mod'], 'cell'),
		# 		(0, 'compartment_0', ['mapk_mod'], 'cell'),
		# 		(0, 'compartment_0', ['sos_mod'], 'cell'),
		# 		(0, 'compartment_0', ['internal_modified'], 'cell'),
		# 		(0, 'rasgtp', ['ras_mod'], 'ras_gtp'),
		# 		(0, 'rasgtp', ['mapk_mod'], 'ras_gtp'),
		# 		(0, 'erkpp', ['mapk_mod'], 'mapk_pp'),
		# 		(0, 'erkpp', ['sos_mod'], 'erkpp')
		# 	]
		# )