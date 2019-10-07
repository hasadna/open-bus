/* In "react-selct", list items\options are objects with "value" and "label"
 * properties, thus we need to convert all of our "lists data" to these objects.
 * TODO: Should we do the conversions in the reducer\store? 
 * Logically it makes more since to do it here since it's react-select specifc.
 * The current downside is that we're "wasting" more memory. */
export const  toSelectOption = (value, labelField = null) => {
    if (!value) {
      return null;
    }
  
    const label = labelField ? value[labelField] : value;
    return { value, label };
  }

/* Note: I'm always wrapping toSelectOption with a function, and not 
 * calling it directly, since we use those functions the callback
 * for Array.map, which passes additional arguments to the calback, thus
 * passing some value as labelField. */ 
export const agencyToOption = (agency) => toSelectOption(agency, "name");
export const lineToOption = (line) => toSelectOption(line);
export const alternativeToOption = (alternative) => toSelectOption(alternative, "longName");
export const timeToOption = (time) => toSelectOption(time);

/* TODO: currently, the selected items doesn't really refer to objects from the lists,
 * we reconstruct on assignment. For example, when selecting an agency, we'll
 * recreate selectedAgency from the store, as a new object (with value\label).
 * Does it matter in any way to react-select? */


export const getSelectedRideDateTime = (selectedDate, selectedTime) => {
  const datePart = selectedDate.toISOString().split("T")[0];
  return new Date(`${datePart}T${selectedTime}`);
}