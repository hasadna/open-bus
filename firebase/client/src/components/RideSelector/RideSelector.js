import "./RideSelector.css";
import DateSelector from "./DateSelector";
import ListSelect from "./ListSelect";
import { selectDateAndFetchAgenciesAndLinesForIt,
         selectAgency,
         selectLineAndFetchAlternativesAndTimesForIt,
         selectAlternative,
         selectTime,
         fetchRideData } from "../../store/actions";

import React from "react";
import { connect } from "react-redux";
import Grid from "@material-ui/core/Grid";

/* In "react-selct", list items\options are objects with "value" and "label"
 * properties, thus we need to convert all of our "lists data" to these objects.
 * TODO: Should we do the conversions in the reducer\store? 
 * Logically it makes more since to do it here since it's react-select specifc.
 * The current downside is that we're "wasting" more memory. */
function toSelectOption(value, labelField = null) {
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
const agencyToOption = (agency) => toSelectOption(agency, "name");
const lineToOption = (line) => toSelectOption(line);
const alternativeToOption = (alternative) => toSelectOption(alternative, "longName");
const timeToOption = (time) => toSelectOption(time);

/* TODO: currently, the selected items doesn't really refer to objects from the lists,
 * we reconstruct on assignment. For example, when selecting an agency, we'll
 * recreate selectedAgency from the store, as a new object (with value\label).
 * Does it matter in any way to react-select? */
function mapStateToProps(state) {
  const { agency: selectedAgency, alternative: selectedAlternative } = state.userSelection;
  const { agenciesAndLines, currentLineAlternativesAndTimes } = state.data;

  return {
    // Selections, converting selected list items to react-select options
    selectedDate: state.userSelection.date,
    selectedAgency: agencyToOption(selectedAgency),
    selectedLine: lineToOption(state.userSelection.line),
    selectedAlternative: alternativeToOption(selectedAlternative),
    selectedTime: timeToOption(state.userSelection.time),

    // List items, converting data from our store to react-select options
    agencies: agenciesAndLines ? agenciesAndLines.map(agencyToOption) : null,
    lines: selectedAgency ? selectedAgency.lines.map(lineToOption) : null,
    alternatives: currentLineAlternativesAndTimes ? currentLineAlternativesAndTimes.map(alternativeToOption) : null,
    times: selectedAlternative ? selectedAlternative.times.map(timeToOption) : null,
  };
};

const mapDispatchToProps = { selectDateAndFetchAgenciesAndLinesForIt,
                             selectAgency,
                             selectLineAndFetchAlternativesAndTimesForIt,
                             selectAlternative,
                             selectTime,
                             fetchRideData };

function getSelectedRideDateTime(selectedDate, selectedTime) {
  const datePart = selectedDate.toISOString().split("T")[0];
  return new Date(`${datePart}T${selectedTime}`);
}

function RideSelector(props) {
  const handleLineSelect = (line) => {
    props.selectLineAndFetchAlternativesAndTimesForIt(props.selectedDate,
                                                      props.selectedAgency.value.id,
                                                      line);
  };

  const handleTimeSelect = (time) => {
    /* Note that currently I've made selectTime and fetchRideData two different actions
     * in case we'll want to use a (separate) button the actually fetch the data */
    props.selectTime(time);

    const dateTime = getSelectedRideDateTime(props.selectedDate, time);
    const routeId = props.selectedAlternative.value.routeId;
    props.fetchRideData(routeId, dateTime);
  };

  return (
    <div className="selector-container">
      <Grid container spacing={1} alignItems="center" justify="center">
        <Grid item xs={2}>
          <DateSelector
            value={props.selectedDate}
            onChange={props.selectDateAndFetchAgenciesAndLinesForIt}
          />
        </Grid>
        <Grid item xs={2}>
          <ListSelect 
            label="Agency:"
            options={props.agencies}
            value={props.selectedAgency}
            onChange={props.selectAgency}
            isLoading={props.selectedDate && !props.agencies}
          />
        </Grid>
        <Grid item xs={2}>
          <ListSelect
            label="Line:"
            options={props.lines}
            value={props.selectedLine}
            onChange={handleLineSelect}
          />
        </Grid>
        <Grid item xs={3}>
          <ListSelect
            label="Direction\\Alternative:"
            options={props.alternatives}
            value={props.selectedAlternative}
            onChange={props.selectAlternative}
            isLoading={props.selectedLine && !props.alternatives}
          />
        </Grid>
        <Grid item xs={2}>
          <ListSelect
            label="Time:"
            options={props.times}
            value={props.selectedTime}
            onChange={handleTimeSelect}
          />
        </Grid>
      </Grid>
    </div>
  );
}

export default connect(mapStateToProps, mapDispatchToProps)(RideSelector);