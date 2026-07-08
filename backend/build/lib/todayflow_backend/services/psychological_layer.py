"""Psychological layer service: mapping astrology to psychology patterns."""

from __future__ import annotations

from typing import Dict, List, Any
from todayflow_backend.core import models
from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine


class PsychologicalLayerService:
    """Service for generating psychological interpretations from astrological data."""

    def __init__(self, aspect_engine: AspectEngine | None = None):
        """Initialize psychological layer service."""
        self.aspect_engine = aspect_engine or AspectEngine()

    def generate_psychological_patterns(
        self,
        chart_response: astro.ChartResponse,
        internal_model: models.InternalModelSnapshot,
        snapshot: models.ChartSnapshot,
        locale: str | None = None,
    ) -> models.PsychologicalLayer:
        """
        Generate psychological patterns from astrological chart data.
        
        Returns PsychologicalLayer with interpretations for:
        - attachment_needs: attachment style patterns
        - defense_mechanisms: defense reactions (fight/flight/freeze/fawn)
        - cognitive_patterns: cognitive distortions
        - relational_style: relationship patterns (boundaries, dependency/avoidance)
        - emotional_regulation: emotion regulation strategies
        - behavioral_scenarios: behavior loops (trigger → reaction → consequence)
        """
        positions_list = chart_response.positions
        positions = {p["body"]: p for p in positions_list if "body" in p}
        houses = chart_response.houses or {}
        
        # Get aspects for analysis - create lookup by planet pairs
        aspect_response = self.aspect_engine.callouts(positions_list, locale=locale)
        aspects_by_pair: Dict[str, Any] = {}
        for callout in aspect_response.callouts:
            # Create keys like "Moon-Saturn", "Venus-Pluto" for easy lookup
            bodies = callout.bodies.split(" · ")
            if len(bodies) == 2:
                key1 = f"{bodies[0]}-{bodies[1]}"
                key2 = f"{bodies[1]}-{bodies[0]}"
                aspects_by_pair[key1] = callout
                aspects_by_pair[key2] = callout
        
        return models.PsychologicalLayer(
            attachment_needs=self._analyze_attachment_needs(positions, houses, internal_model, aspects_by_pair, snapshot),
            defense_mechanisms=self._analyze_defense_mechanisms(positions, houses, internal_model, aspects_by_pair, snapshot),
            cognitive_patterns=self._analyze_cognitive_patterns(positions, houses, internal_model, aspects_by_pair, snapshot),
            relational_style=self._analyze_relational_style(positions, houses, internal_model, aspects_by_pair, snapshot),
            emotional_regulation=self._analyze_emotional_regulation(positions, houses, internal_model, aspects_by_pair, snapshot),
            behavioral_scenarios=self._analyze_behavioral_scenarios(positions, houses, internal_model, aspects_by_pair, snapshot),
        )

    def _analyze_attachment_needs(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        internal_model: models.InternalModelSnapshot,
        aspects: Dict[str, Any],
        snapshot: models.ChartSnapshot,
    ) -> List[models.PsychologicalPattern]:
        """Analyze attachment needs and security patterns."""
        patterns: List[models.PsychologicalPattern] = []
        indicators: List[str] = []
        
        # Check Moon-Saturn aspects for anxious/avoidant patterns
        moon_saturn_key = "Moon-Saturn"
        if moon_saturn_key in aspects:
            aspect = aspects[moon_saturn_key]
            indicators.append(f"Moon {aspect.aspect_id} Saturn")
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="attachment_needs",
                    title="Anxious or Avoidant Attachment Patterns",
                    description="Moon-Saturn aspects often indicate challenges with emotional security and attachment. This can manifest as either anxious attachment (fear of abandonment) or avoidant attachment (difficulty with emotional closeness).",
                    astro_indicators=indicators.copy(),
                    insights=[
                        "You may struggle with feeling emotionally secure in relationships",
                        "There's a tension between your emotional needs and your ability to trust others",
                        "Early experiences around security and care may have shaped your attachment style"
                    ],
                    recommendations=[
                        "Practice recognizing when fear or avoidance patterns emerge",
                        "Build trust gradually in safe relationships",
                        "Consider therapy or support to work through attachment patterns"
                    ]
                ))
        
        # Check 4th house emphasis - look for planets in 4th house
        house_4_cusp = houses.get("4") or houses.get("4th")
        planets_in_4th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 4:
                planets_in_4th.append(body)
                indicators.append(f"{body} in 4th house")
        
        if planets_in_4th:
            patterns.append(models.PsychologicalPattern(
                pattern_type="attachment_needs",
                title="Security and Home Base Needs",
                description="Planets in the 4th house emphasize your relationship with security, home, and emotional foundations. This indicates a deep need for emotional safety and a stable base.",
                astro_indicators=[f"{body} in 4th house" for body in planets_in_4th],
                insights=[
                    "You have a strong need for emotional security and a stable home environment",
                    "Your sense of safety is deeply connected to your private space and family connections",
                    "You may feel most secure when you have a strong foundation to return to"
                ],
                recommendations=[
                    "Create safe spaces for yourself where you can recharge",
                    "Work on building emotional security from within",
                    "Understand that security comes from stability in your inner world, not just external circumstances"
                ]
            ))
        
        # Check Venus-Pluto aspects for attachment style in relationships (already covered in Venus-Moon, but add for depth)
        venus_pluto_key = "Venus-Pluto"
        if venus_pluto_key in aspects:
            aspect = aspects[venus_pluto_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="attachment_needs",
                    title="Intense and Transformative Attachment Patterns",
                    description="Venus-Pluto aspects create intense attachment patterns with themes of transformation, intensity, and potential power dynamics. Your relationships may have deep, transformative qualities but also intensity and complexity.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Pluto"],
                    insights=[
                        "Your attachments tend to be intense and transformative",
                        "You may experience deep, all-consuming connections",
                        "There can be themes of power, control, or intensity in relationships"
                    ],
                    recommendations=[
                        "Recognize patterns of intensity in your attachments",
                        "Work on maintaining your sense of self in intense relationships",
                        "Learn to create healthy boundaries even in deep connections"
                    ]
                ))
        
        # Check Moon-Venus aspects for attachment style in relationships
        venus_moon_key = "Venus-Moon"
        if venus_moon_key in aspects:
            aspect = aspects[venus_moon_key]
            indicators.append(f"Venus {aspect.aspect_id} Moon")
            if aspect.aspect_id in ["conjunction", "trine", "sextile"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="attachment_needs",
                    title="Harmonious Emotional Connection",
                    description="Venus-Moon aspects create a natural flow between your emotional needs and how you relate to others. You have an innate ability to connect emotionally and create harmony in relationships.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Moon"],
                    insights=[
                        "Your emotional needs and relationship desires are well-aligned",
                        "You naturally seek harmony and emotional connection in your relationships",
                        "You're able to express your needs and respond to others' needs with ease"
                    ],
                    recommendations=[
                        "Trust your ability to create emotional connection",
                        "Allow yourself to be vulnerable in safe relationships",
                        "Use your natural emotional intelligence to deepen connections"
                    ]
                ))
            elif aspect.aspect_id in ["square", "opposition"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="attachment_needs",
                    title="Tension Between Needs and Desires",
                    description="Venus-Moon aspects with tension can create challenges balancing your emotional needs with your relationship desires. There may be conflict between what you need emotionally and what you want in relationships.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Moon"],
                    insights=[
                        "You may struggle to balance your emotional needs with your relationship desires",
                        "There can be tension between what you need for emotional security and what you want in partnership",
                        "You may find yourself choosing relationships that don't fully meet your emotional needs"
                    ],
                    recommendations=[
                        "Get clear on what you truly need emotionally versus what you think you should want",
                        "Practice communicating your emotional needs clearly to partners",
                        "Work on accepting that your needs are valid and important"
                    ]
                ))
        
        # Check Moon-Mars aspects for emotional passion and aggression in attachment
        moon_mars_key = "Moon-Mars"
        if moon_mars_key in aspects:
            aspect = aspects[moon_mars_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="attachment_needs",
                    title="Passionate and Reactive Emotional Attachment",
                    description="Moon-Mars aspects create passionate but potentially reactive attachment patterns. Your emotional connections may be intense and passionate, but there can also be emotional reactivity, conflict, or volatility in close relationships.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Mars"],
                    insights=[
                        "Your emotional attachments have a passionate, energetic quality",
                        "You may experience strong emotional reactions in close relationships",
                        "There can be a tendency toward emotional intensity and potential conflict"
                    ],
                    recommendations=[
                        "Channel passionate energy constructively in relationships",
                        "Practice emotional regulation to avoid reactive patterns",
                        "Learn to express intensity without creating unnecessary conflict"
                    ]
                ))
        
        # Check 12th house emphasis - unconscious attachment patterns
        planets_in_12th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 12:
                planets_in_12th.append(body)
                indicators.append(f"{body} in 12th house")
        
        if planets_in_12th:
            patterns.append(models.PsychologicalPattern(
                pattern_type="attachment_needs",
                title="Unconscious Attachment Patterns",
                description="Planets in the 12th house suggest unconscious patterns in attachment and connection. Your attachment needs may operate beneath conscious awareness, influenced by past experiences, karmic patterns, or unconscious material.",
                astro_indicators=[f"{body} in 12th house" for body in planets_in_12th],
                insights=[
                    "Your attachment patterns may operate at an unconscious level",
                    "Past experiences or karmic patterns may influence your connections",
                    "You may not always be aware of what drives your attachment needs"
                ],
                recommendations=[
                    "Explore your unconscious patterns through therapy or self-reflection",
                    "Pay attention to recurring themes in your relationships",
                    "Work on bringing unconscious patterns into conscious awareness"
                ]
            ))
        
        # Check Neptune in 4th house - idealization/disappointment in home/family
        neptune_pos = positions.get("Neptune")
        if neptune_pos and neptune_pos.get("house") == 4:
            patterns.append(models.PsychologicalPattern(
                pattern_type="attachment_needs",
                title="Idealization and Disappointment in Home and Family",
                description="Neptune in the 4th house suggests idealization of home, family, or security, which can lead to disappointment. Your attachment needs may be shaped by illusions about safety, family, or what security should look like.",
                astro_indicators=["Neptune in 4th house"],
                insights=[
                    "You may idealize home, family, or emotional security",
                    "There can be patterns of disappointment when reality doesn't match ideals",
                    "Your sense of safety may be influenced by fantasies or illusions"
                ],
                recommendations=[
                    "Work on distinguishing between ideals and reality in relationships",
                    "Accept that perfection in security and home life isn't realistic",
                    "Build practical, realistic foundations for emotional security"
                ]
            ))
        
        # Check Neptune in 7th house - idealization/disappointment in relationships
        if neptune_pos and neptune_pos.get("house") == 7:
            patterns.append(models.PsychologicalPattern(
                pattern_type="attachment_needs",
                title="Idealization and Disappointment in Relationships",
                description="Neptune in the 7th house suggests idealization of partners and relationships, which can lead to disappointment. You may have fantasies about perfect partnerships, making it difficult to see partners clearly or accept their humanity.",
                astro_indicators=["Neptune in 7th house"],
                insights=[
                    "You may idealize partners and romantic relationships",
                    "There can be patterns of disappointment when partners don't match your ideals",
                    "You might have difficulty seeing partners clearly or accepting their flaws"
                ],
                recommendations=[
                    "Work on seeing partners as they are, not as you want them to be",
                    "Accept that no relationship or partner is perfect",
                    "Build realistic expectations while maintaining capacity for love and connection"
                ]
            ))
        
        # Check Saturn in 4th house - emotional restrictions in childhood
        saturn_pos = positions.get("Saturn")
        if saturn_pos and saturn_pos.get("house") == 4:
            patterns.append(models.PsychologicalPattern(
                pattern_type="attachment_needs",
                title="Emotional Restrictions and Limitations in Childhood",
                description="Saturn in the 4th house suggests restrictions, limitations, or responsibilities in the home and family environment during childhood. Your attachment patterns may be shaped by early experiences of emotional constraint, responsibility, or lack of emotional security.",
                astro_indicators=["Saturn in 4th house"],
                insights=[
                    "Your early home environment may have involved restrictions or limitations",
                    "You may have learned to be self-reliant or emotionally reserved",
                    "There can be patterns of feeling responsible for others' emotions or security"
                ],
                recommendations=[
                    "Work on recognizing how early restrictions may affect your attachments now",
                    "Practice allowing yourself to receive emotional support and security",
                    "Learn to distinguish between healthy responsibility and over-responsibility"
                ]
            ))
        
        return patterns

    def _analyze_defense_mechanisms(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        internal_model: models.InternalModelSnapshot,
        aspects: Dict[str, Any],
        snapshot: models.ChartSnapshot,
    ) -> List[models.PsychologicalPattern]:
        """Analyze defense mechanisms (fight/flight/freeze/fawn)."""
        patterns: List[models.PsychologicalPattern] = []
        indicators: List[str] = []
        
        # Mars aspects → fight response
        mars_sun_key = "Mars-Sun"
        if mars_sun_key in aspects:
            aspect = aspects[mars_sun_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Mars {aspect.aspect_id} Sun")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Fight Response Patterns",
                    description="Mars-Sun aspects with tension can indicate a tendency toward fight responses when triggered. You may react with assertiveness, anger, or confrontation when you feel threatened.",
                    astro_indicators=[f"Mars {aspect.aspect_id} Sun"],
                    insights=[
                        "You may have a strong reaction to perceived threats or challenges",
                        "Your natural defense is to stand your ground and fight back",
                        "Anger or confrontation may be your go-to response when feeling unsafe"
                    ],
                    recommendations=[
                        "Practice recognizing when fight responses are triggered",
                        "Develop healthy outlets for assertive energy",
                        "Learn to distinguish between healthy boundaries and defensive aggression"
                    ]
                ))
        
        # Pluto aspects → freeze/fawn patterns
        pluto_moon_key = "Pluto-Moon"
        if pluto_moon_key in aspects:
            aspect = aspects[pluto_moon_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Pluto {aspect.aspect_id} Moon")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Freeze and Fawn Response Patterns",
                    description="Pluto-Moon aspects can indicate freeze or fawn responses under stress. You may shut down emotionally or become overly accommodating to avoid conflict or danger.",
                    astro_indicators=[f"Pluto {aspect.aspect_id} Moon"],
                    insights=[
                        "Under threat, you may freeze or become overly accommodating",
                        "You might shut down emotionally to protect yourself",
                        "There can be a pattern of fawning (excessive pleasing) to avoid conflict"
                    ],
                    recommendations=[
                        "Practice recognizing when you're freezing or fawning",
                        "Work on developing healthy boundaries",
                        "Learn to stay present and connected even when feeling threatened"
                    ]
                ))
        
        # Moon-Saturn → flight/freeze
        moon_saturn_key = "Moon-Saturn"
        if moon_saturn_key in aspects:
            aspect = aspects[moon_saturn_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Moon {aspect.aspect_id} Saturn")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Flight or Freeze Response Patterns",
                    description="Moon-Saturn aspects with tension often indicate flight or freeze responses. You may withdraw emotionally or shut down when feeling overwhelmed or unsafe.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Saturn"],
                    insights=[
                        "You may withdraw or shut down when feeling emotionally overwhelmed",
                        "There's a tendency to freeze or flee rather than engage with difficult emotions",
                        "You might isolate yourself as a protective mechanism"
                    ],
                    recommendations=[
                        "Practice staying present with difficult emotions",
                        "Develop safe spaces to process feelings without shutting down",
                        "Work on building emotional capacity gradually"
                    ]
                ))
        
        # Mars-Pluto → fight response (suppression/explosion)
        mars_pluto_key = "Mars-Pluto"
        if mars_pluto_key in aspects:
            aspect = aspects[mars_pluto_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Mars {aspect.aspect_id} Pluto")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Suppression and Explosive Fight Response",
                    description="Mars-Pluto aspects create patterns of suppression followed by explosive reactions. You may suppress anger or aggression until it builds to an explosive point, then react with intense fight responses.",
                    astro_indicators=[f"Mars {aspect.aspect_id} Pluto"],
                    insights=[
                        "You may suppress anger or aggression until it builds to explosive levels",
                        "There's a pattern of controlled suppression followed by intense reactions",
                        "You might have difficulty expressing assertiveness in moderate, healthy ways"
                    ],
                    recommendations=[
                        "Practice expressing assertiveness and boundaries before they build to explosive levels",
                        "Learn to recognize and address anger early, in small doses",
                        "Develop healthy outlets for aggressive energy and intensity"
                    ]
                ))
        
        # Saturn-Neptune → dissociation/freeze (detachment)
        saturn_neptune_key = "Saturn-Neptune"
        if saturn_neptune_key in aspects:
            aspect = aspects[saturn_neptune_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Saturn {aspect.aspect_id} Neptune")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Detachment and Dissociation Patterns",
                    description="Saturn-Neptune aspects create patterns of detachment and dissociation as defense mechanisms. You may disconnect from reality, emotions, or difficult situations as a way to protect yourself from overwhelm.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} Neptune"],
                    insights=[
                        "You may disconnect or dissociate when facing overwhelming situations",
                        "There's a tendency to detach from reality or emotions as protection",
                        "You might use withdrawal or dissociation to cope with stress"
                    ],
                    recommendations=[
                        "Practice grounding techniques to stay present when feeling overwhelmed",
                        "Work on building capacity to tolerate difficult emotions without dissociating",
                        "Consider therapy to address patterns of detachment and dissociation"
                    ]
                ))
        
        # Moon-Chiron → emotional protection through avoidance (fawn)
        moon_chiron_key = "Moon-Chiron"
        if moon_chiron_key in aspects:
            aspect = aspects[moon_chiron_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Moon {aspect.aspect_id} Chiron")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Emotional Protection Through Pleasing (Fawn Response)",
                    description="Moon-Chiron aspects can indicate fawn responses—protecting yourself by being overly accommodating, pleasing, or self-sacrificing. You may avoid conflict or danger by becoming what others need you to be.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Chiron"],
                    insights=[
                        "You may protect yourself by being overly accommodating or pleasing",
                        "There's a tendency to avoid conflict by becoming what others need",
                        "You might sacrifice your own needs to maintain safety or avoid rejection"
                    ],
                    recommendations=[
                        "Practice recognizing when you're fawning to avoid conflict or rejection",
                        "Work on developing healthy boundaries and saying no",
                        "Learn that your needs are just as important as others' needs"
                    ]
                ))
        
        # 12th house emphasis → dissociation patterns
        planets_in_12th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 12:
                planets_in_12th.append(body)
        
        if planets_in_12th:
            neptune_in_12th = any(body == "Neptune" for body in planets_in_12th)
            if neptune_in_12th or "Neptune" in [p.get("body") for p in positions.values() if p.get("house") == 12]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="defense_mechanisms",
                    title="Dissociation and Unconscious Escapism",
                    description="Planets in the 12th house, especially Neptune, suggest dissociation and unconscious escapism as defense mechanisms. You may disconnect from reality, escape into fantasy, or use various forms of dissociation to cope with difficult emotions or situations.",
                    astro_indicators=[f"{body} in 12th house" for body in planets_in_12th],
                    insights=[
                        "You may use dissociation or escapism as primary defense mechanisms",
                        "There's a tendency to disconnect from reality or emotions when overwhelmed",
                        "Unconscious patterns may drive your defensive responses"
                    ],
                    recommendations=[
                        "Work on developing awareness of dissociation patterns",
                        "Practice grounding techniques to stay present with difficult experiences",
                        "Consider therapy to address unconscious patterns and dissociation"
                    ]
                ))
        
        # 8th house + Pluto → suppression and repression
        pluto_pos = positions.get("Pluto")
        planets_in_8th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 8:
                planets_in_8th.append(body)
        
        if pluto_pos and pluto_pos.get("house") == 8:
            patterns.append(models.PsychologicalPattern(
                pattern_type="defense_mechanisms",
                title="Suppression and Repression Patterns",
                description="Pluto in the 8th house suggests patterns of suppression and repression as defense mechanisms. You may deeply suppress difficult emotions, memories, or experiences, keeping them buried in the unconscious where they can create powerful undercurrents.",
                astro_indicators=["Pluto in 8th house"],
                insights=[
                    "You may deeply suppress difficult emotions, memories, or experiences",
                    "There's a tendency to repress material that feels too difficult to process",
                    "Suppressed material may create powerful unconscious undercurrents"
                ],
                recommendations=[
                    "Work on gradually processing suppressed material in safe settings",
                    "Consider therapy to address patterns of repression",
                    "Practice allowing difficult emotions to surface and be processed"
                ]
            ))
        elif planets_in_8th and any(body == "Pluto" for body in planets_in_8th):
            patterns.append(models.PsychologicalPattern(
                pattern_type="defense_mechanisms",
                title="Transformation Through Suppression",
                description="Planets in the 8th house suggest patterns of suppression and transformation. You may use suppression as a defense, but also have capacity for deep transformation when material is eventually processed.",
                astro_indicators=[f"{body} in 8th house" for body in planets_in_8th if body == "Pluto"],
                insights=[
                    "You may suppress difficult material, but also have capacity for transformation",
                    "There's a pattern of keeping things buried until ready to process",
                    "Suppression serves as protection but can also prevent growth"
                ],
                recommendations=[
                    "Work on creating safe spaces to process suppressed material",
                    "Practice allowing transformation through facing what has been suppressed",
                    "Consider therapy to support deep processing and transformation"
                ]
            ))
        
        return patterns

    def _analyze_cognitive_patterns(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        internal_model: models.InternalModelSnapshot,
        aspects: Dict[str, Any],
        snapshot: models.ChartSnapshot,
    ) -> List[models.PsychologicalPattern]:
        """Analyze cognitive distortions and thinking patterns."""
        patterns: List[models.PsychologicalPattern] = []
        indicators: List[str] = []
        
        # Mercury-Saturn → catastrophization
        mercury_saturn_key = "Mercury-Saturn"
        if mercury_saturn_key in aspects:
            aspect = aspects[mercury_saturn_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Mercury {aspect.aspect_id} Saturn")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="cognitive_patterns",
                    title="Tendency Toward Catastrophizing",
                    description="Mercury-Saturn aspects with tension can indicate a tendency to catastrophize or expect the worst. Your thinking may default to negative outcomes or worst-case scenarios.",
                    astro_indicators=[f"Mercury {aspect.aspect_id} Saturn"],
                    insights=[
                        "You may have a tendency to think of worst-case scenarios",
                        "Your mind may automatically jump to negative conclusions",
                        "There's a pattern of expecting problems or obstacles"
                    ],
                    recommendations=[
                        "Practice challenging catastrophic thoughts with evidence",
                        "Develop a habit of considering multiple possible outcomes",
                        "Work on balancing caution with optimism"
                    ]
                ))
        
        # Neptune aspects → black-and-white thinking, idealization
        neptune_mercury_key = "Neptune-Mercury"
        if neptune_mercury_key in aspects:
            aspect = aspects[neptune_mercury_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Neptune {aspect.aspect_id} Mercury")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="cognitive_patterns",
                    title="Black-and-White Thinking Patterns",
                    description="Neptune-Mercury aspects with tension can create black-and-white thinking patterns. You may see things as all good or all bad, with difficulty seeing nuance or gray areas.",
                    astro_indicators=[f"Neptune {aspect.aspect_id} Mercury"],
                    insights=[
                        "You may see situations in extremes—all good or all bad",
                        "There's a tendency to idealize or demonize",
                        "Nuance and complexity can be challenging to hold"
                    ],
                    recommendations=[
                        "Practice noticing when you're thinking in absolutes",
                        "Look for the gray areas and complexity in situations",
                        "Work on holding multiple perspectives simultaneously"
                    ]
                ))
        
        # Saturn aspects → negative filtering
        saturn_sun_key = "Saturn-Sun"
        if saturn_sun_key in aspects:
            aspect = aspects[saturn_sun_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Saturn {aspect.aspect_id} Sun")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="cognitive_patterns",
                    title="Negative Filtering Patterns",
                    description="Saturn-Sun aspects with tension can create negative filtering—focusing on what's wrong or problematic while overlooking positive aspects.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} Sun"],
                    insights=[
                        "You may naturally notice problems or what's not working",
                        "There's a tendency to focus on limitations and obstacles",
                        "Positive aspects of situations may be overlooked"
                    ],
                    recommendations=[
                        "Practice consciously looking for what's working well",
                        "Balance critical thinking with appreciation",
                        "Develop a habit of acknowledging both challenges and strengths"
                    ]
                ))
        
        # Mercury-Pluto → fixation on negative, paranoia
        mercury_pluto_key = "Mercury-Pluto"
        if mercury_pluto_key in aspects:
            aspect = aspects[mercury_pluto_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Mercury {aspect.aspect_id} Pluto")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="cognitive_patterns",
                    title="Fixation on Negative and Suspicious Thinking",
                    description="Mercury-Pluto aspects can create fixation on negative possibilities, suspicious thinking, or paranoia. Your mind may automatically search for hidden dangers, threats, or negative motivations behind situations.",
                    astro_indicators=[f"Mercury {aspect.aspect_id} Pluto"],
                    insights=[
                        "You may fixate on negative possibilities or hidden dangers",
                        "There's a tendency toward suspicious thinking or looking for hidden motivations",
                        "Your mind may automatically search for threats or problems"
                    ],
                    recommendations=[
                        "Practice questioning suspicious thoughts with evidence",
                        "Balance healthy skepticism with trust",
                        "Work on distinguishing between real threats and imagined ones"
                    ]
                ))
        
        # Mercury-Neptune → confusion, illusions (already covered, but add more detail)
        # This is already covered above, but we can enhance it
        
        # 3rd house emphasis → information processing style
        planets_in_3rd = []
        mercury_pos = positions.get("Mercury")
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 3:
                planets_in_3rd.append(body)
        
        if planets_in_3rd or (mercury_pos and mercury_pos.get("house") == 3):
            patterns.append(models.PsychologicalPattern(
                pattern_type="cognitive_patterns",
                title="Active Information Processing and Communication Style",
                description="Planets in the 3rd house, especially Mercury, emphasize your information processing and communication style. You may have an active mind that processes information quickly, enjoys learning, and communicates readily.",
                astro_indicators=[f"{body} in 3rd house" for body in planets_in_3rd] + (["Mercury in 3rd house"] if mercury_pos and mercury_pos.get("house") == 3 else []),
                insights=[
                    "You have an active, information-processing mind",
                    "You may enjoy learning, communication, and mental stimulation",
                    "Your thinking style may be quick, curious, or information-gathering"
                ],
                recommendations=[
                    "Channel your active mind into learning and communication",
                    "Balance information gathering with processing and integration",
                    "Use your communication skills to express and clarify thoughts"
                ]
            ))
        
        # 9th house emphasis → belief systems
        planets_in_9th = []
        jupiter_pos = positions.get("Jupiter")
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 9:
                planets_in_9th.append(body)
        
        if planets_in_9th or (jupiter_pos and jupiter_pos.get("house") == 9):
            patterns.append(models.PsychologicalPattern(
                pattern_type="cognitive_patterns",
                title="Strong Belief Systems and Worldview",
                description="Planets in the 9th house, especially Jupiter, emphasize your belief systems and worldview. You may have strong convictions, a philosophical mind, or patterns of thinking based on beliefs, ideals, or broader perspectives.",
                astro_indicators=[f"{body} in 9th house" for body in planets_in_9th] + (["Jupiter in 9th house"] if jupiter_pos and jupiter_pos.get("house") == 9 else []),
                insights=[
                    "You have strong belief systems and a philosophical worldview",
                    "Your thinking may be influenced by convictions, ideals, or broader perspectives",
                    "You may think in terms of meaning, purpose, or higher principles"
                ],
                recommendations=[
                    "Examine your belief systems and their influence on your thinking",
                    "Balance strong convictions with openness to different perspectives",
                    "Use your philosophical mind to find meaning while staying grounded"
                ]
            ))
        
        # Cognitive distortions: Mercury-Saturn (already covered as catastrophizing)
        # Add more specific cognitive distortions based on other aspects
        
        # Mercury-Jupiter → expansion/overgeneralization
        mercury_jupiter_key = "Mercury-Jupiter"
        if mercury_jupiter_key in aspects:
            aspect = aspects[mercury_jupiter_key]
            if aspect.aspect_id in ["conjunction", "trine", "sextile"]:
                indicators.append(f"Mercury {aspect.aspect_id} Jupiter")
                # This is generally positive, but can lead to overgeneralization
            elif aspect.aspect_id in ["square", "opposition"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="cognitive_patterns",
                    title="Overgeneralization and Expansion of Thoughts",
                    description="Mercury-Jupiter aspects with tension can create overgeneralization—taking one experience and applying it broadly, or expanding thoughts beyond what's warranted. You may think in broad strokes without considering nuances.",
                    astro_indicators=[f"Mercury {aspect.aspect_id} Jupiter"],
                    insights=[
                        "You may overgeneralize—taking one experience and applying it broadly",
                        "There's a tendency to expand thoughts beyond what's warranted",
                        "You might think in broad strokes without considering nuances"
                    ],
                    recommendations=[
                        "Practice looking for nuances and exceptions",
                        "Avoid applying one experience to all situations",
                        "Balance broad thinking with attention to details and specifics"
                    ]
                ))
        
        return patterns

    def _analyze_relational_style(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        internal_model: models.InternalModelSnapshot,
        aspects: Dict[str, Any],
        snapshot: models.ChartSnapshot,
    ) -> List[models.PsychologicalPattern]:
        """Analyze relational style (boundaries, dependency/avoidance)."""
        patterns: List[models.PsychologicalPattern] = []
        indicators: List[str] = []
        
        # Venus-Pluto → boundary issues, dependency, intensity
        venus_pluto_key = "Venus-Pluto"
        if venus_pluto_key in aspects:
            aspect = aspects[venus_pluto_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Venus {aspect.aspect_id} Pluto")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="relational_style",
                    title="Intense Relational Patterns with Boundary Challenges",
                    description="Venus-Pluto aspects create intense relational patterns with challenges around boundaries, dependency, and power dynamics. Relationships may be deep and transformative, but there can be issues with boundaries, control, or excessive dependency.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Pluto"],
                    insights=[
                        "Your relationships tend to be intense and transformative",
                        "There can be challenges with boundaries, control, or dependency",
                        "You may experience power dynamics or intense emotional connections"
                    ],
                    recommendations=[
                        "Work on developing and maintaining healthy boundaries",
                        "Practice recognizing and addressing power dynamics in relationships",
                        "Learn to create space for yourself even in intense connections"
                    ]
                ))
        
        # Venus-Mars → balance of passion and tenderness
        venus_mars_key = "Venus-Mars"
        if venus_mars_key in aspects:
            aspect = aspects[venus_mars_key]
            indicators.append(f"Venus {aspect.aspect_id} Mars")
            if aspect.aspect_id in ["conjunction", "trine", "sextile"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="relational_style",
                    title="Balanced Passion and Tenderness",
                    description="Venus-Mars aspects in harmony create a natural balance between passion and tenderness in relationships. You're able to express both desire and care, creating dynamic and fulfilling connections.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Mars"],
                    insights=[
                        "You naturally balance passion and tenderness in relationships",
                        "You're able to express both desire and care",
                        "Your relationships have dynamic, fulfilling qualities"
                    ],
                    recommendations=[
                        "Trust your natural ability to balance different aspects of connection",
                        "Continue to express both passion and tenderness authentically",
                        "Use your balanced relational style as a strength"
                    ]
                ))
            elif aspect.aspect_id in ["square", "opposition"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="relational_style",
                    title="Tension Between Passion and Tenderness",
                    description="Venus-Mars aspects with tension create challenges balancing passion and tenderness. You may struggle to integrate desire and care, or experience conflict between different aspects of relationships.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Mars"],
                    insights=[
                        "You may struggle to balance passion and tenderness",
                        "There can be tension between desire and care in relationships",
                        "You might experience conflict between different relational needs"
                    ],
                    recommendations=[
                        "Work on integrating different aspects of relationships",
                        "Practice expressing both passion and tenderness",
                        "Learn that desire and care can coexist harmoniously"
                    ]
                ))
        
        # Venus-Uranus → need for freedom vs closeness
        venus_uranus_key = "Venus-Uranus"
        if venus_uranus_key in aspects:
            aspect = aspects[venus_uranus_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Venus {aspect.aspect_id} Uranus")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="relational_style",
                    title="Need for Freedom and Autonomy in Relationships",
                    description="Venus-Uranus aspects create a strong need for freedom and autonomy within relationships. You may struggle with traditional relationship structures, needing space and independence even in close connections.",
                    astro_indicators=[f"Venus {aspect.aspect_id} Uranus"],
                    insights=[
                        "You have a strong need for freedom and autonomy in relationships",
                        "Traditional relationship structures may feel restrictive",
                        "You may need space and independence even in close connections"
                    ],
                    recommendations=[
                        "Communicate your need for freedom and space to partners",
                        "Seek relationships that honor both connection and autonomy",
                        "Work on balancing your need for independence with intimacy"
                    ]
                ))
        
        # 7th house emphasis → relationship focus
        planets_in_7th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 7:
                planets_in_7th.append(body)
                indicators.append(f"{body} in 7th house")
        
        if planets_in_7th:
            patterns.append(models.PsychologicalPattern(
                pattern_type="relational_style",
                title="Strong Focus on Partnerships and Relationships",
                description="Planets in the 7th house emphasize your focus on partnerships and relationships. You may be highly relationship-oriented, seeing yourself through others, or placing significant importance on close connections.",
                astro_indicators=[f"{body} in 7th house" for body in planets_in_7th],
                insights=[
                    "You have a strong focus on partnerships and relationships",
                    "You may see yourself through others or define yourself through connections",
                    "Close relationships are central to your experience"
                ],
                recommendations=[
                    "Maintain your own identity and sense of self within relationships",
                    "Balance relationship focus with individual development",
                    "Use your relationship orientation as a strength while maintaining autonomy"
                ]
            ))
        
        # 11th house emphasis → friendship and social connections
        planets_in_11th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 11:
                planets_in_11th.append(body)
        
        if planets_in_11th:
            patterns.append(models.PsychologicalPattern(
                pattern_type="relational_style",
                title="Friendship and Social Connection Orientation",
                description="Planets in the 11th house emphasize friendships and social connections. You may prioritize friendship-oriented relationships, group connections, or relationships based on shared values and ideals rather than emotional intensity.",
                astro_indicators=[f"{body} in 11th house" for body in planets_in_11th],
                insights=[
                    "You may prioritize friendship-oriented and social connections",
                    "Relationships based on shared values and ideals may be important",
                    "You may prefer less intense, more freedom-based connections"
                ],
                recommendations=[
                    "Honor your preference for friendship-based relationships",
                    "Create relationships that allow for both connection and freedom",
                    "Recognize that different types of relationships serve different needs"
                ]
            ))
        
        # 5th house emphasis → romance, play, creativity in relationships
        planets_in_5th = []
        for body, pos in positions.items():
            body_house = pos.get("house")
            if body_house == 5:
                planets_in_5th.append(body)
        
        if planets_in_5th:
            patterns.append(models.PsychologicalPattern(
                pattern_type="relational_style",
                title="Romantic and Playful Relationship Style",
                description="Planets in the 5th house emphasize romance, play, and creativity in relationships. You may approach relationships with a sense of play, creativity, and romantic excitement, preferring relationships that feel fun and expressive.",
                astro_indicators=[f"{body} in 5th house" for body in planets_in_5th],
                insights=[
                    "You approach relationships with romance, play, and creativity",
                    "You may prefer relationships that feel fun and expressive",
                    "Relationships may serve as outlets for creative self-expression"
                ],
                recommendations=[
                    "Honor your need for play and creativity in relationships",
                    "Find partners who appreciate your romantic and playful style",
                    "Balance fun and play with depth and commitment when needed"
                ]
            ))
        
        # Boundary themes: Saturn-Venus, Saturn in 7th, etc.
        saturn_pos = positions.get("Saturn")
        if saturn_pos and saturn_pos.get("house") == 7:
            patterns.append(models.PsychologicalPattern(
                pattern_type="relational_style",
                title="Structured Boundaries and Commitment in Relationships",
                description="Saturn in the 7th house suggests structured boundaries and commitment in relationships. You may have clear boundaries, take relationships seriously, and approach partnerships with responsibility and structure.",
                astro_indicators=["Saturn in 7th house"],
                insights=[
                    "You have structured boundaries and take relationships seriously",
                    "You approach partnerships with responsibility and commitment",
                    "You may have clear expectations and structures in relationships"
                ],
                recommendations=[
                    "Continue to maintain healthy boundaries while staying open to connection",
                    "Balance structure and commitment with flexibility and spontaneity",
                    "Ensure your boundaries support rather than restrict intimacy"
                ]
            ))
        
        saturn_venus_key = "Saturn-Venus"
        if saturn_venus_key in aspects:
            aspect = aspects[saturn_venus_key]
            if aspect.aspect_id in ["square", "opposition"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="relational_style",
                    title="Challenges with Boundaries and Expression",
                    description="Saturn-Venus aspects with tension can create challenges with boundaries and expression in relationships. You may struggle to express love freely, set healthy boundaries, or balance responsibility with intimacy.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} Venus"],
                    insights=[
                        "You may struggle to express love or affection freely",
                        "There can be challenges with setting healthy boundaries",
                        "You might balance responsibility and intimacy with difficulty"
                    ],
                    recommendations=[
                        "Work on expressing love and affection more freely",
                        "Practice setting boundaries that support rather than restrict connection",
                        "Learn to balance responsibility with intimacy and play"
                    ]
                ))
        
        return patterns

    def _analyze_emotional_regulation(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        internal_model: models.InternalModelSnapshot,
        aspects: Dict[str, Any],
        snapshot: models.ChartSnapshot,
    ) -> List[models.PsychologicalPattern]:
        """Analyze emotional regulation strategies."""
        patterns: List[models.PsychologicalPattern] = []
        indicators: List[str] = []
        
        # Neptune aspects → dissociation patterns
        neptune_moon_key = "Neptune-Moon"
        if neptune_moon_key in aspects:
            aspect = aspects[neptune_moon_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Neptune {aspect.aspect_id} Moon")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Dissociation and Emotional Escape Patterns",
                    description="Neptune-Moon aspects can indicate dissociation as an emotional regulation strategy. You may disconnect from emotions, escape into fantasy, or use substances/activities to avoid feeling.",
                    astro_indicators=[f"Neptune {aspect.aspect_id} Moon"],
                    insights=[
                        "You may disconnect from difficult emotions rather than process them",
                        "There's a tendency to escape or numb emotional pain",
                        "You might use fantasy, distraction, or substances to avoid feeling"
                    ],
                    recommendations=[
                        "Practice staying present with emotions, even difficult ones",
                        "Develop healthy ways to process and regulate emotions",
                        "Consider therapy to work through patterns of dissociation"
                    ]
                ))
        
        # Saturn aspects → suppression patterns
        saturn_moon_key = "Saturn-Moon"
        if saturn_moon_key in aspects:
            aspect = aspects[saturn_moon_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Saturn {aspect.aspect_id} Moon")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Emotional Suppression Patterns",
                    description="Saturn-Moon aspects with tension can indicate emotional suppression as a regulation strategy. You may control, suppress, or deny emotions, believing they should be managed or hidden.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} Moon"],
                    insights=[
                        "You may suppress or control your emotions rather than express them",
                        "There's a tendency to believe emotions should be managed or hidden",
                        "You might feel that emotions are weaknesses to be overcome"
                    ],
                    recommendations=[
                        "Practice allowing emotions to exist without immediate suppression",
                        "Learn that emotions are information, not problems to solve",
                        "Work on creating safe spaces to feel and express emotions"
                    ]
                ))
        
        # Moon in water signs → emotional processing strength
        moon_pos = positions.get("Moon")
        if moon_pos:
            moon_sign = moon_pos.get("sign", "")
            if moon_sign in ["Cancer", "Scorpio", "Pisces"]:
                indicators.append(f"Moon in {moon_sign}")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Strong Emotional Processing Capacity",
                    description="Moon in water signs indicates natural emotional intelligence and depth. You have the capacity to process and understand emotions, though you may also feel them very intensely.",
                    astro_indicators=[f"Moon in {moon_sign}"],
                    insights=[
                        "You have natural emotional intelligence and depth",
                        "You feel emotions intensely and process them deeply",
                        "You may be highly sensitive to emotional undercurrents"
                    ],
                    recommendations=[
                        "Use your emotional intelligence as a strength",
                        "Protect your sensitivity—set boundaries when needed",
                        "Channel your emotional depth into creative or healing pursuits"
                    ]
                ))
        
        # Moon-Mercury → ability to verbalize emotions
        moon_mercury_key = "Moon-Mercury"
        if moon_mercury_key in aspects:
            aspect = aspects[moon_mercury_key]
            if aspect.aspect_id in ["conjunction", "trine", "sextile"]:
                indicators.append(f"Moon {aspect.aspect_id} Mercury")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Ability to Verbalize and Process Emotions",
                    description="Moon-Mercury aspects in harmony create an ability to verbalize and process emotions through language and communication. You can think about feelings, express them, and process emotions through talking or writing.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Mercury"],
                    insights=[
                        "You have the ability to verbalize and think about your emotions",
                        "You can process emotions through communication, talking, or writing",
                        "Expressing feelings through language helps you regulate and understand them"
                    ],
                    recommendations=[
                        "Use talking, writing, or communication to process emotions",
                        "Express feelings verbally to understand and regulate them",
                        "Share your emotional experience with trusted others"
                    ]
                ))
            elif aspect.aspect_id in ["square", "opposition"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Challenges Verbalizing Emotions",
                    description="Moon-Mercury aspects with tension can create challenges verbalizing or thinking about emotions. There may be a disconnect between feelings and words, or difficulty expressing emotions through language.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Mercury"],
                    insights=[
                        "You may struggle to verbalize or think about your emotions",
                        "There can be a disconnect between feelings and words",
                        "You might find it difficult to express emotions through language"
                    ],
                    recommendations=[
                        "Practice putting feelings into words, even if it's challenging",
                        "Use creative or non-verbal ways to express emotions",
                        "Work on bridging the gap between feelings and language"
                    ]
                ))
        
        # Moon-Jupiter → emotional expansion/positivity
        moon_jupiter_key = "Moon-Jupiter"
        if moon_jupiter_key in aspects:
            aspect = aspects[moon_jupiter_key]
            if aspect.aspect_id in ["conjunction", "trine", "sextile"]:
                indicators.append(f"Moon {aspect.aspect_id} Jupiter")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Emotional Expansion and Positive Outlook",
                    description="Moon-Jupiter aspects in harmony create emotional expansion, optimism, and a tendency toward positive emotional regulation. You may naturally look for the positive, find meaning in experiences, or regulate emotions through expansion and optimism.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Jupiter"],
                    insights=[
                        "You tend toward emotional expansion and positive outlook",
                        "You may naturally look for meaning and positivity in experiences",
                        "Your emotional regulation may involve finding the bigger picture or meaning"
                    ],
                    recommendations=[
                        "Use your natural optimism as a resource for emotional regulation",
                        "Balance positivity with acknowledging difficult emotions when needed",
                        "Find meaning in experiences to help process and regulate emotions"
                    ]
                ))
            elif aspect.aspect_id in ["square", "opposition"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Challenges with Emotional Expansion",
                    description="Moon-Jupiter aspects with tension can create challenges with emotional expansion or positivity. You may struggle to find meaning or maintain optimism, or experience tension between emotional needs and ideals.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Jupiter"],
                    insights=[
                        "You may struggle to find meaning or maintain optimism",
                        "There can be tension between emotional needs and ideals",
                        "You might experience difficulty with emotional expansion or positivity"
                    ],
                    recommendations=[
                        "Work on finding small sources of meaning and positivity",
                        "Balance ideals with realistic emotional processing",
                        "Practice emotional regulation that acknowledges both difficulty and potential"
                    ]
                ))
        
        # Moon-Pluto → intense emotional transformation
        moon_pluto_key = "Moon-Pluto"
        if moon_pluto_key in aspects:
            aspect = aspects[moon_pluto_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Moon {aspect.aspect_id} Pluto")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="emotional_regulation",
                    title="Intense Emotional Intensity and Transformation",
                    description="Moon-Pluto aspects create intense emotional experiences and patterns of emotional transformation. Your emotions may be very intense, deep, and transformative, requiring powerful regulation strategies.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Pluto"],
                    insights=[
                        "Your emotions tend to be very intense and transformative",
                        "You experience deep emotional processes that require powerful regulation",
                        "Emotional intensity may require strong coping strategies"
                    ],
                    recommendations=[
                        "Develop strong emotional regulation strategies for intense feelings",
                        "Allow time and space for deep emotional processing",
                        "Work with the transformative power of your emotions rather than suppressing them"
                    ]
                ))
        
        return patterns

    def _analyze_behavioral_scenarios(
        self,
        positions: Dict[str, Dict],
        houses: Dict[str, Any],
        internal_model: models.InternalModelSnapshot,
        aspects: Dict[str, Any],
        snapshot: models.ChartSnapshot,
    ) -> List[models.PsychologicalPattern]:
        """Analyze behavioral scenarios (trigger → reaction → consequence loops)."""
        patterns: List[models.PsychologicalPattern] = []
        indicators: List[str] = []
        
        # Mars-Pluto → reactive patterns
        mars_pluto_key = "Mars-Pluto"
        if mars_pluto_key in aspects:
            aspect = aspects[mars_pluto_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Mars {aspect.aspect_id} Pluto")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="behavioral_scenarios",
                    title="Reactive Behavioral Loops",
                    description="Mars-Pluto aspects create intense reactive patterns. You may experience loops where triggers lead to strong reactions, which create consequences that trigger again. There's potential for explosive or controlling behaviors.",
                    astro_indicators=[f"Mars {aspect.aspect_id} Pluto"],
                    insights=[
                        "You may have intense reactive patterns that create behavioral loops",
                        "Triggers can lead to strong reactions that escalate situations",
                        "There's a tendency toward all-or-nothing responses in conflict"
                    ],
                    recommendations=[
                        "Practice pausing between trigger and reaction",
                        "Develop awareness of your reactive patterns",
                        "Work on breaking cycles by responding rather than reacting"
                    ]
                ))
        
        # Saturn aspects → constraint loops
        saturn_mars_key = "Saturn-Mars"
        if saturn_mars_key in aspects:
            aspect = aspects[saturn_mars_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Saturn {aspect.aspect_id} Mars")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="behavioral_scenarios",
                    title="Constraint and Inhibition Loops",
                    description="Saturn-Mars aspects with tension create patterns of constraint and inhibition. You may experience loops where fear or self-doubt prevents action, which leads to frustration, which increases self-doubt.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} Mars"],
                    insights=[
                        "You may experience patterns where fear or self-doubt inhibits action",
                        "There's a cycle of constraint leading to frustration",
                        "You might hold yourself back and then feel frustrated about it"
                    ],
                    recommendations=[
                        "Practice taking small actions despite fear",
                        "Break the cycle by acting before self-doubt sets in",
                        "Work on building confidence through gradual risk-taking"
                    ]
                ))
        
        # Moon-Mars → emotional reactivity loops
        moon_mars_key = "Moon-Mars"
        if moon_mars_key in aspects:
            aspect = aspects[moon_mars_key]
            if aspect.aspect_id in ["square", "opposition"]:
                indicators.append(f"Moon {aspect.aspect_id} Mars")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="behavioral_scenarios",
                    title="Emotional Reactivity Loops",
                    description="Moon-Mars aspects with tension create emotional reactivity patterns. Emotional triggers can lead to immediate action or reaction, which creates emotional consequences that trigger again.",
                    astro_indicators=[f"Moon {aspect.aspect_id} Mars"],
                    insights=[
                        "You may have strong emotional reactions that lead to immediate action",
                        "There's a pattern of emotions driving behaviors, which create more emotions",
                        "You might act on feelings before processing them"
                    ],
                    recommendations=[
                        "Practice sitting with emotions before acting on them",
                        "Develop a pause between feeling and reacting",
                        "Learn to process emotions through expression rather than action"
                    ]
                ))
        
        # Saturn-Neptune → sabotage patterns
        saturn_neptune_key = "Saturn-Neptune"
        if saturn_neptune_key in aspects:
            aspect = aspects[saturn_neptune_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Saturn {aspect.aspect_id} Neptune")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="behavioral_scenarios",
                    title="Self-Sabotage and Constraint Loops",
                    description="Saturn-Neptune aspects create patterns of self-sabotage, where constraints, limitations, or fear prevent action, which leads to frustration or escape, which reinforces constraints. There can be cycles of self-undermining behaviors.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} Neptune"],
                    insights=[
                        "You may experience patterns of self-sabotage or self-undermining",
                        "Constraints or fear may prevent action, creating frustration",
                        "There can be cycles where limitations reinforce themselves"
                    ],
                    recommendations=[
                        "Identify self-sabotage patterns and their triggers",
                        "Break cycles by taking small actions despite fear or constraints",
                        "Work on building realistic structures that support rather than limit"
                    ]
                ))
        
        # Nodes + Saturn → karmic patterns, repeating lessons
        saturn_node_key = "Saturn-North Node"
        if saturn_node_key in aspects:
            aspect = aspects[saturn_node_key]
            if aspect.aspect_id in ["square", "opposition", "conjunction"]:
                indicators.append(f"Saturn {aspect.aspect_id} North Node")
                patterns.append(models.PsychologicalPattern(
                    pattern_type="behavioral_scenarios",
                    title="Karmic Patterns and Repeating Life Lessons",
                    description="Saturn-Nodes aspects suggest karmic patterns and repeating life lessons. You may experience cycles where similar challenges or themes recur, requiring you to learn specific lessons or work through particular patterns before moving forward.",
                    astro_indicators=[f"Saturn {aspect.aspect_id} North Node"],
                    insights=[
                        "You may experience repeating patterns or life lessons",
                        "Similar challenges or themes may recur until lessons are learned",
                        "There can be karmic cycles that require working through specific patterns"
                    ],
                    recommendations=[
                        "Identify recurring themes and patterns in your life",
                        "Work consciously with karmic lessons rather than repeating them unconsciously",
                        "Use challenges as opportunities for growth and learning"
                    ]
                ))
        
        # Decision-making style: Mercury + Moon integration
        mercury_pos = positions.get("Mercury")
        moon_pos = positions.get("Moon")
        mercury_moon_key = "Mercury-Moon"
        if mercury_pos and moon_pos and mercury_moon_key in aspects:
            aspect = aspects[mercury_moon_key]
            if aspect.aspect_id in ["conjunction", "trine", "sextile"]:
                patterns.append(models.PsychologicalPattern(
                    pattern_type="behavioral_scenarios",
                    title="Integrated Decision-Making Through Feelings and Thoughts",
                    description="The integration of Mercury and Moon suggests decision-making that combines both feelings and thoughts. Your behavioral patterns may involve processing both emotional and rational information before acting.",
                    astro_indicators=[f"Mercury {aspect.aspect_id} Moon"],
                    insights=[
                        "Your decisions integrate both feelings and thoughts",
                        "You process both emotional and rational information before acting",
                        "There's a pattern of considering multiple types of information"
                    ],
                    recommendations=[
                        "Trust your integrated approach to decision-making",
                        "Continue balancing emotional and rational information",
                        "Use both feelings and thoughts as valuable input for decisions"
                    ]
                ))
        
        return patterns

