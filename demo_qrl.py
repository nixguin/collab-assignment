#!/usr/bin/env python3
"""
QRL Traffic System Demo
Shows how to use the QRL service and agent
"""

import sys
import json
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ai.qrl_service import get_segment_status
from ai.qrl_traffic_agent import QRLTrafficAgent

def demo_basic_usage():
    """Demo 1: Basic segment analysis"""
    print("=" * 60)
    print("DEMO 1: Basic Traffic Analysis")
    print("=" * 60)
    
    # Analyze a single segment
    result = get_segment_status("fgcu_blvd", hours_ahead=1)
    
    print(f"\n📍 Segment: {result['segment_id']}")
    print(f"⏰ Timestamp: {result['timestamp']}")
    print(f"\n📊 Forecast:")
    print(f"   Predicted Volume: {result['forecast']['predicted_volume']} vehicles/hour")
    print(f"   Confidence: {result['forecast']['confidence']:.2%}")
    
    print(f"\n🚦 QRL Risk Analysis:")
    print(f"   Risk Level: {result['qrl_risk']['risk_label']}")
    print(f"   Action Index: {result['qrl_risk']['action_index']}")
    
    print(f"\n   Probability Distribution:")
    for label, prob in result['qrl_risk']['probs'].items():
        bar = "█" * int(prob * 50)
        print(f"   {label:12} {prob:5.1%} {bar}")
    
    print("\n" + "=" * 60 + "\n")


def demo_multi_segment():
    """Demo 2: Compare multiple segments"""
    print("=" * 60)
    print("DEMO 2: Multi-Segment Comparison")
    print("=" * 60)
    
    segments = ['fgcu_blvd', 'bh_griffin_pkwy', 'campus_loop']
    results = []
    
    for seg in segments:
        result = get_segment_status(seg, hours_ahead=1)
        results.append({
            'segment': seg,
            'volume': result['forecast']['predicted_volume'],
            'risk': result['qrl_risk']['risk_label'],
            'risk_idx': result['qrl_risk']['action_index']
        })
    
    print("\n🗺️  Campus Traffic Overview:")
    print(f"{'Segment':<20} {'Volume':<12} {'Risk Level':<15} {'Status'}")
    print("-" * 60)
    
    for r in sorted(results, key=lambda x: x['risk_idx'], reverse=True):
        volume = f"{r['volume']} veh/hr"
        status = "🔴" if r['risk_idx'] >= 2 else "🟡" if r['risk_idx'] == 1 else "🟢"
        print(f"{r['segment']:<20} {volume:<12} {r['risk']:<15} {status}")
    
    print("\n" + "=" * 60 + "\n")


def demo_time_series():
    """Demo 3: Multi-hour forecast"""
    print("=" * 60)
    print("DEMO 3: 6-Hour Forecast")
    print("=" * 60)
    
    segment = "fgcu_blvd"
    hours = 6
    
    print(f"\n📈 Forecasting next {hours} hours for {segment}:\n")
    print(f"{'Hour':<8} {'Volume':<12} {'Risk':<12} {'Confidence'}")
    print("-" * 50)
    
    for h in range(1, hours + 1):
        result = get_segment_status(segment, hours_ahead=h)
        volume = result['forecast']['predicted_volume']
        risk = result['qrl_risk']['risk_label']
        conf = result['forecast']['confidence']
        
        print(f"+{h}h      {volume:<12} {risk:<12} {conf:.1%}")
    
    print("\n" + "=" * 60 + "\n")


def demo_quantum_circuit():
    """Demo 4: Direct quantum circuit usage"""
    print("=" * 60)
    print("DEMO 4: Quantum Circuit Analysis")
    print("=" * 60)
    
    print("\n🔬 Direct QRL Agent Usage:\n")
    
    agent = QRLTrafficAgent(n_qubits=2, n_layers=2)
    
    # Test different scenarios
    scenarios = [
        (150, 3, "Early morning - low traffic"),
        (450, 8, "Morning rush hour"),
        (600, 17, "Evening rush hour"),
        (80, 22, "Late night - minimal traffic"),
    ]
    
    print(f"{'Scenario':<30} {'Volume':<10} {'Hour':<8} {'Risk':<12} {'Confidence'}")
    print("-" * 75)
    
    for volume, hour, desc in scenarios:
        risk_data = agent.classify_risk(volume=volume, hour=hour)
        risk = risk_data['risk_label']
        confidence = max(risk_data['probs'].values())
        
        print(f"{desc:<30} {volume:<10} {hour:<8} {risk:<12} {confidence:.1%}")
    
    print("\n🧮 Quantum Circuit Details:")
    print(f"   Number of Qubits: {agent.n_qubits}")
    print(f"   Number of Layers: {agent.n_layers}")
    print(f"   Parameter Shape: {agent.weights.shape}")
    print(f"   Device: {agent.dev.name}")
    
    print("\n" + "=" * 60 + "\n")


def demo_risk_alert():
    """Demo 5: Alert system simulation"""
    print("=" * 60)
    print("DEMO 5: Traffic Alert System")
    print("=" * 60)
    
    segments = ['fgcu_blvd', 'bh_griffin_pkwy', 'campus_loop', 'parking_access']
    alerts = []
    
    print("\n🚨 Checking for traffic alerts...\n")
    
    for seg in segments:
        result = get_segment_status(seg, hours_ahead=1)
        risk = result['qrl_risk']['risk_label']
        risk_idx = result['qrl_risk']['action_index']
        volume = result['forecast']['predicted_volume']
        
        if risk_idx >= 2:  # CONGESTED or CRITICAL
            alerts.append({
                'segment': seg,
                'risk': risk,
                'volume': volume,
                'severity': risk_idx
            })
    
    if alerts:
        print(f"⚠️  {len(alerts)} ALERT(S) DETECTED\n")
        for alert in sorted(alerts, key=lambda x: x['severity'], reverse=True):
            emoji = "🔴" if alert['severity'] == 3 else "🟠"
            print(f"{emoji} {alert['risk']} on {alert['segment']}")
            print(f"   Volume: {alert['volume']} vehicles/hour")
            print(f"   Recommended: Monitor closely and consider intervention\n")
    else:
        print("✅ No alerts - All traffic levels normal\n")
    
    print("=" * 60 + "\n")


def demo_json_output():
    """Demo 6: JSON API response"""
    print("=" * 60)
    print("DEMO 6: JSON API Response Format")
    print("=" * 60)
    
    print("\n📋 Sample API Response:\n")
    
    result = get_segment_status("fgcu_blvd", hours_ahead=1)
    print(json.dumps(result, indent=2))
    
    print("\n" + "=" * 60 + "\n")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "QRL TRAFFIC SYSTEM - LIVE DEMO" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        demo_basic_usage()
        demo_multi_segment()
        demo_time_series()
        demo_quantum_circuit()
        demo_risk_alert()
        demo_json_output()
        
        print("✨ All demos completed successfully!")
        print("\nNext steps:")
        print("  1. Read QRL_USAGE_GUIDE.md for detailed documentation")
        print("  2. Start the API: python -m uvicorn api.main:app --reload")
        print("  3. Test endpoint: http://localhost:8000/api/qrl/fgcu_blvd")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("\nMake sure models are trained first:")
        print("  python -m ai.traffic_forecasting")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
