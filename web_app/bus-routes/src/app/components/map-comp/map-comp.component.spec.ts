import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MapCompComponent } from './map-comp.component';

describe('MapCompComponent', () => {
  let component: MapCompComponent;
  let fixture: ComponentFixture<MapCompComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MapCompComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MapCompComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
