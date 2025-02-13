from flask import Flask, render_template, Response
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from scipy.signal import find_peaks
import seaborn as sns
import numpy as np
import io
import plotly.graph_objects as go
#kaleido

app = Flask(__name__)

# Load the fixed CSV file
FILE_PATH = "data.csv"
df = pd.read_csv(FILE_PATH)
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d-%m-%Y %H:%M:%S")

df = df.sort_values("Timestamp")

# Function to generate and return each chart

def chart_1():
    fig, ax = plt.subplots(figsize=(15, 6))
    sns.lineplot(x=df["Timestamp"], y=df["Values"], label="Voltage", color="blue")
    
    ax.xaxis.set_major_formatter(DateFormatter("%d-%m-%Y %H:%M:%S"))
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Voltage")
    ax.set_title("Voltage Over Time")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend()
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img


def chart_2():
    df["Moving_Avg"] = df["Values"].rolling(window=5).mean()
    fig, ax = plt.subplots(figsize=(15, 6))
    sns.lineplot(x=df["Timestamp"], y=df["Values"], label="Voltage", color="blue")
    sns.lineplot(x=df["Timestamp"], y=df["Moving_Avg"], label="5-Day Moving Average", color="red")
    
    ax.xaxis.set_major_formatter(DateFormatter("%d-%m-%Y %H:%M:%S"))
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Voltage")
    ax.set_title("Voltage with 5-Day Moving Average")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img


def chart_3():
    df["Moving_Avg"] = df["Values"].rolling(window=5).mean()
    peaks, _ = find_peaks(df["Values"])
    lows, _ = find_peaks(-df["Values"])
    
    fig, ax = plt.subplots(figsize=(15, 6))
    sns.lineplot(x=df["Timestamp"], y=df["Values"], label="Voltage", color="blue")
    sns.lineplot(x=df["Timestamp"], y=df["Moving_Avg"], label="5-Day Moving Average", color="red")
    
    ax.scatter(df["Timestamp"].iloc[peaks], df["Values"].iloc[peaks], color="green", label="Peaks", marker="^")
    ax.scatter(df["Timestamp"].iloc[lows], df["Values"].iloc[lows], color="orange", label="Lows", marker="v")
    
    ax.xaxis.set_major_formatter(DateFormatter("%d-%m-%Y %H:%M:%S"))
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Voltage")
    ax.set_title("Voltage Over Time with Peaks & Lows")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img


def chart_4():
    df["1000_MA"] = df["Values"].rolling(window=1000).mean()
    df["5000_MA"] = df["Values"].rolling(window=5000).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["Values"],
        mode="lines",
        name="Original Value",
        line=dict(color="blue")
    ))
    
    fig.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["1000_MA"],
        mode="lines",
        name="1000 Value MA",
        line=dict(color="red")
    ))
    
    fig.add_trace(go.Scatter(
        x=df["Timestamp"],
        y=df["5000_MA"],
        mode="lines",
        name="5000 Value MA",
        line=dict(color="green")
    ))
    
    fig.update_layout(
        title="Values with 1000 and 5000 Value Moving Averages",
        xaxis_title="Timestamp",
        yaxis_title="Values",
        legend_title="Legend",
        xaxis=dict(
            tickangle=-45,
            tickformat="%d-%m-%Y %H:%M:%S",
            tickmode="auto",
        ),
        template="plotly_white"
    )
    
    img = io.BytesIO()
    fig.write_image(img, format='png')
    img.seek(0)
    return img



def chart_5():
    df["dV/dt"] = df["Values"].diff()
    df["d²V/dt²"] = df["dV/dt"].diff()
    downward_acceleration_points = df[df["d²V/dt²"] < df["d²V/dt²"].quantile(0.05)]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Timestamp"], df["Values"], label="Values", color="blue")
    ax.scatter(
        downward_acceleration_points["Timestamp"],
        downward_acceleration_points["Values"],
        color="red",
        label="Downward Acceleration Points"
    )
    
    ax.xaxis.set_major_formatter(DateFormatter("%d-%m-%Y %H:%M:%S"))
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Values")
    plt.xticks(rotation=45)
    plt.legend()
    plt.title("Values Drop Acceleration Points")
    plt.grid(True)
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)
    return img



# Define routes for each chart
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/1')
def route_chart_1():
    img = chart_1()
    return Response(img.getvalue(), mimetype='image/png')


@app.route('/2')
def route_chart_2():
    img = chart_2()
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/3')
def route_chart_3():
    img = chart_3()
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/4')
def route_chart_4():
    img = chart_4()
    return Response(img.getvalue(), mimetype='image/png')

@app.route('/5')
def route_chart_5():
    img = chart_5()
    return Response(img.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)
