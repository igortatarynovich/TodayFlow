/**
 * @deprecated Use buildProfileProgressiveDetailsProjection — matrix slots are Explore, not PersonStory.
 * Thin re-export kept so old imports fail loudly toward the rename.
 */
export {
  buildProfileProgressiveDetailsProjection as buildProfilePersonStoryProjection,
  buildProfileProgressiveDetailsProjection,
  PROGRESSIVE_DETAILS_SLOT_ORDER,
  PROFILE_SLOT_CATALOG,
  PROFILE_SLOT_NAME,
  PROFILE_SLOT_NATAL,
  PROFILE_SLOT_EMOTIONAL,
  PROFILE_SLOT_DECISION,
  PROFILE_SLOT_RELATIONSHIP,
  PROFILE_SLOT_WORK,
  PROFILE_SLOT_MONEY,
  PROFILE_SLOT_HOME,
  PROFILE_SLOT_STRENGTHS,
  PROFILE_SLOT_TENSIONS,
  type ProgressiveDetailItem as PersonStoryChapter,
  type ProgressiveDetailKind as PersonStoryChapterKind,
  type ProgressiveDetailsProjection as PersonStoryProjection,
} from "@/lib/profilePage/buildProfileProgressiveDetailsProjection";

/** @deprecated Slot order is Explore-only — not Journey IA. */
export { PROGRESSIVE_DETAILS_SLOT_ORDER as PERSON_STORY_SLOT_ORDER } from "@/lib/profilePage/buildProfileProgressiveDetailsProjection";

export { PROFILE_SLOT_HELPS } from "@/lib/profilePage/profileMatrixAccess";
export const PROFILE_SLOT_SUN = "sun_element_numerology";
export { PROFILE_SLOT_IDENTITY } from "@/lib/profilePage/profileMatrixAccess";
