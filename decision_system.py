import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    BANKER = "banker"
    CUSTOMER = "customer"
    CEO = "ceo"

class OpinionType(Enum):
    SUPPORT = "support"
    OPPOSE = "oppose"
    NEUTRAL = "neutral"

@dataclass
class DecisionFactor:
    name: str
    weight: float
    score: float
    reasoning: str

@dataclass
class Opinion:
    id: str
    agent_id: str
    role: AgentRole
    type: OpinionType
    reasoning: str
    confidence: float
    decision_factors: List[DecisionFactor]

class DecisionAgent:
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.opinions: List[Opinion] = []

    def _calculate_factors(self) -> List[DecisionFactor]:
        factors = []
        if self.role == AgentRole.CEO:
            factors = [
                DecisionFactor("Cost Savings", 0.4, 0.9, "Branch operations are expensive"),
                DecisionFactor("Digital Transformation", 0.3, 0.8, "Future of banking is digital"),
                DecisionFactor("Customer Impact", 0.2, 0.6, "Some customers may be affected"),
                DecisionFactor("Employee Impact", 0.1, 0.7, "Need to manage workforce transition")
            ]
        elif self.role == AgentRole.BANKER:
            factors = [
                DecisionFactor("Customer Service", 0.4, 0.8, "Physical branches provide better service"),
                DecisionFactor("Operational Costs", 0.3, 0.7, "High maintenance costs"),
                DecisionFactor("Employee Morale", 0.2, 0.6, "Job security concerns"),
                DecisionFactor("Technology Readiness", 0.1, 0.5, "Digital infrastructure needs improvement")
            ]
        elif self.role == AgentRole.CUSTOMER:
            factors = [
                DecisionFactor("Service Quality", 0.4, 0.9, "Prefer face-to-face interactions"),
                DecisionFactor("Convenience", 0.3, 0.7, "Physical branches are more accessible"),
                DecisionFactor("Trust", 0.2, 0.8, "Physical presence builds trust"),
                DecisionFactor("Digital Comfort", 0.1, 0.4, "Not all customers are tech-savvy")
            ]
        return factors

    def _calculate_final_opinion(self, factors: List[DecisionFactor]) -> tuple[OpinionType, float, str]:
        total_score = sum(factor.weight * factor.score for factor in factors)
        support_score = sum(factor.weight * factor.score for factor in factors if factor.score > 0.7)
        oppose_score = sum(factor.weight * factor.score for factor in factors if factor.score < 0.4)
        
        if support_score > oppose_score and total_score > 0.6:
            return OpinionType.SUPPORT, total_score, "Factors support the change"
        elif oppose_score > support_score and total_score < 0.4:
            return OpinionType.OPPOSE, 1 - total_score, "Factors oppose the change"
        else:
            return OpinionType.NEUTRAL, 0.5, "Mixed factors, neutral position"

    async def form_opinion(self, topic: str) -> Opinion:
        # Calculate decision factors
        factors = self._calculate_factors()
        
        # Determine final opinion
        opinion_type, confidence, general_reasoning = self._calculate_final_opinion(factors)
        
        # Build detailed reasoning
        detailed_reasoning = f"As a {self.role.value}, I considered the following factors:\n"
        for factor in factors:
            detailed_reasoning += f"- {factor.name} (Weight: {factor.weight}, Score: {factor.score}): {factor.reasoning}\n"
        detailed_reasoning += f"\nOverall: {general_reasoning}"

        opinion = Opinion(
            id=str(uuid.uuid4()),
            agent_id=self.agent_id,
            role=self.role,
            type=opinion_type,
            reasoning=detailed_reasoning,
            confidence=confidence,
            decision_factors=factors
        )
        self.opinions.append(opinion)
        return opinion

class DecisionSupervisor:
    def __init__(self):
        self.agents: Dict[str, DecisionAgent] = {}
        self.topic: Optional[str] = None
        self.opinions: List[Opinion] = []
        self.final_decision: Optional[str] = None

    def register_agent(self, agent: DecisionAgent):
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered {agent.role.value} agent: {agent.agent_id}")

    def set_topic(self, topic: str):
        self.topic = topic
        logger.info(f"Topic set: {topic}")

    async def collect_opinions(self):
        self.opinions = []
        for agent in self.agents.values():
            opinion = await agent.form_opinion(self.topic)
            self.opinions.append(opinion)
            logger.info(f"Agent {agent.agent_id} ({agent.role.value}) submitted opinion: {opinion.type.value}")

    def make_decision(self) -> str:
        if not self.opinions:
            return "No opinions collected yet"

        weights = {
            AgentRole.CEO: 0.4,
            AgentRole.BANKER: 0.3,
            AgentRole.CUSTOMER: 0.3
        }

        support_score = 0
        oppose_score = 0
        neutral_score = 0

        for opinion in self.opinions:
            weight = weights[opinion.role] * opinion.confidence
            if opinion.type == OpinionType.SUPPORT:
                support_score += weight
            elif opinion.type == OpinionType.OPPOSE:
                oppose_score += weight
            else:
                neutral_score += weight

        if support_score > oppose_score and support_score > neutral_score:
            decision = "Proceed with branch removal, but implement gradual transition and maintain some key locations"
        elif oppose_score > support_score and oppose_score > neutral_score:
            decision = "Maintain current branch structure, but invest in digital transformation"
        else:
            decision = "Implement hybrid approach: reduce branches gradually while enhancing digital services"

        self.final_decision = decision
        return decision

    def get_detailed_analysis(self) -> str:
        analysis = f"\nTopic: {self.topic}\n"
        analysis += "\nDetailed Analysis:\n"
        
        for opinion in self.opinions:
            analysis += f"\n{opinion.role.value.upper()} ({opinion.agent_id}):\n"
            analysis += f"Final Position: {opinion.type.value}\n"
            analysis += f"Confidence Level: {opinion.confidence:.2f}\n"
            analysis += "\nDecision Factors:\n"
            for factor in opinion.decision_factors:
                analysis += f"- {factor.name}:\n"
                analysis += f"  Weight: {factor.weight}\n"
                analysis += f"  Score: {factor.score}\n"
                analysis += f"  Reasoning: {factor.reasoning}\n"
            analysis += f"\nOverall Reasoning:\n{opinion.reasoning}\n"
            analysis += "-" * 50 + "\n"
        
        analysis += f"\nFinal Decision: {self.final_decision}\n"
        return analysis

async def main():
    supervisor = DecisionSupervisor()
    supervisor.set_topic("Should the bank remove physical branches?")

    agents = [
        DecisionAgent("ceo1", AgentRole.CEO),
        DecisionAgent("banker1", AgentRole.BANKER),
        DecisionAgent("customer1", AgentRole.CUSTOMER)
    ]

    for agent in agents:
        supervisor.register_agent(agent)

    await supervisor.collect_opinions()
    decision = supervisor.make_decision()
    print(supervisor.get_detailed_analysis())

if __name__ == "__main__":
    asyncio.run(main()) 