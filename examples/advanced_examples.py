#!/usr/bin/env python3
"""
Advanced Examples for TauTranslator
===================================

Demonstrates complex requirements engineering scenarios
with the enhanced TauTranslator system.
"""

import asyncio
from pathlib import Path
from requirements_to_tau_system import RequirementsToTauSystem
from refactored_llm_translator import TranslationRequest, TranslatorFactory


class AdvancedExamples:
    """Collection of advanced example scenarios."""
    
    EXAMPLES = {
        "autonomous_vehicle": {
            "title": "Autonomous Vehicle Safety System",
            "requirements": """
                Design a safety-critical control system for an autonomous vehicle.
                
                The system must continuously monitor multiple sensors:
                - LIDAR for obstacle detection (range: 0-200 meters)
                - Cameras for lane detection and traffic signs
                - Radar for velocity measurement of nearby objects
                - GPS for position tracking with accuracy within 1 meter
                
                Safety requirements:
                - Emergency braking must engage within 100 milliseconds when obstacle detected
                - Always maintain minimum safe distance: 2 seconds * current_velocity
                - Never exceed speed limit for current road segment
                - If any sensor fails, system must switch to degraded mode immediately
                
                Behavioral requirements:
                - Follow traffic rules based on detected signs and signals
                - Yield to pedestrians at all crosswalks
                - Maintain lane position within 30 centimeters of center
                - Signal lane changes 3 seconds before execution
                
                Data logging:
                - Record all sensor data at 100Hz
                - Log all decisions with timestamp and reasoning
                - Store last 30 seconds in circular buffer for incident analysis
                
                The system must be certified for ASIL-D compliance.
            """
        },
        
        "medical_device": {
            "title": "Insulin Pump Control System",
            "requirements": """
                Create a control system for an automated insulin pump.
                
                Patient monitoring:
                - Continuous glucose monitoring (CGM) every 5 minutes
                - Blood glucose range: 70-180 mg/dL (normal)
                - Hypoglycemia threshold: below 70 mg/dL
                - Hyperglycemia threshold: above 180 mg/dL
                
                Insulin delivery rules:
                - Basal rate: 0.5-2.0 units/hour (configurable)
                - Bolus dose calculation based on carbohydrate intake
                - Correction factor: 1 unit per 50 mg/dL above target
                
                Safety constraints:
                - Maximum bolus: 10 units
                - Maximum daily dose: 100 units
                - Minimum time between boluses: 15 minutes
                - Always check for occlusion before delivery
                
                Alarms and notifications:
                - Low glucose alarm when below 80 mg/dL
                - Urgent low alarm when below 55 mg/dL
                - High glucose alarm when above 250 mg/dL
                - Occlusion detected alarm
                - Low battery warning at 20%
                
                The pump must maintain delivery accuracy within ±5%.
                All alarms must be both audible and vibration.
                System must log all events for medical review.
            """
        },
        
        "industrial_robot": {
            "title": "Industrial Robot Arm Controller",
            "requirements": """
                Develop a control system for a 6-axis industrial robot arm.
                
                Motion control:
                - Joint angles: -180 to +180 degrees for each axis
                - Maximum angular velocity: 180 degrees/second
                - Position accuracy: ±0.1 mm at tool tip
                - Repeatability: ±0.05 mm
                
                Safety zones:
                - Define workspace boundaries as 2m x 2m x 2m cube
                - Restricted zones where speed is limited to 10% max
                - Forbidden zones that must never be entered
                - Emergency stop zone when human detected within 1 meter
                
                Force control:
                - Maximum force at tool tip: 100 N
                - Force feedback sampling: 1000 Hz
                - Collision detection threshold: 20 N unexpected force
                - Automatic retraction on collision detection
                
                Path planning:
                - Smooth trajectory generation with jerk limitation
                - Obstacle avoidance using 3D vision system
                - Optimal path calculation to minimize cycle time
                - Real-time path adjustment based on sensor feedback
                
                Human collaboration mode:
                - Reduce speed to 250 mm/s when human present
                - Force limiting to 50 N in collaborative mode
                - Visual indicators showing robot intent
                - Hand-guiding mode with gravity compensation
                
                System must comply with ISO 10218 and ISO/TS 15066.
            """
        },
        
        "smart_grid": {
            "title": "Smart Grid Energy Management",
            "requirements": """
                Design an energy management system for a smart grid.
                
                Grid monitoring:
                - Monitor voltage levels at all nodes (±5% of nominal)
                - Track power flow between all segments
                - Measure frequency (49.5-50.5 Hz acceptable range)
                - Monitor phase angles and power factor
                
                Renewable integration:
                - Solar generation varies 0-100% based on weather
                - Wind generation varies 0-100% based on wind speed
                - Battery storage: charge when excess, discharge when deficit
                - Maintain grid stability with up to 60% renewables
                
                Load balancing:
                - Predict demand using historical data and weather
                - Shift flexible loads to off-peak hours
                - Implement demand response during peak periods
                - Maintain reserve capacity of at least 10%
                
                Fault management:
                - Detect faults within 100 milliseconds
                - Isolate faulty segments automatically
                - Reroute power through alternate paths
                - Restore service within 5 minutes when possible
                
                Optimization objectives:
                - Minimize transmission losses
                - Maximize renewable energy utilization
                - Minimize customer interruptions
                - Balance load across all transformers
                
                The system must log all events and maintain 99.9% uptime.
            """
        },
        
        "blockchain_validator": {
            "title": "Blockchain Transaction Validator",
            "requirements": """
                Create a formal specification for blockchain transaction validation.
                
                Transaction structure:
                - Sender address (256-bit hash)
                - Receiver address (256-bit hash)
                - Amount (positive integer, max 10^18 units)
                - Fee (positive integer, minimum 1000 units)
                - Nonce (sequential counter per sender)
                - Signature (ECDSA signature)
                
                Validation rules:
                - Sender must have sufficient balance (amount + fee)
                - Nonce must be exactly previous_nonce + 1
                - Signature must be valid for transaction hash
                - Transaction size must not exceed 1 KB
                - Fee must meet current network minimum
                
                Smart contract interaction:
                - If receiver is contract, validate contract exists
                - Check contract accepts the transaction type
                - Verify gas limit is sufficient for execution
                - Simulate execution to check for errors
                
                Double-spend prevention:
                - Check transaction not in current block
                - Check transaction not in previous 1000 blocks
                - Check no conflicting transaction in mempool
                - Lock sender account during validation
                
                Consensus rules:
                - Transaction must be included within 10 blocks
                - If not included, return fee to sender
                - Maintain transaction order by fee priority
                - Respect maximum block size of 1 MB
                
                All validations must complete within 10 milliseconds.
            """
        }
    }
    
    @staticmethod
    async def run_example(example_key: str, interactive: bool = True):
        """Run a specific example."""
        if example_key not in AdvancedExamples.EXAMPLES:
            print(f"Unknown example: {example_key}")
            print(f"Available: {', '.join(AdvancedExamples.EXAMPLES.keys())}")
            return
        
        example = AdvancedExamples.EXAMPLES[example_key]
        
        print("\n" + "="*70)
        print(f"🚀 Example: {example['title']}")
        print("="*70)
        
        system = RequirementsToTauSystem()
        
        if interactive:
            # Run interactive session
            session = await system.start_interactive_session(
                initial_requirements=example['requirements']
            )
            return session
        else:
            # Run automated translation
            translator = TranslatorFactory.create("auto")
            request = TranslationRequest(
                text=example['requirements'],
                max_iterations=3,
                interactive=False
            )
            
            response = await translator.translate(request)
            
            print("\nGenerated Tau Specification:")
            print("-"*70)
            print(response.tau_code)
            print("-"*70)
            print(f"\nConfidence: {response.confidence:.2f}")
            print(f"Iterations used: {response.iterations_used}")
            
            return response
    
    @staticmethod
    async def demonstrate_capabilities():
        """Demonstrate various system capabilities."""
        print("\n" + "="*70)
        print("TauTranslator Advanced Capabilities Demonstration")
        print("="*70)
        
        # 1. Multi-domain translation
        print("\n1. Multi-Domain Requirements Handling")
        print("-"*40)
        
        domains = ["autonomous_vehicle", "medical_device", "smart_grid"]
        for domain in domains:
            print(f"\n  Processing {domain}...")
            response = await AdvancedExamples.run_example(domain, interactive=False)
            lines_count = len(response.tau_code.split('\n'))
            print(f"  ✓ Generated {lines_count} lines of Tau code")
        
        # 2. Complex constraint handling
        print("\n\n2. Complex Constraint Translation")
        print("-"*40)
        
        complex_constraints = """
        The system must ensure:
        - Temperature between 20 and 30 degrees
        - Pressure less than 100 PSI
        - Flow rate between 10 and 50 liters per minute
        - If pressure > 80, reduce flow rate by 50%
        - If temperature > 28, increase cooling by 20%
        - Never allow pressure > 90 and temperature > 25 simultaneously
        """
        
        translator = TranslatorFactory.create("auto")
        request = TranslationRequest(text=complex_constraints, max_iterations=2)
        response = await translator.translate(request)
        
        print("Input constraints:")
        print(complex_constraints)
        print("\nGenerated Tau:")
        print(response.tau_code)
        
        # 3. Temporal logic examples
        print("\n\n3. Temporal Logic Specifications")
        print("-"*40)
        
        temporal_reqs = """
        Safety properties:
        - Always maintain emergency stop capability
        - Never allow unsafe states
        - Eventually reach stable state
        - Response time always less than 100ms
        
        Liveness properties:
        - System must make progress
        - Requests are eventually served
        - No starvation of any process
        """
        
        request = TranslationRequest(text=temporal_reqs, max_iterations=2)
        response = await translator.translate(request)
        
        print("Temporal requirements:")
        print(temporal_reqs)
        print("\nGenerated Tau:")
        print(response.tau_code)
        
        print("\n" + "="*70)
        print("Demonstration complete!")
    
    @staticmethod
    async def benchmark_performance():
        """Benchmark translation performance."""
        print("\n" + "="*70)
        print("Performance Benchmark")
        print("="*70)
        
        import time
        
        translator = TranslatorFactory.create("pattern")  # Use fastest mode
        
        test_sizes = [
            ("Small", "The temperature must always be between 20 and 30 degrees."),
            ("Medium", AdvancedExamples.EXAMPLES["medical_device"]["requirements"][:500]),
            ("Large", AdvancedExamples.EXAMPLES["autonomous_vehicle"]["requirements"])
        ]
        
        for size_name, requirements in test_sizes:
            start_time = time.time()
            
            request = TranslationRequest(
                text=requirements,
                max_iterations=1,
                interactive=False
            )
            
            response = await translator.translate(request)
            
            elapsed = time.time() - start_time
            
            print(f"\n{size_name} requirements:")
            print(f"  Input length: {len(requirements)} chars")
            print(f"  Output length: {len(response.tau_code)} chars")
            print(f"  Translation time: {elapsed:.3f} seconds")
            print(f"  Throughput: {len(requirements)/elapsed:.0f} chars/second")


async def main():
    """Main entry point for examples."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "demo":
            await AdvancedExamples.demonstrate_capabilities()
        elif command == "benchmark":
            await AdvancedExamples.benchmark_performance()
        elif command in AdvancedExamples.EXAMPLES:
            interactive = "--interactive" in sys.argv
            await AdvancedExamples.run_example(command, interactive)
        else:
            print(f"Unknown command: {command}")
            print(f"Available examples: {', '.join(AdvancedExamples.EXAMPLES.keys())}")
            print("Commands: demo, benchmark")
    else:
        # Show menu
        print("\nTauTranslator Advanced Examples")
        print("="*40)
        print("\nAvailable examples:")
        for key, example in AdvancedExamples.EXAMPLES.items():
            print(f"  {key}: {example['title']}")
        
        print("\nUsage:")
        print("  python advanced_examples.py <example_key> [--interactive]")
        print("\nOr run demonstrations:")
        print("  python advanced_examples.py demo")
        print("  python advanced_examples.py benchmark")


if __name__ == "__main__":
    asyncio.run(main())