import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(page_title="Mutual Fund CAGR Analysis", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('MF_CAGR_Analysis_API_Names.xlsx')
    # Convert percentage strings back to floats for plotting
    for col in ['1st year cagr', '2nd year cagr', '3rd year cagr']:
        df[col] = df[col].str.replace('%', '').replace('N/A', '0').astype(float)
    return df

df = load_data()

st.title("📊 Mutual Fund CAGR Analysis Dashboard (2019-2022)")
st.markdown("""
This dashboard analyzes the performance of various mutual fund schemes based on the day of the month the investment was initiated. 
It helps identify the **optimal day of the month** for investing to maximize returns.
""")

# Sidebar filters
st.sidebar.header("Filters")
selected_schemes = st.sidebar.multiselect(
    "Select Schemes to Compare",
    options=df['scheme name'].unique(),
    default=df['scheme name'].unique()[:3]
)

# Filter data
filtered_df = df[df['scheme name'].isin(selected_schemes)]

# 1. Best Day Analysis
st.header("🔍 Best Day of the Month to Invest")
col1, col2 = st.columns(2)

with col1:
    metric = st.selectbox("Select CAGR Period", ["1st year cagr", "2nd year cagr", "3rd year cagr"])
    
    # Calculate average CAGR per day across selected schemes
    avg_cagr_per_day = filtered_df.groupby('Day of Month')[metric].mean().reset_index()
    best_day = avg_cagr_per_day.loc[avg_cagr_per_day[metric].idxmax()]
    
    st.success(f"Across selected schemes, the best day to invest for **{metric}** is the **{int(best_day['Day of Month'])}th** of the month with an average return of **{best_day[metric]:.2f}%**.")

    fig_avg = px.line(avg_cagr_per_day, x='Day of Month', y=metric, 
                      title=f"Average {metric} by Day of Month",
                      labels={metric: "Average CAGR (%)", "Day of Month": "Day of Month (1-28)"})
    st.plotly_chart(fig_avg, use_container_width=True)

with col2:
    # Heatmap of returns
    pivot_df = filtered_df.pivot(index='scheme name', columns='Day of Month', values=metric)
    fig_heat = px.imshow(pivot_df, 
                         labels=dict(x="Day of Month", y="Scheme Name", color="CAGR (%)"),
                         title=f"Heatmap of {metric} across Schemes and Days",
                         aspect="auto")
    st.plotly_chart(fig_heat, use_container_width=True)

# 2. Scheme Comparison
st.header("⚖️ Scheme Comparison")
fig_comp = px.box(filtered_df, x='scheme name', y=metric, 
                  title=f"Distribution of {metric} for Selected Schemes",
                  points="all", color='scheme name')
st.plotly_chart(fig_comp, use_container_width=True)

# 3. Detailed Insights Table
st.header("📋 Detailed Performance Data")
st.dataframe(filtered_df.sort_values(['scheme name', 'Day of Month']), use_container_width=True)

# 4. Summary Insights
st.header("💡 Key Insights")
best_per_scheme = []
for scheme in selected_schemes:
    scheme_data = df[df['scheme name'] == scheme]
    best_row = scheme_data.loc[scheme_data[metric].idxmax()]
    best_per_scheme.append({
        "Scheme": scheme,
        "Best Day": int(best_row['Day of Month']),
        "Max CAGR (%)": f"{best_row[metric]:.2f}%"
    })

st.table(pd.DataFrame(best_per_scheme))

st.markdown("""
**Note:** The analysis assumes a one-time investment of ₹5,000 on the specified day in January 2019 and calculates the CAGR for the subsequent 1, 2, and 3 years.
""")
