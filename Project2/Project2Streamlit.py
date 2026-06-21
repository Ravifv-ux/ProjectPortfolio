import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from Project2 import getResponse, loadPrompts
import json
from datetime import datetime

#The Basics Required
promptfile = "prompts.json"

with open(promptfile, 'r') as file:

    data = json.load(file)
    
prompts = [item['text'] for item in data if 'text' in item]
id  = [item['id'] for item in data if 'id' in item]

# ANSI COLORS
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
now = datetime.now()
#Ends Here


fig = go.Figure()
conn = sqlite3.connect("responses.db")
df = pd.read_sql("SELECT * FROM responses", conn)

st.title("LLM GRAPH DASHBOARD")
st.dataframe(df)

def makeTable(index, column):
    latency_df = (
    df.groupby(index)[column]
    .mean()
    .reset_index()
)

    st.subheader(f"Average {column} Per Run")

    st.line_chart(
    latency_df.set_index("runid"), x_label = "run_id", y_label = f"Average {column}"
)

makeTable("runid", "latency")
makeTable("runid", "rating")

def minmax(index, column):
    min_df = df.groupby(index)[column].min().reset_index()
    max_df = df.groupby(index)[column].max().reset_index()

    st.markdown('•The points on the scatter plot in blue are the prompts that are consistently rated highly by the model, •The area shaded in red is where the model performs below average, while blue is viceversa')
    st.markdown(f"\t\t\t•Min and Max {column} Per Run")


    fig.add_trace(
    go.Scatter(
        x=max_df["runid"],
        y=max_df["rating"],
        mode="lines",
        name="Max"
        )
    )

    fig.add_trace(
    go.Scatter(
        x=min_df["runid"],
        y=min_df["rating"],
        mode="lines",
        fill="tonexty",
        name="Min"
        )
    )
    threshold = df["rating"].mean()

    fig.add_hrect(
    y0=6,
    y1=threshold,
    fillcolor="red",
    opacity=0.2,
    line_width=0
        )   
    fig.update_yaxes(range = [0, 10])

    fig.add_hrect(
    y0=threshold,
    y1=df["rating"].max(),
    fillcolor="blue",
    opacity=0.1,
    line_width=0
    )

    st.plotly_chart(fig)
    
minmax("runid", "rating")

if st.button("Refresh Data"):
    conn = sqlite3.connect("responses.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS RESPONSES")
    conn.commit()
    prompts, id = loadPrompts()
    getResponse(prompts, id)
    getResponse(prompts, id)
    print(f"{Color.GREEN}Data refreshed successfully.{Color.RESET}")
    st.subheader('•Data refreshed successfully. Refreshing page now...')
    st.rerun()





