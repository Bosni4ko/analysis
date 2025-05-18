This Python script analyzes participant performance in a visual search experiment involving emotional stimuli. The experiment measures how emotional valence (positive/negative) and distractor presence affect reaction time. <br>

The script performs the following analyses:

1. **Processes raw experiment data**:
   - Reads `stimulus_times.csv` and participant JSON logs from the `data/` folder.
   - Converts wide-format data into a tidy, long-format dataframe for analysis.

2. **Analyzes delayed responses for no-target stimuli**:
   - Computes "excess delay" when reaction time exceeds 20 seconds.
   - Categorizes delays into time intervals (e.g., 1–5 ms, >50 ms).
   - Outputs a summary and a delay distribution plot.

3. **Computes reaction time statistics**:
   - Per-stimulus mean and median reaction times.
   - Per-block (e.g., Stimuli 1–5) reaction statistics.
   - Trend plots for stimulus blocks 1–5 and 11–15.
   - Grouped bar charts comparing stimulus blocks.

4. **Performs correlation analysis**:
   - Examines the relationship between the number of distractors and reaction time.
   - Calculates Pearson correlation and visualizes results.

5. **Saves all outputs** to the `results/` folder:
   - `.png` figures
   - `.csv` files containing stimulus-level and block-level summaries

Structure:
project/ <br>
├── analyze_results.py # This analysis script <br>
├── data/ <br>
│ ├── stimulus_times.csv # Main timing dataset <br>
│ └── Participant_*.json # Session logs with metadata per trial <br>
├── results/ <br>
│ ├── *.png # Generated plots <br>
│ └── *.csv # Summary data exports <br>
