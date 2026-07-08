"""Psychological compatibility service: conflict styles, boundaries, communication."""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.mapping import InternalModelMapper
from todayflow_backend.services.psychological_layer import PsychologicalLayerService
from todayflow_backend.services.aspects import AspectEngine

_RISING_FOR_PSYCH = frozenset({"Ascendant", "ASC", "rising", "Rising"})


def build_psych_inputs_from_natal_charts(
    chart1: astro.ChartResponse,
    chart2: astro.ChartResponse,
) -> tuple[models.InternalModelSnapshot, models.InternalModelSnapshot, models.ChartSnapshot, models.ChartSnapshot]:
    """Build internal models and chart snapshots for ``analyze_compatibility`` (group, business, etc.)."""

    def _sign(chart: astro.ChartResponse, body_name: str) -> str:
        want = body_name.strip().title()
        for p in chart.positions or []:
            if not isinstance(p, dict) or "body" not in p:
                continue
            if str(p["body"]).strip().title() == want:
                return str(p.get("sign") or "Unknown")
        return "Unknown"

    def _rising(chart: astro.ChartResponse) -> str:
        for p in chart.positions or []:
            if isinstance(p, dict) and p.get("body") in _RISING_FOR_PSYCH:
                return str(p.get("sign") or "Unknown")
        return "Unknown"

    mapper = InternalModelMapper()
    internal_model1 = mapper.map(chart1.model_dump())
    internal_model2 = mapper.map(chart2.model_dump())
    snapshot1 = models.ChartSnapshot(
        sun=_sign(chart1, "Sun"),
        moon=_sign(chart1, "Moon"),
        rising=_rising(chart1),
        houses=chart1.houses,
    )
    snapshot2 = models.ChartSnapshot(
        sun=_sign(chart2, "Sun"),
        moon=_sign(chart2, "Moon"),
        rising=_rising(chart2),
        houses=chart2.houses,
    )
    return internal_model1, internal_model2, snapshot1, snapshot2


class PsychCompatibilityService:
    """Service for analyzing psychological compatibility between two people."""
    
    def __init__(
        self,
        psychological_service: PsychologicalLayerService | None = None,
        aspect_engine: AspectEngine | None = None,
    ):
        self.psychological_service = psychological_service or PsychologicalLayerService()
        self.aspect_engine = aspect_engine or AspectEngine()
    
    async def analyze_compatibility(
        self,
        chart1: astro.ChartResponse,
        chart2: astro.ChartResponse,
        internal_model1: models.InternalModelSnapshot,
        internal_model2: models.InternalModelSnapshot,
        snapshot1: models.ChartSnapshot,
        snapshot2: models.ChartSnapshot,
        locale: str | None = None,
    ) -> models.PsychCompatibilityReport:
        """
        Analyze psychological compatibility between two people.
        
        Returns:
        - Conflict styles
        - Closeness vs autonomy needs
        - Boundary themes
        - Communication recommendations
        - What you do perfectly
        - Where you'll argue
        - What saves you
        - Relationship rules
        """
        # Generate psychological layers for both people
        psych_layer1 = self.psychological_service.generate_psychological_patterns(
            chart1, internal_model1, snapshot1, locale=locale
        )
        psych_layer2 = self.psychological_service.generate_psychological_patterns(
            chart2, internal_model2, snapshot2, locale=locale
        )
        
        # Analyze compatibility
        conflict_styles = self._analyze_conflict_styles(psych_layer1, psych_layer2, locale=locale)
        closeness_autonomy = self._analyze_closeness_autonomy(psych_layer1, psych_layer2, locale=locale)
        boundary_themes = self._analyze_boundary_themes(psych_layer1, psych_layer2, locale=locale)
        communication_recommendations = self._generate_communication_recommendations(
            psych_layer1, psych_layer2, conflict_styles, locale=locale
        )
        
        # Generate summary
        summary = self._generate_compatibility_summary(
            psych_layer1, psych_layer2, conflict_styles, closeness_autonomy, boundary_themes, locale=locale
        )
        
        return models.PsychCompatibilityReport(
            conflict_styles=conflict_styles,
            closeness_autonomy=closeness_autonomy,
            boundary_themes=boundary_themes,
            communication_recommendations=communication_recommendations,
            what_you_do_perfectly=summary["what_you_do_perfectly"],
            where_youll_argue=summary["where_youll_argue"],
            what_saves_you=summary["what_saves_you"],
            relationship_rules=summary["relationship_rules"],
        )
    
    
    def _analyze_conflict_styles(
        self,
        psych1: models.PsychologicalLayer,
        psych2: models.PsychologicalLayer,
        locale: str | None = None,
    ) -> models.ConflictStyleAnalysis:
        """Analyze conflict styles for both people."""
        # Get defense mechanisms (fight/flight/freeze/fawn)
        defenses1 = psych1.defense_mechanisms
        defenses2 = psych2.defense_mechanisms
        
        # Identify primary conflict styles
        style1 = self._identify_conflict_style(defenses1)
        style2 = self._identify_conflict_style(defenses2)
        
        # Analyze compatibility of styles
        compatibility = self._assess_conflict_compatibility(style1, style2)
        
        return models.ConflictStyleAnalysis(
            person1_style=style1,
            person2_style=style2,
            compatibility=compatibility["compatibility"],
            description=compatibility["description"],
            recommendations=compatibility["recommendations"],
        )
    
    def _analyze_closeness_autonomy(
        self,
        psych1: models.PsychologicalLayer,
        psych2: models.PsychologicalLayer,
        locale: str | None = None,
    ) -> models.ClosenessAutonomyAnalysis:
        """Analyze closeness vs autonomy needs."""
        # Get attachment needs
        attachment1 = psych1.attachment_needs
        attachment2 = psych2.attachment_needs
        
        # Identify attachment styles
        style1 = self._identify_attachment_style(attachment1)
        style2 = self._identify_attachment_style(attachment2)
        
        # Analyze needs
        needs1 = self._assess_closeness_needs(attachment1)
        needs2 = self._assess_closeness_needs(attachment2)
        
        # Generate insights
        insights = self._generate_closeness_insights(style1, style2, needs1, needs2)
        
        return models.ClosenessAutonomyAnalysis(
            person1_style=style1,
            person2_style=style2,
            person1_needs=needs1,
            person2_needs=needs2,
            insights=insights,
            recommendations=self._generate_closeness_recommendations(style1, style2, needs1, needs2),
        )
    
    def _analyze_boundary_themes(
        self,
        psych1: models.PsychologicalLayer,
        psych2: models.PsychologicalLayer,
        locale: str | None = None,
    ) -> models.BoundaryThemesAnalysis:
        """Analyze boundary themes (jealousy, control, independence)."""
        # Get relational styles
        relational1 = psych1.relational_style
        relational2 = psych2.relational_style
        
        # Identify boundary patterns
        boundaries1 = self._identify_boundary_patterns(relational1)
        boundaries2 = self._identify_boundary_patterns(relational2)
        
        # Analyze themes
        themes = self._identify_boundary_themes(boundaries1, boundaries2)
        
        return models.BoundaryThemesAnalysis(
            person1_patterns=boundaries1,
            person2_patterns=boundaries2,
            themes=themes,
            recommendations=self._generate_boundary_recommendations(boundaries1, boundaries2),
        )
    
    def _generate_communication_recommendations(
        self,
        psych1: models.PsychologicalLayer,
        psych2: models.PsychologicalLayer,
        conflict_styles: models.ConflictStyleAnalysis,
        locale: str | None = None,
    ) -> List[models.CommunicationTechnique]:
        """Generate specific communication techniques and phrases."""
        techniques = []
        
        # Based on conflict styles
        if conflict_styles.compatibility == "challenging":
            techniques.append(models.CommunicationTechnique(
                technique="Пауза в конфликте" if (locale or "").startswith("ru") else "Time-out protocol",
                description="Если напряжение быстро растет, лучше сделать паузу и вернуться к разговору позже, чем продолжать из перегруза." if (locale or "").startswith("ru") else "When conflict escalates, agree to pause and return after 20 minutes",
                example_phrases=[
                    "Мне нужно немного времени, чтобы переварить это. Давай вернемся к разговору через 20 минут." if (locale or "").startswith("ru") else "I need a moment to process this. Can we pause and come back in 20 minutes?",
                    "Сейчас я перегружаюсь. Давай сделаем паузу и продолжим чуть позже." if (locale or "").startswith("ru") else "I'm feeling overwhelmed. Let's take a break and talk later."
                ],
            ))
        
        # Based on attachment styles
        attachment1 = self._identify_attachment_style(psych1.attachment_needs)
        attachment2 = self._identify_attachment_style(psych2.attachment_needs)
        
        if attachment1 == "anxious" or attachment2 == "anxious":
            techniques.append(models.CommunicationTechnique(
                technique="Подтверждение контакта" if (locale or "").startswith("ru") else "Reassurance protocol",
                description="Короткие регулярные сверки снижают тревогу и помогают не достраивать худшие сценарии в голове." if (locale or "").startswith("ru") else "Regular check-ins to provide emotional security",
                example_phrases=[
                    "Я рядом, и я не исчезаю." if (locale or "").startswith("ru") else "I'm here and I'm not going anywhere.",
                    "Мне важно понять, что ты сейчас чувствуешь. Поможешь мне это услышать?" if (locale or "").startswith("ru") else "I want to understand what you're feeling. Can you help me understand?",
                ],
            ))
        
        if attachment1 == "avoidant" or attachment2 == "avoidant":
            techniques.append(models.CommunicationTechnique(
                technique="Пространство без разрыва" if (locale or "").startswith("ru") else "Space and respect",
                description="Важно уважать потребность в дистанции, не превращая ее в исчезновение из контакта." if (locale or "").startswith("ru") else "Honor need for space while maintaining connection",
                example_phrases=[
                    "Я уважаю твою потребность в пространстве. Когда будет хороший момент вернуться к разговору?" if (locale or "").startswith("ru") else "I respect your need for space. When would be a good time to reconnect?",
                    "Я на связи, когда ты будешь готов(а) говорить." if (locale or "").startswith("ru") else "I'm here when you're ready to talk.",
                ],
            ))
        
        return techniques
    
    def _generate_compatibility_summary(
        self,
        psych1: models.PsychologicalLayer,
        psych2: models.PsychologicalLayer,
        conflict_styles: models.ConflictStyleAnalysis,
        closeness_autonomy: models.ClosenessAutonomyAnalysis,
        boundary_themes: models.BoundaryThemesAnalysis,
        locale: str | None = None,
    ) -> Dict[str, List[str]]:
        """Generate overall compatibility summary."""
        # What you do perfectly
        what_you_do_perfectly = []
        if conflict_styles.compatibility == "harmonious":
            what_you_do_perfectly.append("Вы способны проходить напряжение без взаимного унижения и быстрее возвращаться к диалогу." if (locale or "").startswith("ru") else "Navigate conflicts with mutual respect")
        if closeness_autonomy.insights.get("balanced"):
            what_you_do_perfectly.append("У вас есть шанс сохранить и близость, и личное пространство без ощущения потери связи." if (locale or "").startswith("ru") else "Balance closeness and independence")
        
        # Where you'll argue
        where_youll_argue = []
        if conflict_styles.compatibility == "challenging":
            where_youll_argue.append(
                f"Разные способы реагировать на конфликт: {conflict_styles.person1_style} против {conflict_styles.person2_style}. Именно здесь легко начать спорить не о сути, а о форме."
                if (locale or "").startswith("ru")
                else f"Different conflict styles: {conflict_styles.person1_style} vs {conflict_styles.person2_style}"
            )
        if boundary_themes.themes.get("control"):
            where_youll_argue.append("Границы, свобода и вопрос, кто в паре решает больше." if (locale or "").startswith("ru") else "Boundaries and independence")
        
        # What saves you
        what_saves_you = []
        if conflict_styles.recommendations:
            what_saves_you.append("Готовность замечать, как каждый из вас реагирует под напряжением, и не считать свой стиль единственно правильным." if (locale or "").startswith("ru") else "Willingness to understand each other's conflict styles")
        if closeness_autonomy.recommendations:
            what_saves_you.append("Уважение к разной потребности в близости и дистанции без обесценивания друг друга." if (locale or "").startswith("ru") else "Respect for each other's needs for closeness and space")
        
        # Relationship rules
        relationship_rules = []
        relationship_rules.append("Говорите о потребностях прямо, а не через молчание, исчезновение или давление." if (locale or "").startswith("ru") else "Communicate needs directly, not through behavior")
        relationship_rules.append("Уважайте границы друг друга, даже когда вам не нравится их форма." if (locale or "").startswith("ru") else "Respect each other's boundaries")
        if conflict_styles.compatibility == "challenging":
            relationship_rules.append("В конфликте делайте паузу, если разговор уже идет из перегруза, а не из желания понять друг друга." if (locale or "").startswith("ru") else "Take breaks during conflicts, don't push through")
        
        return {
            "what_you_do_perfectly": what_you_do_perfectly,
            "where_youll_argue": where_youll_argue,
            "what_saves_you": what_saves_you,
            "relationship_rules": relationship_rules,
        }
    
    # Helper methods
    def _identify_conflict_style(self, defenses: List[models.PsychologicalPattern]) -> str:
        """Identify primary conflict style from defense mechanisms."""
        for defense in defenses:
            title_lower = defense.title.lower()
            if "fight" in title_lower or "aggressive" in title_lower:
                return "fight"
            elif "flight" in title_lower or "avoid" in title_lower:
                return "flight"
            elif "freeze" in title_lower:
                return "freeze"
            elif "fawn" in title_lower or "people-please" in title_lower:
                return "fawn"
        return "balanced"
    
    def _identify_attachment_style(self, attachments: List[models.PsychologicalPattern]) -> str:
        """Identify attachment style from attachment needs."""
        for attachment in attachments:
            title_lower = attachment.title.lower()
            if "anxious" in title_lower:
                return "anxious"
            elif "avoidant" in title_lower:
                return "avoidant"
        return "secure"
    
    def _assess_conflict_compatibility(self, style1: str, style2: str) -> Dict[str, Any]:
        """Assess compatibility of conflict styles."""
        if style1 == style2:
            return {
                "compatibility": "harmonious",
                "description": "Похожие реакции на конфликт помогают быстрее считывать друг друга." if style1 and style2 else "Похожие реакции на конфликт помогают быстрее считывать друг друга.",
                "recommendations": [
                    "Вы легче понимаете, почему другой реагирует именно так.",
                    "Но похожесть может создавать и общие слепые зоны, если никто не останавливает привычный сценарий.",
                ],
            }
        elif (style1 == "fight" and style2 == "fawn") or (style1 == "fawn" and style2 == "fight"):
            return {
                "compatibility": "challenging",
                "description": "Противоположные стили легко создают перекос силы и накопленное недовольство.",
                "recommendations": [
                    "Тому, кто давит, важно учиться терпению и слышанию, а не только напору.",
                    "Тому, кто подстраивается, важно возвращать себе право на прямой запрос.",
                    "Создавайте формат, в котором оба голоса звучат одинаково законно.",
                ],
            }
        else:
            return {
                "compatibility": "balanced",
                "description": "Разные стили не мешают связи, если вы умеете замечать триггеры и не требуете одинаковых реакций.",
                "recommendations": ["Изучайте триггеры друг друга", "Уважайте разный способ входить в трудный разговор"],
            }
    
    def _assess_closeness_needs(self, attachments: List[models.PsychologicalPattern]) -> Dict[str, str]:
        """Assess closeness vs autonomy needs."""
        # Simplified assessment
        return {
            "closeness": "medium",
            "autonomy": "medium",
        }
    
    def _generate_closeness_insights(
        self, style1: str, style2: str, needs1: Dict, needs2: Dict
    ) -> Dict[str, Any]:
        """Generate insights about closeness/autonomy balance."""
        return {
            "balanced": style1 == style2 or (style1 == "secure" or style2 == "secure"),
            "tension": style1 == "anxious" and style2 == "avoidant",
        }
    
    def _generate_closeness_recommendations(
        self, style1: str, style2: str, needs1: Dict, needs2: Dict
    ) -> List[str]:
        """Generate recommendations for closeness/autonomy balance."""
        recommendations = []
        if style1 == "anxious" and style2 == "avoidant":
            recommendations.append("Тревожной стороне важно не растворяться в ожидании подтверждения, а возвращать себе опору." )
            recommendations.append("Избегающей стороне важно не исчезать из контакта, а обозначать свое присутствие и сроки возвращения.")
        return recommendations
    
    def _identify_boundary_patterns(self, relational: List[models.PsychologicalPattern]) -> List[str]:
        """Identify boundary patterns from relational style."""
        patterns = []
        for pattern in relational:
            title_lower = pattern.title.lower()
            if "boundary" in title_lower or "independence" in title_lower:
                patterns.append("independence")
            if "dependency" in title_lower or "enmeshment" in title_lower:
                patterns.append("dependency")
        return patterns if patterns else ["balanced"]
    
    def _identify_boundary_themes(self, boundaries1: List[str], boundaries2: List[str]) -> Dict[str, bool]:
        """Identify boundary themes."""
        return {
            "control": "control" in str(boundaries1) or "control" in str(boundaries2),
            "jealousy": "jealousy" in str(boundaries1) or "jealousy" in str(boundaries2),
            "independence": "independence" in boundaries1 or "independence" in boundaries2,
        }
    
    def _generate_boundary_recommendations(self, boundaries1: List[str], boundaries2: List[str]) -> List[str]:
        """Generate boundary recommendations."""
        recommendations = []
        if "independence" in boundaries1 or "independence" in boundaries2:
            recommendations.append("Уважайте потребность друг друга в пространстве, не считывая дистанцию автоматически как холодность или отказ.")
        if "dependency" in boundaries1 or "dependency" in boundaries2:
            recommendations.append("Стройте взаимность так, чтобы поддержка не превращалась в слияние и потерю собственного центра.")
        return recommendations


async def get_psych_compatibility_service() -> PsychCompatibilityService:
    """Dependency function for PsychCompatibilityService."""
    return PsychCompatibilityService()
