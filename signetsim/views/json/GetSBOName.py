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


from signetsim.views.json.JsonView import JsonView
from libsignetsim.uris.URI import URI

class GetSBOName(JsonView):

	def __init__(self):
		JsonView.__init__(self)


	def post(self, request, *args, **kwargs):

		uri = URI()
		uri.setSBO(int(request.POST['sboterm']))
		name = uri.getName()

		self.data.update({
			'name': "" if name is None else name,
		})

		return JsonView.post(self, request, *args, **kwargs)
