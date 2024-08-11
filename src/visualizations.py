# visualizations.py

import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import streamlit as st

def generate_bar_chart(data: pd.DataFrame, x_column: str, y_column: str):
    plt.figure(figsize=(10, 6))
    plt.bar(data[x_column], data[y_column])
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f'Bar Chart of {y_column} vs {x_column}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Display the image in Streamlit
    st.image(buffer, use_column_width=True)
    plt.close()

def generate_pie_chart(data: pd.DataFrame, labels_column: str, values_column: str):
    plt.figure(figsize=(8, 8))
    plt.pie(data[values_column], labels=data[labels_column], autopct='%1.1f%%', startangle=140)
    plt.title(f'Pie Chart of {values_column} by {labels_column}')

    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Display the image in Streamlit
    st.image(buffer, use_column_width=True)
    plt.close()

def generate_line_chart(data: pd.DataFrame, x_column: str, y_column: str):
    plt.figure(figsize=(10, 6))
    plt.plot(data[x_column], data[y_column], marker='o')
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f'Line Chart of {y_column} over {x_column}')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Display the image in Streamlit
    st.image(buffer, use_column_width=True)
    plt.close()
