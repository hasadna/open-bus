import { Action } from '@ngrx/store';
import { Trip } from 'src/app/data/trip';

export namespace ETripActions {
  export const ADD_TRIP = '[Trip] add trip';
  export const ADD_TRIP_SUCCESS = '[Trip] add trip success';

  export const GET_TRIP = '[Trip] get trip';
  export const GET_TRIP_SUCCESS = '[Trip] get trip success';
}

export class TripAddAction implements Action {
  public readonly type = ETripActions.ADD_TRIP;
  public payload: number;

  constructor(public tripID: number) {
    this.payload = tripID;
  }
}

export class TripAddActionSuccess implements Action {
  public readonly type = ETripActions.ADD_TRIP_SUCCESS;
  public payload: Trip;

  constructor(public trip: Trip) {
    this.payload = trip;
  }
}

export class TripGetAction implements Action {
  public readonly type = ETripActions.GET_TRIP;
  public payload: number;

  constructor(public tripID: number) {
    this.payload = tripID;
  }
}

export class TripGetActionSuccess implements Action {
  public readonly type = ETripActions.GET_TRIP_SUCCESS;
  public payload: Trip;

  constructor(public trip: Trip) {
    this.payload = trip;
  }
}

export type TripActions =
TripAddAction | TripAddActionSuccess |
TripGetAction | TripGetActionSuccess ;
