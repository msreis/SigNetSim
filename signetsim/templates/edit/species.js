{% load bootstrap3 %}
{% load tags %}
{% include 'commons/js/sbmlid_form.js' %}
{% include 'commons/js/float_form.js' %}
{% include 'commons/js/sboterm_input.js' %}

let form_group = new FormGroup();

let form_value_type = new Dropdown("species_value_type", post_treatment=null, default_value="1", default_label="Concentration");
form_group.addForm(form_value_type);

let form_units = new Dropdown("species_unit", post_treatment=null, default_value="", default_label="Choose an unit");
form_group.addForm(form_units);

let form_compartment = new Dropdown("species_compartment", post_treatment=null, default_value="0", default_value="{{ list_of_compartments|my_lookup:0 }}");
form_group.addForm(form_compartment);

let form_sbmlid = new SbmlIdForm("species_sbml_id", "The identifier of the species", default_value="");
form_group.addForm(form_sbmlid, error_checking=true);

let form_value = new FloatForm("species_value", "The initial value of the species", false, default_value="0");
form_group.addForm(form_value, error_checking=true);

let form_sboterm = new SBOTermInput("species_sboterm");
form_group.addForm(form_sboterm);

function modal_show()
{
    $("#general").tab('show');
    $("#modal_species").on('shown.bs.modal', () => { $("#species_name").focus(); });
    $('#modal_species').modal('show');
}

function new_species()
{
    $("#modal_title").html("New species");
    $("#species_id").attr("value", "");
    $("#species_name").attr("value", "");

    $("#species_constant").attr("value", 0);
    $("#species_boundary").attr("value", 0);

    form_group.clearForms();

    modal_show();
}

function view_species(sbml_id)
{

    $("#modal_title").html("Edit species");

    ajax_call(
        "POST",
        "{% url 'get_species' %}", {'sbml_id': sbml_id},
        (data) =>
        {
           $.each(data, (index, element) =>
           {
               if (index == "id") { $("#species_id").val(element.toString()); }
               else if (index == "sbml_id") {
                   form_sbmlid.setValue(element.toString());
                   form_sbmlid.setInitialValue(element.toString());
               }
               else if (index == "name") { $("#species_name").val(element.toString()); }

               else if (index == "value") {
                   if (element == null) { form_value.setValue(""); }
                   else { form_value.setValue(element.toString()); }
               }

               else if (index == "compartment_name") { form_compartment.setLabel(element.toString()); }
               else if (index == "compartment_id") { form_compartment.setValue(element.toString()); }

               else if (index == "unit_name") { form_units.setLabel(element.toString()); }
               else if (index == "unit_id") { form_units.setValue(element.toString()); }

               else if (index == "constant") {
                   if (element == "1") { $("#species_constant").prop('checked', true); }
                   else { $("#species_constant").prop('checked', false); }
               }
               else if (index == "boundaryCondition") {
                   if (element == "1") { $("#species_boundary").prop('checked', true); }
                   else { $("#species_boundary").prop('checked', false); }
               }

               else if (index == "isConcentration") {
                   form_value_type.setValue(element.toString());
                   if (element == "1") {
                       form_value_type.setLabel("Concentration");
                   }
                   else {
                       form_value_type.setLabel("Amount");
                   }
               }
               else if (index == "notes") { $("#specie_notes").val(element.toString()); }

               else if (index == "sboterm") {
                   form_sboterm.setValue(element.toString());
                   form_sboterm.setLink(element.toString());
               }
               else if (index == "sboterm_name") { form_sboterm.setLabel(element.toString()); }
           });

           form_sbmlid.check();
           form_group.resetErrors();
        },
        () => { console.log("failed"); }
    )

    modal_show();
}

function save_species()
{

    form_group.checkErrors();
    if (form_group.nb_errors == 0)
    {
        $("#modal_species").modal("hide");
    }

    return (nb_errors == 0);
}
