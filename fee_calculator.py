import pandas as pd
import numpy as np

def calculate_differential_fees(df: pd.DataFrame, max_fee_rate: float = 0.20, min_fee_rate: float = 0.06) -> pd.DataFrame:
    """
    Calculate differential fee rates based on total transaction amounts.
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with '총금액' column
        max_fee_rate (float): Maximum fee rate (default: 0.20 or 20%)
        min_fee_rate (float): Minimum fee rate (default: 0.06 or 6%)
    
    Returns:
        pd.DataFrame: DataFrame with added columns for differential fee rate and expected profit
    """
    # Create a copy to avoid modifying the original dataframe
    df_copy = df.copy()
    
    # Set pandas display format for float values
    pd.options.display.float_format = '{:.2f}'.format
    
    # Calculate mean total amount for sensitivity parameter
    mean_total = df_copy['총금액'].mean()
    sensitivity = 1 / mean_total
    
    # Calculate differential fee rate using exponential decay
    df_copy['차등_수수료율'] = max_fee_rate * np.exp(-sensitivity * df_copy['총금액'])
    
    # Apply minimum fee rate constraint
    df_copy['차등_수수료율'] = df_copy['차등_수수료율'].apply(lambda x: min_fee_rate if x < min_fee_rate else x)
    
    # Calculate expected profit
    df_copy['예상_영업이익'] = df_copy['총금액'] * df_copy['차등_수수료율']
    
    return df_copy

def analyze_fee_distribution(df: pd.DataFrame) -> dict:
    """
    Analyze the distribution of calculated fees.
    
    Args:
        df (pd.DataFrame): DataFrame with calculated fees
        
    Returns:
        dict: Dictionary containing fee distribution statistics
    """
    stats = {
        'mean_fee_rate': df['차등_수수료율'].mean(),
        'min_fee_rate': df['차등_수수료율'].min(),
        'max_fee_rate': df['차등_수수료율'].max(),
        'mean_profit': df['예상_영업이익'].mean(),
        'total_profit': df['예상_영업이익'].sum(),
        'total_transactions': len(df)
    }
    
    return stats 