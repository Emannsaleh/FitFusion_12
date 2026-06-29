import { TestBed } from '@angular/core/testing';

import { VtonService } from './vton.service';

describe('VtonService', () => {
  let service: VtonService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(VtonService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
