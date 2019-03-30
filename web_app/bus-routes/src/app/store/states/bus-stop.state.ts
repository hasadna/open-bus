import { BusStop } from 'src/app/data/bus-stop';

export interface IBusStopState {
  busStops: BusStop[];
}

export const initialBusState: IBusStopState = {
  busStops: null
};
