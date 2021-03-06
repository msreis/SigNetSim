{#   edit/reactions.js : Javascript methods for reactions   				  #}

{#   Copyright (C) 2016 Vincent Noel (vincent.noel@butantan.gov.br) 		  #}

{#   This program is free software: you can redistribute it and/or modify     #}
{#   it under the terms of the GNU Affero General Public License as published #}
{#   by the Free Software Foundation, either version 3 of the License, or     #}
{#   (at your option) any later version. 									  #}

{#   This program is distributed in the hope that it will be useful, 		  #}
{#   but WITHOUT ANY WARRANTY; without even the implied warranty of 		  #}
{#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 			  #}
{#   GNU Affero General Public License for more details.					  #}

{#   You should have received a copy of the GNU Affero General Public License #}
{#   along with this program. If not, see <http://www.gnu.org/licenses/>. 	  #}

{% load static from staticfiles %}
{% load tags %}

class ListOfSpeciesReference extends ListForm{

    constructor(field, description, parent_form_name, form_name, post_treatment=null) {
        super(field, description, parent_form_name, form_name, post_treatment, true);
    }

    add(species_stoichiometry="1", species_id="", species_name="Choose a species")
	{

        super.add(
            [
                $("<td>").attr('class', 'col-xs-3').append(
                    $("<input>").attr({
                        'type': 'text', 'class': 'form-control input-sm text-center',
                        'placeholder': 'Input stoichiometry',
                        'name': this.field + '_' + this.index + "_stoichiometry",
                        'value': species_stoichiometry
                    })
                ),
                $("<td>").attr('class', 'col-xs-7').append(
                    $("<input>").attr({
                        'type': 'hidden',
                        'id': this.field + '_' + this.index + '_value',
                        'name': this.field + '_' + this.index,
                        'value': species_id
                    }),
                    $("<div>").attr('class', 'dropdown').append(
                        $("<button>").attr({
                            'type': 'button', 'class': 'btn btn-primary btn-sm dropdown-toggle',
                            'data-toggle': 'dropdown'
                        }).append(
                            $("<span>").attr({
                                'id': this.field + '_' + this.index + '_label'
                            }).text(species_name),
                            $("<span>").attr('class', 'caret')
                        ),
                        $("<ul>").attr({
                            'class': 'dropdown-menu',
                            'id': this.field + '_' + this.index + '_list'
                        }).append(
                            {% for species in list_of_species %}
                            $("<li>").append($("<a>").attr("href", "#").text("{{ species }}")),
                            {% endfor %}
                        )
                    )
                )
            ],

        ""

		);
		this.objects.push(
        	new Dropdown(
        		this.field + '_' + (this.index-1),
				'The ' + nth(this.index) + ' species of the ' + this.description,
				() => {this.post_treatment();},
				'',
				'Choose a species',
				true
			)
		);
        this.update();
    }

    remove(element_id){
        super.remove(element_id);
        this.update();
    }

    update(){
        // let m_id = 0;

        $("#body_" + this.field + "s").children("tr").each((tr_id, tr)=>
        {
            $('input', $(tr)).each((input_id, input) =>
            {
                let id = new RegExp('^' + this.field + '_[0-9]+$');
                if (id.test($(input).attr('name')))
                {
                    $(input).attr('name', this.field + '_' + tr_id.toString());
                }

                let exp = new RegExp('^' + this.field + '_[0-9]+_stoichiometry');
                if (exp.test($(input).attr('name')))
                {
                    $(input).attr('name', this.field + '_' + tr_id.toString() + '_stoichiometry');
                }
            });
            // m_id = m_id + 1;
        });
        super.update();
    }

    getSpecies(){
        let result = "";
        $("#body_" + this.field + "s").children("tr").each((index) =>
        {
            if ($("#" + this.field + "_" + index.toString()).val() != "") {
                if (result != "") {
                    result += " + "
                }
            result += $("#" + this.field + "_" + index.toString() + "_label").html();
            }
        });
        return result;
    }
}

class ListOfParameters extends ListForm {

    constructor(field, description, parent_form_name, form_name, post_treatment=null) {
        super(field, description, parent_form_name, form_name, post_treatment, false);
        this.form_local_parameters = null;
        // this.list_dropdowns = [];
    }

    setLocalParameters(form_local_parameters){
        this.form_local_parameters = form_local_parameters;
    }

    add(name, default_value="", default_label="Choose a parameter")
    {
        super.add(
            [
                $("<td>").attr("class", "col-xs-6").append(
                    $("<span>").attr("id", this.field + "_" + this.index + "_name").text(name)
                ),
                $("<td>").attr("class", "col-xs-6").append(
                    $("<input>").attr({
                        'type': 'hidden',
                        'id': this.field + '_' + this.index + '_value',
                        'name': this.field + '_' + this.index,
                        'value': default_value
                    }),
                    $("<div>").attr("class", "dropdown").append(
                        $("<button>").attr({
                            'type': 'button',
                            'class': 'btn btn-primary btn-sm dropdown-toggle',
                            'data-toggle': 'dropdown'
                        }).append(
                            $("<span>").attr({
                                'id': this.field + '_' + this.index + '_label',

                            }).text(default_label),
                            $("<span>").attr("class", "caret")
                        ),
                        $("<ul>").attr({
                            "id": this.field + "_" + this.index + "_list",
                            "class": "dropdown-menu"
                        })
                    )
                )
            ],
            ""
        );
    }

    update()
    {
        this.objects = [];

        $("#body_" + this.field + "s").children("tr").each((index, element) =>
        {
            let list_dropdown = $("#" + this.field + "_" + index.toString() + "_list");
            list_dropdown.empty();

            if (this.form_local_parameters.local_parameters.length > 0)
            {
                $.each(this.form_local_parameters.local_parameters, (sub_index, sub_element) =>
                {
                    list_dropdown.append("<li><a>" + sub_element[0] + "</a></li>");
                });

                list_dropdown.append("<li role='separator' class='divider'></li>");
            }

            {% for t_parameter in list_of_parameters %}
                list_dropdown.append("<li><a>{{ t_parameter }}</a></li>")
            {% endfor %}

            this.objects.push(
            	new Dropdown(
            		this.field + "_" + index.toString(),
					'The ' + nth(index+1) + ' parameter of the kinetic law',
					null, '', 'Choose a parameter', true
				)
			);
        });
    }
}

class ListOfLocalParameters extends ListForm{

    constructor(field, description, parent_form_name, form_name, post_treatment=null, list_of_parameters=null) {
        super(field, description, parent_form_name, form_name, post_treatment, true);
        this.local_parameters = [];
        this.list_of_parameters = list_of_parameters
    }


    changed_local_parameter_name(parameter_id)
    {
        this.local_parameters[parameter_id][0] = $("#local_parameter_" + parameter_id.toString() + "_name").val();
        if (this.list_of_parameters !== null) { this.list_of_parameters.update(); }
    }

    changed_local_parameter_value(parameter_id)
    {
        this.local_parameters[parameter_id][1] = $("#local_parameter_" + parameter_id.toString() + "_value").val();
        if (this.list_of_parameters !== null){ this.list_of_parameters.update(); }
    }

    add(name="", value=""){

        super.add(
            [
                $("<td>").attr('class', 'col-xs-6').append(
                    $("<input>").attr({
                        'type': 'input', 'class': "form-control input-sm",
                        'placeholder': "Input parameter's name",
                        'id': 'local_parameter_' + this.index + "_name",
                        'name': 'local_parameter_' + this.index + "_name",
                        'value': name
                    })
                ),
                $("<td>").attr('class', 'col-xs-4').append(
                    $("<input>").attr({
                        'type': 'input', 'class': "form-control input-sm",
                        'placeholder': "Input parameter's value",
                        'id': 'local_parameter_' + this.index + "_value",
                        'name': 'local_parameter_' + this.index + "_value",
                        'value': value
                    })
                )
            ],
			""
        );
		this.objects.push(
			new ValueForm(
				'local_parameter_' + (this.index-1) + '_name',
				'The name of the #' + (this.index-1) + ' local parameter',
				'', () => { this.changed_local_parameter_name(this.index-1); }
			)
		);

		this.objects.push(
			new ValueForm(
				'local_parameter_' + (this.index-1) + '_value',
				'The value of the #' + (this.index-1) + ' local parameter',
				'', () => { this.changed_local_parameter_value(this.index-1); }
			)
		);

        this.local_parameters.push([name, value]);
        this.update();
        if (this.list_of_parameters !== null){
            this.list_of_parameters.update();
        }
    }


    remove(element_id){
        super.remove(element_id);
        this.local_parameters.splice(element_id, 1);
        this.update();
        if (this.list_of_parameters !== null){
            this.list_of_parameters.update();
        }
    }

    clear(){
        super.clear();
        if (this.list_of_parameters !== null){
            this.list_of_parameters.update();
        }
    }


    update() {

        $("#body_" + this.field + "s").children("tr").each((tr_id, tr) =>
        {
            $('input', $(tr)).each((input_id, input) =>
            {
                let id = new RegExp('^' + this.field + '_[0-9]+_name$');
                if (id.test($(input).attr('name'))) {
                    $(input).attr('name', this.field + '_' + tr_id.toString() + '_name');
                }

                let exp = new RegExp('^' + this.field + '_[0-9]+_value');
                if (exp.test($(input).attr('name'))) {
                    $(input).attr('name', this.field + '_' + tr_id.toString() + '_value');
                }
            });

        })
        super.update();
    }
}

class FormReaction extends FormGroup{

    constructor(field){
        super();
        this.field = field;
        this.selected_parameters = []

        this.form_id = new ValueForm("reaction_id", "The id of the reaction", "");
        this.addForm(this.form_id);

        this.form_name = new ValueForm("reaction_name", "The name of the reaction", "");
        this.addForm(this.form_name);

        this.form_sbmlid = new SbmlIdForm("reaction_sbml_id", "The identifier of the reaction", "");
        this.addForm(this.form_sbmlid, true);

        this.form_kinetic_law = new MathForm("reaction_kinetic_law", "The kinetic law of the reaction", "");
        this.addForm(this.form_kinetic_law, true);

        this.form_list_reactants = new ListOfSpeciesReference(
            "reaction_reactant",
            "the list of reactants",
            "form_reaction", "form_list_reactants",
            ()=>{this.buildReactionDescription();}
        );
        this.addForm(this.form_list_reactants, true);

        this.form_list_modifiers = new ListOfSpeciesReference(
            "reaction_modifier",
            "the list of modifiers",
            "form_reaction", "form_list_modifiers", ()=>{this.buildReactionDescription();}
        );
        this.addForm(this.form_list_modifiers, true);

        this.form_list_products = new ListOfSpeciesReference(
            "reaction_product",
            "the list of products",
            "form_reaction", "form_list_products",
            ()=>{this.buildReactionDescription();}
        );
        this.addForm(this.form_list_products, true);

        this.form_parameters = new ListOfParameters(
            "reaction_parameter",
            "the list of reaction parameters",
            "form_reaction", "form_parameters",
            null,
        );
        this.addForm(this.form_parameters, true);

        this.form_local_parameters = new ListOfLocalParameters(
            "local_parameter",
            "the list of local parameters",
            "form_reaction", "form_local_parameters",
            null,
            this.form_parameters
        );
        this.addForm(this.form_local_parameters);
        this.form_parameters.setLocalParameters(this.form_local_parameters);

        this.form_reaction_type = new Dropdown(
            "reaction_type",
            "The type of the reaction",
            ()=>{this.select_reaction_type();},
            0,
            "{{reaction_types|my_lookup:0}}"
        )
        this.addForm(this.form_reaction_type);

        this.form_reversible = new SliderForm(
            "reaction_reversible", "The reversibility of the reaction", "1",
            ()=>
            {
                this.updateParameters();
                this.buildReactionDescription();
            }
        );
        this.addForm(this.form_reversible);

        this.form_sboterm = new SBOTermInput("reaction_sboterm");
        this.addForm(this.form_sboterm);

        this.form_notes = new ValueForm("reaction_notes", "The notes of the reaction", "");
        this.addForm(this.form_notes);


    }

    buildReactionDescription()
    {

        let result_reactants = this.form_list_reactants.getSpecies();
        let result_modifiers = this.form_list_modifiers.getSpecies();
        let result_products = this.form_list_products.getSpecies();

        let result = result_reactants;
        if (result_modifiers != "")
        {
            if (result_reactants === ""){
              result += result_modifiers;
            } else {
              result += " + " + result_modifiers;
            }
        }

        if (this.form_reversible.getValue()) {
            result += " <-> ";

        } else {
            result += " -> ";
        }

        if (result_modifiers != "")
        {
            if (result_products === ""){
                result += result_modifiers;
            } else {
                result += result_modifiers + " + ";
            }
        }

        result += result_products;

        $("#reaction_summary").html(result);
    }

    updateReversibleToggle()
    {
        this.form_reversible.switch_off();

        switch(this.form_reaction_type.getValue())
        {
            {% for t_type in reaction_types %}
            case {{forloop.counter0}}:

                {% if allow_reversible|my_lookup:forloop.counter0 == True %}
                this.form_reversible.enable();
                {% else %}
                this.form_reversible.disable();
                {% endif %}
            break;
            {% endfor %}
        }
    }

    updateParameters()
    {
        this.form_parameters.clear();

        switch(this.form_reaction_type.getValue()) {

            {% for t_type in reaction_types %}
            case {{forloop.counter0}}:

                {% if allow_reversible|my_lookup:forloop.counter0 == True %}
                if (this.form_reversible.getValue()){
                    {% for parameter in parameters_list|my_lookup:forloop.counter0|my_lookup:True %}
                    this.form_parameters.add("{{parameter}}");
                    {% endfor %}

                } else {
                    {% for parameter in parameters_list|my_lookup:forloop.counter0|my_lookup:False %}
                    this.form_parameters.add("{{parameter}}");
                    {% endfor %}
                }

                {% else %}
                {% for parameter in parameters_list|my_lookup:forloop.counter0|my_lookup:False %}
                this.form_parameters.add("{{parameter}}");
                {% endfor %}
                {% endif %}

                break;

            {% endfor %}
        }

        this.form_parameters.update();
    }

    select_reaction_type ()
    {
//        this.form_reaction_type.getValue()
        this.updateReversibleToggle();
        this.updateParameters();
        if (this.form_reaction_type.getValue() === 2) {
            $("#input_parameters").removeClass("in");
            $("#input_kinetic_law").addClass("in");
        } else {
            $("#input_kinetic_law").removeClass("in");
            $("#input_parameters").addClass("in");

        }
    }



    show(){
        $("#summary").tab('show');
        $("#" + this.field).on('shown.bs.modal', () => { $("#reaction_name").focus(); });
        $('#' + this.field).modal('show');
    }

    new(){
        this.clearForms();
        this.buildReactionDescription();
        this.select_reaction_type();
        this.show();
    }

    load(sbml_id)
    {
        $("#modal_reaction-title").html("Edit reaction");
        $("#loading_wait").addClass("in");
        $("#loading_done").removeClass("in");

        this.clearForms();

        ajax_call(
            "POST",
            "{% url 'get_reaction' %}", {'sbml_id': sbml_id},
            (data) =>
            {
                $.each(data, (index, element) =>
                {
                    if (index === "id") {
                        this.form_id.setValue(element.toString());
                        this.form_kinetic_law.setScope(parseInt(element));

                    } else if (index === "sbml_id") {
                        this.form_sbmlid.setInitialValue(element.toString());
						this.form_sbmlid.setValue(element.toString());

                    } else if (index === "name") {
                        this.form_name.setValue(element.toString());

                    } else if (index === "list_of_reactants") {
                        $.each(element, (index, subelement) => {
                            this.form_list_reactants.add(subelement[1], subelement[0], get_species_name(subelement[0]));
                        });

                    }
                    else if (index === "list_of_modifiers") {
                        $.each(element, (index, subelement) => {
                            this.form_list_modifiers.add(subelement[1], subelement[0], get_species_name(subelement[0]));

                        });
                    }
                    else if (index === "list_of_products") {
                        $.each(element, (index, subelement) => {
                            this.form_list_products.add(subelement[1], subelement[0], get_species_name(subelement[0]));
                        });
                    }

                    else if (index === "reaction_type") {
                        this.form_reaction_type.setValue(element);
                        this.select_reaction_type();
                    }
                    else if (index === "reaction_type_name"){
                        this.form_reaction_type.setLabel(element);
                    }
                    else if (index === "reversible") {
                        if (element == 0) {
                            this.form_reversible.switch_off();
                            this.updateParameters();
                        } else {
                            this.form_reversible.switch_on();
                            this.updateParameters();
                        }

                    }

                    else if (index === "kinetic_law"){
                        this.form_kinetic_law.setValue(element);
                    }
                    else if (index == "list_of_local_parameters"){

                        this.form_local_parameters.local_parameters = [];
                        $.each(element, (index, subelement) => {
                            this.form_local_parameters.add(subelement[0], subelement[1]);
                        });
                    }

                    else if (index == "notes") {
                        this.form_notes.setValue(element.toString());

                    }
                    else if (index == "sboterm") {
                       this.form_sboterm.setValue(element.toString());
                       this.form_sboterm.setLink(element.toString());
                    }
                    else if (index == "sboterm_name") {
                        this.form_sboterm.setLabel(element.toString());
                    }
                });

               $.each(data, (index, element) => {
                   if (index === "list_of_parameters") {
                       $.each(element, (sub_index, subelement) => {
                           this.selected_parameters.push(element[0]);
                           $("#reaction_parameter_" + sub_index.toString() + "_value").val(subelement[0]);
                           $("#reaction_parameter_" + sub_index.toString() + "_label").html(subelement[1]);
                       });
                       this.form_parameters.update();

                   }
               });
               this.buildReactionDescription();
               // this.checkErrors();
               $("#loading_wait").removeClass("in");
               $("#loading_done").addClass("in");
               $("#summary").tab('show');
            },
            () => { console.log("failed"); }
        );

        this.show();

    }

    save(){
        this.checkErrors();

        if ((this.form_list_reactants.objects.length + this.form_list_products.objects.length) === 0) {
        	this.addGlobalError('speciesreferences', 'There must be at least one reactant, or one product !');
		}

        if (this.nb_errors == 0)
        {
            $("#" + this.field).hide();
        }

        return (this.nb_errors == 0);
    }
}

let form_reaction = new FormReaction("modal_reaction");


function get_species_name(species_id)
{
    switch(species_id)
    {
        {% for species in list_of_species %}
        case {{forloop.counter0}}:
            return "{{species}}";
        {% endfor %}
    }
}



$(window).on('load',() =>
{
    {% for reaction in list_of_reactions %}
         load_reaction_kinetic_law({{forloop.counter0}});
    {% endfor %}
});


function load_reaction_kinetic_law(reaction_id)
{
    ajax_call(
        "POST",
        "{% url 'get_reaction_kinetic_law' %}", {'reaction_id': reaction_id.toString()},
        (data) => {
            $.each(data, (index, element) => {
             if (index === 'kinetic_law') { $("#kinetic_law_" + reaction_id.toString()).html(element.toString());  }
            });
        },
        () => {}
    );
}
