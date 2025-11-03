import pandas as pd
import duckdb
from datetime import datetime

class EgyptianTelecomTransformer:
    def __init__(self):
        self.operator_colors = {
            'vodafone': '#E60000',
            'orange': '#FF6600', 
            'etisalat': '#00A1E9',
            'we': '#800080'
        }
    
    def calculate_network_health_metrics(self, complaints_df):
        """Calculate daily network health scores"""
        
        # Convert date to datetime if it's not
        complaints_df['date'] = pd.to_datetime(complaints_df['date'])
        
        # Daily aggregation by operator
        daily_metrics = complaints_df.groupby(['operator', 'date']).agg({
            'sentiment_score': 'mean',
            'complaint_id': 'count',
            'likes': 'mean',
            'replies': 'mean'
        }).reset_index()
        
        daily_metrics.rename(columns={
            'complaint_id': 'daily_complaints',
            'sentiment_score': 'avg_sentiment',
            'likes': 'avg_likes',
            'replies': 'avg_replies'
        }, inplace=True)
        
        # Calculate network health score (0-100 scale)
        max_complaints = daily_metrics['daily_complaints'].max()
        
        daily_metrics['network_health_score'] = (
            (100 - (daily_metrics['daily_complaints'] / max_complaints * 50)) +  # Complaint volume (50%)
            ((daily_metrics['avg_sentiment'] + 1) * 25) +  # Sentiment (25%)
            (daily_metrics['avg_likes'] * 5)  # Engagement (25%)
        ).clip(0, 100)
        
        # Find dominant complaint category per day
        dominant_categories = complaints_df.groupby(['operator', 'date', 'complaint_category']).size().reset_index(name='count')
        idx = dominant_categories.groupby(['operator', 'date'])['count'].idxmax()
        dominant_categories = dominant_categories.loc[idx][['operator', 'date', 'complaint_category']]
        dominant_categories.rename(columns={'complaint_category': 'dominant_complaint_category'}, inplace=True)
        
        # Merge dominant categories
        daily_metrics = pd.merge(daily_metrics, dominant_categories, on=['operator', 'date'], how='left')
        
        # Calculate 7-day moving average of complaints
        daily_metrics['complaint_trend_7d'] = daily_metrics.groupby('operator')['daily_complaints'].transform(
            lambda x: x.rolling(7, min_periods=1).mean()
        )
        
        return daily_metrics.round(3)
    
    def create_operator_benchmarks(self, complaints_df, health_df):
        """Create operator performance benchmarks"""
        
        benchmarks = complaints_df.groupby('operator').agg({
            'sentiment_score': 'mean',
            'complaint_id': 'count',
            'likes': 'mean',
            'replies': 'mean'
        }).reset_index()
        
        benchmarks.rename(columns={
            'complaint_id': 'total_complaints',
            'sentiment_score': 'avg_sentiment',
            'likes': 'avg_likes',
            'replies': 'avg_replies'
        }, inplace=True)
        
        # Add health scores
        health_avg = health_df.groupby('operator')['network_health_score'].mean().reset_index()
        benchmarks = pd.merge(benchmarks, health_avg, on='operator')
        
        # Find most common complaint category per operator
        common_categories = complaints_df.groupby(['operator', 'complaint_category']).size().reset_index(name='count')
        idx = common_categories.groupby('operator')['count'].idxmax()
        common_categories = common_categories.loc[idx][['operator', 'complaint_category']]
        common_categories.rename(columns={'complaint_category': 'most_common_category'}, inplace=True)
        
        benchmarks = pd.merge(benchmarks, common_categories, on='operator')
        
        # Calculate performance rating
        def get_performance_rating(score):
            if score >= 80: return 'Excellent'
            elif score >= 60: return 'Good'
            elif score >= 40: return 'Fair'
            else: return 'Poor'
        
        benchmarks['performance_rating'] = benchmarks['network_health_score'].apply(get_performance_rating)
        
        return benchmarks.round(3)

# Transform the data
if __name__ == "__main__":
    # Load the complaints data
    complaints_df = pd.read_csv('egypt_telecom_complaints.csv')
    complaints_df['date'] = pd.to_datetime(complaints_df['date'])
    
    transformer = EgyptianTelecomTransformer()
    
    # Calculate health metrics
    health_df = transformer.calculate_network_health_metrics(complaints_df)
    health_df.to_csv('network_health_metrics.csv', index=False)
    print("✅ Saved network health metrics")
    
    # Calculate benchmarks
    benchmarks_df = transformer.create_operator_benchmarks(complaints_df, health_df)
    benchmarks_df.to_csv('operator_benchmarks.csv', index=False)
    print("✅ Saved operator benchmarks")
    
    print("\nOperator Benchmarks:")
    print(benchmarks_df)