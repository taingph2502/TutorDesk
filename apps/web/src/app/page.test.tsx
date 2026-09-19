import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "./page";

describe("TutorDesk home", () => {
  it("introduces the local learning workspace", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: "TutorDesk" })).toBeInTheDocument();
    expect(screen.getByText(/local-first learning workspace/i)).toBeInTheDocument();
  });
});
