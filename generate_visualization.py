import json
import asyncio
from decision_system import DecisionSupervisor, DecisionAgent, AgentRole

async def generate_visualization_data():
    # Create supervisor
    supervisor = DecisionSupervisor()
    supervisor.set_topic("Should the bank remove physical branches?")

    # Create and register agents
    agents = [
        DecisionAgent("ceo1", AgentRole.CEO),
        DecisionAgent("banker1", AgentRole.BANKER),
        DecisionAgent("customer1", AgentRole.CUSTOMER)
    ]

    for agent in agents:
        supervisor.register_agent(agent)

    # Collect opinions
    await supervisor.collect_opinions()

    # Prepare data for visualization
    visualization_data = {
        "topic": supervisor.topic,
        "agents": []
    }

    for opinion in supervisor.opinions:
        agent_data = {
            "role": opinion.role.value.upper(),
            "id": opinion.agent_id,
            "factors": [],
            "finalOpinion": {
                "type": opinion.type.value.upper(),
                "confidence": opinion.confidence,
                "reasoning": opinion.reasoning.split("\n")[-1]  # Get the last line as summary
            }
        }

        # Add factors
        for factor in opinion.decision_factors:
            agent_data["factors"].append({
                "name": factor.name,
                "weight": factor.weight,
                "score": factor.score,
                "reasoning": factor.reasoning
            })

        visualization_data["agents"].append(agent_data)

    return visualization_data

def update_html_file(data):
    # Read the HTML template
    with open("visualize.html", "r") as f:
        html_content = f.read()

    # Replace the sample data with actual data
    new_content = html_content.replace(
        "// Sample data (this would come from your Python system)",
        f"// Generated data from the decision system\nconst data = {json.dumps(data, indent=4)};"
    )

    # Write the updated HTML file
    with open("visualize.html", "w") as f:
        f.write(new_content)

async def main():
    # Generate visualization data
    data = await generate_visualization_data()
    
    # Update the HTML file
    update_html_file(data)
    
    print("Visualization data generated and HTML file updated.")
    print("Open visualize.html in your web browser to see the visualization.")

if __name__ == "__main__":
    asyncio.run(main()) 