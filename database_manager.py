import duckdb
import pandas as pd
import os

class TelecomDatabase:
    def __init__(self, db_path='egypt_telecom.duckdb'):
        self.db_path = db_path
        # Remove existing database to avoid conflicts
        if os.path.exists(db_path):
            os.remove(db_path)
        self.conn = duckdb.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        
        # Customer complaints table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS customer_complaints (
                complaint_id INTEGER PRIMARY KEY,
                operator VARCHAR,
                complaint_text VARCHAR,
                complaint_category VARCHAR,
                sentiment_score DECIMAL(4,3),
                date DATE,
                governorate VARCHAR,
                likes INTEGER,
                replies INTEGER,
                source VARCHAR,
                collection_timestamp TIMESTAMP
            )
        """)
        
        # Network health daily table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS network_health_daily (
                operator VARCHAR,
                date DATE,
                daily_complaints INTEGER,
                avg_sentiment DECIMAL(4,3),
                avg_likes DECIMAL(6,3),
                avg_replies DECIMAL(6,3),
                network_health_score DECIMAL(5,2),
                dominant_complaint_category VARCHAR,
                complaint_trend_7d DECIMAL(6,3),
                PRIMARY KEY (operator, date)
            )
        """)
        
        # Operator benchmarks table - FIXED: corrected avg_sentiment precision
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS operator_benchmarks (
                operator VARCHAR PRIMARY KEY,
                total_complaints INTEGER,
                avg_sentiment DECIMAL(4,3),  -- Changed from DECIMAL(5,2) to DECIMAL(4,3)
                avg_likes DECIMAL(6,3),
                avg_replies DECIMAL(6,3),
                network_health_score DECIMAL(5,2),
                most_common_category VARCHAR,
                performance_rating VARCHAR
            )
        """)
        
        print("✅ Database tables created successfully!")
    
    def load_data(self):
        """Load CSV data into database"""
        
        try:
            # Load complaints data
            if not os.path.exists('egypt_telecom_complaints.csv'):
                raise FileNotFoundError("Complaints CSV file not found")
                
            complaints_df = pd.read_csv('egypt_telecom_complaints.csv')
            print(f"Loaded complaints data: {len(complaints_df)} rows")
            
            # Ensure date is properly formatted
            complaints_df['date'] = pd.to_datetime(complaints_df['date']).dt.date
            
            # Register and insert complaints data
            self.conn.register('complaints_df', complaints_df)
            self.conn.execute("""
                INSERT INTO customer_complaints 
                SELECT * FROM complaints_df
            """)
            print(f"✅ Loaded {len(complaints_df)} complaints into database")
            
        except Exception as e:
            print(f"❌ Error loading complaints data: {e}")
            return
        
        try:
            # Load health metrics
            if not os.path.exists('network_health_metrics.csv'):
                raise FileNotFoundError("Health metrics CSV file not found")
                
            health_df = pd.read_csv('network_health_metrics.csv')
            print(f"Loaded health data: {len(health_df)} rows")
            
            # Ensure date is properly formatted
            health_df['date'] = pd.to_datetime(health_df['date']).dt.date
            
            # Register and insert health data
            self.conn.register('health_df', health_df)
            self.conn.execute("""
                INSERT INTO network_health_daily 
                SELECT * FROM health_df
            """)
            print(f"✅ Loaded {len(health_df)} health records into database")
            
        except Exception as e:
            print(f"❌ Error loading health metrics: {e}")
            return
        
        try:
            # Load benchmarks
            if not os.path.exists('operator_benchmarks.csv'):
                raise FileNotFoundError("Benchmarks CSV file not found")
                
            benchmarks_df = pd.read_csv('operator_benchmarks.csv')
            print(f"Loaded benchmarks data: {len(benchmarks_df)} rows")
            
            # FIX: Ensure avg_sentiment is properly scaled (already between -1 and 1)
            # Remove the division by 100 that was causing the error
            if 'avg_sentiment' in benchmarks_df.columns:
                # Convert to float and ensure it's within proper range
                benchmarks_df['avg_sentiment'] = pd.to_numeric(benchmarks_df['avg_sentiment'], errors='coerce')
                # No division needed - sentiment is already between -1 and 1
            
            # Register and insert benchmarks data
            self.conn.register('benchmarks_df', benchmarks_df)
            self.conn.execute("""
                INSERT INTO operator_benchmarks 
                SELECT * FROM benchmarks_df
            """)
            print("✅ Loaded operator benchmarks into database")
            
        except Exception as e:
            print(f"❌ Error loading benchmarks: {e}")
            return
        
        print("🎉 All data loaded successfully!")
    
    def run_analytics(self):
        """Run analytical queries"""
        
        print("\n" + "="*50)
        print("📊 EGYPTIAN TELECOM ANALYTICS DASHBOARD")
        print("="*50)
        
        try:
            # 1. Operator Performance Ranking
            print("\n1. 🏆 OPERATOR PERFORMANCE RANKING:")
            result = self.conn.execute("""
                SELECT 
                    operator,
                    ROUND(network_health_score, 2) as health_score,
                    performance_rating,
                    total_complaints,
                    most_common_category,
                    ROUND(avg_sentiment, 3) as sentiment
                FROM operator_benchmarks
                ORDER BY health_score DESC
            """).fetchdf()
            print(result.to_string(index=False))
            
        except Exception as e:
            print(f"Error in operator performance query: {e}")
        
        try:
            # 2. Complaint Category Analysis
            print("\n2. 📋 COMPLAINT CATEGORY BREAKDOWN:")
            result = self.conn.execute("""
                SELECT 
                    complaint_category,
                    COUNT(*) as complaint_count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_complaints), 2) as percentage,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment
                FROM customer_complaints
                GROUP BY complaint_category
                ORDER BY complaint_count DESC
            """).fetchdf()
            print(result.to_string(index=False))
            
        except Exception as e:
            print(f"Error in complaint category query: {e}")
        
        try:
            # 3. Geographic Analysis
            print("\n3. 🗺️ COMPLAINTS BY GOVERNORATE:")
            result = self.conn.execute("""
                SELECT 
                    governorate,
                    COUNT(*) as complaint_count,
                    ROUND(AVG(sentiment_score), 3) as avg_sentiment,
                    CASE 
                        WHEN AVG(sentiment_score) > 0 THEN 'Positive'
                        WHEN AVG(sentiment_score) > -0.3 THEN 'Neutral' 
                        ELSE 'Negative'
                    END as sentiment_category
                FROM customer_complaints
                WHERE governorate != 'Unknown'
                GROUP BY governorate
                ORDER BY complaint_count DESC
                LIMIT 10
            """).fetchdf()
            print(result.to_string(index=False))
            
        except Exception as e:
            print(f"Error in geographic analysis query: {e}")
        
        try:
            # 4. Weekly Trends
            print("\n4. 📈 WEEKLY PERFORMANCE TRENDS:")
            result = self.conn.execute("""
                SELECT 
                    operator,
                    DATE_TRUNC('week', date) as week_start,
                    ROUND(AVG(network_health_score), 2) as weekly_health_score,
                    SUM(daily_complaints) as weekly_complaints
                FROM network_health_daily
                GROUP BY operator, DATE_TRUNC('week', date)
                ORDER BY week_start DESC, weekly_health_score DESC
                LIMIT 12
            """).fetchdf()
            print(result.to_string(index=False))
            
        except Exception as e:
            print(f"Error in weekly trends query: {e}")

# Initialize database
if __name__ == "__main__":
    try:
        db = TelecomDatabase()
        db.load_data()
        db.run_analytics()
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("1. Make sure all CSV files exist in the same directory")
        print("2. Run data_collector.py and data_transformer.py first")
        print("3. Check that all required columns are present in CSV files")