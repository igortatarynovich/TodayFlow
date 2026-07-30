import { lookupPracticeDetail } from "@/lib/practices/fetchPracticeDetailServer";

describe("lookupPracticeDetail", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("returns ok for a free practice payload", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: "loving-kindness-meditation",
        title: "Медитация любящей доброты",
        description: "Практика метта",
      }),
    }) as unknown as typeof fetch;

    await expect(lookupPracticeDetail("loving-kindness-meditation")).resolves.toEqual({
      status: "ok",
      practice: {
        id: "loving-kindness-meditation",
        title: "Медитация любящей доброты",
        description: "Практика метта",
      },
    });
  });

  it("returns missing on HTTP 404", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 404,
    }) as unknown as typeof fetch;

    await expect(lookupPracticeDetail("gone-practice")).resolves.toEqual({ status: "missing" });
  });

  it("returns unavailable on transport failure", async () => {
    global.fetch = jest.fn().mockRejectedValue(new TypeError("Failed to fetch")) as unknown as typeof fetch;

    await expect(lookupPracticeDetail("loving-kindness-meditation")).resolves.toEqual({
      status: "unavailable",
    });
  });
});
