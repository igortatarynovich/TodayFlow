/**
 * @jest-environment jsdom
 */
import {
  clearCoreProfileCache,
  readCoreProfileFromCache,
  writeCoreProfileToCache,
} from "@/lib/coreProfileCacheStorage";
import type { CoreProfile } from "@/lib/types";

function makeProfile(hash = "abc"): CoreProfile {
  return {
    profile_version: "core-v2",
    generated_at: new Date().toISOString(),
    is_ready: true,
    missing_fields: [],
    profile_hash: hash,
    person: {},
    astro: { birth_date: "1990-05-15", profile_id: 3 },
    numerology: { life_path: 7 },
    baseline: {},
  } as CoreProfile;
}

describe("coreProfileCacheStorage dual-scope", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    localStorage.setItem("todayflow_token", "tok");
  });

  afterEach(() => {
    clearCoreProfileCache();
    localStorage.clear();
    sessionStorage.clear();
  });

  it("reads profile written under u:pending after scope becomes u:pending (token, no me)", () => {
    writeCoreProfileToCache(makeProfile("pending-write"), null);
    const hit = readCoreProfileFromCache(null);
    expect(hit?.profile_hash).toBe("pending-write");
    expect(localStorage.getItem("todayflow_core_profile:v3:u:pending:default")).toBeTruthy();
  });
});
