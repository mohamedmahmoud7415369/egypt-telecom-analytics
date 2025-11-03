import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Egyptian Telecom Analytics",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .operator-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🇪🇬 Egyptian Telecom Customer Experience Analytics</h1>', unsafe_allow_html=True)

# Connect to database
@st.cache_resource
def get_db_connection():
    try:
        conn = duckdb.connect('egypt_telecom.duckdb')
        # Test connection
        conn.execute("SELECT 1").fetchall()
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info("💡 Please run the data collection and transformation scripts first.")
        return None

conn = get_db_connection()

if conn is None:
    st.stop()

# Safe database query function
def safe_db_query(query, default_value=None):
    try:
        result = conn.execute(query).fetchall()
        return result
    except Exception as e:
        st.warning(f"Query failed: {e}")
        return default_value

# Safe dataframe query function
def safe_df_query(query, default_df=None):
    try:
        result = conn.execute(query).fetchdf()
        return result
    except Exception as e:
        st.warning(f"DataFrame query failed: {e}")
        return default_df if default_df is not None else pd.DataFrame()

# Sidebar filters
st.sidebar.title("🔧 Filters & Controls")

# Get available operators safely
operators_result = safe_db_query("SELECT DISTINCT operator FROM customer_complaints")
available_operators = ["All"] + [op[0] for op in operators_result] if operators_result else ["All"]

selected_operator = st.sidebar.selectbox(
    "Select Operator",
    available_operators
)

# Date range filter with safe defaults
try:
    min_date_result = safe_db_query("SELECT MIN(date) FROM customer_complaints")
    max_date_result = safe_db_query("SELECT MAX(date) FROM customer_complaints")
    
    if min_date_result and max_date_result:
        min_date = min_date_result[0][0]
        max_date = max_date_result[0][0]
    else:
        min_date = datetime.now().date() - timedelta(days=30)
        max_date = datetime.now().date()
except:
    min_date = datetime.now().date() - timedelta(days=30)
    max_date = datetime.now().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Main dashboard layout

# Key Metrics Row
st.markdown("### 📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_complaints_result = safe_db_query("SELECT COUNT(*) FROM customer_complaints")
    total_complaints = total_complaints_result[0][0] if total_complaints_result else 0
    st.metric("Total Complaints", f"{total_complaints:,}")

with col2:
    avg_sentiment_result = safe_db_query("SELECT AVG(sentiment_score) FROM customer_complaints")
    avg_sentiment = avg_sentiment_result[0][0] if avg_sentiment_result else 0.0
    st.metric("Average Sentiment", f"{avg_sentiment:.3f}")

with col3:
    best_operator_result = safe_db_query("""
        SELECT operator, network_health_score 
        FROM operator_benchmarks 
        ORDER BY network_health_score DESC 
        LIMIT 1
    """)
    
    if best_operator_result and len(best_operator_result) > 0:
        best_operator = best_operator_result[0]
        st.metric("Best Performer", f"{best_operator[0]}", f"{best_operator[1]:.1f}")
    else:
        st.metric("Best Performer", "N/A", "0.0")

with col4:
    worst_category_result = safe_db_query("""
        SELECT complaint_category, COUNT(*) 
        FROM customer_complaints 
        GROUP BY complaint_category 
        ORDER BY COUNT(*) DESC 
        LIMIT 1
    """)
    
    if worst_category_result and len(worst_category_result) > 0:
        worst_category = worst_category_result[0]
        st.metric("Most Common Issue", worst_category[0])
    else:
        st.metric("Most Common Issue", "N/A")

# Operator Performance Comparison
st.markdown("### 🏆 Operator Performance Comparison")

col1, col2 = st.columns(2)

with col1:
    # Network Health Over Time
    health_data = safe_df_query("""
        SELECT operator, date, network_health_score 
        FROM network_health_daily 
        ORDER BY date
    """)
    
    if not health_data.empty:
        fig = px.line(health_data, x='date', y='network_health_score', color='operator',
                      title="📈 Network Health Score Over Time",
                      labels={'network_health_score': 'Health Score', 'date': 'Date'},
                      color_discrete_map={
                          'vodafone': '#E60000',
                          'orange': '#FF6600',
                          'etisalat': '#00A1E9', 
                          'we': '#800080'
                      })
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No network health data available")

with col2:
    # Complaint Categories by Operator
    category_data = safe_df_query("""
        SELECT operator, complaint_category, COUNT(*) as count
        FROM customer_complaints
        GROUP BY operator, complaint_category
    """)
    
    if not category_data.empty:
        fig = px.bar(category_data, x='operator', y='count', color='complaint_category',
                     title="📋 Complaint Categories by Operator",
                     barmode='stack',
                     labels={'count': 'Number of Complaints', 'operator': 'Operator'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No complaint category data available")

# Geographic Analysis
st.markdown("### 🗺️ Geographic Performance Analysis")

geo_data = safe_df_query("""
    SELECT governorate, operator, COUNT(*) as complaints, 
           AVG(sentiment_score) as avg_sentiment
    FROM customer_complaints
    WHERE governorate != 'Unknown'
    GROUP BY governorate, operator
""")

if not geo_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment by Governorate
        fig = px.bar(geo_data, x='governorate', y='avg_sentiment', color='operator',
                     title="😊 Average Sentiment by Governorate",
                     barmode='group',
                     color_discrete_map={
                         'vodafone': '#E60000',
                         'orange': '#FF6600',
                         'etisalat': '#00A1E9',
                         'we': '#800080'
                     })
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Complaint Distribution Heatmap
        try:
            pivot_data = geo_data.pivot_table(
                index='governorate', columns='operator', values='complaints', fill_value=0
            )
            fig = px.imshow(pivot_data, 
                           title="🔥 Complaint Distribution Heatmap",
                           aspect="auto",
                           color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Not enough data for heatmap visualization")
else:
    st.info("No geographic data available")

# Recent Complaints Section
st.markdown("### 📝 Recent Customer Complaints")

recent_complaints = safe_df_query("""
    SELECT operator, complaint_text, complaint_category, sentiment_score, date, governorate
    FROM customer_complaints
    ORDER BY date DESC, collection_timestamp DESC
    LIMIT 15
""")

if not recent_complaints.empty:
    # Color code sentiment
    def color_sentiment(val):
        try:
            if val > 0.1:
                return 'color: green'
            elif val < -0.1:
                return 'color: red'
            else:
                return 'color: orange'
        except:
            return 'color: black'
    
    styled_complaints = recent_complaints.style.applymap(color_sentiment, subset=['sentiment_score'])
    st.dataframe(styled_complaints, use_container_width=True, height=400)
else:
    st.info("No recent complaints data available")

# Operator-specific deep dive
if selected_operator != "All":
    st.markdown(f"### 🔍 Deep Dive: {selected_operator.upper()}")
    
    op_data = safe_df_query(f"""
        SELECT * FROM network_health_daily 
        WHERE operator = '{selected_operator}'
        ORDER BY date
    """)
    
    if not op_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily complaints trend
            fig = px.area(op_data, x='date', y='daily_complaints',
                         title=f"📊 Daily Complaints - {selected_operator}",
                         labels={'daily_complaints': 'Complaints', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment trend
            fig = px.line(op_data, x='date', y='avg_sentiment',
                         title=f"😊 Average Sentiment - {selected_operator}",
                         labels={'avg_sentiment': 'Sentiment Score', 'date': 'Date'})
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No detailed data available for {selected_operator}")

# Data Quality Check
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Data Status")

# Check table existence and row counts
tables_to_check = ['customer_complaints', 'network_health_daily', 'operator_benchmarks']
for table in tables_to_check:
    try:
        count_result = safe_db_query(f"SELECT COUNT(*) FROM {table}")
        count = count_result[0][0] if count_result else 0
        st.sidebar.text(f"{table}: {count} rows")
    except:
        st.sidebar.text(f"{table}: Not found")

# Footer
st.markdown("---")
st.markdown("""
**📝 Note:** This dashboard uses synthetic Egyptian telecom complaints data for demonstration purposes.  
**🕒 Last Updated:** {}  
**📊 Data Source:** Generated synthetic data representing typical Egyptian telecom customer complaints
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")))

# Debug information (collapsible)
with st.expander("🔧 Debug Information"):
    st.write("### Database Tables Check")
    for table in tables_to_check:
        try:
            sample = safe_df_query(f"SELECT * FROM {table} LIMIT 1")
            st.write(f"**{table}:** {len(sample)} sample rows")
            if len(sample) > 0:
                st.write(sample.columns.tolist())
        except Exception as e:
            st.write(f"**{table}:** Error - {e}")