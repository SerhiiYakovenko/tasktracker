/**
 * Vitest global setup. Registers jest-dom matchers and clears the DOM and
 * mocks between tests.
 */
import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

afterEach(() => {
  cleanup();
});
