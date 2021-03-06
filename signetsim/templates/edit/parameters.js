{% comment %}

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

{% endcomment %}

class ParameterForm extends FormGroup{

    constructor(field){
        super();
        this.field = field;

        this.form_value = new FloatForm("parameter_value", "The value of the parameter", false, "1");
        this.addForm(this.form_value, true);

        this.form_sbmlid = new SbmlIdForm("parameter_sbml_id", "The identifier of the parameter", "", true, "parameter_scope_value");
        this.addForm(this.form_sbmlid, true);

        this.dropdown_unit = new Dropdown("parameter_unit", "The unit of the parameter", null, "", "Choose an unit");
        this.addForm(this.dropdown_unit);

        this.dropdown_scope = new Dropdown("parameter_scope", "The scope of the parameter", () => {this.form_sbmlid.check();}, "0", "Global");
        this.addForm(this.dropdown_scope);

        this.form_sboterm = new SBOTermInput("parameter_sboterm");
        this.addForm(this.form_sboterm);

        this.form_constant = new SliderForm("parameter_constant", "The constant setting of the parameter", true);
        this.addForm(this.form_constant);

        this.form_name = new ValueForm("parameter_name", "The name of the parameter", "");
        this.addForm(this.form_name);

        this.form_id = new ValueForm("parameter_id", "The id of the parameter", "");
        this.addForm(this.form_id);

        this.form_reaction_id = new ValueForm("parameter_reaction_id", "The scope id of the parameter", "");
        this.addForm(this.form_reaction_id);

        this.form_notes = new ValueForm("parameter_notes", "The notes of the parameter", "");
        this.addForm(this.form_notes);

    }

    show(){
        $("#general").tab('show');
        $("#modal_parameter").on('shown.bs.modal', () => { $("#parameter_name").focus(); });
        $('#modal_parameter').modal('show');
    }

    new(){
        $("#modal_title").html("New parameter");
        this.clearForms();
        this.show();
    }

    load(sbml_id, reaction)
    {
        $("#modal_title").html("Edit parameter");

        ajax_call(
            "POST",
            "{% url 'get_parameter' %}", {'sbml_id': sbml_id, 'reaction': reaction},
            (data) =>
            {
               $.each(data, (index, element) =>
               {
                    if (index == "id") {
                        this.form_id.setValue(element.toString());

                    } else if (index == "reaction_id") {

                        this.form_reaction_id.setValue(element.toString());

                        if (element.toString() === ""){
                            this.dropdown_scope.setValue(0);
                            this.dropdown_scope.setLabel("Global");
                            this.form_sbmlid.setInitialScope(0);

                        } else {
                            this.dropdown_scope.setValue(parseInt(element)+1);
                            this.form_sbmlid.setInitialScope(parseInt(element)+1);

                            switch(parseInt(element)+1) {
                                {% for reaction in list_of_reactions %}
                                case {{forloop.counter0}}:
                                    this.dropdown_scope.setLabel("{{reaction}}");
                                    break;
                                {% endfor %}
                            }
                        }

                    } else if (index == "sbml_id") {
                       this.form_sbmlid.setInitialValue(element.toString());
                       this.form_sbmlid.setValue(element.toString());

                    } else if (index == "name") {
                       this.form_name.setValue(element.toString());

                    } else if (index == "value") {
                       if (element == null) {
                           this.form_value.setValue("");
                       } else {
                           this.form_value.setValue(element.toString());
                       }

                    } else if (index == "unit_name") {
                       this.dropdown_unit.setLabel(element.toString());

                    } else if (index == "unit_id") {
                       this.dropdown_unit.setValue(element.toString());

                    } else if (index == "constant") {

                       if (element == "1") {
                           this.form_constant.switch_on();
                       } else {
                           this.form_constant.switch_off();
                       }

                    } else if (index == "notes") {
                       this.form_notes.setValue(element.toString());

                    } else if (index == "sboterm") {
                       this.form_sboterm.setValue(element.toString());
                       this.form_sboterm.setLink(element.toString());

                    } else if (index == "sboterm_name") {
                       this.form_sboterm.setLabel(element.toString());

                    }
               });
            },
            () => { console.log("failed"); }
        );

        this.show();
    }

    save()
    {
        this.checkErrors();

        if (this.nb_errors == 0)
        {
            $("#modal_parameter").modal("hide");
        }
        return (this.nb_errors == 0);
    }

}

let form_parameter = new ParameterForm("modal_parameter");
