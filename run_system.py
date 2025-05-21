import asyncio
from decision_system import DecisionSupervisor, DecisionAgent, AgentRole
from visualization import visualize_discussion
import argparse

async def run_decision_system(topic: str = None):
    # Create supervisor
    supervisor = DecisionSupervisor()
    
    # Set topic (use default if none provided)
    if not topic:
        topic = "Should the bank remove physical branches?"
    supervisor.set_topic(topic)

    # Create and register agents
    agents = [
        DecisionAgent("ceo1", AgentRole.CEO),
        DecisionAgent("banker1", AgentRole.BANKER),
        DecisionAgent("customer1", AgentRole.CUSTOMER)
    ]

    print("\n=== Starting Decision Making System ===")
    print(f"Topic: {topic}\n")

    # Register agents
    for agent in agents:
        supervisor.register_agent(agent)
        print(f"Registered {agent.role.value} agent: {agent.agent_id}")

    print("\n=== Collecting Opinions ===")
    # Collect opinions
    await supervisor.collect_opinions()

    print("\n=== Making Decision ===")
    # Make decision
    decision = supervisor.make_decision()

    # Print detailed analysis
    print(supervisor.get_detailed_analysis())

    # Visualize the discussion
    print("\n=== Generating Visualization ===")
    visualize_discussion(supervisor.opinions)

def main():
    parser = argparse.ArgumentParser(description='Run the decision-making system')
    parser.add_argument('--topic', type=str, help='Topic for decision making')
    args = parser.parse_args()

    asyncio.run(run_decision_system(args.topic))

if __name__ == "__main__":
    main() 