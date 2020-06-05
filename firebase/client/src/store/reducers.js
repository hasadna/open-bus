import { actionTypes } from "./actions";
import { combineReducers } from "redux";

const initialState = {
    userSelection: {
        date: null,
        agency: null,
        line: null,
        alternative: null,
        time: null
    },
    data: {
        agenciesAndLines: null,
        currentLineAlternativesAndTimes: null,
        
        isFetchingCurrentRideData: false,
        currentRideData: null,
    }
};

function userSelectionReducer(state = initialState.userSelection, action) {
    switch (action.type) {
        // Set the date, reset everything else
        case actionTypes.selectDate:
            return {...initialState.userSelection,
                    date: action.date};
        // Set the agency, reset line\alternative\time
        case actionTypes.selectAgency:
            return {...state, 
                    agency: action.agency,
                    line: null,
                    alternative: null, 
                    time: null};
        // Set the line, reset alternative\time
        case actionTypes.selectLine:
            return {...state, 
                    line: action.line,
                    alternative: null, 
                    time: null};
        // Set the alternative, reset time
        case actionTypes.selectAlternative:
            return {...state, 
                    alternative: action.alternative, 
                    time: null};
        // Set the time
        case actionTypes.selectTime:
            return {...state, 
                    time: action.time};
        
        default:
            return state;
    }
}

function extractAgenciesAndLines(data) {
    return data.map((agency) => {
        return {
            id: agency.agency_id,
            name: agency.agency_name,
            lines: agency.gtfs_route_short_names
        };
    });
}

function extractAlternativesAndTimes(data) {
    return data.map((alternative) => {
        return {
            routeId: alternative.route_id,
            longName: alternative.route_long_name,
            times: alternative.siri_planned_start_times
        };
    });
}

function extractRideData(data) {
    // Note: we currently take the first ride (in most cases there should be one anyway)
    const ride = data[0];
    
    return {
        busId: ride.bus_id,
        points: ride.points.map((point) => {
            return {
                point: point.point,
                predictedDateTime: point.pred_dt,
                recordedDateTime: point.rec_dt
            };
        })
    };
}

function dataReducer(state = initialState.data, action) {
    switch (action.type) {
        // "Data Actions"
        // Set the agenciesAndLines, reset everything else 
        case actionTypes.receivedAgenciesAndLines:
            return {...initialState.data, 
                    agenciesAndLines: extractAgenciesAndLines(action.data)};
        // Set currentLineAlternativesAndTimes, reset currentRouteData\isFetchingCurrentRideData 
        case actionTypes.receivedAlternativesAndTimes:
            return {...state, 
                    currentLineAlternativesAndTimes: extractAlternativesAndTimes(action.data),
                    isFetchingCurrentRideData: false,
                    currentRideData: null};
        // Fetching ride data (no action data, just indicate we're getting the data)
        case actionTypes.fetchRideData:
            return {...state, 
                    isFetchingCurrentRideData: true,
                    currentRideData: null};
        // Got ride data
        case actionTypes.receivedRideData:
            return {...state, 
                    isFetchingCurrentRideData: false,
                    currentRideData: extractRideData(action.data)};

        // "Selection Actions"
        /* When selecting agency no new data is fetched, but we need to 
         * throw away all agency\line related data we've previously fetched*/
        case actionTypes.selectAgency:
            return {...initialState.data,
                    agenciesAndLines: state.agenciesAndLines };

        default:
            return state;
    }
}

const rootReducer = combineReducers({
    userSelection: userSelectionReducer,
    data: dataReducer
});

export default rootReducer;