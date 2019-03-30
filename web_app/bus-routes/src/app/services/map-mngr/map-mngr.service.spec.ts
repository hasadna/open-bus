import { TestBed } from '@angular/core/testing';

import { MapMngrService } from './map-mngr.service';

describe('MapMngrService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: MapMngrService = TestBed.get(MapMngrService);
    expect(service).toBeTruthy();
  });
});
