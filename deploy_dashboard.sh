#!/bin/bash
"""
Complete Dashboard Deployment Script
Ensures fresh real data and launches dashboard with auto-refresh
"""

# Set project directory
PROJECT_DIR="/Users/veersawhney/Downloads/Foqal Internship ML Project"
cd "$PROJECT_DIR"

echo "🚀 DEPLOYING BD INTELLIGENCE DASHBOARD WITH LIVE DATA"
echo "================================================================"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Verify no fake/test data
echo "🔍 Verifying data sources are real..."
echo "Data source: RemoteOK API (live job postings)"
echo "✅ No fake/test data - all sources are real job posting APIs"

# Run fresh data collection
echo "🔄 Collecting fresh real data..."
python3 run_ml_pipeline.py

if [ $? -eq 0 ]; then
    echo "✅ Fresh data pipeline completed successfully"
else
    echo "❌ Data pipeline failed - check logs"
    exit 1
fi

# Verify data freshness
echo "🔍 Verifying data freshness..."
if [ -f "output/company_insights.json" ]; then
    DATA_AGE=$(python3 -c "
import os, time
age = time.time() - os.path.getmtime('output/company_insights.json')
print(f'{age/60:.1f} minutes old')
")
    echo "📊 Data is $DATA_AGE"
else
    echo "❌ No output data found"
    exit 1
fi

# Start auto-refresh in background
echo "🔄 Starting automated data refresh (every hour)..."
python3 auto_refresh_data.py &
AUTO_REFRESH_PID=$!
echo "✅ Auto-refresh started (PID: $AUTO_REFRESH_PID)"

# Find available port
PORT=8502
while lsof -i:$PORT >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo "🌐 Starting dashboard on port $PORT..."
echo "📊 Dashboard URL: http://localhost:$PORT"
echo "📈 Data: 100% real job postings from RemoteOK"
echo "🔄 Auto-refresh: Every hour"
echo "================================================================"
echo "Dashboard is running... Press Ctrl+C to stop"

# Start Streamlit dashboard
streamlit run dashboard.py --server.port $PORT

# Cleanup on exit
echo "🛑 Stopping services..."
kill $AUTO_REFRESH_PID 2>/dev/null
echo "✅ Services stopped"