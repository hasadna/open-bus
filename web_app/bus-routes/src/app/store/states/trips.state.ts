import { Trip } from 'src/app/data/trip';

export interface ITripState {
  trip: Trip;
}

export const initialTripState: ITripState = {
  trip: null
};
