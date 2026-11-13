import { describe, it, expect } from 'vitest';
import { DEMO_LOCATIONS } from '../components/layout/LocationSelector';

describe('Frontend Foundation Smoke Tests', () => {
  it('should have 5 Tamil Nadu demonstration operational locations configured', () => {
    expect(DEMO_LOCATIONS).toHaveLength(5);
    const cities = DEMO_LOCATIONS.map((l) => l.city);
    expect(cities).toContain('Coimbatore');
    expect(cities).toContain('Tiruppur');
    expect(cities).toContain('Chennai');
    expect(cities).toContain('Madurai');
    expect(cities).toContain('Salem');
  });

  it('should have correct facility codes assigned', () => {
    const coimbatore = DEMO_LOCATIONS.find((l) => l.city === 'Coimbatore');
    expect(coimbatore?.code).toBe('CBE-MF01');
    expect(coimbatore?.type).toBe('factory');
  });
});
