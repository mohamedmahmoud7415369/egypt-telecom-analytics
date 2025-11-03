#!/usr/bin/env python3
"""
Egyptian Telecom Analytics - Main Execution Script
Run this file to execute the complete project
"""

import os
import sys
from datetime import datetime

def main():
    print("🚀 Starting Egyptian Telecom Analytics Project...")
    print("=" * 60)
    
    # Check if required files exist, if not generate data
    if not os.path.exists('egypt_telecom_complaints.csv'):
        print("\n📊 PHASE 1: Data Collection")
        print("-" * 30)
        
        from data_collector import EgyptianTelecomDataCollector
        collector = EgyptianTelecomDataCollector()
        
        print("Generating synthetic Egyptian telecom complaints...")
        df_complaints = collector.generate_realistic_complaints(600)
        collector.save_complaints_data(df_complaints)
        print(f"✅ Generated {len(df_complaints)} realistic complaints")
    
    # Phase 2: Data Transformation
    print("\n🔄 PHASE 2: Data Transformation")
    print("-" * 30)
    
    from data_transformer import EgyptianTelecomTransformer
    transformer = EgyptianTelecomTransformer()
    
    # Load and transform data
    complaints_df = pd.read_csv('egypt_telecom_complaints.csv')
    complaints_df['date'] = pd.to_datetime(complaints_df['date'])
    
    health_df = transformer.calculate_network_health_metrics(complaints_df)
    health_df.to_csv('network_health_metrics.csv', index=False)
    print("✅ Network health metrics calculated")
    
    benchmarks_df = transformer.create_operator_benchmarks(complaints_df, health_df)
    benchmarks_df.to_csv('operator_benchmarks.csv', index=False)
    print("✅ Operator benchmarks calculated")
    
    # Phase 3: Database Setup
    print("\n🗄️ PHASE 3: Data Warehouse")
    print("-" * 30)
    
    from database_manager import TelecomDatabase
    db = TelecomDatabase()
    db.load_data()
    print("✅ Data loaded into database")
    
    # Run analytics
    print("\n📈 PHASE 4: Analytics")
    print("-" * 30)
    db.run_analytics()
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 PROJECT SETUP COMPLETED SUCCESSFULLY!")
    print("\n🚀 NEXT STEPS:")
    print("1. Run the dashboard: streamlit run telecom_dashboard.py")
    print("2. Open http://localhost:8501 in your browser")
    print("3. Explore the Egyptian telecom analytics!")
    print("\n💡 TIPS:")
    print("- Use the sidebar filters to analyze specific operators")
    print("- Hover over charts for detailed information")
    print("- Check the geographic analysis for regional insights")

if __name__ == "__main__":
    import pandas as pd
    main()