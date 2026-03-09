import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock GridBackground component to avoid canvas issues in tests
vi.mock('../components/GridBackground', () => ({
  default: () => null,
}));

// Cleanup after each test
afterEach(() => {
  cleanup();
});
