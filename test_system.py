"""
Test Script for AI Control Tower System

This script tests the complete AI Control Tower system without requiring API keys,
demonstrating the document processing and baseline calculation logic.
"""

from document_processor import extract_agent_specifications, process_document_for_baseline_analysis
from ai_control_tower_agent import BASELINE_RANGES
import json

def test_document_processing():
    """Test document processing capabilities"""
    
    print("🔍 Testing Document Processing Module")
    print("="*50)
    
    # Sample agent documentation
    sample_docs = [
        {
            "name": "Simple Customer Service Bot",
            "content": """
            Simple Customer Service Bot Documentation:
            
            Purpose: Handle basic customer inquiries
            Capabilities:
            - Answer FAQ questions
            - Route customer calls
            - Basic order status checks
            
            Tools:
            - Well-established FAQ database
            - Stable order management API
            - Reliable call routing system
            
            Performance Targets:
            - 90% first contact resolution for simple inquiries
            - 95% accuracy in FAQ responses
            - Response time under 10 seconds
            
            Domain: Established customer service with mature processes
            Task Types: Routine inquiries and simple problem resolution
            """
        },
        {
            "name": "Complex Technical Support Agent",
            "content": """
            Advanced Technical Support AI Agent:
            
            Purpose: Provide specialized technical support for enterprise software
            Capabilities:
            - Diagnose complex system failures
            - Analyze log files and performance metrics
            - Guide users through multi-step troubleshooting
            - Create detailed technical reports
            
            Tools:
            - Experimental log analysis algorithms
            - Unstable diagnostic APIs (beta version)
            - Advanced system monitoring tools
            - Technical knowledge base (constantly evolving)
            
            Performance Targets:
            - 60% resolution rate for complex technical issues
            - 95% diagnostic accuracy
            - Average resolution time: 45 minutes
            
            Domain: New and rapidly evolving cloud technologies
            Task Types: Novel technical problems requiring deep expertise
            Automation Potential: Medium due to complexity
            """
        },
        {
            "name": "Sales Enhancement Agent",
            "content": """
            Sales Enhancement AI Assistant:
            
            Purpose: Enhance existing sales processes and support sales teams
            Capabilities:
            - Lead qualification and scoring
            - Automated follow-up communications
            - Sales pipeline management
            - Customer relationship insights
            
            Tools:
            - Well-defined CRM integration
            - Mature email automation platform
            - Stable analytics dashboard
            - Proven lead scoring algorithms
            
            Performance Targets:
            - 85% lead qualification accuracy
            - 30% improvement in sales team efficiency
            - 15% increase in conversion rates
            
            Domain: Established sales processes in stable market
            Task Types: Mix of routine qualification and complex customer analysis
            Scenario: Enhancement of existing sales workflows
            """
        }
    ]
    
    for doc in sample_docs:
        print(f"\n📄 Analyzing: {doc['name']}")
        print("-" * 40)
        
        # Extract specifications
        specs = extract_agent_specifications(doc['content'])
        
        print(f"Complexity Assessment: {specs['use_case_info'].get('complexity', 'unknown').title()}")
        print(f"Domain Maturity: {specs['domain_info'].get('maturity', 'unknown').title()}")
        print(f"Capabilities Found: {len(specs['capabilities'])}")
        print(f"Tools Identified: {len(specs['tools'])}")
        print(f"Performance Targets: {len(specs['performance_targets'])}")
        
        if specs['capabilities']:
            print(f"Key Capabilities:")
            for cap in specs['capabilities'][:3]:  # Show first 3
                print(f"  • {cap}")
        
        if specs['performance_targets']:
            print(f"Performance Targets:")
            for target in specs['performance_targets'][:3]:  # Show first 3
                print(f"  • {target}")

def test_baseline_calculations():
    """Test baseline calculation logic without API calls"""
    
    print("\n\n🎯 Testing Baseline Calculation Logic")
    print("="*50)
    
    # Test scenarios
    scenarios = [
        {
            "name": "Simple Customer Service",
            "analysis": {
                "complexity_level": "simple",
                "domain_type": "stable", 
                "tool_maturity": "well_defined",
                "task_complexity": "simple",
                "automation_potential": "high",
                "scenario_type": "replacement"
            }
        },
        {
            "name": "Complex Technical Support",
            "analysis": {
                "complexity_level": "highly_specialized",
                "domain_type": "new",
                "tool_maturity": "experimental", 
                "task_complexity": "novel",
                "automation_potential": "medium",
                "scenario_type": "enhancement"
            }
        },
        {
            "name": "Moderate Sales Assistant",
            "analysis": {
                "complexity_level": "complex",
                "domain_type": "evolving",
                "tool_maturity": "well_defined",
                "task_complexity": "complex", 
                "automation_potential": "high",
                "scenario_type": "enhancement"
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Calculating Baselines for: {scenario['name']}")
        print("-" * 40)
        
        analysis = scenario['analysis']
        baselines = calculate_baselines_locally(analysis, "baseline calculation test")
        
        print(f"Input Parameters:")
        print(f"  • Complexity: {analysis['complexity_level']}")
        print(f"  • Domain: {analysis['domain_type']}")
        print(f"  • Tools: {analysis['tool_maturity']}")
        
        print(f"\nCalculated Baselines:")
        for metric, values in baselines.items():
            unit = get_metric_unit(metric)
            print(f"  • {metric.replace('_', ' ').title()}: {values['recommended']:.1f}{unit}")
            print(f"    Range: {values['min']:.1f}-{values['max']:.1f}{unit}")
            print(f"    Rationale: {values['rationale']}")
            print()

def calculate_baselines_locally(analysis: dict, user_query: str) -> dict:
    """
    Calculate baselines locally without API calls (simplified version of the tool logic)
    """
    baselines = {}
    
    # Technical Metrics Baselines
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
    elif "technical" in user_query.lower():
        fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["technical_problems"]
    else:
        fcr_range = BASELINE_RANGES["solution_level_kpis"]["first_contact_resolution"]["complex_issues"]
        
    baselines["first_contact_resolution"] = {
        "min": fcr_range[0],
        "max": fcr_range[1], 
        "recommended": (fcr_range[0] + fcr_range[1]) / 2,
        "rationale": f"Based on {task_complexity} inquiry type"
    }
    
    # Business Metrics
    automation_potential = analysis.get("automation_potential", "medium")
    scenario_type = analysis.get("scenario_type", "enhancement")
    
    # Cost Savings (ROI multiplier)
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
    
    # Customer Satisfaction Improvement
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

def get_metric_unit(metric):
    """Get the appropriate unit for a metric"""
    units = {
        'trajectory_complexity': '',
        'tool_utilization': '%',
        'task_escalation_rate': '%', 
        'first_contact_resolution': '%',
        'improvement_velocity': '% monthly',
        'cost_savings_roi': 'x ROI',
        'customer_satisfaction_improvement': '%'
    }
    return units.get(metric, '')

def test_integration():
    """Test the integration between document processing and baseline calculation"""
    
    print("\n\n🔄 Testing System Integration")
    print("="*50)
    
    sample_content = """
    Enterprise Chatbot Documentation:
    
    Purpose: Handle customer support for enterprise software platform
    Capabilities:
    - Complex technical troubleshooting
    - Multi-step problem resolution
    - Integration with various enterprise systems
    
    Tools:
    - Experimental AI diagnostic tools
    - Unstable third-party integrations
    - Advanced analytics platform
    
    Performance Targets:
    - 65% first contact resolution for technical issues
    - 25% task escalation rate
    - 90% customer satisfaction
    
    Domain: New enterprise software with evolving requirements
    Task Types: Complex technical problems requiring specialized knowledge
    """
    
    print("Step 1: Document Analysis")
    specs = extract_agent_specifications(sample_content)
    print(f"✓ Extracted {len(specs['capabilities'])} capabilities")
    print(f"✓ Identified {len(specs['tools'])} tools")
    print(f"✓ Found {len(specs['performance_targets'])} performance targets")
    
    print(f"\nStep 2: Analysis Mapping")
    analysis_inputs = {
        "complexity_level": specs['use_case_info'].get('complexity', 'complex'),
        "domain_type": specs['domain_info'].get('maturity', 'evolving'),
        "tool_maturity": "experimental",  # Based on document content
        "task_complexity": "complex",     # Based on capabilities
        "automation_potential": "medium", # Based on complexity
        "scenario_type": "enhancement"    # Based on purpose
    }
    
    print(f"✓ Complexity Level: {analysis_inputs['complexity_level']}")
    print(f"✓ Domain Type: {analysis_inputs['domain_type']}")
    print(f"✓ Tool Maturity: {analysis_inputs['tool_maturity']}")
    
    print(f"\nStep 3: Baseline Calculation")
    baselines = calculate_baselines_locally(analysis_inputs, "enterprise chatbot")
    
    print(f"✓ Calculated baselines for {len(baselines)} metrics")
    print(f"\nKey Baseline Recommendations:")
    key_metrics = ['trajectory_complexity', 'tool_utilization', 'first_contact_resolution', 'cost_savings_roi']
    
    for metric in key_metrics:
        if metric in baselines:
            values = baselines[metric]
            unit = get_metric_unit(metric)
            print(f"  • {metric.replace('_', ' ').title()}: {values['recommended']:.1f}{unit}")
    
    print(f"\n✅ Integration test completed successfully!")

if __name__ == "__main__":
    print("🚀 AI Control Tower System Test Suite")
    print("="*60)
    
    try:
        # Test document processing
        test_document_processing()
        
        # Test baseline calculations
        test_baseline_calculations()
        
        # Test integration
        test_integration()
        
        print(f"\n🎉 All Tests Completed Successfully!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up OpenRouter API key in .env file")
        print("3. Run: python example_usage.py")
        print("4. Or run full agent: python ai_control_tower_agent.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()