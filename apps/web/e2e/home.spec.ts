import { expect, test } from "@playwright/test";

test("learner can open the TutorDesk workspace", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "TutorDesk" })).toBeVisible();
  await expect(page.getByRole("status")).toHaveText("The workspace foundation is ready.");
});
