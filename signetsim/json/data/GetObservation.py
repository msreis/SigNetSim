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

""" GetObservation.py

	This file...

"""

from signetsim.json import JsonRequest
from signetsim.views.HasWorkingProject import HasWorkingProject
from signetsim.models import Observation

class GetObservation(JsonRequest, HasWorkingProject):

	def __init__(self):
		JsonRequest.__init__(self)
		HasWorkingProject.__init__(self)


	def post(self, request, *args, **kwargs):

		HasWorkingProject.load(self, request, *args, **kwargs)

		if Observation.objects.filter(id=int(request.POST['id'])).exists():

			observation = Observation.objects.get(id=int(request.POST['id']))

			self.data.update({
				'species': observation.species,
				'time': observation.time,
				'value': observation.value,
				'value': observation.value,
				'stddev': observation.stddev,
				'steady_state': 1 if observation.steady_state else 0,
				'min_steady_state': 0 if observation.min_steady_state is None else observation.min_steady_state,
				'max_steady_state': 0 if observation.max_steady_state is None else observation.max_steady_state
			})

		return JsonRequest.post(self, request, *args, **kwargs)
