# AI Control Tower - Baseline Generation Logic

## Overview

The AI Control Tower uses a sophisticated baseline generation system that combines predefined framework ranges with intelligent document analysis and context-aware selection. This document explains the complete logic behind baseline creation.

## Architecture of Baseline Generation

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Document      │    │    LLM           │    │  Predefined     │
│   Analysis      │───▶│  Categorization  │◄──▶│  Framework      │
│                 │    │                  │    │  Ranges         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   Baseline           │
                    │   Selection Logic    │
                    └──────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   Document Target    │
                    │   Integration        │
                    └──────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   Final Baseline     │
                    │   Generation         │
                    └──────────────────────┘
```

## Predefined Framework Ranges

### Complete Baseline Range Structure

```python
BASELINE_RANGES = {
    "technical_metrics": {
        "trajectory_complexity": {
            "simple_queries": (20, 30),
            "complex_multi_step": (40, 60),
            "highly_specialized": (60, 80)
        },
        "tool_utilization": {
            "well_defined_tools": (80, 95),
            "experimental_tools": (60, 80),
            "unstable_tools": (40, 60)
        }
    },
    "solution_level_kpis": {
        "task_escalation_rate": {
            "simple_tasks": (5, 10),
            "complex_tasks": (15, 25),
            "novel_tasks": (25, 40)
        },
        "first_contact_resolution": {
            "simple_inquiries": (80, 90),
            "complex_issues": (60, 75),
            "technical_problems": (40, 60)
        }
    },
    "learning_safety_metrics": {
        "improvement_velocity": {
            "stable_domain": (3, 5),
            "evolving_domain": (5, 10),
            "new_domain": (10, 20)
        },
        "guardrail_violations": {
            "strict_requirements": (0, 0.5),
            "moderate_requirements": (1, 2),
            "lenient_requirements": (2, 5)
        }
    },
    "business_metrics": {
        "cost_savings": {
            "high_automation_potential": (5, 10),
            "medium_automation": (2, 5),
            "low_automation": (1, 2)
        },
        "customer_satisfaction": {
            "replacement_scenarios": (10, 20),
            "enhancement_scenarios": (5, 15),
            "new_capability_scenarios": (0, 10)
        }
    }
}
```

## Baseline Generation Process

### Step 1: Document Analysis & Categorization

The LLM analyzes agent documentation and assigns categories:

```python
# Input Document Analysis
analysis = {
    "complexity_level": "simple|complex|highly_specialized",
    "domain_type": "stable|evolving|new",
    "tool_maturity": "well_defined|experimental|unstable",
    "task_complexity": "simple|complex|novel",
    "automation_potential": "high|medium|low",
    "scenario_type": "replacement|enhancement|new_capability",
    "performance_targets": {
        "first_contact_resolution": "75%",
        "escalation_rate": "<15%",
        "customer_satisfaction": ">70%"
    }
}
```

### Step 2: Context-Aware Range Selection

Based on categorization, the system selects appropriate predefined ranges:

#### Technical Metrics

**Trajectory Complexity Selection:**
```python
if complexity_level == "simple":
    traj_range = (20, 30)      # Simple queries
elif complexity_level == "highly_specialized":
    traj_range = (60, 80)      # Highly specialized tasks
else:  # complex
    traj_range = (40, 60)      # Complex multi-step tasks
```

**Tool Utilization Selection:**
```python
if tool_maturity == "well_defined":
    tool_range = (80, 95)      # Mature, reliable tools
elif tool_maturity == "unstable":
    tool_range = (40, 60)      # Unreliable tools
else:  # experimental
    tool_range = (60, 80)      # Developing tools
```

#### Solution Level KPIs

**Task Escalation Rate Selection:**
```python
if task_complexity == "simple":
    escalation_range = (5, 10)     # Simple tasks
elif task_complexity == "novel":
    escalation_range = (25, 40)    # Novel tasks
else:  # complex
    escalation_range = (15, 25)    # Complex tasks
```

**First Contact Resolution Selection:**
```python
if task_complexity == "simple":
    fcr_range = (80, 90)           # Simple inquiries
elif "technical" in user_query.lower():
    fcr_range = (40, 60)           # Technical problems
else:
    fcr_range = (60, 75)           # Complex issues
```

### Step 3: Document Target Integration

When explicit targets exist in documentation, they override framework defaults:

#### Priority Logic:
1. **Document Targets** (Highest Priority)
2. **Framework Ranges** (Fallback)
3. **Default Values** (Last Resort)

#### Target Processing Examples:

**First Contact Resolution with Document Target:**
```python
# Document contains: "Expected to resolve 75% of issues on first contact"
performance_targets = {"first_contact_resolution": "75%"}
fcr_target = "75%"

if fcr_target and "%" in fcr_target:
    target_pct = 75.0
    baseline = {
        "min": max(target_pct - 10, 40),    # 65.0 (floor at 40%)
        "max": min(target_pct + 5, 95),     # 80.0 (ceiling at 95%)
        "recommended": target_pct,           # 75.0 (exact target)
        "rationale": "Based on documented target of 75%"
    }
```

**Task Escalation Rate with Document Target:**
```python
# Document contains: "Performance targets: <15% escalation rate"
escalation_target = "<15%"

if escalation_target and "<" in escalation_target:
    target_pct = 15.0
    baseline = {
        "min": max(target_pct - 5, 0),      # 10.0 (floor at 0%)
        "max": target_pct + 3,              # 18.0 (small variance)
        "recommended": target_pct,           # 15.0 (target ceiling)
        "rationale": "Based on documented target of <15%"
    }
```

### Step 4: Business Logic Application

#### Range Validation Rules:
- **Minimum Floors**: Ensure baselines don't go below realistic minimums
- **Maximum Ceilings**: Cap baselines at achievable maximums
- **Variance Logic**: Apply appropriate variance based on metric type

```python
# Example: FCR baseline validation
baseline = {
    "min": max(calculated_min, 40),      # Never below 40% FCR
    "max": min(calculated_max, 95),      # Never above 95% FCR
    "recommended": target_value,
    "rationale": explanation
}
```

## Complete Baseline Generation Examples

### Example 1: Customer Service Agent (With Document Targets)

**Input:**
```
Document: "Expected to resolve 75% of issues on first contact, <15% escalation rate"
Analysis: complexity_level="complex", tool_maturity="well_defined", domain_type="stable"
```

**Generated Baselines:**
```python
{
    "trajectory_complexity": {
        "min": 40, "max": 60, "recommended": 50.0,
        "rationale": "Based on complex complexity level"
    },
    "tool_utilization": {
        "min": 80, "max": 95, "recommended": 87.5,
        "rationale": "Based on well_defined tool maturity"  
    },
    "task_escalation_rate": {
        "min": 10.0, "max": 18.0, "recommended": 15.0,
        "rationale": "Based on documented target of <15%"
    },
    "first_contact_resolution": {
        "min": 65.0, "max": 80.0, "recommended": 75.0,
        "rationale": "Based on documented target of 75%"
    }
}
```

### Example 2: Research Agent (Framework-Only)

**Input:**
```
Document: "Handles complex research tasks in emerging AI domain"
Analysis: complexity_level="highly_specialized", domain_type="new", tool_maturity="experimental"
```

**Generated Baselines:**
```python
{
    "trajectory_complexity": {
        "min": 60, "max": 80, "recommended": 70.0,
        "rationale": "Based on highly_specialized complexity level"
    },
    "tool_utilization": {
        "min": 60, "max": 80, "recommended": 70.0,
        "rationale": "Based on experimental tool maturity"
    },
    "improvement_velocity": {
        "min": 10, "max": 20, "recommended": 15.0,
        "rationale": "Based on new domain characteristics"
    }
}
```

## Fallback Mechanisms

### Error Handling Hierarchy:
1. **Document Target Parsing Failure** → Fall back to framework ranges
2. **Framework Range Missing** → Use default reasonable values
3. **Complete Analysis Failure** → Return error with safe defaults

```python
try:
    target_pct = float(fcr_target.replace("%", ""))
    # Use document target logic
except ValueError:
    # Fall back to framework ranges
    if task_complexity == "simple":
        fcr_range = BASELINE_RANGES["..."]["simple_inquiries"]
    # ... framework selection logic
```

## Key Design Principles

1. **Document Priority**: Explicit targets override framework defaults
2. **Context Sensitivity**: Same metric gets different ranges based on context
3. **Business Logic**: Apply floors, ceilings, and variance rules
4. **Graceful Fallback**: Always provide reasonable baselines even with incomplete data
5. **Traceability**: Every baseline includes rationale explaining its derivation

## Customization Points

### Adding New Baseline Categories:
1. Add new ranges to `BASELINE_RANGES` dictionary
2. Add selection logic in baseline calculation tool
3. Update document analysis to detect relevant characteristics

### Modifying Existing Ranges:
1. Update values in `BASELINE_RANGES` dictionary
2. Ranges are automatically picked up by selection logic
3. No code changes needed for range modifications

This architecture provides a flexible, maintainable system for generating context-aware baselines that can evolve with changing requirements while maintaining consistency and traceability.