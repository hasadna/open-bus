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
import PropTypes from 'prop-types';
import { 
  agencyToOption,
  lineToOption,
  alternativeToOption,
  timeToOption,
  getSelectedRideDateTime
 } from './../../util'

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

RideSelector.propTypes = {
  agencies: PropTypes.array,
  alternatives:PropTypes.array,
  fetchRideData: PropTypes.func,
  lines: PropTypes.array,
  selectAlternative: PropTypes.func,
  selectTime: PropTypes.func,
  selectedAgency: PropTypes.object,
  selectedAlternative: PropTypes.object,
  selectedDate: PropTypes.object,
  selectedLine: PropTypes.object,
  selectLineAndFetchAlternativesAndTimesForIt: PropTypes.func,
  selectedTime: PropTypes.object,
  times: PropTypes.array,
}

export default connect(mapStateToProps, mapDispatchToProps)(RideSelector);