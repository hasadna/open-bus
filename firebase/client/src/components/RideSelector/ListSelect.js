import React from "react";
import Select from "react-select";

/* A simple react-select wrapper:
 * - onChange propagates the value, not the option object.
 * - Uses menuPortalTarget to make sure the list will be displayed on top of everything.
 * - If "options" is empty the list is disabled. */
function ListSelect(props) {
    return (
        <Select
            placeholder={props.label}
            options={props.options}
            value={props.value}
            onChange={(option) => props.onChange(option.value)}
            menuPortalTarget={document.querySelector("body")}
            isDisabled={!props.options}
            isLoading={props.isLoading || false}
        />
    )
}

export default ListSelect;