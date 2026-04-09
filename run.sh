#!/bin/bash

# Start the background threat detection engine
python main.py &

# Start the Streamlit dashboard on the port provided by Render
streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
