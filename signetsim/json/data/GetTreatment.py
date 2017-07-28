#!/usr/bin/env python
""" GetTreatment.py


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

from signetsim.json import JsonRequest
from signetsim.views.HasWorkingProject import HasWorkingProject
from signetsim.models import Treatment


class GetTreatment(JsonRequest, HasWorkingProject):

	def __init__(self):
		JsonRequest.__init__(self)
		HasWorkingProject.__init__(self)

	def post(self, request, *args, **kwargs):

		HasWorkingProject.load(self, request, *args, **kwargs)

		if Treatment.objects.filter(id=int(request.POST['id'])).exists():

			treatment = Treatment.objects.get(id=int(request.POST['id']))

			self.data.update({
				'species': treatment.species,
				'time': treatment.time,
				'value': treatment.value
			})

		return JsonRequest.post(self, request, *args, **kwargs)

