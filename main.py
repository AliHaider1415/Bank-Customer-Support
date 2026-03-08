"""
Bank Customer Support Chatbot — Streamlit app (no API).
Run: streamlit run app_streamlit.py
Or:  python main.py
"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py", "--server.headless", "true"], check=True)
