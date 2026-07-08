#!/usr/bin/env python3
"""
Content Coverage Audit Script
Проверяет покрытие paragraph templates согласно Content Backbone v1
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Content Backbone patterns (from spec/Content_Backbone_v1.md)
REQUIRED_PATTERNS = {
    "Emotional Patterns": {
        "sub_blocks": [
            "Emotional Baseline",
            "Stress Response",
            "Recovery & Regulation",
            "Growth Levers"
        ],
        "canonical_patterns": [
            "Emotional depth vs surface processing",
            "Emotional containment vs overflow",
            "Response delay vs immediate reaction",
            "Sensitivity to emotional environments",
            "Stress accumulation vs discharge",
            "Self-soothing capacity",
            "Emotional boundaries",
            "Tolerance to uncertainty",
            "Emotional resilience",
            "Suppression vs expression bias"
        ]
    },
    "Relationships": {
        "sub_blocks": [
            "Connection Style",
            "Attachment & Boundaries",
            "Conflict Patterns",
            "Repair & Growth"
        ],
        "canonical_patterns": [
            "Attachment orientation (secure / anxious / avoidant / mixed)",
            "Intimacy pacing",
            "Boundary negotiation",
            "Conflict response style",
            "Dependency vs autonomy tension",
            "Emotional availability",
            "Trust calibration",
            "Projection tendencies"
        ]
    },
    "Career & Responsibility": {
        "sub_blocks": [
            "Career Baseline",
            "Pressure & Burnout",
            "Recovery & Sustainability",
            "Growth Levers"
        ],
        "canonical_patterns": [
            "Responsibility internalization",
            "Authority response",
            "Performance pressure handling",
            "Control vs delegation",
            "Consistency vs burnout risk",
            "Motivation source (internal / external)",
            "Role identification"
        ]
    },
    "Money & Security": {
        "sub_blocks": [
            "Money Baseline",
            "Financial Stress",
            "Stability & Recovery",
            "Growth Levers"
        ],
        "canonical_patterns": [
            "Risk tolerance",
            "Financial control need",
            "Security anchoring",
            "Long-term planning comfort",
            "Scarcity sensitivity",
            "Resource accumulation vs flow"
        ]
    },
    "Life Themes": {
        "sub_blocks": [
            "Life Baseline",
            "Tensions & Blind Spots",
            "Integration & Grounding",
            "Growth Levers"
        ],
        "canonical_patterns": [
            "Meaning orientation",
            "Growth tension",
            "Stability vs change bias",
            "Identity consolidation",
            "Life pacing",
            "Adaptation cycles"
        ]
    },
    "Name Resonance & Numerology": {
        "sub_blocks": [],
        "canonical_patterns": [
            "Life Path Number",
            "Expression/Destiny Number",
            "Soul Urge/Heart's Desire",
            "Personality Number",
            "Maturity/Balance Numbers",
            "Daily/Personal Year Numbers",
            "Name ↔ Astro Alignment"
        ]
    }
}

REQUIRED_LAYERS = ["observation", "interpretation", "context"]
MIN_VARIANTS_PER_TEMPLATE = 3


def load_meta_templates(meta_path: Path) -> List[Dict]:
    """Загружает метаданные templates"""
    templates = []
    with open(meta_path, 'r') as f:
        for line in f:
            if line.strip():
                templates.append(json.loads(line))
    return templates


def load_text_templates(text_path: Path) -> Dict[str, Dict]:
    """Загружает текстовые templates, группирует по paragraph_id"""
    templates = {}
    with open(text_path, 'r') as f:
        for line in f:
            if line.strip():
                template = json.loads(line)
                para_id = template.get('paragraph_id')
                if para_id:
                    templates[para_id] = template
    return templates


def extract_base_id(para_id: str) -> str:
    """Извлекает базовый ID из paragraph_id (убирает -INT, -CON суффиксы)"""
    if para_id.endswith('-INT') or para_id.endswith('-CON'):
        return para_id.rsplit('-', 1)[0]
    return para_id


def audit_coverage(meta_templates: List[Dict], text_templates: Dict[str, Dict]) -> Dict:
    """Проводит аудит покрытия"""
    
    # Группируем templates по базовому ID
    templates_by_base: Dict[str, Dict[str, Dict]] = defaultdict(lambda: {
        "observation": None,
        "interpretation": None,
        "context": None,
        "meta": {}
    })
    
    for meta in meta_templates:
        para_id = meta.get('paragraph_id', '')
        base_id = extract_base_id(para_id)
        layer = meta.get('layer', 'unknown')
        
        if layer in REQUIRED_LAYERS:
            templates_by_base[base_id][layer] = meta
            templates_by_base[base_id]["meta"] = meta  # Сохраняем последнюю мету как референс
    
    # Проверяем наличие текстов
    # Текстовые templates могут иметь базовый ID (без -INT/-CON) или полный ID
    for base_id, layers in templates_by_base.items():
        for layer in REQUIRED_LAYERS:
            meta = layers[layer]
            if meta:
                para_id = meta.get('paragraph_id')
                # Проверяем полный ID и базовый ID
                has_text = False
                variant_count = 0
                
                if para_id in text_templates:
                    text_template = text_templates[para_id]
                    variants = text_template.get('variants', [])
                    has_text = any(
                        v.get('text', '').strip() 
                        for v in variants 
                        if isinstance(v, dict)
                    )
                    variant_count = len(variants)
                elif base_id in text_templates:
                    # Если текстовый template имеет базовый ID, это observation слой
                    if layer == 'observation':
                        text_template = text_templates[base_id]
                        variants = text_template.get('variants', [])
                        has_text = any(
                            v.get('text', '').strip() 
                            for v in variants 
                            if isinstance(v, dict)
                        )
                        variant_count = len(variants)
                
                layers[f"{layer}_has_text"] = has_text
                layers[f"{layer}_variant_count"] = variant_count
            else:
                layers[f"{layer}_has_text"] = False
                layers[f"{layer}_variant_count"] = 0
    
    # Анализ по секциям
    section_stats: Dict[str, Dict] = defaultdict(lambda: {
        "total_base_templates": 0,
        "complete_templates": 0,  # Все 3 слоя + тексты
        "incomplete_templates": 0,
        "missing_observation": 0,
        "missing_interpretation": 0,
        "missing_context": 0,
        "missing_texts": 0,
        "sub_blocks": defaultdict(lambda: {
            "total": 0,
            "complete": 0,
            "incomplete": 0
        })
    })
    
    for base_id, layers in templates_by_base.items():
        meta = layers["meta"]
        section = meta.get('section', 'Unknown')
        sub_block = meta.get('sub_block', 'Unknown')
        
        has_obs = layers.get('observation') is not None
        has_int = layers.get('interpretation') is not None
        has_con = layers.get('context') is not None
        
        obs_has_text = layers.get('observation_has_text', False)
        int_has_text = layers.get('interpretation_has_text', False)
        con_has_text = layers.get('context_has_text', False)
        
        is_complete = has_obs and has_int and has_con and obs_has_text and int_has_text and con_has_text
        
        section_stats[section]["total_base_templates"] += 1
        section_stats[section]["sub_blocks"][sub_block]["total"] += 1
        
        if is_complete:
            section_stats[section]["complete_templates"] += 1
            section_stats[section]["sub_blocks"][sub_block]["complete"] += 1
        else:
            section_stats[section]["incomplete_templates"] += 1
            section_stats[section]["sub_blocks"][sub_block]["incomplete"] += 1
            
            if not has_obs or not obs_has_text:
                section_stats[section]["missing_observation"] += 1
            if not has_int or not int_has_text:
                section_stats[section]["missing_interpretation"] += 1
            if not has_con or not con_has_text:
                section_stats[section]["missing_context"] += 1
            if not (obs_has_text and int_has_text and con_has_text):
                section_stats[section]["missing_texts"] += 1
    
    return {
        "templates_by_base": dict(templates_by_base),
        "section_stats": dict(section_stats),
        "total_base_templates": len(templates_by_base),
        "total_meta_templates": len(meta_templates),
        "total_text_templates": len(text_templates)
    }


def print_report(audit_result: Dict):
    """Выводит отчет аудита"""
    print("=" * 80)
    print("CONTENT COVERAGE AUDIT REPORT")
    print("=" * 80)
    print()
    
    print(f"Total base templates: {audit_result['total_base_templates']}")
    print(f"Total meta entries: {audit_result['total_meta_templates']}")
    print(f"Total text entries: {audit_result['total_text_templates']}")
    print()
    
    print("=" * 80)
    print("SECTION COVERAGE")
    print("=" * 80)
    print()
    
    for section, stats in sorted(audit_result['section_stats'].items()):
        print(f"\n### {section}")
        print(f"  Total base templates: {stats['total_base_templates']}")
        print(f"  Complete (all 3 layers + texts): {stats['complete_templates']}")
        print(f"  Incomplete: {stats['incomplete_templates']}")
        print(f"  Missing observation: {stats['missing_observation']}")
        print(f"  Missing interpretation: {stats['missing_interpretation']}")
        print(f"  Missing context: {stats['missing_context']}")
        print(f"  Missing texts: {stats['missing_texts']}")
        
        completion_rate = (
            stats['complete_templates'] / stats['total_base_templates'] * 100
            if stats['total_base_templates'] > 0 else 0
        )
        print(f"  Completion rate: {completion_rate:.1f}%")
        
        print(f"\n  Sub-blocks:")
        for sub_block, sub_stats in sorted(stats['sub_blocks'].items()):
            sub_completion = (
                sub_stats['complete'] / sub_stats['total'] * 100
                if sub_stats['total'] > 0 else 0
            )
            print(f"    - {sub_block}: {sub_stats['complete']}/{sub_stats['total']} ({sub_completion:.1f}%)")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    # Выявляем приоритетные пробелы
    priorities = []
    for section, stats in audit_result['section_stats'].items():
        if stats['incomplete_templates'] > 0:
            priorities.append({
                'section': section,
                'incomplete': stats['incomplete_templates'],
                'missing_texts': stats['missing_texts'],
                'priority': 'HIGH' if stats['missing_texts'] > stats['incomplete_templates'] * 0.5 else 'MEDIUM'
            })
    
    priorities.sort(key=lambda x: (x['priority'] == 'HIGH', x['missing_texts']), reverse=True)
    
    print("Priority gaps to fill:")
    for i, p in enumerate(priorities[:10], 1):
        print(f"{i}. {p['section']} ({p['priority']})")
        print(f"   - {p['incomplete']} incomplete templates")
        print(f"   - {p['missing_texts']} missing texts")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Fill missing texts for incomplete templates")
    print("2. Create missing observation layers for templates that only have INT/CON")
    print("3. Ensure all templates have 3+ variants per layer")
    print("4. Validate tone and style consistency")
    print("5. Fill i18n (EN + RU) for all templates")


def main():
    content_dir = Path(__file__).parent.parent / "CONTENT"
    meta_path = content_dir / "paragraph_templates_v1.meta.jsonl"
    text_path = content_dir / "paragraph_templates_v1.jsonl"
    
    if not meta_path.exists():
        print(f"Error: {meta_path} not found", file=sys.stderr)
        sys.exit(1)
    
    if not text_path.exists():
        print(f"Error: {text_path} not found", file=sys.stderr)
        sys.exit(1)
    
    print("Loading templates...")
    meta_templates = load_meta_templates(meta_path)
    text_templates = load_text_templates(text_path)
    
    print("Auditing coverage...")
    audit_result = audit_coverage(meta_templates, text_templates)
    
    print_report(audit_result)
    
    # Сохраняем детальный отчет в JSON
    report_path = content_dir / "content_coverage_audit.json"
    with open(report_path, 'w') as f:
        json.dump(audit_result, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()

