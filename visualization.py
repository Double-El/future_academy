import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict
from decision_system import Opinion, DecisionFactor, AgentRole, OpinionType
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors

class DiscussionVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(15, 10))
        plt.ion()  # Turn on interactive mode

    def _get_role_color(self, role: AgentRole) -> str:
        colors = {
            AgentRole.CEO: '#FF6B6B',      # Red
            AgentRole.BANKER: '#4ECDC4',   # Teal
            AgentRole.CUSTOMER: '#45B7D1'  # Blue
        }
        return colors.get(role, '#CCCCCC')

    def _get_opinion_color(self, opinion_type: OpinionType) -> str:
        colors = {
            OpinionType.SUPPORT: '#2ECC71',  # Green
            OpinionType.OPPOSE: '#E74C3C',   # Red
            OpinionType.NEUTRAL: '#F1C40F'   # Yellow
        }
        return colors.get(opinion_type, '#CCCCCC')

    def plot_discussion_flow(self, opinions: List[Opinion]):
        self.ax.clear()
        self.ax.set_title('Discussion Flow and Decision Making Process', pad=20)
        
        # Create positions for agents
        positions = {
            'ceo': (0.2, 0.8),
            'banker': (0.2, 0.5),
            'customer': (0.2, 0.2)
        }
        
        # Plot agent nodes
        for opinion in opinions:
            role = opinion.role.value
            pos = positions[role]
            color = self._get_role_color(opinion.role)
            
            # Draw agent node
            self.ax.add_patch(Rectangle(
                (pos[0] - 0.1, pos[1] - 0.05),
                0.2, 0.1,
                facecolor=color,
                alpha=0.3
            ))
            self.ax.text(pos[0], pos[1], role.upper(), 
                        ha='center', va='center', fontweight='bold')
            
            # Plot decision factors
            factor_x = pos[0] + 0.3
            for i, factor in enumerate(opinion.decision_factors):
                factor_y = pos[1] - 0.04 + i * 0.05
                
                # Draw factor node
                self.ax.add_patch(Rectangle(
                    (factor_x - 0.15, factor_y - 0.02),
                    0.3, 0.04,
                    facecolor='white',
                    edgecolor='black',
                    alpha=0.7
                ))
                
                # Add factor text
                self.ax.text(factor_x, factor_y,
                           f"{factor.name} (W:{factor.weight:.1f}, S:{factor.score:.1f})",
                           ha='center', va='center', fontsize=8)
                
                # Draw connection line
                self.ax.plot([pos[0] + 0.1, factor_x - 0.15],
                           [pos[1], factor_y],
                           'k-', alpha=0.3)
            
            # Plot final opinion
            final_x = factor_x + 0.4
            final_y = pos[1]
            opinion_color = self._get_opinion_color(opinion.type)
            
            self.ax.add_patch(Rectangle(
                (final_x - 0.15, final_y - 0.05),
                0.3, 0.1,
                facecolor=opinion_color,
                alpha=0.5
            ))
            self.ax.text(final_x, final_y,
                        f"{opinion.type.value.upper()}\nConf: {opinion.confidence:.2f}",
                        ha='center', va='center', fontweight='bold')
            
            # Draw connection to final opinion
            self.ax.plot([factor_x + 0.15, final_x - 0.15],
                        [pos[1], final_y],
                        'k-', alpha=0.3)

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        
        # Add legend
        legend_elements = [
            Rectangle((0, 0), 1, 1, facecolor=self._get_role_color(AgentRole.CEO), alpha=0.3, label='CEO'),
            Rectangle((0, 0), 1, 1, facecolor=self._get_role_color(AgentRole.BANKER), alpha=0.3, label='Banker'),
            Rectangle((0, 0), 1, 1, facecolor=self._get_role_color(AgentRole.CUSTOMER), alpha=0.3, label='Customer'),
            Rectangle((0, 0), 1, 1, facecolor=self._get_opinion_color(OpinionType.SUPPORT), alpha=0.5, label='Support'),
            Rectangle((0, 0), 1, 1, facecolor=self._get_opinion_color(OpinionType.OPPOSE), alpha=0.5, label='Oppose'),
            Rectangle((0, 0), 1, 1, facecolor=self._get_opinion_color(OpinionType.NEUTRAL), alpha=0.5, label='Neutral')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1))

    def plot_decision_weights(self, opinions: List[Opinion]):
        plt.figure(figsize=(10, 6))
        
        # Prepare data
        roles = [opinion.role.value for opinion in opinions]
        weights = [0.4 if role == 'ceo' else 0.3 for role in roles]  # Using system weights
        confidences = [opinion.confidence for opinion in opinions]
        final_weights = [w * c for w, c in zip(weights, confidences)]
        
        # Create bar chart
        x = np.arange(len(roles))
        width = 0.35
        
        plt.bar(x - width/2, weights, width, label='Base Weight', color='#3498DB')
        plt.bar(x + width/2, final_weights, width, label='Weighted by Confidence', color='#2ECC71')
        
        plt.xlabel('Agent Role')
        plt.ylabel('Weight')
        plt.title('Decision Weights by Agent Role')
        plt.xticks(x, [role.upper() for role in roles])
        plt.legend()
        
        # Add value labels
        for i, v in enumerate(weights):
            plt.text(i - width/2, v + 0.01, f'{v:.2f}', ha='center')
        for i, v in enumerate(final_weights):
            plt.text(i + width/2, v + 0.01, f'{v:.2f}', ha='center')

    def show(self):
        plt.tight_layout()
        plt.show()

def visualize_discussion(opinions: List[Opinion]):
    visualizer = DiscussionVisualizer()
    visualizer.plot_discussion_flow(opinions)
    plt.figure()  # Create new figure for weights
    visualizer.plot_decision_weights(opinions)
    visualizer.show() 