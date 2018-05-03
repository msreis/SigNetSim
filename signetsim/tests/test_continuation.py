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

""" test_simulation.py

	This file...

"""

from django.test import TestCase, Client
from django import __version__
from signetsim.models import User, Project, SbmlModel, ContinuationComputation

from os.path import dirname, join
from json import loads
from time import sleep


class TestContinuation(TestCase):

	fixtures = ["user_with_project.json"]

	def testBistable(self):

		user = User.objects.filter(username='test_user')[0]
		self.assertEqual(len(Project.objects.filter(user=user)), 1)
		project = Project.objects.filter(user=user)[0]

		c = Client()
		self.assertTrue(c.login(username='test_user', password='password'))

		response_choose_project = c.get('/project/%s/' % project.folder)
		self.assertRedirects(response_choose_project, '/models/', status_code=302, target_status_code=200)

		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 0)

		files_folder = join(dirname(__file__), "files")
		model_filename = join(files_folder, "tyson2.xml")

		response_load_model = c.post('/models/', {
			'action': 'load_model',
			'docfile': open(model_filename, 'rb')
		})

		self.assertEqual(response_load_model.status_code, 200)
		self.assertEqual(len(SbmlModel.objects.filter(project=project)), 1)
		self.assertEqual(len(ContinuationComputation.objects.filter(project=project)), 0)

		response_compute_curve = c.post('/analyse/bifurcations/', {
			'action': 'compute_curve',
			'parameter': 3,
			'variable': 1,
			'from_value': 0,
			'to_value': 5000,
			'max_steps': 500,
			'ds': 5
		})

		self.assertEqual(response_compute_curve.status_code, 200)
		self.assertEqual(len(response_compute_curve.context['list_of_computations']), 1)
		self.assertEqual(len(ContinuationComputation.objects.filter(project=project)), 1)

		response_get_status = c.post('/json/get_continuation_status/', {'continuation_id': 0})

		self.assertEqual(response_get_status.status_code, 200)
		json_response = loads(response_get_status.content.decode('utf-8'))

		self.assertEqual(json_response['status'], 'BU')

		sleep(20)

		response_get_status = c.post('/json/get_continuation_status/', {'continuation_id': 0})

		self.assertEqual(response_get_status.status_code, 200)
		json_response = loads(response_get_status.content.decode('utf-8'))

		# we cannot really test, because the test database doesn't like threads.
		# Maybe we could find a trick for that, but for now i will give up
		# Actually, it works with the django2 version, maybe earlier
		if int(__version__.split('.')[0]) >= 2:
			self.assertEquals(json_response['status'], 'EN')

		response_get_curve = c.post('/json/get_equilibrium_curve/', {'id': 0})

		self.assertEqual(response_get_curve.status_code, 200)
		json_response = loads(response_get_curve.content.decode('utf-8'))

		results_x = [86.21626556089748, 86.93136694242513, 86.94136664253448, 86.95636588693405, 86.97886476364202, 87.01261309970393, 87.0632356457539, 87.13916954386701, 87.25307052670914, 87.42392219789149, 87.68019988610622, 87.93647750061857, 88.19275478462879, 88.44903150259645, 88.70530739977113, 88.96158217168826, 89.21785542721256, 89.47412663532754, 89.73039504055562, 89.98665951951536, 90.24291832449998, 90.49916860217002, 90.75540544872487, 91.0116199967866, 91.2677956036832, 91.52390157555016, 91.77989210265201, 92.03575224504068, 92.2916069887797, 92.54761930179735, 92.8037697036536, 93.0599857623939, 93.31623220069396, 93.57249438783006, 93.8287654431462, 94.08504180486419, 94.34132150954666, 94.59760341765312, 94.85388683671873, 95.11017132823656, 95.36645660412772, 95.62274246886504, 95.87902878586507, 96.26345891675822, 96.64788962815832, 97.03232075827674, 97.41675220826578, 97.99339984566075, 98.57004789353306, 99.14669623978276, 99.72334481626827, 100.58831801810842, 101.45329152519751, 102.31826526008953, 103.183239175166, 104.04821323655267, 105.34567455379258, 106.64313608729213, 107.94059779260975, 109.23805964068934, 111.18425263761446, 113.13044585614014, 115.07663925538233, 117.02283280770853, 119.94212338125946, 122.8614142000694, 125.78070522116666, 128.69999641449544, 131.61928775634857, 135.99822500984263, 140.37716250627656, 144.75610020357604, 149.13503807138557, 153.51397608534575, 157.89291422561152, 164.46132164049422, 171.02972926072346, 177.59813704915535, 184.16654497886415, 190.73495302827374, 197.3033611798905, 203.87176941938367, 210.44017773490575, 217.00858611658194, 223.57699455612052, 233.4296073100613, 243.2822201600283, 253.1348330893996, 262.9874460858843, 272.84005913950733, 282.6926722420998, 292.54528538691727, 302.3978985683488, 312.2505117816942, 322.1031250229907, 336.8820449306969, 351.66096488488546, 366.4398848775416, 381.2188049027232, 395.9977249556008, 410.77664503221536, 425.5555651292957, 440.3344852441193, 455.11340537440503, 469.89232551822937, 492.06070575612307, 514.2290860165135, 536.3974662955129, 558.5658465902391, 580.7342268983501, 602.9026072179273, 625.0709875473859, 647.2393678854078, 669.4077482308886, 691.5761285828979, 724.8286991215903, 758.0812696711193, 791.3338402296085, 824.5864107956661, 857.8389813681619, 891.0915519461701, 924.3441225289263, 957.5966931157949, 990.8492637062436, 1024.1018342998236, 1073.980690195309, 1123.8595460959802, 1173.738402000934, 1223.6172579094982, 1273.4961138211258, 1323.3749697353683, 1373.2538256518537, 1423.1326815702719, 1473.0115374903617, 1522.8903934119012, 1572.7692493347008, 1647.58753322093, 1722.405817109175, 1797.2241009990273, 1872.0423848901576, 1946.860668782274, 2021.6789526751081, 2096.4972365683993, 2171.31552046188, 2246.1338043552564, 2320.952088248184, 2395.7703721402336, 2470.588656030846, 2545.4069399192604, 2620.2252238044252, 2695.043507684898, 2769.8617915587974, 2844.6800754239853, 2919.4983592787917, 2994.3166431234426, 3069.13492696142, 3143.953210798908, 3218.7714946418932, 3293.589778493592, 3368.408062354334, 3443.2263462228975, 3518.044630097655, 3592.862913977101, 3667.681197859983, 3742.49948174527, 3817.3177656320604, 3892.1360495194563, 3966.9543334063414, 4041.7726172908388, 4116.590901168191, 4154.000043098162, 4172.704614055171, 4191.409184990714, 4196.085327703541, 4197.254363366462, 4197.838881181483, 4198.423398947319, 4198.715657915437]
		results_y_min = [0.015, 0.01779248945502492, 0.01781466715442101, 0.01784814446747936, 0.017897610027032624, 0.017970902620809023, 0.018079271045145166, 0.018238208415341954, 0.01847126939258336, 0.01881051666378573, 0.019305356919514405, 0.019794467664002596, 0.020285748283462638, 0.02078748660799787, 0.02130700451266831, 0.02185242686262597, 0.022433682717773365, 0.023062677206187803, 0.02375511389830091, 0.02453260758714392, 0.025425674049219825, 0.02647963781620497, 0.02776856978970085, 0.029410680319980738, 0.031610024337097704, 0.034726897799411995, 0.03932877014518192, 0.04601587394134079, 0.05460644763550759, 0.06381677453817167, 0.07247671841679726, 0.08011427017070318, 0.0867397606728453, 0.0925263319586254, 0.0975933691845283, 0.10205930864509616, 0.1061053256316217, 0.10972482938513746, 0.11301831932468002, 0.11604845017702685, 0.11879049581093279, 0.12139823905473571, 0.12378244752249859, 0.12709474349049438, 0.130069504557534, 0.1328199904208261, 0.13537348222690082, 0.13879542245006585, 0.14192438994822912, 0.1447268702157785, 0.14730853344717082, 0.1507760615453077, 0.15383733398545604, 0.15662042049667121, 0.1591028854040179, 0.1613893673874808, 0.1644281832486283, 0.16712444656553793, 0.16949268085111988, 0.1716523111017552, 0.17444447883598924, 0.1768938853138476, 0.1789720368151608, 0.1808269116402629, 0.1831954477245585, 0.18512199516638175, 0.18676795249280798, 0.18812306196208597, 0.1892753972195709, 0.1906418274919116, 0.19167933810647023, 0.19245560775782786, 0.1930321734576467, 0.19341461746110294, 0.19365924509497814, 0.1938143752188859, 0.1937797004176894, 0.19357370566612236, 0.19324493971482118, 0.1928089620150613, 0.1922915559879814, 0.19172804217675363, 0.1911305185579582, 0.19048571362559427, 0.18978214312974617, 0.18873144545371104, 0.1876629199978579, 0.18656124308248598, 0.18545076312894732, 0.18433148486020326, 0.18320441652755481, 0.18211719501875914, 0.18103519102990565, 0.17993037943853663, 0.17888328607369688, 0.17733747750093387, 0.17579400386362903, 0.17433156576257358, 0.17290352076659338, 0.17149960790637864, 0.17013239876242758, 0.16882052805184136, 0.16755196934041847, 0.166302199537738, 0.1650857871542732, 0.16335709190488507, 0.1616733263236863, 0.16005400122141833, 0.158535032690282, 0.15704698674293444, 0.15561213573594232, 0.15424106780403124, 0.15290774495805673, 0.1516199169576196, 0.15040371660207963, 0.1486284223502365, 0.14693315403049792, 0.14530496216184446, 0.14376870455592214, 0.14229393289706316, 0.14087594000737147, 0.13951030972566653, 0.1381939194089944, 0.13692725360905944, 0.1357134001130735, 0.13396430021146344, 0.1322810309057875, 0.13068408923881478, 0.12916360659552625, 0.1276948173757566, 0.12627366641084253, 0.12490836748142213, 0.12359069510333424, 0.12231145231445813, 0.12106450391647534, 0.11983452066712103, 0.11806061709708432, 0.11632958474173705, 0.11461806339488086, 0.1129419109211148, 0.11127070930167597, 0.10958230592861472, 0.10787666027808301, 0.10612519164120864, 0.10431205380552988, 0.10240290412490836, 0.10036160434644706, 0.09814220338721417, 0.09568146752056707, 0.09294118584463974, 0.08980748445267493, 0.08620366745941492, 0.08204818040400452, 0.07733958898818614, 0.07213794952360476, 0.06666614519144401, 0.06120243510843881, 0.05601161975336735, 0.051258065564562166, 0.04698389607330316, 0.043173865538347664, 0.03976962029537009, 0.03670102016416955, 0.03390735045586199, 0.03133300523283533, 0.028922727381242734, 0.026631118719707938, 0.02439937293180102, 0.02214964074296716, 0.019718390664111976, 0.018282620834660743, 0.017406476849576424, 0.0161818624043725, 0.015647591255827396, 0.015432508900836119, 0.015271569258573625, 0.015000160118060336, 0.01500007079793588]
		results_y_max = [0.015, 0.012534264754228688, 0.012517014368486849, 0.012491369869760845, 0.012453392783801583, 0.012397497486646702, 0.012315675345077461, 0.012196312017180203, 0.012025663526074164, 0.011783772507285883, 0.011444616052897413, 0.011126465172851532, 0.01082236245979298, 0.010526877904158736, 0.010236562869673274, 0.009948218012102732, 0.009659050156982383, 0.00936393327936833, 0.009061222769991207, 0.008744229480719548, 0.008408376956995285, 0.0080459763457337, 0.007647120848241773, 0.007195741837286061, 0.006674292500042547, 0.0060595011663057835, 0.0053426402523300215, 0.004572538254385119, 0.0038749584618548464, 0.0033479924375637814, 0.002986502366284256, 0.0027384532238182778, 0.0025622055057415603, 0.002435865904728113, 0.002336736399966977, 0.002258861983013471, 0.0021970368066777037, 0.002145826715008738, 0.0021030695516715938, 0.002067469553634481, 0.002036049646205007, 0.002008727527684407, 0.001984382272711667, 0.0019533609711444863, 0.0019270621747126341, 0.0019065929979655111, 0.0018863816627336417, 0.001860369148790495, 0.0018393111696830566, 0.0018219877660465632, 0.001807368451209874, 0.0017835886551585511, 0.0017668411379635279, 0.0017531473091314004, 0.0017414081978817046, 0.0017297501035202808, 0.0017155672108435925, 0.0017068748538581612, 0.0016948027641555522, 0.00168514391131058, 0.0016776081767589143, 0.0016736825641594827, 0.0016606799514123772, 0.0016501670706449783, 0.0016460494275206373, 0.0016358766528365668, 0.0016272837551583527, 0.0016257931394156849, 0.0016199949967516036, 0.0016125740897525937, 0.0016039086635181153, 0.0016013208967950786, 0.001594712594446004, 0.0015931300306848799, 0.001591158329712106, 0.001588134400998554, 0.0015789195067751022, 0.0015765197728761302, 0.0015717680150328572, 0.0015725725754542096, 0.001566547475955274, 0.0015645215825848787, 0.0015611708327354194, 0.001561780769238155, 0.0015589122862886208, 0.00156059096485287, 0.0015524393897311916, 0.0015495851836002472, 0.0015498293117081816, 0.001550346119081149, 0.0015445577615843592, 0.0015465327417541674, 0.0015433947279573882, 0.0015405941581496867, 0.0015397947379674065, 0.0015419169592059926, 0.001540254486710611, 0.001535952871074679, 0.001536547403524718, 0.001534571852451974, 0.0015365666945997623, 0.001535142590259309, 0.0015366105582365174, 0.001534040084211, 0.0015344248217052656, 0.0015365508313836887, 0.0015387826253372204, 0.001536200324072751, 0.001537285866249574, 0.0015396692350562258, 0.0015445286508095242, 0.0015457388381933264, 0.001544325846526447, 0.0015459833519596824, 0.0015488154843095031, 0.0015538134039891993, 0.0015556471640707627, 0.0015607861979179335, 0.001566303653610892, 0.0015693855496971248, 0.0015751484053101441, 0.0015843352272207948, 0.0015869431855743106, 0.0015919428915231923, 0.0015989507978459868, 0.0016105032632677213, 0.0016189635379107073, 0.0016324607435556108, 0.0016431843495952189, 0.0016553306829635817, 0.0016718384898788666, 0.0016830994402972793, 0.0016987388615838, 0.001717236574454972, 0.001731073454768622, 0.001749113799547458, 0.0017787785354525323, 0.0018086891005735237, 0.0018444064226043094, 0.001880209883636673, 0.0019241655795429133, 0.0019672636477568012, 0.0020192145100548604, 0.0020749229276047854, 0.002139138291241035, 0.002212801356330611, 0.0022957572283281687, 0.0023931778861117506, 0.002506072326216011, 0.0026408834554555553, 0.0028006515739885164, 0.0029943149979535506, 0.0032271096719927814, 0.0035059594262233343, 0.0038323186988080352, 0.0042023881580846535, 0.0046051201740328505, 0.005025483295606982, 0.00545355200514633, 0.00588065609085823, 0.0063064723792300905, 0.0067338980769049905, 0.007166783842958959, 0.00761204250310208, 0.008080547064544044, 0.00858483863348207, 0.009143407280710112, 0.009786924055892257, 0.010574186868621695, 0.01165059887012554, 0.012446014162856046, 0.013010359544461425, 0.013928527030370294, 0.014387119488881016, 0.014583232496931468, 0.014734718105243402, 0.01499983829289777, 0.014999928013256687]

		results_y = [[0.8333333333333334, 0.7843159339200015, 0.7326044445035558, 0.6788911899587932, 0.6239908892510664, 0.5687941386232487, 0.5142108486903624, 0.4611110588320116, 0.41027114816011584], [0.4010838917701569], [0.3471948943768529, 0.29898884639695344, 0.25628787636022327, 0.21879111116443942, 0.18611512357614748, 0.1578293478118742, 0.13348490439314156, 0.1126365134135259, 0.09485799450183797, 0.07975229568782109, 0.06695715359259546, 0.05614746214037572, 0.04703529928793173, 0.03936839121806458, 0.03292761927501417, 0.027524017606943972, 0.022995578073929674, 0.019612988083479492, 0.017097927256941214], [0.015582774896335588], [0.013952173100764704]]

		if int(__version__.split('.')[0]) >= 2:
			self.assertEquals(json_response['stability'], ['S', 'N', 'U', 'N', 'S'])

			for i, x_i in enumerate(json_response['curve_lc_x']):
				self.assertAlmostEquals(x_i, results_x[i], delta=1e-6*x_i)

			for i, y_i in enumerate(json_response['curve_lc_ys']['cyclin_cdk_p']['min']):
				self.assertAlmostEquals(y_i, results_y_min[i], delta=1e-6*y_i)

			for i, y_i in enumerate(json_response['curve_lc_ys']['cyclin_cdk_p']['max']):
				self.assertAlmostEquals(y_i, results_y_max[i], delta=1e-6*y_i)

			for i, ys_i in enumerate(json_response['curve_ys']['cyclin_cdk']):
				for ii, y_i in enumerate(ys_i):
					self.assertAlmostEquals(y_i, results_y[i][ii], delta=1e-6*y_i)
