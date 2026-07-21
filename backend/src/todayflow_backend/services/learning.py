"""Learning layer for generation logging, prompt registry and feedback signals."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db import models
from todayflow_backend.services.meaning_surface_patterns import build_meaning_surface_patterns_v0


class LearningService:
    """Persists prompt versions, generation traces and explicit user feedback."""

    def build_user_learning_context(
        self,
        db: Session,
        *,
        user_id: int,
        target_date: date | None = None,
    ) -> dict[str, Any]:
        reference_date = target_date or date.today()
        feedback_rows = (
            db.query(models.GenerationFeedback, models.GenerationLog)
            .join(models.GenerationLog, models.GenerationFeedback.generation_log_id == models.GenerationLog.id)
            .filter(models.GenerationFeedback.user_id == user_id)
            .order_by(models.GenerationFeedback.created_at.desc())
            .limit(60)
            .all()
        )
        diary_rows = (
            db.query(models.ObservationDiaryEntry)
            .filter(
                models.ObservationDiaryEntry.user_id == user_id,
                models.ObservationDiaryEntry.date >= reference_date - timedelta(days=21),
                models.ObservationDiaryEntry.date <= reference_date,
            )
            .order_by(models.ObservationDiaryEntry.date.desc())
            .all()
        )
        signal_rows = (
            db.query(models.DayConnection)
            .filter(
                models.DayConnection.user_id == user_id,
                models.DayConnection.date >= reference_date - timedelta(days=21),
                models.DayConnection.date <= reference_date,
            )
            .order_by(models.DayConnection.date.desc(), models.DayConnection.updated_at.desc())
            .all()
        )

        feedback_summary = self._summarize_feedback_rows(feedback_rows)
        diary_summary = self._summarize_diary_rows(diary_rows)
        signal_summary = self._summarize_signal_rows(signal_rows)
        quality_memory = self._summarize_quality_memory(feedback_rows)
        bridge_memory = self._summarize_bridge_memory(feedback_rows)
        natal_memory = self._summarize_natal_memory(feedback_rows)
        meaning_patterns = build_meaning_surface_patterns_v0(
            db, user_id=user_id, reference_date=reference_date, window_days=28
        )
        psychotype = self._build_psychotype_summary(
            feedback_summary, diary_summary, signal_summary, meaning_patterns
        )
        stats: dict[str, Any] = {
            "helpful_answers": feedback_summary["helpful_answers"],
            "unclear_answers": feedback_summary["unclear_answers"],
            "routes_opened": feedback_summary["routes_opened"],
            "routes_completed": feedback_summary["routes_completed"],
            "bridge_actions": bridge_memory["bridge_actions"],
            "natal_actions": natal_memory["natal_actions"],
            "diary_entries": diary_summary["entries_count"],
            "signal_days": signal_summary["signal_days"],
            "meaning_events_28d": int(meaning_patterns["total_events"]) if meaning_patterns else 0,
        }
        out: dict[str, Any] = {
            "summary": psychotype["summary"],
            "response_style": psychotype["response_style"],
            "support_style": psychotype["support_style"],
            "dominant_lanes": feedback_summary["dominant_lanes"],
            "dominant_routes": feedback_summary["dominant_routes"],
            "dominant_diary_topics": diary_summary["dominant_topics"],
            "signal_bias": signal_summary["signal_bias"],
            "quality_memory": quality_memory,
            "bridge_memory": bridge_memory,
            "natal_memory": natal_memory,
            "stats": stats,
        }
        if meaning_patterns:
            out["meaning_surface_patterns"] = meaning_patterns
        return out

    def _summarize_feedback_rows(
        self,
        feedback_rows: list[tuple[models.GenerationFeedback, models.GenerationLog]],
    ) -> dict[str, Any]:
        helpful_answers = 0
        unclear_answers = 0
        routes_opened = 0
        routes_completed = 0
        lane_counter: Counter[str] = Counter()
        route_counter: Counter[str] = Counter()

        for feedback, generation in feedback_rows:
            metadata = feedback.meta_payload if isinstance(feedback.meta_payload, dict) else {}
            lane = str(metadata.get("lane") or "").strip()
            route = str(
                metadata.get("route_href")
                or metadata.get("arrived_route")
                or metadata.get("day_spine_target_href")
                or metadata.get("day_spine_arrived_path")
                or ""
            ).strip()
            if feedback.signal == "answer_helpful":
                helpful_answers += 1
            elif feedback.signal == "still_unclear":
                unclear_answers += 1
            elif feedback.signal == "route_opened":
                routes_opened += 1
            elif feedback.signal in {"route_completed", "day_spine_route_completed"}:
                routes_completed += 1

            if lane:
                lane_counter[lane] += 1
            if route:
                route_counter[route] += 1

        dominant_lanes = [item[0] for item in lane_counter.most_common(3)]
        dominant_routes = [item[0] for item in route_counter.most_common(3)]
        return {
            "helpful_answers": helpful_answers,
            "unclear_answers": unclear_answers,
            "routes_opened": routes_opened,
            "routes_completed": routes_completed,
            "dominant_lanes": dominant_lanes,
            "dominant_routes": dominant_routes,
        }

    def _summarize_diary_rows(self, diary_rows: list[models.ObservationDiaryEntry]) -> dict[str, Any]:
        topic_counter: Counter[str] = Counter()
        for item in diary_rows:
            text = " ".join(filter(None, [item.noticed, item.hardest, item.easier_than_expected])).lower()
            for topic in self._classify_text_topics(text):
                topic_counter[topic] += 1
        return {
            "entries_count": len(diary_rows),
            "dominant_topics": [item[0] for item in topic_counter.most_common(3)],
        }

    def _summarize_signal_rows(self, signal_rows: list[models.DayConnection]) -> dict[str, Any]:
        relevant = [
            item for item in signal_rows
            if item.ritual_feedback or item.quick_decision_answer or item.question_of_day_answer
        ]
        yes_days = sum(1 for item in relevant if item.ritual_feedback == "yes")
        no_days = sum(1 for item in relevant if item.ritual_feedback == "no")
        unclear_days = sum(1 for item in relevant if item.quick_decision_answer == "unclear")
        bias = "neutral"
        if no_days >= 3 and no_days >= yes_days:
            bias = "needs_closure"
        elif unclear_days >= 3:
            bias = "needs_clarity"
        elif yes_days >= 4:
            bias = "stable"
        return {
            "signal_days": len(relevant),
            "ritual_feedback_yes_days": yes_days,
            "ritual_feedback_no_days": no_days,
            "unclear_decision_days": unclear_days,
            "signal_bias": bias,
        }

    def _summarize_quality_memory(
        self,
        feedback_rows: list[tuple[models.GenerationFeedback, models.GenerationLog]],
    ) -> dict[str, Any]:
        per_surface: dict[str, dict[str, int]] = {}
        for feedback, generation in feedback_rows:
            key = f"{generation.module}:{generation.surface or 'default'}"
            bucket = per_surface.setdefault(
                key,
                {
                    "helpful": 0,
                    "unclear": 0,
                    "route_opened": 0,
                    "route_completed": 0,
                },
            )
            if feedback.signal == "answer_helpful":
                bucket["helpful"] += 1
            elif feedback.signal == "still_unclear":
                bucket["unclear"] += 1
            elif feedback.signal == "route_opened":
                bucket["route_opened"] += 1
            elif feedback.signal in {"route_completed", "day_spine_route_completed"}:
                bucket["route_completed"] += 1

        strongest_surfaces: list[dict[str, Any]] = []
        weakest_surfaces: list[dict[str, Any]] = []
        for surface_key, bucket in per_surface.items():
            helpful = bucket["helpful"]
            unclear = bucket["unclear"]
            completed = bucket["route_completed"]
            opened = max(bucket["route_opened"], completed)
            quality_score = helpful * 2 + completed - unclear * 2
            entry = {
                "surface": surface_key,
                "quality_score": quality_score,
                "helpful": helpful,
                "unclear": unclear,
                "route_completion_rate": round(completed / opened, 2) if opened else None,
            }
            if helpful or completed:
                strongest_surfaces.append(entry)
            if unclear:
                weakest_surfaces.append(entry)

        strongest_surfaces.sort(key=lambda item: item["quality_score"], reverse=True)
        weakest_surfaces.sort(key=lambda item: item["quality_score"])
        return {
            "best_patterns": strongest_surfaces[:3],
            "weak_patterns": weakest_surfaces[:3],
        }

    def _summarize_bridge_memory(
        self,
        feedback_rows: list[tuple[models.GenerationFeedback, models.GenerationLog]],
    ) -> dict[str, Any]:
        bridge_buckets: dict[str, dict[str, int]] = {}
        for feedback, _generation in feedback_rows:
            metadata = feedback.meta_payload if isinstance(feedback.meta_payload, dict) else {}
            bridge_target = self._extract_bridge_target(feedback.signal, metadata)
            if not bridge_target:
                continue

            bucket = bridge_buckets.setdefault(
                bridge_target,
                {
                    "selected": 0,
                    "opened": 0,
                    "completed": 0,
                },
            )

            if feedback.signal in {"practice_bridge_selected", "today_bridge_tab_opened", "compatibility_bridge_selected"}:
                bucket["selected"] += 1
            elif feedback.signal == "route_opened":
                bucket["opened"] += 1
            elif feedback.signal in {"route_completed", "day_spine_route_completed", "compatibility_compare_completed"}:
                bucket["completed"] += 1

        ranked: list[dict[str, Any]] = []
        for target, bucket in bridge_buckets.items():
            selected = int(bucket["selected"])
            opened = int(bucket["opened"])
            completed = int(bucket["completed"])
            score = selected * 2 + opened + completed * 3
            ranked.append(
                {
                    "target": target,
                    "score": score,
                    "selected": selected,
                    "opened": opened,
                    "completed": completed,
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return {
            "preferred_targets": ranked[:3],
            "bridge_actions": sum(item["selected"] + item["opened"] + item["completed"] for item in ranked),
        }

    def _summarize_natal_memory(
        self,
        feedback_rows: list[tuple[models.GenerationFeedback, models.GenerationLog]],
    ) -> dict[str, Any]:
        target_buckets: dict[str, dict[str, int]] = {}
        source_buckets: dict[tuple[str, str, str], dict[str, int]] = {}

        for feedback, _generation in feedback_rows:
            metadata = feedback.meta_payload if isinstance(feedback.meta_payload, dict) else {}
            if str(metadata.get("source_surface") or "").strip() != "natal_chart":
                continue

            target = self._extract_route_target(feedback.signal, metadata)
            if not target:
                continue

            source_type = str(metadata.get("natal_source_type") or "editorial").strip().lower()
            if source_type not in {"house", "planet", "aspect", "editorial"}:
                source_type = "editorial"
            source_key = str(metadata.get("natal_source_key") or "").strip()
            if not source_key:
                source_key = "editorial_next_step" if source_type == "editorial" else "unknown"

            target_bucket = target_buckets.setdefault(
                target,
                {
                    "opened": 0,
                    "completed": 0,
                },
            )
            source_bucket = source_buckets.setdefault(
                (source_type, source_key, target),
                {
                    "opened": 0,
                    "completed": 0,
                },
            )

            if feedback.signal == "route_opened":
                target_bucket["opened"] += 1
                source_bucket["opened"] += 1
            elif feedback.signal in {"route_completed", "day_spine_route_completed", "compatibility_compare_completed"}:
                target_bucket["completed"] += 1
                source_bucket["completed"] += 1

        ranked_targets: list[dict[str, Any]] = []
        for target, bucket in target_buckets.items():
            opened = int(bucket["opened"])
            completed = int(bucket["completed"])
            score = opened + completed * 3
            ranked_targets.append(
                {
                    "target": target,
                    "score": score,
                    "opened": opened,
                    "completed": completed,
                }
            )
        ranked_targets.sort(key=lambda item: item["score"], reverse=True)

        typed_entries: dict[str, list[dict[str, Any]]] = {
            "house": [],
            "planet": [],
            "aspect": [],
            "editorial": [],
        }
        for (source_type, source_key, target), bucket in source_buckets.items():
            opened = int(bucket["opened"])
            completed = int(bucket["completed"])
            score = opened + completed * 3
            typed_entries[source_type].append(
                {
                    "source_key": source_key,
                    "target": target,
                    "score": score,
                    "opened": opened,
                    "completed": completed,
                }
            )

        for items in typed_entries.values():
            items.sort(key=lambda item: item["score"], reverse=True)

        return {
            "preferred_targets": ranked_targets[:4],
            "best_houses": typed_entries["house"][:6],
            "best_planets": typed_entries["planet"][:6],
            "best_aspects": typed_entries["aspect"][:6],
            "best_editorial_targets": typed_entries["editorial"][:3],
            "natal_actions": sum(item["opened"] + item["completed"] for item in ranked_targets),
        }

    def _extract_route_target(
        self,
        signal: str,
        metadata: dict[str, Any],
    ) -> str | None:
        route = str(
            metadata.get("route_href")
            or metadata.get("arrived_route")
            or metadata.get("day_spine_target_href")
            or metadata.get("day_spine_arrived_path")
            or ""
        ).strip()

        if route.startswith("/compatibility") or signal == "compatibility_compare_completed":
            return "compatibility"
        if route.startswith("/practices"):
            return "practices"
        if route.startswith("/today"):
            return "today"
        if route.startswith("/questions/money-career"):
            return "money_career"
        if route.startswith("/questions/state"):
            return "state"
        if route.startswith("/questions/pattern"):
            return "pattern"
        if route.startswith("/questions/decision"):
            return "decision"
        if route.startswith("/questions"):
            return "questions"
        return None

    def _extract_bridge_target(
        self,
        signal: str,
        metadata: dict[str, Any],
    ) -> str | None:
        route = str(
            metadata.get("route_href")
            or metadata.get("arrived_route")
            or metadata.get("day_spine_target_href")
            or metadata.get("day_spine_arrived_path")
            or ""
        ).strip()
        target_tab = str(metadata.get("target_tab") or "").strip()
        source_surface = str(metadata.get("source_surface") or "").strip()
        bridge_lane = str(metadata.get("bridge_lane") or "").strip()

        if route.startswith("/compatibility") or signal in {"compatibility_bridge_selected", "compatibility_compare_completed"}:
            return "compatibility"
        if route.startswith("/practices") or signal == "practice_bridge_selected":
            return "practices"
        if route.startswith("/questions/decision"):
            return "decision"
        if route.startswith("/today") or signal == "today_bridge_tab_opened" or target_tab in {"guide", "spheres", "morning", "day", "evening"}:
            return "today"
        if source_surface == "questions_memory_bridge":
            if bridge_lane == "money_career" or bridge_lane == "love":
                return "compatibility"
            if bridge_lane in {"state", "pattern"}:
                return "practices"
        return None

    def _build_psychotype_summary(
        self,
        feedback_summary: dict[str, Any],
        diary_summary: dict[str, Any],
        signal_summary: dict[str, Any],
        meaning_patterns: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        helpful = int(feedback_summary["helpful_answers"])
        unclear = int(feedback_summary["unclear_answers"])
        routes_completed = int(feedback_summary["routes_completed"])
        signal_bias = str(signal_summary["signal_bias"])
        diary_topics = diary_summary["dominant_topics"]

        if unclear >= helpful + 2 or signal_bias == "needs_clarity":
            response_style = "Нуждается в большей ясности и разборе до действия."
        elif routes_completed >= 3 or helpful >= unclear + 2:
            response_style = "Лучше отвечает на конкретный следующий шаг и прямой маршрут."
        else:
            response_style = "Лучше раскрывается через сочетание смысла и одного практического хода."

        if signal_bias == "needs_closure":
            support_style = "Ему полезны спокойное сужение фронта, завершение дня и снижение перегруза."
        elif diary_topics and diary_topics[0] in {"отношения", "семья"}:
            support_style = "Ему особенно важно, чтобы объяснение учитывало людей и атмосферу контакта."
        elif diary_topics and diary_topics[0] in {"работа", "деньги"}:
            support_style = "Ему полезнее язык конкретных решений, роли и результата, а не абстрактных состояний."
        else:
            support_style = "Ему полезнее короткая, живая и практически применимая интерпретация без лишнего шума."

        top_lane = feedback_summary["dominant_lanes"][0] if feedback_summary["dominant_lanes"] else None
        lane_line = f" Чаще всего он приходит через тему `{top_lane}`." if top_lane else ""
        topic_line = f" В дневниках сейчас чаще звучит `{diary_topics[0]}`." if diary_topics else ""
        hint_line = ""
        if meaning_patterns and isinstance(meaning_patterns.get("pattern_hints"), list):
            hints = [str(h).strip() for h in meaning_patterns["pattern_hints"][:2] if str(h).strip()]
            if hints:
                hint_line = " Сигналы поверхности Today: " + " ".join(hints)
        summary = f"{response_style} {support_style}{lane_line}{topic_line}{hint_line}".strip()
        return {
            "summary": summary,
            "response_style": response_style,
            "support_style": support_style,
        }

    def _classify_text_topics(self, text: str) -> list[str]:
        topics: list[str] = []
        mapping = {
            "работа": ["работ", "проект", "задач", "дел", "карьер"],
            "деньги": ["деньг", "доход", "финанс", "оплат", "бюдж"],
            "отношения": ["отнош", "партнер", "люб", "контакт", "разговор"],
            "семья": ["сем", "дом", "ребен", "родител", "близк"],
            "состояние": ["устал", "энерг", "стресс", "состоя", "трев", "спокой"],
        }
        for topic, needles in mapping.items():
            if any(needle in text for needle in needles):
                topics.append(topic)
        return topics

    def get_or_create_prompt_version(
        self,
        db: Session,
        *,
        module: str,
        version: str,
        prompt_kind: str,
        prompt_text: str,
        label: str | None = None,
        metadata: dict[str, Any] | None = None,
        is_active: bool = True,
    ) -> models.PromptVersion:
        prompt_version = (
            db.query(models.PromptVersion)
            .filter_by(module=module, version=version, prompt_kind=prompt_kind)
            .first()
        )
        if prompt_version:
            changed = False
            if prompt_version.prompt_text != prompt_text:
                prompt_version.prompt_text = prompt_text
                changed = True
            if label is not None and prompt_version.label != label:
                prompt_version.label = label
                changed = True
            if metadata is not None and prompt_version.meta_payload != metadata:
                prompt_version.meta_payload = metadata
                changed = True
            if prompt_version.is_active != is_active:
                prompt_version.is_active = is_active
                changed = True
            if changed:
                db.add(prompt_version)
                db.commit()
                db.refresh(prompt_version)
            return prompt_version

        prompt_version = models.PromptVersion(
            module=module,
            version=version,
            prompt_kind=prompt_kind,
            label=label,
            prompt_text=prompt_text,
            meta_payload=metadata,
            is_active=is_active,
        )
        db.add(prompt_version)
        db.commit()
        db.refresh(prompt_version)
        return prompt_version

    def log_generation(
        self,
        db: Session,
        *,
        module: str,
        surface: str | None = None,
        user_id: int | None = None,
        core_profile_snapshot_id: int | None = None,
        prompt_version_id: int | None = None,
        model: str | None = None,
        locale: str | None = None,
        input_payload: dict[str, Any] | None = None,
        system_prompt: str | None = None,
        user_prompt: str | None = None,
        raw_response: str | None = None,
        normalized_response: dict[str, Any] | None = None,
        status: str = "success",
        used_fallback: bool = False,
        error_message: str | None = None,
        duration_ms: int | None = None,
    ) -> models.GenerationLog:
        enriched_payload = dict(input_payload or {})
        snap_id = core_profile_snapshot_id
        if snap_id is None and enriched_payload.get("core_profile_snapshot_id") is not None:
            try:
                snap_id = int(enriched_payload["core_profile_snapshot_id"])
            except (TypeError, ValueError):
                snap_id = None
        if snap_id is not None:
            snap = (
                db.query(models.CoreProfileSnapshot)
                .filter(models.CoreProfileSnapshot.id == snap_id)
                .first()
            )
            if snap is not None:
                enriched_payload["core_profile_snapshot_id"] = snap.id
                enriched_payload["profile_hash"] = snap.profile_hash
                enriched_payload["profile_version"] = snap.profile_version
                enriched_payload["generated_from_snapshot"] = True
            else:
                enriched_payload.setdefault("core_profile_snapshot_id", snap_id)
                enriched_payload.setdefault("generated_from_snapshot", True)

        generation = models.GenerationLog(
            user_id=user_id,
            core_profile_snapshot_id=snap_id,
            prompt_version_id=prompt_version_id,
            module=module,
            surface=surface,
            model=model,
            locale=locale,
            input_payload=enriched_payload or None,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            raw_response=raw_response,
            normalized_response=normalized_response,
            status=status,
            used_fallback=used_fallback,
            error_message=error_message,
            duration_ms=duration_ms,
        )
        db.add(generation)
        db.commit()
        db.refresh(generation)
        return generation

    def add_feedback(
        self,
        db: Session,
        *,
        generation_log_id: int,
        signal: str,
        user_id: int | None = None,
        score: int | None = None,
        note: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> models.GenerationFeedback:
        feedback = models.GenerationFeedback(
            generation_log_id=generation_log_id,
            user_id=user_id,
            signal=signal,
            score=score,
            note=note,
            meta_payload=metadata,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback


_learning_service = LearningService()


def get_learning_service() -> LearningService:
    return _learning_service
