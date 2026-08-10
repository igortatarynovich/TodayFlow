/**
 * @jest-environment jsdom
 */

import { syncDayPromiseToConnection } from "@/lib/todayPromiseSync";

const postJson = jest.fn();

jest.mock("@/lib/api", () => ({
  postJson: (...args: unknown[]) => postJson(...args),
}));

describe("syncDayPromiseToConnection", () => {
  beforeEach(() => {
    postJson.mockReset();
    postJson.mockResolvedValue({});
  });

  it("posts morning_intention to day-connection", async () => {
    await syncDayPromiseToConnection("2026-08-10", "  Закрыть один хвост  ");
    expect(postJson).toHaveBeenCalledWith("/day-connection/2026-08-10", {
      morning_intention: "Закрыть один хвост",
      morning_completed: true,
    });
  });

  it("no-ops on empty text", async () => {
    await syncDayPromiseToConnection("2026-08-10", "   ");
    expect(postJson).not.toHaveBeenCalled();
  });

  it("swallows transport errors", async () => {
    postJson.mockRejectedValue(new Error("network"));
    await expect(syncDayPromiseToConnection("2026-08-10", "ok")).resolves.toBeUndefined();
  });
});
