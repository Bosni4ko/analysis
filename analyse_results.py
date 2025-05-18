import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import glob
import os
from scipy.stats import pearsonr
#Define input and output folder
DATA_FOLDER = "data"
RESULTS_FOLDER = "results"

os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Load data
df = pd.read_csv(os.path.join(DATA_FOLDER, "stimulus_times.csv"))

# Prepare long format for easier analysis
long_df = pd.DataFrame()

for i in range(1, 21):
    temp_df = df[["participant_number", f"stimulus_{i}_time", f"stimulus_{i}_no_target"]].copy()
    temp_df.columns = ["participant", "reaction_time", "no_target"]
    temp_df["stimulus"] = i
    long_df = pd.concat([long_df, temp_df], ignore_index=True)

# --- 6: Analyze no-target delays (reaction time beyond 20s) ---
no_target_df = long_df[long_df["no_target"] == True].copy()
no_target_df["excess_delay"] = no_target_df["reaction_time"] - 20.0

# Filter invalid negatives
invalid_rows = no_target_df[no_target_df["excess_delay"] < 0]
if not invalid_rows.empty:
    print("\n⚠️ Warning: Found delays less than 0 (reaction_time < 20s) — check data")
    print(invalid_rows)
    no_target_df = no_target_df[no_target_df["excess_delay"] >= 0]

# Core statistics
max_delay = no_target_df["excess_delay"].max()
mean_delay = no_target_df["excess_delay"].mean()
std_delay = no_target_df["excess_delay"].std()
count_total = len(no_target_df)

# Print statistics
print(f"\n=== Delay Statistics ===")
print(f"Total valid no-target trials: {count_total}")
print(f"Maximum delay: {max_delay:.6f} sec")
print(f"Mean delay:    {mean_delay:.6f} sec")
print(f"Std deviation: {std_delay:.6f} sec")

# Delay bins and labels
bins = [0, 0.001, 0.005, 0.010, 0.025, 0.050, float("inf")]
labels = ["<1ms", "1–5ms", "5–10ms", "10–25ms", "25–50ms", ">50ms"]

# Categorize delays
no_target_df["delay_range"] = pd.cut(no_target_df["excess_delay"], bins=bins, labels=labels, right=False)

# Count per bin
delay_counts = no_target_df["delay_range"].value_counts().reindex(labels, fill_value=0)

# Print range summary
print(f"\n=== Delay Range Summary ===")
for label, count in delay_counts.items():
    print(f"{label}: {count} trials")

# Plot bar chart of ranges
plt.figure(figsize=(8, 5))
sns.barplot(x=delay_counts.index, y=delay_counts.values, palette="pastel")
plt.title("Reģistrēto aizturu sadalījums (stimuli bez mērķa)")
plt.xlabel("Aiztures intervāls")
plt.ylabel("Stimulu skaits")
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FOLDER,"no_target_excess_delay_ranges.png"))
plt.close()

# Filter only trials with target present
long_df = long_df[long_df["no_target"] == False]

# --- 1. Average and median reaction time for each stimulus ---
stimulus_stats = long_df.groupby("stimulus")["reaction_time"].agg(["mean", "median"])

plt.figure(figsize=(12, 6))
stimulus_stats.plot(kind="bar")
plt.title("Vidējais un mediānas reakcijas laiks katram stimulus")
plt.xlabel("Stimula numurs")
plt.ylabel("Reakcijas laiks (sekundēs)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_FOLDER,"stimulus_avg_median.png"))
plt.close()

# --- 2. Time trend for 1-5 and 11-15 ---
def plot_time_trend(start, end, filename):
    subset = long_df[long_df["stimulus"].between(start, end)]
    stats = subset.groupby("stimulus")["reaction_time"].agg(["mean", "median"])
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=stats)
    plt.title(f"Reakcijas laika tendence (stimuli {start}–{end})")
    plt.ylabel("Reakcijas laiks (sekundēs)")
    plt.xlabel("Stimula numurs")
    plt.xticks(range(start, end + 1))
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_FOLDER,filename))
    plt.close()

plot_time_trend(1, 5, "trend_1_5.png")
plot_time_trend(11, 15, "trend_11_15.png")

# --- 3. Compare average/median times ---
def compare_ranges(range1, range2, label1, label2, filename):
    set1 = long_df[long_df["stimulus"].between(*range1)]["reaction_time"]
    set2 = long_df[long_df["stimulus"].between(*range2)]["reaction_time"]
    stats = pd.DataFrame({
        "Vidējais": [set1.mean(), set2.mean()],
        "Mediāna": [set1.median(), set2.median()]
    }, index=[label1, label2])
    stats.plot(kind="bar")
    plt.title(f"Salīdzinājums: {label1} vs {label2}")
    plt.ylabel("Reakcijas laiks (sekundēs)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_FOLDER,filename))
    plt.close()

compare_ranges((1, 5), (6, 10), "Stimuli 1-5", "Stimuli 6-10", "compare_1_5_vs_6_10.png")
compare_ranges((11, 15), (16, 20), "Stimuli 11-15", "Stimuli 16-20", "compare_11_15_vs_16_20.png")

# --- 4. Cross-range comparison: 1-5 vs 11-15 and 6-10 vs 16-20 ---
compare_ranges((1, 5), (11, 15), "Stimuli 1-5", "Stimuli 11-15", "compare_1_5_vs_11_15.png")
compare_ranges((6, 10), (16, 20), "Stimuli 6-10", "Stimuli 16-20", "compare_6_10_vs_16_20.png")

# --- 5. Correlation: Reaction time vs number of distractors for stimuli 1-5 and 11-15 ---
json_files = glob.glob(os.path.join(DATA_FOLDER, "Participant_*.json"))


for stim_range, label in [((1, 5), "1_5"), ((11, 15), "11_15")]:
    all_corr_data = []
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            participant_data = json.load(f)
            participant_id = participant_data.get("participant_number")
            for stim in participant_data["stimulus_log"]:
                if stim_range[0] <= stim["stimulus_number"] <= stim_range[1] and not stim["no_target"]:
                    all_corr_data.append({
                        "participant": participant_id,
                        "stimulus_number": stim["stimulus_number"],
                        "reaction_time": stim["reaction_time_seconds"],
                        "distractor_count": stim["number_of_distractors"]
                    })

    corr_df = pd.DataFrame(all_corr_data)
    if not corr_df.empty:
        corr, p_val = pearsonr(corr_df["distractor_count"], corr_df["reaction_time"])
        plt.figure(figsize=(6, 4))
        plt.scatter(corr_df["distractor_count"], corr_df["reaction_time"])
        plt.title(f"Distraktoru skaita un reakcijas laika korelācija (stimuli {stim_range[0]}–{stim_range[1]})")
        plt.xlabel("Distraktoru skaits")
        plt.ylabel("Reakcijas laiks (sekundēs)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_FOLDER,f"distractor_vs_time_corr_{label}.png"))
        plt.close()
        print(f"Stimuli {stim_range[0]}–{stim_range[1]} Correlation: {corr:.3f}, p-value: {p_val:.3f}")
# === Save per-stimulus stats to CSV ===
stimulus_stats.to_csv(os.path.join(RESULTS_FOLDER, "stimulus_stats_individual.csv"))

# === Save per-range stats to CSV ===
ranges = {
    "Stimuli 1-5": (1, 5),
    "Stimuli 6-10": (6, 10),
    "Stimuli 11-15": (11, 15),
    "Stimuli 16-20": (16, 20)
}
range_stats = []
for label, (start, end) in ranges.items():
    subset = long_df[long_df["stimulus"].between(start, end)]
    range_stats.append({
        "Range": label,
        "Mean": subset["reaction_time"].mean(),
        "Median": subset["reaction_time"].median()
    })

range_stats_df = pd.DataFrame(range_stats)
range_stats_df.to_csv(os.path.join(RESULTS_FOLDER, "stimulus_stats_ranges.csv"), index=False)

#  7. Create grouped bar chart of mean and median by stimulus range 

# Create bar chart of range means and medians
x = range_stats_df["Range"]
mean_vals = range_stats_df["Mean"]
median_vals = range_stats_df["Median"]

x_indices = range(len(x))
bar_width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x_indices, mean_vals, width=bar_width, label="Vidējais")
ax.bar([i + bar_width for i in x_indices], median_vals, width=bar_width, label="Mediāna")

ax.set_xlabel("Stimulu intervāls")
ax.set_ylabel("Reakcijas laiks (sekundēs)")
ax.set_title("Reakcijas laiks pēc emocionālā stimulu bloka")
ax.set_xticks([i + bar_width / 2 for i in x_indices])
ax.set_xticklabels(x, rotation=15, ha='right')
ax.legend()
plt.tight_layout()

plt.savefig(os.path.join(RESULTS_FOLDER,"reaction_time_by_range.png"))
plt.close()