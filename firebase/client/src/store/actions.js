import * as db from "../db";

export const actionTypes = {
    selectDate: "SELECT_DATE",
    selectAgency: "SELECT_AGENCY",
    selectLine: "SELECT_LINE",
    selectAlternative: "SELECT_ALTERNATIVE",
    selectTime: "SELECT_TIME",

    receivedAgenciesAndLines: "RECEIVED_AGENCIES_AND_LINES",
    receivedAlternativesAndTimes: "RECEIVED_ALTERNATIVES_AND_TIMES",
    fetchRideData: "FETCH_RIDE_DATA",
    receivedRideData: "RECEIVED_RIDE_DATA",
    dbFetchError: "DB_FETCH_ERROR",
};

export function selectDateAndFetchAgenciesAndLinesForIt(date) {
    return async (dispatch) => {
        dispatch(selectDate(date));
        try {
            const agenciesAndLines = await db.fetchAgenciesAndRides(date);
            dispatch(receivedAgenciesAndLines(agenciesAndLines));
        } catch(e) {
            dispatch(dbFetchError(e));
        }
    };
}

export const selectAgency = (agency) => ({ type: actionTypes.selectAgency, agency });

export function selectLineAndFetchAlternativesAndTimesForIt(date, agencyId, line) {
    return async (dispatch) => {
        dispatch(selectLine(line));
        try {
            const alternativesAndTimes = await db.fetchRouteRides(date, agencyId, line);
            dispatch(receivedAlternativesAndTimes(alternativesAndTimes));
        } catch(e) {
            dispatch(dbFetchError(e));
        }
    };
}

export const selectAlternative = (alternative) => ({ type: actionTypes.selectAlternative, alternative });
export const selectTime = (time) => ({ type: actionTypes.selectTime, time });

export function fetchRideData(routeId, dateTime) {
    return async (dispatch) => {
        dispatch({ type: actionTypes.fetchRideData });
        try {
            const rideData = await db.fetchRideData(routeId, dateTime);
            dispatch(receivedRideData(rideData));
        } catch(e) {
            dispatch(dbFetchError(e));
        }
    };
}

const selectDate = (date) => ({ type: actionTypes.selectDate, date });
const receivedAgenciesAndLines = (data) => ({ type: actionTypes.receivedAgenciesAndLines, data });
const selectLine = (line) => ({ type: actionTypes.selectLine, line });
const receivedAlternativesAndTimes = (data) => ({ type: actionTypes.receivedAlternativesAndTimes, data });
const receivedRideData = (data )=> ({ type: actionTypes.receivedRideData, data });
const dbFetchError = (error) => ({ type: actionTypes.dbFetchError, error });