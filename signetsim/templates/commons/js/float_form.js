/**
 * Copyright 2014-2017 Vincent Noel (vincent.noel@butantan.gov.br)
 *
 * This file is part of SigNetSim.
 *
 * libSigNetSim is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * SigNetSim is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SigNetSim.  If not, see <http://www.gnu.org/licenses/>.
 */

{% load static from staticfiles %}

class FloatForm extends Form
{
    constructor(field, description, required, default_value=1)
    {
        super(field, description, default_value);
        this.required = required;
        $("#" + this.field).on('paste keyup', () => { this.check(); });

    }

    check() {
        ajax_call(
            "POST", "{% url 'float_validator' %}",
            {'value' : $.trim($("#" + this.field).val()), 'required': this.required},
            (data) => {
                $.each(data, (index, element) => {
                    if (index == "error"){ this.setError(element.toString()); }
                    else { this.setError("couldn't be validated : unknown response"); }
                });
            },
            () => { this.setError("couldn't be validated : unable to connect"); }
        );
    }
    clear() {
        super.clearError();
    }
}
