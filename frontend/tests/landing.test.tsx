import { render, screen } from "@testing-library/react";
import LandingPage from "../app/page";

describe("LandingPage", () => {
  it("renders product value prop", () => {
    render(<LandingPage />);
    expect(screen.getByText(/Sustainable productivity/i)).toBeTruthy();
  });
});
