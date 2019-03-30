import { initialBusState, IBusStopState } from 'src/app/store/states/bus-stop.state';
import { BusStopActions, EBusStopActions } from 'src/app/store/actions/bus-stop.action';

export const busStopReducers = (
  state = initialBusState,
  action: BusStopActions
): IBusStopState => {
  switch (action.type){
    case EBusStopActions.ADD_STOP_SUCCESS: {
      return {
        ...state,
        //busStops: action.payload,
      };
    }

    default:
      return state;
  }
};
