import {
  DEFAULT_MUSIC_LAYER_PREFS,
  normalizeMusicLayerPrefs,
  resolveLayerGains,
} from "@/lib/practicesPage/practiceMusicLayer";

describe("practiceMusicLayer", () => {
  it("resolves silent mode to zero gains", () => {
    expect(
      resolveLayerGains({
        ...DEFAULT_MUSIC_LAYER_PREFS,
        mode: "silent",
        voiceVolume: 1,
        musicVolume: 1,
        natureVolume: 1,
      }),
    ).toEqual({ voice: 0, music: 0, nature: 0 });
  });

  it("mutes voice in music_only mode", () => {
    const gains = resolveLayerGains({
      ...DEFAULT_MUSIC_LAYER_PREFS,
      mode: "music_only",
      voiceVolume: 0.9,
      musicVolume: 0.4,
      natureVolume: 0.2,
    });
    expect(gains.voice).toBe(0);
    expect(gains.music).toBe(0.4);
    expect(gains.nature).toBe(0.2);
  });

  it("clamps volumes and continue minutes", () => {
    const prefs = normalizeMusicLayerPrefs({
      mode: "with_voice",
      voiceVolume: 2,
      musicVolume: -1,
      natureVolume: 0.55,
      continueAfter: true,
      continueMinutes: 999,
    });
    expect(prefs.voiceVolume).toBe(1);
    expect(prefs.musicVolume).toBe(0);
    expect(prefs.natureVolume).toBe(0.55);
    expect(prefs.continueMinutes).toBe(60);
  });
});
