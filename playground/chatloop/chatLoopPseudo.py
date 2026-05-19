# moved to app/regressWorkoutWeek.py — run: python app/regressWorkoutWeek.py
import runpy
import os
import sys

repoRoot=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
script=os.path.join(repoRoot,'app','regressWorkoutWeek.py')
sys.argv=[script]+sys.argv[1:]
runpy.run_path(script,run_name='__main__')
