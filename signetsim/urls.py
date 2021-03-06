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

""" urls.py

	This file ...

"""

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout

from .json import FloatValidator, MathValidator, SbmlIdValidator, UnitIdValidator, ModelNameValidator
from .json import GetListOfObjectsFromSubmodels, UsernameValidator
from .json import GetSBOName, SetAccountActive, SetAccountStaff, GetUserQuotas
from .json import GetSpecies, GetParameter, GetCompartment, GetReactionKineticLaw, GetReaction, GetRule
from .json import GetEvent, GetSubmodel, GetSubstitution, GetSubmodels, GetListOfObjects
from .json import GetUnitDefinition
from .json import GetContinuationStatus, GetProject, SearchBiomodels, GetBiomodelsName
from .json import GetExperiment, GetCondition, GetTreatment, GetObservation
from .json import GetInstallStatus, AddDataset
from .json import GetEquilibriumCurve

from .views import AnalyseMainView, AnalyseSensitivityView, AnalyseBifurcationsView
from .views import DataOptimizationView, ModelOptimizationView
from .views import DataView, ExperimentView, ConditionView, DataArchive
from .views import HelpView, SuccessView, InstallView
from .views import ListOfModelsView, ListOfProjectsView, ProjectArchive, SimulationArchive
from .views import ListOfOptimizationsView, OptimizationResultView
from .views import ListOfSimulationsView, SedmlSimulationView
from .views import LoginView, ActivateAccountView, ProfileView
from .views import UsersView, ComputationsView, SettingsView
from .views import ModelCompartmentsView, ModelOverviewView, ModelAnnotationsView
from .views import ModelReactionsView, ModelRulesView, ModelSubmodelsView
from .views import ModelSpeciesView, ModelParametersView
from .views import ModelUnitsView, ModelEventsView, ModelMiscView
from .views import SignUpView, SignUpSuccessView, ValidateEmailView
from .views import TimeSeriesSimulationView, SteadyStateSimulationView, PhasePlaneSimulationView


if settings.RUN_INSTALL:
	urlpatterns = [
		url(r'^$', InstallView.as_view(), name='home'),
	]
	if settings.DEBUG:
		urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

else:
	urlpatterns = [
		url(r'^$', ListOfProjectsView.as_view(), name='home'),
	]
	if settings.DEBUG:
		urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from django import __version__
if int(__version__.split('.')[0]) < 2:
	from django.conf.urls import include
	urlpatterns += [
		url(r'^admin_db/', include(admin.site.urls)),
	]

else:
	from django.urls import path
	urlpatterns += [
		path('admin_db/', admin.site.urls),
	]

urlpatterns += [

	# Basic
	url(r'^help/$', HelpView.as_view(), name='help'),
	url(r'^install/$', InstallView.as_view(), name='install'),
	url(r'^success/$', SuccessView.as_view(), name='success'),
	url(r'^profile/(.*)/$', ProfileView.as_view(), name='profile'),
	url(r'^admin/$', UsersView.as_view(), name='admin_users'),
	url(r'^admin/computations/$', ComputationsView.as_view(), name='admin_computations'),
	url(r'^admin/settings/$', SettingsView.as_view(), name='admin_settings'),

	# Model import/export
	url(r'^project/([^/]+)/$', ListOfModelsView.as_view(), name='project'),
	url(r'^project_archive/([^/]+)/$', ProjectArchive.as_view(), name='project_archive'),
	url(r'^models/$', ListOfModelsView.as_view(), name='models'),

	# Authentication
	url(r'^accounts/register/$', SignUpView.as_view(), name='signup'),
	url(r'^accounts/register_success/$', SignUpSuccessView.as_view(), name='signup_success'),
	url(r'^accounts/login/$', LoginView.as_view(), name='login'),
	url(r'^accounts/logout/$',  logout, {'next_page': 'login'}, name='logout'),
	url(r'^accounts/validate_email/', ValidateEmailView.as_view(), name='validate_email'),
	url(r'^accounts/activate_account/', ActivateAccountView.as_view(), name='activate_account'),

	# Model editing
	url(r'^edit/model/([^/]+)/$', ModelOverviewView.as_view(), name='edit_model'),
	url(r'^edit/overview/$', ModelOverviewView.as_view(), name='edit_overview'),
	url(r'^edit/annotations/$', ModelAnnotationsView.as_view(), name='edit_annotations'),
	url(r'^edit/species/$', ModelSpeciesView.as_view(), name='edit_species'),
	url(r'^edit/parameters/$', ModelParametersView.as_view(), name='edit_parameters'),
	url(r'^edit/reactions/$', ModelReactionsView.as_view(), name='edit_reactions'),
	url(r'^edit/rules/$', ModelRulesView.as_view(), name='edit_rules'),
	url(r'^edit/events/$', ModelEventsView.as_view(), name='edit_events'),
	url(r'^edit/units/$', ModelUnitsView.as_view(), name='edit_units'),
	url(r'^edit/compartments/$', ModelCompartmentsView.as_view(), name='edit_compartments'),
	url(r'^edit/misc/$', ModelMiscView.as_view(), name='edit_misc'),
	url(r'^edit/submodels/$', ModelSubmodelsView.as_view(), name='edit_submodels'),

	# Simulation
	url(r'^simulate/timeseries/$', TimeSeriesSimulationView.as_view(), name='simulate_model'),
	url(r'^simulate/steady_states/$', SteadyStateSimulationView.as_view(), name='simulate_steady_states'),
	url(r'^simulate/phase_plane/$', PhasePlaneSimulationView.as_view(), name='simulate_phase_plane'),
	url(r'^simulate/stored/$', ListOfSimulationsView.as_view(), name='list_of_simulations'),
	url(r'^simulate/stored/([^/]+)/$', SedmlSimulationView.as_view(), name='sedml_simulation'),
	url(r'^simulate/archive/([^/]+)/$', SimulationArchive.as_view(), name='simulation_archive'),

	# Optimization
	url(r'^fit/model/$', ModelOptimizationView.as_view(), name='optimize_model'),
	url(r'^fit/data/$', DataOptimizationView.as_view(), name='optimize_data'),
	url(r'^fit/list/$', ListOfOptimizationsView.as_view(), name='list_of_optimizations'),
	url(r'^fit/([0-9]+)/$', OptimizationResultView.as_view(), name='view_optimization'),

	# Experimental data
	url(r'^data/$', DataView.as_view(), name='experimental_data'),
	url(r'^data_archive/([^/]+)/$', DataArchive.as_view(), name='data_archive'),
	url(r'^data/([^/]+)/$', ExperimentView.as_view(), name='experiment'),
	url(r'^data/([^/]+)/([^/]+)/$', ConditionView.as_view(), name='experiment_data'),

	# Analyses
	url(r'^analyse/$', AnalyseMainView.as_view(), name='analyse'),
	url(r'^analyse/sensitivity/$', AnalyseSensitivityView.as_view(), name='sensitivity'),
	url(r'^analyse/bifurcations/$', AnalyseBifurcationsView.as_view(), name='bifurcations'),

	# JSON requests
	url(r'^json/float_validator/$', FloatValidator.as_view(), name='float_validator'),
	url(r'^json/math_validator/$', MathValidator.as_view(), name='math_validator'),
	url(r'^json/sbml_id_validator/$', SbmlIdValidator.as_view(), name='sbml_id_validator'),
	url(r'^json/unit_id_validator/$', UnitIdValidator.as_view(), name='unit_id_validator'),
	url(r'^json/modelname_validator/$', ModelNameValidator.as_view(), name='modelname_validator'),
	url(r'^json/username_validator/$', UsernameValidator.as_view(), name='username_validator'),

	url(r'^json/get_submodels/$', GetSubmodels.as_view(), name='get_submodels'),
	url(r'^json/get_list_of_objects/$', GetListOfObjects.as_view(), name='get_list_of_objects'),
	url(r'^json/get_list_of_objects_from_submodels/$', GetListOfObjectsFromSubmodels.as_view(), name='get_list_of_objects_from_submodels'),

	url(r'^json/get_species/$', GetSpecies.as_view(), name='get_species'),
	url(r'^json/get_parameter/$', GetParameter.as_view(), name='get_parameter'),
	url(r'^json/get_compartment/$', GetCompartment.as_view(), name='get_compartment'),
	url(r'^json/get_reaction/$', GetReaction.as_view(), name='get_reaction'),
	url(r'^json/get_reaction_kinetic_law/$', GetReactionKineticLaw.as_view(), name='get_reaction_kinetic_law'),
	url(r'^json/get_rule/$', GetRule.as_view(), name='get_rule'),
	url(r'^json/get_event/$', GetEvent.as_view(), name='get_event'),
	url(r'^json/get_submodel/$', GetSubmodel.as_view(), name='get_submodel'),
	url(r'^json/get_substitution/$', GetSubstitution.as_view(), name='get_substitution'),
	url(r'^json/get_unit_definition/$', GetUnitDefinition.as_view(), name='get_unit_definition'),
	url(r'^json/get_sbo_name/$', GetSBOName.as_view(), name='get_sbo_name'),

	url(r'^json/set_account_active/$', SetAccountActive.as_view(), name='set_account_active'),
	url(r'^json/set_account_staff/$', SetAccountStaff.as_view(), name='set_account_staff'),
	url(r'^json/get_user_quotas/$', GetUserQuotas.as_view(), name='get_user_quotas'),
	url(r'^json/get_project/$', GetProject.as_view(), name='get_project'),

	url(r'^json/get_experiment/$', GetExperiment.as_view(), name='get_experiment'),
	url(r'^json/get_condition/$', GetCondition.as_view(), name='get_condition'),
	url(r'^json/get_treatment/$', GetTreatment.as_view(), name='get_treatment'),
	url(r'^json/get_observation/$', GetObservation.as_view(), name='get_observation'),

	url(r'^json/search_biomodels/$', SearchBiomodels.as_view(), name='search_biomodels'),
	url(r'^json/get_biomodels_name/$', GetBiomodelsName.as_view(), name='get_biomodels_name'),

	url(r'^json/get_continuation_status/$', GetContinuationStatus.as_view(), name='get_continuation_status'),
	url(r'^json/get_equilibrium_curve/$', GetEquilibriumCurve.as_view(), name='get_equilibrium_curve'),

	url(r'^json/get_install_status/$', GetInstallStatus.as_view(), name='get_install_status'),
	url(r'^json/add_dataset/$', AddDataset.as_view(), name='add_dataset'),

]
