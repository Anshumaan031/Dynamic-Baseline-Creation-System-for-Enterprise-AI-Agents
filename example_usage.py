"""
Example Usage of AI Control Tower Agent

This script demonstrates how to use the AI Control Tower agent to analyze
agent documentation and generate dynamic baseline metrics.
"""

from ai_control_tower_agent import run_ai_control_tower

def example_customer_service_agent():
    """Example: Customer Service Agent Baseline Analysis"""
    
    query = "Create dynamic baseline metrics for a customer service chatbot"
    
    document_content = """
    Customer Service Chatbot Documentation:
    
    Purpose: Handle customer inquiries for e-commerce platform
    Capabilities:
    - Order status checking
    - Product recommendations  
    - Basic troubleshooting
    - Account management
    - Returns and refunds processing
    
    Tools Available:
    - Order management system API (mature, well-tested)
    - Product catalog search (stable)
    - Knowledge base retrieval (experimental)
    - Email notification system (reliable)
    
    Expected Performance:
    - Handle 80% of customer inquiries without human intervention
    - Average response time < 30 seconds
    - Customer satisfaction target: >85%
    - Available 24/7 with 99.9% uptime
    
    Use Case Complexity: Mixed - Simple order inquiries to complex product issues
    Domain Maturity: Established e-commerce processes
    Task Types: Routine inquiries (60%), complex issues (30%), edge cases (10%)
    """
    
    print("="*60)
    print("CUSTOMER SERVICE AGENT BASELINE ANALYSIS")  
    print("="*60)
    
    try:
        result = run_ai_control_tower(query, document_content)
        print_results(result)
    except Exception as e:
        print(f"Error: {e}")

def example_technical_support_agent():
    """Example: Technical Support Agent Baseline Analysis"""
    
    query = "Generate baseline metrics for a technical support AI agent"
    
    document_content = """
    Technical Support AI Agent Documentation:
    
    Purpose: Provide technical support for cloud infrastructure services
    Capabilities:
    - Diagnose system issues
    - Guide users through troubleshooting steps
    - Access logs and monitoring data
    - Create support tickets
    - Escalate complex problems
    
    Tools Available:
    - Log analysis tools (experimental, high variability)
    - System monitoring APIs (well-defined, reliable)
    - Troubleshooting knowledge base (mature)
    - Ticket management system (stable)
    - Escalation workflow (well-established)
    
    Expected Performance:
    - Resolve 60% of technical issues without escalation
    - Average resolution time for simple issues: 15 minutes
    - Complex problem initial response: 5 minutes
    - Technical accuracy requirement: >95%
    
    Use Case Complexity: Highly specialized technical problems
    Domain Maturity: New domain with rapidly evolving technologies
    Task Types: Novel technical issues requiring deep analysis
    Automation Potential: Medium due to complexity of technical diagnosis
    """
    
    print("="*60)
    print("TECHNICAL SUPPORT AGENT BASELINE ANALYSIS")
    print("="*60)
    
    try:
        result = run_ai_control_tower(query, document_content)
        print_results(result)
    except Exception as e:
        print(f"Error: {e}")

def example_sales_assistant_agent():
    """Example: Sales Assistant Agent Baseline Analysis"""
    
    query = "Create performance baselines for a sales assistant AI"
    
    document_content = """
    Sales Assistant AI Documentation:
    
    Purpose: Support sales team with lead qualification and initial customer engagement
    Capabilities:
    - Lead scoring and qualification
    - Initial customer outreach
    - Meeting scheduling
    - Product information delivery
    - CRM data management
    
    Tools Available:
    - CRM integration (well-defined, stable)
    - Email automation (mature)
    - Calendar management (reliable)
    - Product database (stable)
    - Analytics dashboard (experimental)
    
    Expected Performance:
    - Qualify 90% of leads within 24 hours
    - Convert 25% of qualified leads to meetings
    - Maintain 95% data accuracy in CRM
    - Response time to new leads: <2 hours
    
    Use Case Complexity: Simple to moderate sales processes
    Domain Maturity: Stable sales processes with established workflows  
    Task Types: Routine qualification tasks with some complex customer scenarios
    Automation Potential: High for lead qualification and initial outreach
    Scenario Type: Enhancement of existing sales processes
    """
    
    print("="*60)
    print("SALES ASSISTANT AGENT BASELINE ANALYSIS")
    print("="*60)
    
    try:
        result = run_ai_control_tower(query, document_content)
        print_results(result)
    except Exception as e:
        print(f"Error: {e}")

def print_results(result):
    """Helper function to print analysis results in a formatted way"""
    
    if not result.get('final_report'):
        print("❌ No results generated")
        return
    
    final_report = result['final_report']
    analysis = final_report.get('analysis', {})
    
    # Print summary
    summary = final_report.get('summary', {})
    print(f"\n📋 ANALYSIS SUMMARY:")
    print(f"• Total Metrics Analyzed: {summary.get('total_metrics_analyzed', 0)}")
    print(f"• Complexity Level: {summary.get('complexity_level', 'Unknown').title()}")
    print(f"• Domain Type: {summary.get('domain_type', 'Unknown').title()}")
    
    # Print baseline calculations
    baselines = analysis.get('baseline_calculations', {}).get('calculated_baselines', {})
    if baselines:
        print(f"\n🎯 DYNAMIC BASELINE METRICS:")
        print("-" * 50)
        
        # Group by category
        technical_metrics = ['trajectory_complexity', 'tool_utilization']
        operational_metrics = ['task_escalation_rate', 'first_contact_resolution', 'improvement_velocity']
        business_metrics = ['cost_savings_roi', 'customer_satisfaction_improvement']
        
        def print_metric_group(title, metrics):
            group_metrics = {k: v for k, v in baselines.items() if k in metrics}
            if group_metrics:
                print(f"\n{title}:")
                for metric, values in group_metrics.items():
                    metric_name = metric.replace('_', ' ').title()
                    unit = get_metric_unit(metric)
                    print(f"  • {metric_name}: {values.get('recommended', 0):.1f}{unit}")
                    print(f"    Range: {values.get('min', 0):.1f}-{values.get('max', 0):.1f}{unit}")
                    print(f"    Rationale: {values.get('rationale', 'N/A')}")
                    print()
        
        print_metric_group("📊 Technical Metrics", technical_metrics)
        print_metric_group("⚙️  Operational Metrics", operational_metrics)
        print_metric_group("💼 Business Metrics", business_metrics)
    
    # Print insights and recommendations
    comparison = analysis.get('comparison_results', {})
    insights = comparison.get('insights', {})
    
    if insights:
        print("💡 KEY INSIGHTS & RECOMMENDATIONS:")
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
    
    # Print readiness assessment
    readiness = comparison.get('readiness_assessment', {})
    if readiness:
        print(f"\n✅ READINESS ASSESSMENT:")
        print("-" * 50)
        for area, level in readiness.items():
            area_name = area.replace('_', ' ').title()
            emoji = "🟢" if level == "high" else "🟡" if level == "medium" else "🔴"
            print(f"  {emoji} {area_name}: {level.upper()}")

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

if __name__ == "__main__":
    print("🤖 AI Control Tower - Dynamic Baseline Creation Examples\n")
    
    # Run different agent examples
    examples = [
        ("1. Customer Service Agent", example_customer_service_agent),
        ("2. Technical Support Agent", example_technical_support_agent), 
        ("3. Sales Assistant Agent", example_sales_assistant_agent)
    ]
    
    for title, example_func in examples:
        print(f"\n{title}")
        print("="*60)
        try:
            example_func()
        except Exception as e:
            print(f"❌ Error running {title}: {e}")
        
        print("\n" + "="*60)
        input("Press Enter to continue to next example...")
        print("\n")