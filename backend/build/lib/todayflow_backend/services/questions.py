"""Question-first JTBD routing and answer assembly."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JTBD_LANES = (
    "love",
    "money_career",
    "self",
    "future",
    "decision",
    "daily",
    "state",
    "pattern",
)


@dataclass
class QuestionService:
    """Classifies user intent and assembles a coherent JTBD answer envelope."""

    def answer(
        self,
        question: str,
        *,
        preferred_lane: str | None = None,
        route_lane_hint: str | None = None,
        core_profile: dict[str, Any] | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        clean_question = " ".join((question or "").split()).strip()
        lane = preferred_lane if preferred_lane in JTBD_LANES else self.classify(clean_question)
        profile_ready = bool((core_profile or {}).get("is_ready"))
        learning_context = self._learning_context(core_profile)
        lane_title = self._lane_title(lane, locale=locale)
        answer = self._lane_answer(
            lane,
            clean_question,
            core_profile=core_profile,
            learning_context=learning_context,
            locale=locale,
        )
        route = self._suggested_route(
            lane,
            profile_ready=profile_ready,
            route_lane_hint=route_lane_hint if route_lane_hint in JTBD_LANES else None,
            learning_context=learning_context,
            locale=locale,
        )
        return {
            "question": clean_question,
            "lane": lane,
            "lane_title": lane_title,
            "profile_ready": profile_ready,
            "answer": answer,
            "suggested_route": route,
        }

    def decision_answer(
        self,
        question: str,
        *,
        option_a: str | None = None,
        option_b: str | None = None,
        core_profile: dict[str, Any] | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        clean_question = " ".join((question or "").split()).strip()
        clean_option_a = " ".join((option_a or "").split()).strip() or None
        clean_option_b = " ".join((option_b or "").split()).strip() or None
        profile_ready = bool((core_profile or {}).get("is_ready"))
        profile_hint = self._profile_hint(core_profile)
        learning_context = self._learning_context(core_profile)
        is_en = (locale or "").startswith("en")

        if is_en:
            answer = {
                "window": "This is a decision that should reduce uncertainty, not maximize emotional relief.",
                "risk": "The main risk is not choosing imperfectly; it is staying too long in a draining ambiguity.",
                "best_next_step": "Choose the option that creates faster reality-testing and clearer feedback.",
                "check_before_deciding": "Check whether the option matches your actual capacity, not only your ideal self-image.",
                "revisit_when": "Revisit this decision after one concrete signal, response, or practical result.",
            }
            route = {
                "href": "/today",
                "label": "Open Today",
                "reason": "Use the daily layer to ground the next move before escalating the situation.",
            }
        else:
            answer = {
                "window": "Это решение стоит принимать не ради мгновенного облегчения, а ради снижения неопределенности и возврата управляемости.",
                "risk": "Главный риск сейчас не в том, что выбор будет неидеальным, а в том, что неопределенность начнет съедать ресурс сильнее самого решения.",
                "best_next_step": "Выбери тот вариант, который быстрее дает контакт с реальностью, обратную связь и понятные последствия.",
                "check_before_deciding": "Перед решением проверь, опираешься ли ты на реальные факты и текущую емкость, а не только на страх, надежду или образ идеального исхода.",
                "revisit_when": "Вернись к вопросу после одного конкретного сигнала: ответа, встречи, цифры, дедлайна или факта из реальности.",
            }
            route = {
                "href": "/today",
                "label": "Заземлить решение в Today",
                "reason": "Следующий шаг — не разгонять тревогу, а привязать решение к сегодняшнему ритму и реальности.",
            }

        if clean_option_a and clean_option_b and not is_en:
            answer["best_next_step"] = (
                f"Если выбор между «{clean_option_a}» и «{clean_option_b}», сначала сравни не обещания вариантов, а их реальную цену, обратимость и уровень ясности."
            )
        elif clean_option_a and not is_en:
            answer["check_before_deciding"] = (
                f"Если ты склоняешься к варианту «{clean_option_a}», проверь, не является ли он попыткой быстро снять напряжение без контакта с фактами."
            )

        if profile_hint and not is_en:
            answer["risk"] = f"{answer['risk']} {profile_hint}"

        answer = self._personalize_decision_answer(answer, learning_context=learning_context, locale=locale)
        route = self._personalize_route(route, lane="decision", learning_context=learning_context, locale=locale)

        return {
            "question": clean_question,
            "profile_ready": profile_ready,
            "option_a": clean_option_a,
            "option_b": clean_option_b,
            "answer": answer,
            "suggested_route": route,
        }

    def classify(self, question: str) -> str:
        q = (question or "").lower().strip()
        if not q:
            return "daily"

        score_map = {lane: 0 for lane in JTBD_LANES}

        keyword_map = {
            "love": [
                "он", "она", "чувствует", "верн", "отнош", "партнер", "бывш", "люб", "игнор", "напис", "совместим", "человек мой",
            ],
            "money_career": [
                "работ", "карьер", "доход", "деньг", "финанс", "професс", "оффер", "проект", "бизнес", "зарабат", "монетиз",
            ],
            "self": [
                "кто я", "кто я на самом деле", "мой потенциал", "моя миссия", "мои сильные", "мои слабые", "мой путь", "я на своем месте",
            ],
            "future": [
                "когда", "будет ли", "что дальше", "будущее", "период", "перелом", "переезд", "улучш", "закончится", "начнется",
            ],
            "decision": [
                "стоит ли", "делать или нет", "делать или не делать", "писать или не писать", "уйти", "остаться", "принять", "выбрать", "решение", "рисковать",
            ],
            "daily": [
                "сегодня", "этот день", "на чем сфокусироваться", "как прожить день", "что делать сегодня", "день для", "сегодня лучше",
            ],
            "state": [
                "тяжело", "тревога", "нет энергии", "устал", "выгора", "что со мной", "когда станет легче", "состояние", "сил нет",
            ],
            "pattern": [
                "постоянно", "почему я снова", "одни и те же", "повторя", "паттерн", "не довожу", "выбираю не тех", "токсич", "не ценят",
            ],
        }

        for lane, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in q:
                    score_map[lane] += 2

        if "?" in q:
            score_map["decision"] += 1
            score_map["future"] += 1

        if any(token in q for token in ("сегодня", "день", "сейчас")):
            score_map["daily"] += 2

        ordered = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
        best_lane, best_score = ordered[0]
        return best_lane if best_score > 0 else "self"

    def _lane_title(self, lane: str, *, locale: str | None = None) -> str:
        if (locale or "").startswith("en"):
            return {
                "love": "Relationships",
                "money_career": "Money and Career",
                "self": "Self-Understanding",
                "future": "Future and Timing",
                "decision": "Decision Support",
                "daily": "Today Guidance",
                "state": "State and Stabilization",
                "pattern": "Patterns",
            }.get(lane, "Guidance")
        return {
            "love": "Отношения",
            "money_career": "Деньги и карьера",
            "self": "Самопонимание",
            "future": "Период и будущее",
            "decision": "Решение",
            "daily": "Сегодня",
            "state": "Состояние",
            "pattern": "Паттерны",
        }.get(lane, "Навигация")

    def _profile_hint(self, core_profile: dict[str, Any] | None) -> str:
        if not core_profile:
            return ""
        interpretation = (core_profile.get("interpretation") or {})
        identity = (interpretation.get("identity") or "").strip()
        baseline = core_profile.get("baseline") or {}
        archetype = (baseline.get("archetype_seed") or "").strip()
        if identity:
            return identity
        if archetype:
            return f"Твоя базовая опора сейчас читается через архетип {archetype}."
        return ""

    def _learning_context(self, core_profile: dict[str, Any] | None) -> dict[str, Any]:
        if not core_profile:
            return {}
        living = core_profile.get("living") if isinstance(core_profile.get("living"), dict) else {}
        learning = living.get("learning_context") if isinstance(living, dict) else {}
        return learning if isinstance(learning, dict) else {}

    def _lane_answer(
        self,
        lane: str,
        question: str,
        *,
        core_profile: dict[str, Any] | None,
        learning_context: dict[str, Any] | None = None,
        locale: str | None = None,
    ) -> dict[str, str]:
        profile_hint = self._profile_hint(core_profile)
        is_en = (locale or "").startswith("en")

        if is_en:
            fallback = {
                "clarity": "The question points to a real uncertainty rather than a need for more information.",
                "explanation": "What matters most now is not collecting every signal, but identifying the live tension in this situation.",
                "forecast": "The situation becomes clearer once you stop trying to solve all layers at once.",
                "decision": "Take one concrete step that reduces uncertainty instead of escalating emotion.",
                "today": "Write down the real question in one sentence and choose one practical action for today.",
            }
        else:
            fallback = {
                "clarity": "Вопрос указывает не на нехватку информации, а на живую неопределенность, которую хочется быстрее снять.",
                "explanation": "Сейчас важно не собрать все сигналы сразу, а понять, где находится главный узел напряжения.",
                "forecast": "Ситуация станет понятнее, если перестать решать все слои одновременно и выделить одну главную линию.",
                "decision": "Лучший ход сейчас — действие, которое уменьшает неопределенность, а не усиливает эмоциональный шум.",
                "today": "Сформулируй вопрос одной фразой и выбери один проверяемый шаг на сегодня.",
            }

        lane_specific: dict[str, dict[str, str]] = {
            "love": {
                "clarity": "Сейчас вопрос не только о другом человеке, а о динамике между вами: кто тянется, кто ждет, где связь застряла.",
                "explanation": "В любовных вопросах тревога обычно усиливается там, где есть чувства, но нет ясного сигнала и договоренности.",
                "forecast": "Без прямого прояснения ситуация будет и дальше качаться между надеждой и додумыванием.",
                "decision": "Смотри не на обещание будущего, а на качество контакта, инициативы и повторяющегося поведения.",
                "today": "Сегодня полезнее искать один честный факт о связи, чем строить десятки версий в голове.",
            },
            "money_career": {
                "clarity": "Здесь вопрос упирается в рост, роль, деньги или цену твоих усилий, а не просто в рабочий дискомфорт.",
                "explanation": "Карьера и доход чаще буксуют не из-за отсутствия потенциала, а из-за расфокуса, неверной ставки или устаревшего сценария.",
                "forecast": "Следующий этап роста откроется, когда станет видно, что именно нужно усиливать: навык, позиционирование, ритм или решение.",
                "decision": "Ищи не абстрактный идеальный путь, а ближайшую точку, где можно получить больше ясности, денег или рычага.",
                "today": "Сегодня выбери одну финансовую или карьерную тему и прими по ней одно проверяемое решение.",
            },
            "self": {
                "clarity": "Этот вопрос про структуру личности и повторяющийся внутренний способ реагировать на жизнь.",
                "explanation": "Когда человек не понимает свой базовый ритм, сильные стороны и уязвимости, даже правильные решения начинают ощущаться чужими.",
                "forecast": "Чем точнее ты увидишь собственный устойчивый паттерн, тем меньше будет ощущения, что жизнь происходит мимо тебя.",
                "decision": "Сейчас полезнее не менять себя силой, а назвать свой реальный способ действовать, чувствовать и восстанавливаться.",
                "today": "Сегодня отмечай не ошибки, а то, где твоя естественная сила уже проявляется без дополнительного нажима.",
            },
            "future": {
                "clarity": "Вопрос про будущее обычно означает, что тебе нужна не магическая гарантия, а ощущение времени и окна для действия.",
                "explanation": "Неопределенность особенно тяжела, когда неясно, ускоряться ли сейчас или подождать разворота периода.",
                "forecast": "Ближайшее будущее станет читабельнее, если смотреть не на всю дальнюю перспективу, а на следующий поворот периода.",
                "decision": "Полезно отделить то, что созревает само, от того, что требует твоего прямого шага уже сейчас.",
                "today": "Сегодня определи, что в твоем вопросе относится к срокам, а что зависит от текущего действия.",
            },
            "decision": {
                "clarity": "Это не просто вопрос выбора, а попытка снять внутренний раскол между импульсом, страхом ошибки и реальностью.",
                "explanation": "Самое тяжелое в решениях — не сам выбор, а риск прожить последствия и взять на себя ясную позицию.",
                "forecast": "Если откладывать решение слишком долго, цена неопределенности начнет расти быстрее, чем риск самого действия.",
                "decision": "Лучшее решение сейчас — то, которое дает больше реальности, обратной связи и управляемости, а не больше иллюзии контроля.",
                "today": "Сегодня сузь выбор до двух реальных вариантов и проверь, какой из них уменьшает шум, а не только обещает облегчение.",
            },
            "daily": {
                "clarity": "Сейчас тебе нужен не большой жизненный ответ, а рабочая настройка именно на этот день.",
                "explanation": "Когда день не собран в один фокус, энергия уходит в реактивность, разрывы внимания и лишние решения.",
                "forecast": "День пройдет лучше, если заранее понять, где действовать, где не форсировать и где беречь контакт с собой.",
                "decision": "Главная задача дня — выбрать один основной ритм: действие, удержание, пауза, разговор или завершение.",
                "today": "Сегодня ориентируйся на один главный фокус и не принимай второстепенные решения в рассеянном состоянии.",
            },
            "state": {
                "clarity": "Это вопрос не только про эмоцию, а про перегрузку системы: тело, внимание и внутренний ресурс уже подают сигнал.",
                "explanation": "Тяжелое состояние часто усиливается, когда человек пытается сначала все объяснить, а не сначала стабилизироваться.",
                "forecast": "Станет легче, когда нагрузка снизится до проживаемого объема и появится один понятный контур опоры.",
                "decision": "Сейчас не нужно требовать от себя дальних решений. Сначала верни управляемость состоянию.",
                "today": "Сегодня полезнее сократить лишнее, чем выжимать из себя дополнительную эффективность.",
            },
            "pattern": {
                "clarity": "Вопрос указывает на повторяющийся сценарий, а не на случайную единичную ситуацию.",
                "explanation": "Повторение возникает там, где один и тот же внутренний способ защиты каждый раз приводит к похожему результату.",
                "forecast": "Сценарий начнет меняться, когда ты увидишь не только итог, но и ранний момент, в котором паттерн запускается.",
                "decision": "Сейчас важнее всего назвать повторяющуюся связку: триггер, привычную реакцию и цену этой реакции.",
                "today": "Сегодня замечай самый первый сигнал паттерна, а не только момент, когда ситуация уже вышла из-под контроля.",
            },
        }

        base = lane_specific.get(lane, fallback)
        if profile_hint and not is_en:
            base = {
                **base,
                "explanation": f"{base['explanation']} {profile_hint}",
            }

        return self._personalize_lane_answer(base, lane=lane, learning_context=learning_context, locale=locale)

    def _suggested_route(
        self,
        lane: str,
        *,
        profile_ready: bool,
        route_lane_hint: str | None = None,
        learning_context: dict[str, Any] | None = None,
        locale: str | None = None,
    ) -> dict[str, str]:
        is_en = (locale or "").startswith("en")
        if not profile_ready and lane in {"love", "self", "future", "money_career"}:
            if is_en:
                return {
                    "href": "/profile?setup=core",
                    "label": "Set up profile",
                    "reason": "A ready profile makes the next answer more personal and precise.",
                }
            return {
                "href": "/profile?setup=core",
                "label": "Собрать профиль",
                "reason": "Готовый профиль даст следующий ответ точнее и глубже.",
            }

        routes = {
            "love": {
                "href": "/compatibility",
                "label": "Открыть совместимость" if not is_en else "Open compatibility",
                "reason": "Это лучший следующий слой для вопросов про чувства, динамику и будущее связи." if not is_en else "Best next layer for feelings, dynamics, and relationship future.",
            },
            "money_career": {
                "href": "/profile",
                "label": "Открыть профиль" if not is_en else "Open profile",
                "reason": "Следующий шаг — смотреть вопрос через твою роль, сильные стороны, деньги и рабочую реализацию внутри общей карты жизни." if not is_en else "Next step: read the question through your role, strengths, money, and work path inside the broader life map.",
            },
            "self": {
                "href": "/profile",
                "label": "Открыть профиль" if not is_en else "Open profile",
                "reason": "Это главный слой для устойчивых паттернов, сильных сторон и жизненной карты." if not is_en else "Main layer for stable patterns, strengths, and the personal map.",
            },
            "future": {
                "href": "/today",
                "label": "Открыть Today" if not is_en else "Open Today",
                "reason": "Следующий шаг — не уходить в абстрактный прогноз, а проверить, что уже требует внимания и действия сейчас." if not is_en else "Next step: stay with what already needs attention and action now instead of abstract forecasting.",
            },
            "decision": {
                "href": "/questions/decision",
                "label": "Открыть Decision OS" if not is_en else "Open Decision OS",
                "reason": "Это отдельный слой для решений: окно выбора, риск ошибки, следующий шаг и момент пересмотра." if not is_en else "Dedicated decision layer: decision window, risk, next step, and revisit point.",
            },
            "daily": {
                "href": "/today",
                "label": "Открыть Today" if not is_en else "Open Today",
                "reason": "Это лучший следующий экран для фокуса дня, рисков и главного ритма." if not is_en else "Best next screen for daily focus, risks, and rhythm.",
            },
            "state": {
                "href": "/practices",
                "label": "Открыть практики" if not is_en else "Open practices",
                "reason": "Следующий шаг — не углублять анализ, а вернуть телу и вниманию опору." if not is_en else "Next step: restore support before deepening analysis.",
            },
            "pattern": {
                "href": "/profile",
                "label": "Открыть карту паттернов" if not is_en else "Open pattern map",
                "reason": "Повторяющиеся сценарии лучше всего раскрываются через устойчивую карту личности." if not is_en else "Repeating scenarios are best understood through the stable personal map.",
            },
        }
        route = routes.get(lane, routes["daily"])
        if route_lane_hint == lane:
            biased_routes = {
                "love": {
                    "href": "/questions/love",
                    "label": "Открыть Love OS" if not is_en else "Open Love OS",
                    "reason": "Эта линия у тебя повторяется чаще, поэтому следующий шаг можно углубить прямо в отдельном любовном question-flow, не расплескивая фокус." if not is_en else "This line repeats most often for you, so the next step can deepen inside the dedicated love question flow.",
                },
                "money_career": {
                    "href": "/questions/money-career",
                    "label": "Открыть Money / Career OS" if not is_en else "Open Money / Career OS",
                    "reason": "Эта тема у тебя уже активна, поэтому следующий шаг лучше держать внутри отдельного money/career flow и продолжить тот же разговор глубже." if not is_en else "This theme is already active for you, so the next step is better kept inside the dedicated money/career flow.",
                },
                "state": {
                    "href": "/questions/state",
                    "label": "Открыть State OS" if not is_en else "Open State OS",
                    "reason": "Эта линия у тебя повторяется, поэтому полезнее углубить вопрос прямо в state-flow и удержать фокус на стабилизации, а не разбрасываться по модулям." if not is_en else "This line repeats for you, so it is better to deepen inside the state flow and keep focus on stabilization.",
                },
                "pattern": {
                    "href": "/questions/pattern",
                    "label": "Открыть Pattern OS" if not is_en else "Open Pattern OS",
                    "reason": "Эта линия у тебя уже звучит как повторяющийся узел, поэтому следующий шаг лучше делать внутри pattern-flow, где легче держать сценарий целиком." if not is_en else "This line already sounds like a repeating knot, so the next step is better inside the pattern flow.",
                },
                "decision": {
                    "href": "/questions/decision",
                    "label": "Открыть Decision OS" if not is_en else "Open Decision OS",
                    "reason": "Так как эта тема у тебя уже повторяется, следующий шаг лучше делать в отдельном Decision OS и быстрее сужать выбор до проверяемого хода." if not is_en else "Since this theme already repeats for you, the next step is better inside Decision OS.",
                },
            }
            route = biased_routes.get(lane, route)
        return self._personalize_route(route, lane=lane, learning_context=learning_context, locale=locale)

    def _personalize_lane_answer(
        self,
        base: dict[str, str],
        *,
        lane: str,
        learning_context: dict[str, Any] | None,
        locale: str | None = None,
    ) -> dict[str, str]:
        if (locale or "").startswith("en"):
            return base

        learning = learning_context or {}
        response_style = str(learning.get("response_style") or "").lower()
        support_style = str(learning.get("support_style") or "").lower()
        signal_bias = str(learning.get("signal_bias") or "").lower()
        diary_topics = [str(item).lower() for item in (learning.get("dominant_diary_topics") or []) if item]

        personalized = dict(base)

        if "ясности" in response_style or signal_bias == "needs_clarity":
            personalized["clarity"] = f"{personalized['clarity']} Сейчас особенно важно сократить вопрос до одного проверяемого узла."
            personalized["decision"] = f"{personalized['decision']} Полезнее выбрать ход, который быстрее даст факт, ответ или наблюдаемую реакцию."

        if "конкретный следующий шаг" in response_style or "конкретных решений" in support_style:
            personalized["today"] = f"{personalized['today']} Лучше, если этот шаг можно проверить уже сегодня по факту, цифре или ответу."

        if signal_bias == "needs_closure":
            personalized["forecast"] = f"{personalized['forecast']} Сейчас лучше работают завершение, сужение фронта и один доведенный контур."

        if lane in {"love", "state"} and any(topic in {"отношения", "семья"} for topic in diary_topics):
            personalized["explanation"] = f"{personalized['explanation']} Здесь важно смотреть не только на факты, но и на качество контакта, атмосферу и отклик другого человека."

        if lane in {"money_career", "decision"} and any(topic in {"работа", "деньги"} for topic in diary_topics):
            personalized["today"] = f"{personalized['today']} Хороший ориентир здесь: цена шага, его обратимость и ближайший измеримый результат."

        return personalized

    def _personalize_decision_answer(
        self,
        answer: dict[str, str],
        *,
        learning_context: dict[str, Any] | None,
        locale: str | None = None,
    ) -> dict[str, str]:
        if (locale or "").startswith("en"):
            return answer

        learning = learning_context or {}
        response_style = str(learning.get("response_style") or "").lower()
        support_style = str(learning.get("support_style") or "").lower()
        signal_bias = str(learning.get("signal_bias") or "").lower()
        diary_topics = [str(item).lower() for item in (learning.get("dominant_diary_topics") or []) if item]

        personalized = dict(answer)

        if "ясности" in response_style or signal_bias == "needs_clarity":
            personalized["check_before_deciding"] = (
                f"{personalized['check_before_deciding']} Перед выбором назови один критерий, по которому поймешь, что решение сработало."
            )

        if signal_bias == "needs_closure":
            personalized["best_next_step"] = (
                f"{personalized['best_next_step']} Сейчас не нужно открывать лишние сценарии, если можно закрыть один незавершенный контур."
            )

        if "конкретных решений" in support_style or any(topic in {"работа", "деньги"} for topic in diary_topics):
            personalized["revisit_when"] = (
                "Вернись к вопросу после одного конкретного результата: цифры, письма, ответа, дедлайна или факта из реальности."
            )

        return personalized

    def _personalize_route(
        self,
        route: dict[str, str],
        *,
        lane: str,
        learning_context: dict[str, Any] | None,
        locale: str | None = None,
    ) -> dict[str, str]:
        if (locale or "").startswith("en"):
            return route

        learning = learning_context or {}
        dominant_routes = [str(item).strip() for item in (learning.get("dominant_routes") or []) if item]
        quality_memory = learning.get("quality_memory") if isinstance(learning.get("quality_memory"), dict) else {}
        bridge_memory = learning.get("bridge_memory") if isinstance(learning.get("bridge_memory"), dict) else {}
        _bp = quality_memory.get("best_patterns") if isinstance(quality_memory, dict) else None
        best_patterns: list[Any] = _bp if isinstance(_bp, list) else []
        best_surfaces = {
            str(item.get("surface") or "").strip()
            for item in best_patterns
            if isinstance(item, dict) and item.get("surface")
        }
        preferred_bridge_targets = [
            str(item.get("target") or "").strip()
            for item in (bridge_memory.get("preferred_targets") or [])
            if isinstance(item, dict) and item.get("target")
        ]

        personalized = dict(route)

        if lane in {"daily", "future"} and ("today" in preferred_bridge_targets or "/today" in dominant_routes):
            personalized["reason"] = "Следующий шаг лучше сделать внутри Today: там проще собрать реальность дня, главный риск и ближайшее действие."
        elif lane in {"self", "money_career", "pattern"} and "/profile" in dominant_routes:
            personalized["reason"] = "Следующий слой лучше читать через Profile: там вопрос быстрее связывается с твоими устойчивыми паттернами и картой жизни."
        elif lane == "love" and ("compatibility" in preferred_bridge_targets or "/compatibility" in dominant_routes):
            personalized["reason"] = "Следующий шаг лучше делать через совместимость: там быстрее становится видно реальную динамику между людьми, а не только тревогу вопроса."
        elif lane == "money_career" and "compatibility" in preferred_bridge_targets:
            personalized["reason"] = "Следующий шаг лучше делать через business-совместимость: этот мост уже показывает, что рабочие роли и динамика дают тебе больше ясности, чем абстрактный совет."
        elif lane in {"state", "pattern"} and "practices" in preferred_bridge_targets:
            personalized["reason"] = "Следующий шаг лучше переводить в практики: этот мост уже показывает, что тебе помогает не только понимать вопрос, но и менять состояние или сценарий действием."
        elif lane == "decision" and ("decision" in preferred_bridge_targets or "questions:decision_os" in best_surfaces):
            personalized["reason"] = "Следующий шаг лучше сделать через Decision OS: этот формат быстрее сужает выбор до проверяемого следующего хода."

        return personalized


_QUESTION_SERVICE = QuestionService()


def get_question_service() -> QuestionService:
    return _QUESTION_SERVICE
