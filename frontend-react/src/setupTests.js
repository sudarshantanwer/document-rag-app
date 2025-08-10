import '@testing-library/jest-dom';

// Mock window.alert for JSDOM environment
global.alert = jest.fn();

// Mock fetch globally if not already mocked in individual tests
if (!global.fetch) {
  global.fetch = jest.fn();
}
