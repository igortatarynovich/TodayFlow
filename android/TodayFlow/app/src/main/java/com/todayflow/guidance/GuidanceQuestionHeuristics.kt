package com.todayflow.guidance

import java.util.regex.Pattern

/**
 * Паритет `guidanceSafetyKeywords` и эвристик совместимости из веба (`catalog.ts`, `guidanceResultChrome.ts`).
 * Параметр [isRussian] — как `FlowPracticesChromeLocale == ru`, а не обязательно системная локаль.
 */
object GuidanceSafetyKeywords {
    private val ruNeedles = listOf(
        "суицид",
        "самоубийств",
        "насили",
        "изнасилован",
        "беремен",
        "аборт",
        "онколог",
        "инфаркт",
        "юрист",
        "адвокат",
        "суд ",
        "иск ",
        "ипотек",
        "кредит",
        "долг миллион",
    )

    private val enNeedles = listOf(
        "suicide",
        "suicidal",
        "kill myself",
        "end my life",
        "self-harm",
        "self harm",
        "hurt myself",
        "sexual assault",
        "domestic violence",
        "raped",
        "rapist",
        "pregnancy",
        "pregnant",
        "abortion",
        "miscarriage",
        "cancer",
        "oncology",
        "heart attack",
        "stroke",
        "lawyer",
        "attorney",
        "lawsuit",
        "malpractice",
        "court case",
        "restraining order",
        "foreclosure",
        "mortgage",
        "debt collector",
        "subpoena",
    )

    private val enRegex = listOf(
        Pattern.compile("\\brape\\b", Pattern.CASE_INSENSITIVE),
        Pattern.compile("\\braping\\b", Pattern.CASE_INSENSITIVE),
    )

    @JvmStatic
    fun matches(question: String): Boolean {
        val q = question.lowercase()
        if (ruNeedles.any { q.contains(it) }) return true
        if (enNeedles.any { q.contains(it) }) return true
        return enRegex.any { it.matcher(q).find() }
    }
}

object GuidanceCompatHint {
    private val loveRu = Pattern.compile(
        "любов|партн|близост|чувств|он |она ",
        Pattern.CASE_INSENSITIVE,
    )
    private val loveEn = Pattern.compile(
        "love|partner|relationship|feel|closeness|crush|dating|them |him |her |they ",
        Pattern.CASE_INSENSITIVE,
    )

    @JvmStatic
    fun loveQuestionHeuristic(isRussian: Boolean, question: String): Boolean {
        val p = if (isRussian) loveRu else loveEn
        return p.matcher(question).find()
    }

    @JvmStatic
    fun showCompatHint(isRussian: Boolean, topicId: String?, lane: String, question: String): Boolean {
        if (topicId != "relationships") return false
        if (lane == "love") return true
        return loveQuestionHeuristic(isRussian, question)
    }
}
