import { initialTripState, ITripState } from 'src/app/store/states/trips.state';
import { TripActions, ETripActions } from 'src/app/store/actions/trip.action';

export const tripReducers = (
  state = initialTripState,
  action: TripActions
): ITripState => {
  switch (action.type){
    case ETripActions.GET_TRIP_SUCCESS: {
      return {
        ...state,
        trip: action.payload
      };
    }

    default:
      return state;
  }
};
