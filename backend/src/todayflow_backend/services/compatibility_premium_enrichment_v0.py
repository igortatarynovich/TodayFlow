"""Explicit paid premium guidance pack — only on user request."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from todayflow_backend.data.astrology import lookup_sign_metadata
from todayflow_backend.services.generation_jobs_v0 import (
    claim_job,
    complete_job_if_fresh,
    get_job,
    mark_job_failed,
    run_with_db,
)

logger = logging.getLogger("todayflow.compatibility.premium")


def run_compatibility_premium_job(job_id: int) -> None:
    def _run(db: Session) -> None:
        job = claim_job(db, job_id)
        if job is None:
            return
        payload = job.request_payload if isinstance(job.request_payload, dict) else {}
        fingerprint = job.fingerprint
        try:
            from todayflow_backend.api.compatibility import _build_static_sign_report
            from todayflow_backend.i18n import localized_sign_name
            from todayflow_backend.services.compatibility_access_v0 import _yes_no_from_score

            from_id = str(payload.get("from_sign") or "")
            to_id = str(payload.get("to_sign") or "")
            locale = str(payload.get("locale") or "ru")
            from_meta = lookup_sign_metadata(from_id) or {}
            to_meta = lookup_sign_metadata(to_id) or {}
            from_display = localized_sign_name(from_id, locale=locale)
            to_display = localized_sign_name(to_id, locale=locale)
            static = _build_static_sign_report(
                from_sign=from_id,
                to_sign=to_id,
                from_name=from_display,
                to_name=to_display,
                from_element=from_meta.get("element", ""),
                to_element=to_meta.get("element", ""),
                from_modality=from_meta.get("modality", ""),
                to_modality=to_meta.get("modality", ""),
                locale=locale,
            )
            score = int(static["score"])
            yn = _yes_no_from_score(score, locale=locale)
            qr = static.get("quick_reading") or {}
            ru = locale.startswith("ru")
            result = {
                "kind": "premium_guidance",
                "generation_source": "template",
                "verdict": {
                    "answer": yn.get("answer"),
                    "why": yn.get("framing"),
                },
                "do": str(qr.get("strongest") or (
                    "Держите ясный контакт и один общий шаг на неделю." if ru else "Keep clear contact and one shared weekly step."
                )),
                "dont": str(qr.get("friction") or (
                    "Не давите на ответ «прямо сейчас»." if ru else "Don't push for an answer right now."
                )),
                "how": (
                    "Назовите один конкретный момент на этой неделе, где вы хотите сблизиться — и обсудите только его."
                    if ru
                    else "Name one specific moment this week where you want closeness — and discuss only that."
                ),
                "next_step": (
                    "Напишите партнёру одно короткое сообщение без обвинений о том, что для вас важно."
                    if ru
                    else "Send one short non-blaming message about what matters to you."
                ),
                "question": payload.get("question"),
                "pair": f"{from_display} × {to_display}",
                "score": score,
                # Mark as baseline-quality pack until dedicated premium LLM prompt lands.
                "is_fully_personal": False,
            }
            # Optional LLM enrichment of premium pack — only if chat configured.
            try:
                from todayflow_backend.core.llm_openai_compatible import (
                    chat_completion_text,
                    get_openai_compatible_client,
                    is_llm_chat_configured,
                    resolve_default_chat_model,
                    resolve_max_tokens,
                )

                if is_llm_chat_configured():
                    client = get_openai_compatible_client(operation="background")
                    if client is not None:
                        import json

                        raw = chat_completion_text(
                            client,
                            model=resolve_default_chat_model(),
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Ты пишешь короткий премиум-разбор совместимости на русском. "
                                        "Верни только JSON: answer, why, do, dont, how, next_step. "
                                        "answer — одно из: да|скорее да|зависит|скорее нет|нет."
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content": json.dumps(
                                        {
                                            "pair": result["pair"],
                                            "score": score,
                                            "question": payload.get("question"),
                                            "seed": result,
                                        },
                                        ensure_ascii=False,
                                    ),
                                },
                            ],
                            temperature=0.5,
                            max_tokens=resolve_max_tokens(900),
                            json_object=True,
                        )
                        parsed = json.loads(raw or "{}") if raw else {}
                        if isinstance(parsed, dict) and parsed.get("answer"):
                            result["verdict"] = {
                                "answer": str(parsed.get("answer")),
                                "why": str(parsed.get("why") or result["verdict"]["why"]),
                            }
                            result["do"] = str(parsed.get("do") or result["do"])
                            result["dont"] = str(parsed.get("dont") or result["dont"])
                            result["how"] = str(parsed.get("how") or result["how"])
                            result["next_step"] = str(parsed.get("next_step") or result["next_step"])
                            result["generation_source"] = "llm"
                            result["is_fully_personal"] = True
            except Exception as llm_exc:
                logger.info("premium_llm_skipped job_id=%s err=%s", job_id, str(llm_exc)[:200])

            fresh = get_job(db, job_id)
            if fresh is None or fresh.fingerprint != fingerprint:
                if fresh is not None:
                    fresh.status = "stale"
                    db.add(fresh)
                    db.commit()
                return
            complete_job_if_fresh(
                db,
                job,
                expected_fingerprint=fingerprint,
                result_payload=result,
            )
        except Exception as exc:
            logger.exception("premium_job_failed job_id=%s", job_id)
            job2 = get_job(db, job_id)
            if job2 is not None:
                mark_job_failed(db, job2, str(exc)[:500])

    run_with_db(_run)
