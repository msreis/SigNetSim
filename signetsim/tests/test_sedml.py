#!/usr/bin/env python
""" test_sedml.py


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

from django.test import TestCase, Client
from django.conf import settings

from signetsim.models import User, Project, SbmlModel, Experiment, SEDMLSimulation
from libsignetsim.combine.CombineArchive import CombineArchive

from os.path import dirname, join
from shutil import rmtree


class TestSedml(TestCase):

	fixtures = ["user_with_project.json"]

	def testImportSedml(self):

		settings.MEDIA_ROOT = "/tmp/"


		user = User.objects.filter(username='test_user')[0]
		self.assertEqual(len(Project.objects.filter(user=user)), 1)
		project = Project.objects.filter(user=user)[0]

		# This test can only run once with success, because the second time the comp model dependencies will
		# actually be in the folder. So cleaning the project folder now
		rmtree(join(join(settings.MEDIA_ROOT, str(project.folder))), "models")

		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 0)

		c = Client()
		self.assertTrue(c.login(username='test_user', password='password'))

		response_choose_project = c.get('/project/%s/' % project.folder)
		self.assertRedirects(response_choose_project, '/models/', status_code=302, target_status_code=200)

		self.assertEqual(len(SEDMLSimulation.objects.filter(project=project)), 0)

		files_folder = join(dirname(__file__), "files")
		sedml_filename = join(files_folder, "specificationL1V2.sedml")

		response_import_sedml = c.post('/simulate/stored/', {
			'action': 'load_simulation',
			'docfile': open(sedml_filename, 'r')
		})

		self.assertEqual(response_import_sedml.status_code, 200)
		self.assertEqual(len(SEDMLSimulation.objects.filter(project=project)), 1)

		response_simulate_sedml = c.get('/simulate/stored/0/')

		self.assertEqual(response_simulate_sedml.status_code, 200)
		self.assertEqual(len(response_simulate_sedml.context['plots_2d']), 3)

		response_delete_sedml = c.post('/simulate/stored/', {
			'action': 'delete_simulation',
			'id': 0
		})
		self.assertEqual(response_delete_sedml.status_code, 200)
		self.assertEqual(len(SEDMLSimulation.objects.filter(project=project)), 0)