$('#search_type_list li').on('click', function()
{
    $("#search_type_name").html($(this).text());
    $('#search_type_id').val($(this).index());

});


function search_biomodels()
{
    search_type = $("#search_type_id").val();
    search_string = $("#search_string").val();
    $("#searching_done").removeClass("in");
    $("#searching_failed").removeClass("in");
    $("#searching_wait").addClass("in");
    ajax_call(
        "POST", "{{csrf_token}}",
        "{% url 'search_biomodels' %}",
        {'search_type': search_type, 'search_string': search_string},
        function(data)
        {
            $("#searching_wait").removeClass("in");
            $.each(data, function(index, element)
            {
               if (index == "results") {
                    if (element.length > 0){
                       $("#table_search_results").empty();

                        $.each(element, function(subindex, subelement){
                            $("#table_search_results").append("\
                                <tr class=\"row\" onclick=\"load_biomodels('" + subelement[0] + "')\">\
                                <td class=\"col-xs-12\"><span role=\"button\" id=\"model_" + subindex.toString() + "_name\">" + subelement[1] + "</span></td>\
                                </tr>");
                        });
                        $("#searching_done").addClass("in");

                    } else {
                        $("#searching_failed").addClass("in");
                    }

               }

            });


        },
        function(){
            $("#searching_wait").removeClass("in");
            $("#searching_failed").addClass("in");
        }
    );
}

function load_biomodels(model_id)
{
    $("#load_biomodels_model_id").val(model_id);
    $("#load_biomodels_form").submit();
}