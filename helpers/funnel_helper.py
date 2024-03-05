import pandas as pd

def create_funnel_step(row):
    level_string = f'_level_{str(row.level)}'
    low_bar = '_'
    if row.event in ['level:started']:
        step=str(row.event) + level_string
        return step.strip()
    elif row.event in ['level:completed']:
        step=str(row.event) + level_string + '_' + str(row.level_reason) 
        return step.strip()
    #elif row.event in ['button:clicked']:
    #    step= str(row.feature) + low_bar + str(row.action) + low_bar + str(row.extra) + level_string 
    #    return step.strip()
    elif row.event in ['button:clicked'] and row.feature in ['gameplay_tutorial','tutorial']:
        step= str(row.extra) + level_string 
        return step.strip()
    elif row.event in ['button:clicked'] and row.feature in ['case_scene']:
        step= str(row.action) + low_bar + str(row.extra) + level_string 
        return step.strip()
    elif row.event in ['app:init:completed']:
        step=str(row.event) + level_string
        return step.strip()
    elif 'ad:' in row.event:
        step = row.event + low_bar + str(row.ad_placement) + level_string
        return step.strip()
    elif 'payment:' in row.event:
        step = row.event + low_bar + str(row.feature) + level_string
        return step.strip()
    else:
        return row.event + level_string