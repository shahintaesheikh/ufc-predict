import pandas as pd

df_fighters = pd.read_csv('fighter_data.csv')
df_events = pd.read_csv('UFC_Events.csv')

for stat, event in df_events.iterrows():
    red = event['RedFighter']
    blue = event['BlueFighter']

    red_stats = df_fighters[df_fighters['name'] == red]
    blue_stats = df_fighters[df_fighters['name'] == blue]

    # Add Red fighter stats
    if not red_stats.empty:
        event['Red_reach_cm'] = red_stats['reach_cm'].values[0]
        event['Red_stance'] = red_stats['stance'].values[0]
        event['Red_dob'] = red_stats['dob'].values[0]
        event['Red_ss_landed_per_minute'] = red_stats['ss_landed_per_minute'].values[0]
        event['Red_ss_accuracy'] = red_stats['ss_accuracy'].values[0]
        event['Red_ss_absorbed_per_min'] = red_stats['ss_absorbed_per_min'].values[0]
        event['Red_ss_defence'] = red_stats['ss_defence'].values[0]
        event['Red_avg_td_per_15'] = red_stats['avg_td_per_15'].values[0]
        event['Red_td_accuracy'] = red_stats['td_accuracy'].values[0]
        event['Red_td_defence'] = red_stats['td_defence'].values[0]
        event['Red_avg_sub_attempt_per_15'] = red_stats['avg_sub_attempt_per_15'].values[0]

    # Add Blue fighter stats
    if not blue_stats.empty:
        event['Blue_reach_cm'] = blue_stats['reach_cm'].values[0]
        event['Blue_stance'] = blue_stats['stance'].values[0]
        event['Blue_dob'] = blue_stats['dob'].values[0]
        event['Blue_ss_landed_per_minute'] = blue_stats['ss_landed_per_minute'].values[0]
        event['Blue_ss_accuracy'] = blue_stats['ss_accuracy'].values[0]
        event['Blue_ss_absorbed_per_min'] = blue_stats['ss_absorbed_per_min'].values[0]
        event['Blue_ss_defence'] = blue_stats['ss_defence'].values[0]
        event['Blue_avg_td_per_15'] = blue_stats['avg_td_per_15'].values[0]
        event['Blue_td_accuracy'] = blue_stats['td_accuracy'].values[0]
        event['Blue_td_defence'] = blue_stats['td_defence'].values[0]
        event['Blue_avg_sub_attempt_per_15'] = blue_stats['avg_sub_attempt_per_15'].values[0]

# Save merged dataframe
df_events.to_csv('UFC_Events_Merged.csv', index=False)
print(f"Saved {len(df_events)} events with merged fighter stats")