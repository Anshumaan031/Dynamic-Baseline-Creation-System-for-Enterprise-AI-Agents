"""
AI Control Tower - Offline Demo

This demo shows the AI Control Tower functionality without requiring API keys.
It demonstrates the complete baseline generation process using local logic.
"""

from document_processor import extract_agent_specifications, process_document_for_baseline_analysis
import json
from datetime import datetime

# Baseline ranges from pdp.md
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

def analyze_document_offline(document_content, user_query):
    """Analyze document without API calls"""
    
    # Extract specifications using local processing
    specs = extract_agent_specifications(document_content)
    
    # Determine analysis parameters based on content
    content_lower = document_content.lower()
    
    # Assess complexity
    if any(word in content_lower for word in ["simple", "basic", "routine", "faq"]):
        complexity_level = "simple"
    elif any(word in content_lower for word in ["specialized", "expert", "advanced", "complex technical"]):
        complexity_level = "highly_specialized"
    else:
        complexity_level = "complex"
    
    # Assess domain maturity
    if any(word in content_lower for word in ["established", "mature", "stable", "proven"]):
        domain_type = "stable"
    elif any(word in content_lower for word in ["new", "novel", "emerging", "experimental"]):
        domain_type = "new"
    else:
        domain_type = "evolving"
    
    # Assess tool maturity
    if any(word in content_lower for word in ["well-defined", "stable", "reliable", "mature"]):
        tool_maturity = "well_defined"
    elif any(word in content_lower for word in ["experimental", "beta", "unstable", "developing"]):
        tool_maturity = "experimental"
    else:
        tool_maturity = "experimental"
    
    # Determine task complexity
    if "technical support" in content_lower or "technical issues" in content_lower:
        task_complexity = "complex"
    elif any(word in content_lower for word in ["novel", "specialized", "expert"]):
        task_complexity = "novel"
    elif any(word in content_lower for word in ["simple", "basic", "routine"]):
        task_complexity = "simple"
    else:
        task_complexity = "complex"
    
    # Assess automation potential
    if complexity_level == "simple" and tool_maturity == "well_defined":
        automation_potential = "high"
    elif complexity_level == "highly_specialized":
        automation_potential = "medium"
    else:
        automation_potential = "medium"
    
    # Determine scenario type
    if any(word in content_lower for word in ["replace", "replacement"]):
        scenario_type = "replacement"
    elif any(word in content_lower for word in ["new capability", "new feature"]):
        scenario_type = "new_capability"
    else:
        scenario_type = "enhancement"
    
    return {
        "agent_capabilities": specs["capabilities"][:5],  # Top 5
        "performance_characteristics": specs["performance_targets"][:3],  # Top 3
        "technical_constraints": specs["tools"],
        "business_objectives": ["Improve efficiency", "Reduce costs", "Enhance customer experience"],
        "complexity_level": complexity_level,
        "domain_type": domain_type,
        "tool_maturity": tool_maturity,
        "task_complexity": task_complexity,
        "automation_potential": automation_potential,
        "scenario_type": scenario_type
    }

def calculate_baselines_offline(analysis):
    """Calculate baselines using local logic"""
    
    baselines = {}
    
    # Technical Metrics
    complexity_level = analysis.get("complexity_level", "complex")
    tool_maturity = analysis.get("tool_maturity", "experimental")
    
    # Trajectory Complexity
    if complexity_level == "simple":
        traj_range = BASELINE_RANGES["technical_metrics"]["trajectory_complexity"]["simple_queries"]
    elif complexity_level == "highly_specialized":
        traj_range = BASELINE_RANGES["technical_metrics"]["trajectory_complexity"]["highly_specialized"]
    else:
        traj_range = BASELINE_RANGES["technical_metrics"]["trajectory_complexity"]["complex_multi_step"]
        
    baselines["trajectory_complexity"] = {
        "min": traj_range[0],
        "max": traj_range[1],
        "recommended": (traj_range[0] + traj_range[1]) / 2,
        "rationale": f"Based on {complexity_level} complexity level"
    }
    
    # Tool Utilization
    if tool_maturity == "well_defined":
        tool_range = BASELINE_RANGES["technical_metrics"]["tool_utilization"]["well_defined_tools"]
    elif tool_maturity == "unstable":
        tool_range = BASELINE_RANGES["technical_metrics"]["tool_utilization"]["unstable_tools"]
    else:
        tool_range = BASELINE_RANGES["technical_metrics"]["tool_utilization"]["experimental_tools"]
        
    baselines["tool_utilization"] = {
        "min": tool_range[0],
        "max": tool_range[1],
        "recommended": (tool_range[0] + tool_range[1]) / 2,
        "rationale": f"Based on {tool_maturity} tool maturity"
    }
    
    # Solution Level KPIs
    task_complexity = analysis.get("task_complexity", "complex")
    
    # Task Escalation Rate
    if task_complexity == "simple":
        escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["simple_tasks"]
    elif task_complexity == "novel":
        escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["novel_tasks"]
    else:
        escalation_range = BASELINE_RANGES["solution_level_kpis"]["task_escalation_rate"]["complex_tasks"]
        
    baselines["task_escalation_rate"] = {
        "min": escalation_range[0],
        "max": escalation_range[1],
        "recommended": (escalation_range[0] + escalation_range[1]) / 2,
        "rationale": f"Based on {task_complexity} task complexity"
    }
    
    # First Contact Resolution
    if task_complexity == "simple":
        fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["simple_inquiries"]
    elif "technical" in str(analysis).lower():
        fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["technical_problems"]
    else:
        fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["complex_issues"]
        
    baselines["first_contact_resolution"] = {
        "min": fcr_range[0],
        "max": fcr_range[1], 
        "recommended": (fcr_range[0] + fcr_range[1]) / 2,
        "rationale": f"Based on technical support requirements"
    }
    
    # Learning and Safety Metrics
    domain_type = analysis.get("domain_type", "evolving")
    
    # Improvement Velocity
    if domain_type == "stable":
        improvement_range = BASELINE_RANGES["learning_safety_metrics"]["improvement_velocity"]["stable_domain"]
    elif domain_type == "new":
        improvement_range = BASELINE_RANGES["learning_safety_metrics"]["improvement_velocity"]["new_domain"]
    else:
        improvement_range = BASELINE_RANGES["learning_safety_metrics"]["improvement_velocity"]["evolving_domain"]
        
    baselines["improvement_velocity"] = {
        "min": improvement_range[0],
        "max": improvement_range[1],
        "recommended": (improvement_range[0] + improvement_range[1]) / 2,
        "rationale": f"Based on {domain_type} domain characteristics"
    }
    
    # Guardrail Violations (assume moderate requirements for technical support)
    guardrail_range = BASELINE_RANGES["learning_safety_metrics"]["guardrail_violations"]["moderate_requirements"]
    baselines["guardrail_violations"] = {
        "min": guardrail_range[0],
        "max": guardrail_range[1],
        "recommended": (guardrail_range[0] + guardrail_range[1]) / 2,
        "rationale": "Based on moderate safety requirements for customer service"
    }
    
    # Business Metrics
    automation_potential = analysis.get("automation_potential", "medium")
    scenario_type = analysis.get("scenario_type", "enhancement")
    
    # Cost Savings
    if automation_potential == "high":
        cost_range = BASELINE_RANGES["business_metrics"]["cost_savings"]["high_automation_potential"]
    elif automation_potential == "low":
        cost_range = BASELINE_RANGES["business_metrics"]["cost_savings"]["low_automation"]
    else:
        cost_range = BASELINE_RANGES["business_metrics"]["cost_savings"]["medium_automation"]
        
    baselines["cost_savings_roi"] = {
        "min": cost_range[0],
        "max": cost_range[1],
        "recommended": (cost_range[0] + cost_range[1]) / 2,
        "rationale": f"Based on {automation_potential} automation potential"
    }
    
    # Customer Satisfaction
    if scenario_type == "replacement":
        csat_range = BASELINE_RANGES["business_metrics"]["customer_satisfaction"]["replacement_scenarios"]
    elif scenario_type == "new_capability":
        csat_range = BASELINE_RANGES["business_metrics"]["customer_satisfaction"]["new_capability_scenarios"]
    else:
        csat_range = BASELINE_RANGES["business_metrics"]["customer_satisfaction"]["enhancement_scenarios"]
        
    baselines["customer_satisfaction_improvement"] = {
        "min": csat_range[0],
        "max": csat_range[1],
        "recommended": (csat_range[0] + csat_range[1]) / 2,
        "rationale": f"Based on {scenario_type} scenario type"
    }
    
    return baselines

def generate_insights_offline(baselines, analysis):
    """Generate insights and recommendations"""
    
    insights = {
        "technical_insights": [],
        "operational_insights": [],
        "business_insights": [],
        "recommendations": []
    }
    
    # Technical insights
    if "trajectory_complexity" in baselines:
        traj = baselines["trajectory_complexity"]
        insights["technical_insights"].append(
            f"Trajectory complexity should average {traj['recommended']:.0f} (range: {traj['min']}-{traj['max']}). {traj['rationale']}."
        )
    
    if "tool_utilization" in baselines:
        tool = baselines["tool_utilization"]
        insights["technical_insights"].append(
            f"Tool utilization should target {tool['recommended']:.0f}% (range: {tool['min']}-{tool['max']}%). {tool['rationale']}."
        )
    
    # Operational insights
    if "task_escalation_rate" in baselines:
        escalation = baselines["task_escalation_rate"]
        insights["operational_insights"].append(
            f"Task escalation rate should be {escalation['recommended']:.1f}% (range: {escalation['min']}-{escalation['max']}%). {escalation['rationale']}."
        )
    
    if "first_contact_resolution" in baselines:
        fcr = baselines["first_contact_resolution"]
        insights["operational_insights"].append(
            f"First contact resolution should achieve {fcr['recommended']:.0f}% (range: {fcr['min']}-{fcr['max']}%). {fcr['rationale']}."
        )
    
    # Business insights
    if "cost_savings_roi" in baselines:
        roi = baselines["cost_savings_roi"]
        insights["business_insights"].append(
            f"Expected ROI should be {roi['recommended']:.1f}x (range: {roi['min']}-{roi['max']}x). {roi['rationale']}."
        )
    
    if "customer_satisfaction_improvement" in baselines:
        csat = baselines["customer_satisfaction_improvement"]
        insights["business_insights"].append(
            f"Customer satisfaction improvement should be {csat['recommended']:.0f}% (range: {csat['min']}-{csat['max']}%). {csat['rationale']}."
        )
    
    # Generate recommendations
    complexity = analysis.get("complexity_level", "complex")
    domain = analysis.get("domain_type", "evolving")
    
    if complexity == "simple":
        insights["recommendations"].append("Focus on high throughput and consistent performance metrics")
    elif complexity == "highly_specialized":
        insights["recommendations"].append("Prioritize accuracy and expert-level reasoning capabilities")
    else:
        insights["recommendations"].append("Balance efficiency with comprehensive problem-solving")
    
    if domain == "new":
        insights["recommendations"].append("Plan for rapid learning and adaptation phases")
    elif domain == "stable":
        insights["recommendations"].append("Optimize for reliability and minimal variance")
    else:
        insights["recommendations"].append("Build flexibility for evolving requirements")
    
    insights["recommendations"].append("Implement progressive escalation pathways for complex issues")
    insights["recommendations"].append("Monitor tool performance and adjust utilization targets accordingly")
    
    return insights

def run_offline_demo(user_query, document_content):
    """Run the complete AI Control Tower analysis offline"""
    
    print("🤖 AI Control Tower Agent Starting (Offline Mode)...")
    print("="*60)
    
    # Step 1: Document Analysis
    print("\n📄 Step 1: Analyzing Document Content")
    print("-" * 40)
    
    analysis = analyze_document_offline(document_content, user_query)
    
    print(f"✓ Document analyzed successfully")
    print(f"✓ Complexity Level: {analysis['complexity_level'].title()}")
    print(f"✓ Domain Type: {analysis['domain_type'].title()}")
    print(f"✓ Tool Maturity: {analysis['tool_maturity'].title()}")
    print(f"✓ Capabilities Found: {len(analysis['agent_capabilities'])}")
    
    # Step 2: Baseline Calculation
    print(f"\n🎯 Step 2: Calculating Dynamic Baselines")
    print("-" * 40)
    
    baselines = calculate_baselines_offline(analysis)
    
    print(f"✓ Calculated baselines for {len(baselines)} metrics")
    print(f"✓ Technical metrics: 2")
    print(f"✓ Operational metrics: 3") 
    print(f"✓ Business metrics: 2")
    
    # Step 3: Generate Insights
    print(f"\n💡 Step 3: Generating Insights & Recommendations")
    print("-" * 40)
    
    insights = generate_insights_offline(baselines, analysis)
    
    print(f"✓ Generated insights across 4 categories")
    print(f"✓ Created {len(insights['recommendations'])} actionable recommendations")
    
    # Final Report
    print(f"\n📊 FINAL BASELINE ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n🎯 DYNAMIC BASELINE METRICS:")
    print("-" * 50)
    
    # Group metrics by category
    technical_metrics = ['trajectory_complexity', 'tool_utilization']
    operational_metrics = ['task_escalation_rate', 'first_contact_resolution', 'improvement_velocity', 'guardrail_violations']
    business_metrics = ['cost_savings_roi', 'customer_satisfaction_improvement']
    
    def print_metric_group(title, metrics):
        group_metrics = {k: v for k, v in baselines.items() if k in metrics}
        if group_metrics:
            print(f"\n{title}:")
            for metric, values in group_metrics.items():
                metric_name = metric.replace('_', ' ').title()
                unit = get_metric_unit(metric)
                print(f"  • {metric_name}: {values['recommended']:.1f}{unit}")
                print(f"    Range: {values['min']:.1f}-{values['max']:.1f}{unit}")
                print(f"    Rationale: {values['rationale']}")
    
    print_metric_group("📊 Technical Metrics", technical_metrics)
    print_metric_group("⚙️  Operational Metrics", operational_metrics)
    print_metric_group("💼 Business Metrics", business_metrics)
    
    # Print insights
    print(f"\n💡 KEY INSIGHTS & RECOMMENDATIONS:")
    print("-" * 50)
    
    for category, insight_list in insights.items():
        if insight_list and category != 'recommendations':
            category_name = category.replace('_', ' ').title()
            print(f"\n{category_name}:")
            for insight in insight_list:
                print(f"  • {insight}")
    
    if insights.get('recommendations'):
        print(f"\n🎯 Action Recommendations:")
        for rec in insights['recommendations']:
            print(f"  ✓ {rec}")
    
    # Readiness Assessment
    print(f"\n✅ READINESS ASSESSMENT:")
    print("-" * 50)
    
    complexity = analysis['complexity_level']
    domain = analysis['domain_type']
    automation = analysis['automation_potential']
    
    technical_readiness = "high" if complexity == "simple" else "medium"
    operational_readiness = "high" if domain == "stable" else "medium"
    business_readiness = automation
    
    assessments = [
        ("Technical Readiness", technical_readiness),
        ("Operational Readiness", operational_readiness),
        ("Business Readiness", business_readiness)
    ]
    
    for area, level in assessments:
        emoji = "🟢" if level == "high" else "🟡" if level == "medium" else "🔴"
        print(f"  {emoji} {area}: {level.upper()}")
    
    print(f"\n🎉 AI Control Tower Analysis Complete!")
    print("="*60)
    
    return {
        'analysis': analysis,
        'baselines': baselines,
        'insights': insights,
        'readiness': {
            'technical': technical_readiness,
            'operational': operational_readiness,
            'business': business_readiness
        }
    }

def get_metric_unit(metric):
    """Get the appropriate unit for a metric"""
    units = {
        'trajectory_complexity': '',
        'tool_utilization': '%',
        'task_escalation_rate': '%', 
        'first_contact_resolution': '%',
        'improvement_velocity': '% monthly',
        'guardrail_violations': '%',
        'cost_savings_roi': 'x ROI',
        'customer_satisfaction_improvement': '%'
    }
    return units.get(metric, '')

if __name__ == "__main__":
    # Sample scenarios
    sample_query = "Create baseline metrics for a customer service agent handling technical support"
    
    sample_document = """
    Technical Customer Service Agent Documentation:
    
    Purpose: Handle technical support inquiries for cloud services platform
    
    Capabilities:
    - Diagnose basic connectivity issues
    - Guide users through account setup processes
    - Troubleshoot common software problems
    - Access knowledge base for solutions
    - Escalate complex technical issues
    
    Tools Available:
    - Knowledge base search system (well-established, reliable)
    - Ticket management platform (stable, mature)
    - Basic diagnostic tools (experimental, improving)
    - Customer account API (well-defined, secure)
    - Escalation workflow system (proven, efficient)
    
    Expected Performance:
    - Resolve 70% of technical issues without escalation
    - Average response time: 2 minutes
    - Customer satisfaction target: 85%
    - First contact resolution for simple issues: 80%
    - Complex issue escalation: 20%
    
    Domain: Established cloud services with evolving technical features
    Task Types: Mix of routine troubleshooting and complex technical problems
    Automation Potential: Medium due to variety of technical scenarios
    """
    
    print(f"Query: {sample_query}\n")
    print(f"Document: Technical Customer Service Agent Documentation")
    
    try:
        result = run_offline_demo(sample_query, sample_document)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()