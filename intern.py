#!/usr/bin/env python
# coding: utf-8

# In[44]:


import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px


# In[45]:


st.set_page_config(page_title="HealthKart Influencer Dashboard", layout="wide")
st.title("📊 HealthKart Influencer Campaign Dashboard")


# In[85]:


@st.cache_data
def load_data():
    # Influencers data
    influencers = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'name': ['JohnFit', 'YogaQueen', 'LiftKing', 'CardioCat', 'WellnessGuru'],
        'category': ['Fitness', 'Yoga', 'Bodybuilding', 'Cardio', 'Wellness'],
        'gender': ['M', 'F', 'M', 'F', 'M'],
        'follower_count': [500000, 300000, 450000, 280000, 360000],
        'platform': ['Instagram', 'YouTube', 'Instagram', 'Twitter', 'Instagram']
    })

    # Generate post dates
    post_dates = pd.date_range(start='2025-01-01', end='2025-07-24', periods=30)

    # Posts data
    posts = pd.DataFrame({
        'influencer_id': np.random.choice([1, 2, 3, 4, 5], size=30),
        'platform': np.random.choice(['Instagram', 'YouTube', 'Twitter'], size=30),
        'date': post_dates,
        'URL': [f"url{i}" for i in range(1, 31)],
        'caption': np.random.choice(['MB Whey', 'Yoga Mat', 'Mass Gainer', 'Creatine', 'Cardio Watch'], size=30),
        'reach': np.random.randint(80000, 150000, size=30),
        'likes': np.random.randint(2000, 8000, size=30),
        'comments': np.random.randint(50, 200, size=30)
    })

    # Generate tracking dates
    tracking_dates = pd.date_range(start='2025-01-01', end='2025-07-24', periods=30)

    # Tracking data
    tracking = pd.DataFrame({
        'source': np.random.choice(['InstaAds', 'YTAds', 'TwitterAds'], size=30),
        'campaign': np.random.choice(['MB July', 'Yoga July', 'Mass Gain May', 'Cardio June'], size=30),
        'influencer_id': np.random.choice([1, 2, 3, 4, 5], size=30),
        'user_id': [f'u{i}' for i in range(1, 31)],
        'product': np.random.choice(['Whey', 'Yoga Mat', 'Mass Gainer', 'Creatine', 'Heart Watch', 'Green Juice'], size=30),
        'date': tracking_dates,
        'orders': np.random.randint(1, 4, size=30),
        'revenue': np.random.randint(1200, 7000, size=30)
    })

    payouts = pd.DataFrame({  
        'influencer_id': [1, 2, 3, 4, 5],
        'basis': ['order', 'post', 'order', 'post', 'order'],
        'rate': [200, 1000, 250, 1200, 180],
        'orders': [5, 2, 4, 1, 3],
        'total_payout': [1000, 2000, 1000, 1200, 540]
    })

    return influencers, posts, tracking, payouts


# In[87]:


influencers, posts, tracking, payouts = load_data()


# In[89]:


# Sidebar Filters
st.sidebar.header("Filter Data")
platforms = st.sidebar.multiselect("Platform", influencers['platform'].unique(), default=influencers['platform'].unique())
categories = st.sidebar.multiselect("Category", influencers['category'].unique(), default=influencers['category'].unique())
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[pd.to_datetime('2025-01-01'), pd.to_datetime('2025-07-24')],
    min_value=pd.to_datetime('2025-01-01'),
    max_value=pd.to_datetime('2025-07-24')
)


# In[91]:


# Filtered Data
filtered_influencers = influencers[influencers['platform'].isin(platforms) & influencers['category'].isin(categories)]
filtered_posts = posts[(posts['date'] >= pd.to_datetime(date_range[0])) &
                       (posts['date'] <= pd.to_datetime(date_range[1])) &
                       (posts['influencer_id'].isin(filtered_influencers['ID']))]
filtered_tracking = tracking[(tracking['influencer_id'].isin(filtered_influencers['ID'])) &
                             (tracking['date'] >= pd.to_datetime(date_range[0])) &
                             (tracking['date'] <= pd.to_datetime(date_range[1]))]
filtered_payouts = payouts[payouts['influencer_id'].isin(filtered_influencers['ID'])]


# In[93]:


# Metrics
total_revenue = filtered_tracking['revenue'].sum()
total_payout = filtered_payouts['total_payout'].sum()
ROI = (total_revenue - total_payout) / total_payout if total_payout != 0 else 0
ROAS = total_revenue / total_payout if total_payout != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{total_revenue:.2f}")
col2.metric("Total Payout", f"₹{total_payout:.2f}")
col3.metric("ROI", f"{ROI:.2f}")
col4.metric("ROAS", f"{ROAS:.2f}")


# In[95]:


# Influencer ROAS Chart
influencer_performance = filtered_tracking.groupby('influencer_id').agg({'revenue': 'sum'}).reset_index()
influencer_performance = influencer_performance.merge(filtered_payouts[['influencer_id', 'total_payout']], on='influencer_id', how='left')
influencer_performance['ROAS'] = influencer_performance['revenue'] / influencer_performance['total_payout']
influencer_performance = influencer_performance.merge(influencers[['ID', 'name']], left_on='influencer_id', right_on='ID')
fig = px.bar(influencer_performance, x='name', y='ROAS', title="Influencer Revenue & ROAS", color='ROAS', text_auto='.2f')
st.plotly_chart(fig, use_container_width=True)


# In[97]:


# Insights
st.subheader("🔍 Insights")
if not influencer_performance.empty:
    top = influencer_performance.loc[influencer_performance['ROAS'].idxmax()]
    st.write(f"**Top Influencer**: {top['name']} with ROAS of {top['ROAS']:.2f}")
    poor = influencer_performance[influencer_performance['ROAS'] < 1.0]
    if not poor.empty:
        st.write("**Poor ROI Influencers:**")
        st.write(poor[['name', 'ROAS']])
else:
    st.write("No data available for selected filters.")


# In[99]:


# Payout Tracking Section
st.subheader("💸 Payout Tracking")
payout_details = filtered_influencers.merge(filtered_payouts, left_on='ID', right_on='influencer_id')
payout_details_display = payout_details[['name', 'basis', 'rate', 'orders', 'total_payout']]
payout_details_display.columns = ['Influencer', 'Basis', 'Rate', 'Orders', 'Total Payout']
st.dataframe(payout_details_display, use_container_width=True)


# In[101]:


# Optional Export
if st.button("📤 Export Data"):
    st.download_button("Download Influencer Performance", influencer_performance.to_csv(index=False), file_name="influencer_performance.csv")


# In[ ]:





# In[ ]:




