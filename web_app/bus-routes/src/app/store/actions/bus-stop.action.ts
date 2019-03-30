import { Action } from '@ngrx/store';
import { BusStop } from 'src/app/data/bus-stop';

export namespace EBusStopActions {
  export const ADD_STOP = '[BusStop] add stop';
  export const ADD_STOP_SUCCESS = '[BusStop] add stop success';
  //export const REMOVE = '[BusStop] remove';
}

export class BusStopAddAction implements Action {
  public readonly type = EBusStopActions.ADD_STOP;
  public payload: number;

  constructor(public busStopID: number) {
    this.payload = busStopID;
  }
}

export class BusStopAddSuccessAction implements Action {
  public readonly type = EBusStopActions.ADD_STOP_SUCCESS;
  public payload: BusStop;

  constructor(public busStop: BusStop) {
    this.payload = busStop;
  }
}
 /*
export class BasketRemoveAction implements Action {
  readonly type = BasketActionTypes.REMOVE;
  public payload: Item;

  constructor(public item: Item) {
    this.payload = item;
  }
}*/

export type BusStopActions = BusStopAddAction
  | BusStopAddSuccessAction;
