import { IBusStopState, initialBusState } from 'src/app/store/states/bus-stop.state';
import { ITripState, initialTripState } from 'src/app/store/states/trips.state';

export interface IAppState {
  //stops: IBusStopState;
  trips: ITripState;
}

export const initialAppState: IAppState = {
  //stops: initialBusState,
  trips: initialTripState
};

export function getInitialState(): IAppState {
  return initialAppState;
}
