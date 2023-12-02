"""
This file is used to run the dashboard
"""
from streamlit.web import bootstrap

real_script_name = 'wallet_analyzer_dashboard.py'
bootstrap.run(real_script_name, f'run.py {real_script_name}', [], {})
