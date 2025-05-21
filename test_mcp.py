import unittest
import pandas as pd
import numpy as np
from typing import List, Dict
from rows_rag import AgentState

class TestMCP(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing
        self.sample_data = {
            'name': ['John', 'Jane', 'Mike'],
            'age': [30, 25, 35],
            'channel': ['email', 'phone', 'chat'],
            'episode': ['ep1', 'ep2', 'ep3']
        }
        self.df = pd.DataFrame(self.sample_data)
        
    def test_agent_state_initialization(self):
        """Test AgentState initialization with multi-channel data"""
        state = AgentState(df=self.df)
        self.assertIsNotNone(state.df)
        self.assertEqual(len(state.df), 3)
        self.assertEqual(state.current_row, 0)
        
    def test_get_current_row(self):
        """Test retrieving current row from multi-channel data"""
        state = AgentState(df=self.df)
        current_row = state.df.iloc[state.current_row]
        self.assertEqual(current_row['name'], 'John')
        self.assertEqual(current_row['channel'], 'email')
        
    def test_move_to_next_row(self):
        """Test moving to next row in multi-channel data"""
        state = AgentState(df=self.df)
        state.current_row += 1
        current_row = state.df.iloc[state.current_row]
        self.assertEqual(current_row['name'], 'Jane')
        self.assertEqual(current_row['channel'], 'phone')
        
    def test_channel_processing(self):
        """Test processing data from different channels"""
        state = AgentState(df=self.df)
        channels = state.df['channel'].unique()
        self.assertEqual(len(channels), 3)
        self.assertIn('email', channels)
        self.assertIn('phone', channels)
        self.assertIn('chat', channels)
        
    def test_episode_tracking(self):
        """Test tracking episodes across different channels"""
        state = AgentState(df=self.df)
        episodes = state.df['episode'].tolist()
        self.assertEqual(episodes, ['ep1', 'ep2', 'ep3'])
        
    def test_state_persistence(self):
        """Test state persistence with multi-channel data"""
        state = AgentState(df=self.df)
        state_dict = state.to_dict()
        new_state = AgentState.from_dict(state_dict)
        self.assertEqual(len(new_state.df), len(state.df))
        self.assertEqual(new_state.current_row, state.current_row)

if __name__ == '__main__':
    unittest.main() 