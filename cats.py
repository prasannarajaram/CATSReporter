#!/usr/bin/python3
import pandas as pd
import numpy as np
import argparse
import pdb
from datetime import date, datetime, timedelta

dump = pd.ExcelFile('EXPORT.XLSX')
df = pd.read_excel(dump, sheet_name='Sheet1')
# df.columns = [c.replace('Sender Cost Center', 'SCC') for c in df.columns]
df.columns = [c.replace(' ', '_') for c in df.columns]
df.columns = [c.replace('Number_(unit)', 'Hours') for c in df.columns]
df.columns = [c.replace('Name_of_employee_or_applicant', 'Employee_Name') for c in df.columns]
df.columns = [c.replace('Personnel_Number', 'Personnel#') for c in df.columns]

# Drop columns where all elements are NaN
df = df.dropna(axis=1, how='all')

# Eliminate unnecessary columns
base_df = df.drop(["Counter", "Sending_PO_item",
                   "Acct_assgnmt_(Recr)", "Acct_assgnt_text",
                   "Int._meas._unit", "Created_on", "Last_change",
                   "Changed_by", "Approved_by", "Approval_date",
                   "Work_Center"], axis=1)

# change date column to string format; Helps in using .drop in df
df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")

df = base_df.set_index('Date')
start_date = '2024-05-01'
end_date = '2024-05-10'
np_start_date = df.index >= start_date # Start date for report
np_end_date = df.index <= end_date # date for report
plant_code = df.Plant == "F887"        # Select only CEC candidates
m4 = df.Hours != 0             # Remove entries for which the hours are zero
np_df = np.logical_and.reduce([np_start_date, np_end_date, plant_code, m4])  # Selects the current month

pd_df = df[np_df]  # Converting numpy array to Dataframe

labe01_df = pd_df[pd_df.Activity_Type == "LABE01"]

holiday_list = ["2024-01-01", "2024-01-15", "2024-01-26", 
                "2024-03-29", 
                "2024-03-25", # optional holidays - holi
                "2024-04-11", 
                "2024-04-09", # optional holidays - Telugu New Year
		        "2024-04-15", # optional holidays - Tamil New Year
                "2024-05-01", 
                "2024-08-15",
                "2024-08-26", # optional holidays - Krishna Jayanthi
                "2024-09-16"  # optional holidays - Onam
                "2024-10-02", "2024-10-11", "2024-10-31",
         		"2024-12-25"
                ] 

def hours_from_dates(start_date, end_date):
    # This function will calculate the number of working hours between start & end dates
    date_format = "%Y-%m-%d"
    billable_hours = 0
    begin_date = datetime.strptime(start_date, date_format)
    end_date = datetime.strptime(end_date, date_format)
    delta = end_date - begin_date
    total_days = delta.days + 1
    for day in range(total_days):
        if begin_date.isoweekday() != 6 and begin_date.isoweekday() != 7 :
            billable_hours = billable_hours + 8
        begin_date = begin_date + timedelta(days=1)
    return(billable_hours)

# def incorrect_sender_cc():
#     "List if the sender CC is 215291. The new sender CC is 215372"
#     incorrect_scc_filt = pd_df['SCC'] == 215291
#     incorrect_scc = pd_df[incorrect_scc_filt]
#     if not incorrect_scc.empty:
#         print("\n Incorrect sender cost centre")
#         print("-" * 120)
#         print(incorrect_scc)
#         print("-" * 120)


def no_entry_found():  # change this to be based on UID
    "Check if anyone has not entered CATS for the duration"

    uids = ['U398463', 'ND85306', 'UA28467', 'U788215', 'U784318', 'NE10306',
            'UA20828', 'U397825', 'UA21109', 'UA28530', 'NE00971',
            'UA21286', 'ND85309', 'UA17322', 'ND85305', 'ND85303', 'U584616',
            'UA26827', 'ND31152', 'NB55227', 'U754981', 'UA22476',
            'UA21949', 'U585159',
            'U589774', 'UA29526', 'UB00272', 'UB00258',
            'UB00746', 'UB00441', 'UB00682', 'UA33631', 'UB04967', 'UB08317' ]

    no_entry_list = []
    created_by_df = pd_df['Created_by'].unique()
    for uid in uids:
        if uid not in created_by_df:
            no_entry_list.append(uid)
    if len(no_entry_list) != 0:
        print("\n No CATS entries found for:")
        print("-" * 72)
        print(*no_entry_list, sep="; ") # the * in the print avoids the square brackets from list from appearing
        print("-" * 72)


def other_NWA_on_holiday():
    "Expected General Receiver = 7500005558 0001 on a holiday - new Sender CC"

    holiday_df = pd.DataFrame()  # create empty df to append values later
    # holiday_list = ['2024-03-01','2024-03-04','2024-03-02']
    for holiday in holiday_list:
        try:
            holiday_date_df = pd_df.loc[holiday]
        except KeyError:
            continue
        frames = [holiday_date_df, holiday_df]
        holiday_df = pd.concat(frames)
    # for holiday in holiday_list:
    #     holiday_df = holiday_df.concat(pd_df.loc[holiday])
    if holiday_df.empty:
        return
    else:
        holiday_df_filt = holiday_df['General_receiver'] != "7500005558 0001"
        other_NWA_on_leave = holiday_df[holiday_df_filt]
        if not other_NWA_on_leave.empty:
            print("\n Other NWA on a holiday - please ignore if you worked on this day")
            print("-" * 72)
            print(other_NWA_on_leave)
            print("-" * 72)


def unfilled_weekly_quota(hours):
    "User has not entered 40 hours/week"

    hours_df = pd_df.groupby("Created_by")['Hours'].sum()
    res = hours_df[hours_df.lt(hours)]
    print('\nExpected ', hours,'hours')
    print("-" * 72)
    print(res)
    print("-" * 72)


def invalid_workcenter():
    "Work center other than productivity format"

    """
    For all LABE01 hour ensure the use of new work center format
    e.g. "IEC-XX01" "IEC-XX02" format instead of "IEC-XX".
    ** Not working on it right now **
    """
    pass


def no_task_ID():
    "Check if LABE01 has a General receiver number starting with 75"

    no_short_txt_df = labe01_df[labe01_df.Short_Text.isnull()]
    if not no_short_txt_df.empty:
        print("\n LABE01 without Task ID")
        print("-" * 72)
        print(no_short_txt_df)
        print("-" * 72)


def labe00_for_project():
    "Check if LABE00 has a General receiver number **not** starting with 75"

    labe00_df = pd_df[pd_df.Activity_Type == "LABE00"]
    labe00_df_filt = labe00_df['General_receiver'].str.startswith('75')
    labe00_error_df = labe00_df[~labe00_df_filt].sort_values('Date')
    if not labe00_error_df.empty:
        print("\n LABE00 for Project NWA")
        print("-" * 72)
        print(labe00_error_df)
        print("-" * 72)


def labe01_for_overhead():
    "Check if LABE01 has a General receiver number starting with 75"

    labe01_df_filt = labe01_df['General_receiver'].str.startswith('75')
    labe01_error_df = labe01_df[labe01_df_filt].sort_values('Date')
    if not labe01_error_df.empty:
        print("\n LABE01 for Overhead NWA")
        print("-" * 72)
        print(labe01_error_df)
        print("-" * 72)


def holidayNWA_on_work_day():
    "User entered holiday NWA on a working day rather than vacation NWA"
    workday_df = pd_df.drop(holiday_list, errors='ignore')
    workday_df_filt = workday_df.General_receiver == "7500005531 0001"
    holiday_NWA_on_workday = workday_df[workday_df_filt]
    if not holiday_NWA_on_workday.empty:
        print("\n Holiday NWA on a Working Day")
        print("-" * 72)
        print(holiday_NWA_on_workday)
        print("-" * 72)


# incorrect_sender_cc()
no_entry_found()
other_NWA_on_holiday()
hours = hours_from_dates(start_date, end_date)
unfilled_weekly_quota(hours)

# invalid_workcenter()
# invalid_task_id()
# no_task_ID()

labe00_for_project()
labe01_for_overhead()
holidayNWA_on_work_day()
