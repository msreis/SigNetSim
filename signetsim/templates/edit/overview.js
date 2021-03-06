{% load tags %}

var cytoscape_style = cytoscape.stylesheet()
	.selector('node').css(
	{
		'padding-left': 10,
		'padding-right': 10,
		'padding-bottom': 10,
		'padding-top': 10,
		'color': '#000',
		'border-width': 2,
		'border-color': '#000',
		'background-color': '#fff'
	})

	.selector(':selected').css(
	{
		'border-width': 3,
		'border-color': '#333'
	})

	.selector('node.reaction').css(
	{
		'shape': 'rectangle',
		'width': '5',
		'height': '5'
	})

	.selector('node.compartment').css(
	{
		'shape': 'roundrectangle',
		'content': 'data(name)',
		'text-halign': 'left',
		'text-valign': 'top',
		'text-outline-width': 2,
		'text-outline-color': '#fff',
		'width': 'label',
		'height': 'label'
	})

	.selector('node.species').css(
	{
		'shape': 'roundrectangle',
		'content': 'data(name)',
		'text-valign': 'center',
		'text-outline-width': 2,
		'text-outline-color': '#fff',
		'width': 'label',
		'height': 'label'
	})

	.selector('node.empty_species').css(
	{
		'padding-left': 0,
		'padding-right': 0,
		'padding-bottom': 0,
		'padding-top': 0,
		'shape': 'roundrectangle',
		'font-family':'FontAwesome',
		'content': '\uf05e',
		'text-valign': 'center',
		'text-outline-width': 2,
		'text-outline-color': '#fff',
		'width': 'label',
		'height': 'label',
		'border-width': 0
	})

	.selector('edge').css(
	{
		'curve-style': 'bezier',
		'opacity': 0.666,
		'source-arrow-shape': 'none',
		'line-color': '#000',
		'source-arrow-color': '#000',
		'target-arrow-color': '#000'
	})

	.selector('edge.positive').css(
	{
		'target-arrow-shape': 'triangle'
	})

	.selector('edge.reversible').css(
	{
		'source-arrow-shape': 'triangle',
		'target-arrow-shape': 'triangle'
	})

	.selector('edge.negative').css(
	{
		'target-arrow-shape': 'tee'
	})

	.selector('edge.regulation').css(
	{
		'target-arrow-shape': 'circle'
	})

	.selector('edge.questionable').css(
	{
		'line-style': 'dotted',
		'target-arrow-shape': 'triangle'
	})

	.selector('.faded').css(
	{
		'opacity': 0.25,
		'text-opacity': 0
	});

function loadReactionGraph ()
{
	var cy = window.cy = cytoscape(

		{
			container: document.getElementById('reactions_graph'),
			layout: {
				name: 'cola',
				nodeSpacing: 5,
				edgeLengthVal: 200,
				maxSimulationTime: 60000,
			},

			style: cytoscape_style,
			elements: {
				nodes: [
					{% for species in list_of_species %}
					{
						data: {
							id: '{{species.getSbmlId}}',
							parent: '{{ species.getCompartment.getSbmlId }}',
							name: '{{species.getNameOrSbmlId}}'
						},
						classes: 'species'
					},
					{% endfor %}
					{% for reaction in list_of_reactions %}
					{
						data: {
							id: '{{reaction.getSbmlId}}',
							parent: '{{ reaction.getCompartment.getSbmlId }}',
							name: '{{reaction.getNameOrSbmlId}}'
						},
						classes: 'reaction'
					},
					{% if reaction.listOfReactants|length == 0 %}
					{
						data: {
							id: '{{reaction.getSbmlId}}_reactant',
							parent: '{{ reaction.getCompartment.getSbmlId }}',
							name: 'empty'
						},
						classes: 'empty_species'
					},
					{% endif %}
					{% if reaction.listOfProducts|length == 0 %}
					{
						data: {
							id: '{{reaction.getSbmlId}}_product',
							parent: '{{ reaction.getCompartment.getSbmlId }}',
							name: 'empty'
						},
						classes: 'empty_species'
					},
					{% endif %}
					{% endfor %}
					{% for compartment in list_of_compartments %}
					{ data: { id: '{{compartment.getSbmlId}}', name: '{{compartment.getNameOrSbmlId}}'}, classes: 'compartment' },
					{% endfor %}
				],
				edges: [
					{% for reaction in list_of_reactions %}
					{% if reaction.listOfReactants|length > 0 %}
					{% for reactant in reaction.listOfReactants %}

					{
						data: {
							source: '{{reactant.getSpecies.getSbmlId}}',
							target: '{{reaction.getSbmlId}}'
						},
						classes: {% if reaction.kineticLaw.isReversible %}'reversible'{% else %}'positive'{% endif %},

					},
					{% endfor %}
					{% else %}
					{
						data: {
							source: '{{reaction.getSbmlId}}_reactant',
							target: '{{reaction.getSbmlId}}'
						},
						classes: {% if reaction.kineticLaw.isReversible %}'reversible'{% else %}'positive'{% endif %},

					},
					{% endif %}
					{% for modifier in reaction.listOfModifiers %}

					{
						data: {
							source: '{{modifier.getSpecies.getSbmlId}}',
							target: '{{reaction.getSbmlId}}'
						},
						classes: 'regulation',

					},
					{% endfor %}
					{% if reaction.listOfProducts|length > 0 %}
					{% for product in reaction.listOfProducts %}

					{
						data: {
							source: '{{reaction.getSbmlId}}',
							target: '{{product.getSpecies.getSbmlId}}'
						},
						classes: {% if reaction.kineticLaw.isReversible %}'reversible'{% else %}'positive'{% endif %},

					},
					{% endfor %}
					{% else %}
					{
						data: {
							source: '{{reaction.getSbmlId}}',
							target: '{{reaction.getSbmlId}}_product'
						},
						classes: {% if reaction.kineticLaw.isReversible %}'reversible'{% else %}'positive'{% endif %},

					},
					{% endif %}
					{% endfor %}
				]
			},

		});

}


$(window).on('load',function()
{
	$("#reactions_graph").css({ height: $(window).height() - $(".navbar-header").height() - 150 + "px" });
	loadReactionGraph();
	//alert("Loading reaction graph");
}); // on dom ready




