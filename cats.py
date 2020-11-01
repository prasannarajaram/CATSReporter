import pandas as pd
import numpy as np

dump = pd.ExcelFile('EXPORT.XLSX')
df = pd.read_excel(dump, sheet_name='Sheet1')
df.columns = [c.replace(' ', '_') for c in df.columns]
df.columns = [c.replace('Number_(unit)', 'Hours') for c in df.columns]

# Drop columns where all elements are NaN
df = df.dropna(axis=1, how='all')

# Eliminate unnecessary columns
base_df = df.drop(["Counter", "Sending_PO_item",
                   "Acct_assgnmt_(Recr)", "Acct_assgnt_text",
                   "Int._meas._unit", "Created_on", "Last_change",
                   "Changed_by", "Approved_by", "Approval_date",
                   "Work_Center"], axis=1)

# change date column to string format; Helps in using .drop in df
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

df = base_df.set_index('Date')
m1 = df.index >= '2020-09-28'  # Start date for report
m2 = df.index <= '2020-10-05'  # End date for report
m3 = df.Plant == "F887"        # Select only CEC candidates
m4 = df.Hours != 0             # Remove entries for which the hours are zero
np_df = np.logical_and.reduce([m1, m2, m3, m4])  # Selects the current month

pd_df = df[np_df]  # Converting numpy array to Dataframe

labe01_df = pd_df[pd_df.Activity_Type == "LABE01"]

holiday_list = ["2020-01-01", "2020-01-15", "2020-04-10",
                "2020-04-14", "2020-05-01", "2020-05-25", "2020-08-11",
                "2020-10-02", "2020-10-26", "2020-11-13", "2020-12-25"]

# "2020-01-16", "2020-02-21", "2020-03-10", "2020-03-25"]


def no_entry_found():  # change this to be based on UID
    "Check if anyone has not entered CATS for the duration"

    uids = ['U398463', 'ND62247', 'UA28467', 'U788215', 'U784318',
            'ND61517', 'UA20828', 'U397825', 'UA21109', 'U788073', 'UA28530',
            'UA21286', 'ND50566', 'UA17322', 'ND47818', 'ND18801', 'U584616',
            'UA26827', 'ND31152', 'NB55227', 'U754981', 'UA32833', 'UA22476',
            'ND32431', 'UA21949', 'UA22432', 'U584617', 'U759004', 'U585159',
            'UA27625', 'UA20085', 'U589774', 'UA29526', 'UB00272', 'UB00258',
            'UB00746', 'UB00441', 'UB00682']

    # CEC_personnel = [398463, 50134664, 1028467, 788215, 784318, 50134131,
    #               1020828, 397825, 1021109, 788073, 1028530, 1021286,
    #               50125308, 1017322, 50123145, 50102217, 584616, 1026827,
    #               50111325, 50043027, 754981, 1032833, 1022476,
    #               50112317, 1021949, 1022432, 584617, 759004, 585159,
    #               1027625, 1020085, 589774, 1029526, 1100272, 1100258,
    #               1100746, 1100441, 1100682]

    # 50140120 - Shankar Srinivasan - removed
    no_entry_list = []
    created_by_df = pd_df['Created_by'].unique()
    for uid in uids:
        if uid not in created_by_df:
            no_entry_list.append(uid)
    if len(no_entry_list) != 0:
        print("\n No CATS entries found for:")
        print("-" * 132)
        print(*no_entry_list, sep="; ")
        print("-" * 132)


def other_NWA_on_holiday():
    "Expected General Receiver = 7500005531 0001 on a holiday"

    holiday_df = pd.DataFrame()  # create empty df to append values later
    for holiday in holiday_list:
        holiday_df = holiday_df.append(pd_df.loc[holiday])
    holiday_df_filt = holiday_df['General_receiver'] != "7500005531 0001"
    other_NWA_on_leave = holiday_df[holiday_df_filt]
    if not other_NWA_on_leave.empty:
        print("\n Other NWA on a holiday")
        print("-" * 132)
        print(other_NWA_on_leave)
        print("-" * 132)


def unfilled_weekly_quota():
    "User has not entered 40 hours/week"

    hours_df = pd_df.groupby("Created_by")['Hours'].sum()
    res = hours_df[hours_df.lt(40)]
    print('\n Unfilled Weekly quota of 40 hours')
    print("-" * 132)
    print(res)
    print("-" * 132)


def invalid_workcenter():
    "Work center other than productivity format"

    """
    For all LABE01 hour ensure the use of new work center format
    e.g. "IEC-XX01" "IEC-XX02" format instead of "IEC-XX".
    ** Not working on it right now **
    """

    pass


def invalid_task_id_app1():
    "Task ID not matching General receiver "

    has_short_text_df = labe01_df[~labe01_df.Short_Text.isnull()]
    has_short_text_df['Gen_rx_Short_Text'] = has_short_text_df['General_receiver'] + ' ' + has_short_text_df['Short_Text']
    # print(has_short_text_df)

    # has_unique_short_text_df = has_short_text_df['Gen_rx_Short_Text'].unique()
    # print(has_unique_short_text_df)
    # has_short_text_df = has_short_text_df.groupby(['General_receiver', 'Short_Text'], sort=False, as_index=False)['Short_Text'].first()
    # print(type(has_unique_short_text_df))

    cec_nwa = pd.ExcelFile('CEC NWA.XLSX')
    cec_nwa_df = pd.read_excel(cec_nwa, sheet_name='Sheet1')
    cec_nwa_df = cec_nwa_df[cec_nwa_df['Status'] == 'Active']
    cec_nwa_df = cec_nwa_df[cec_nwa_df['Task ID'].str.contains('PA')]
    cec_nwa_df['CEC Network'] = cec_nwa_df['CEC Network'].apply(str)
    cec_nwa_df['CEC Activity'] = cec_nwa_df['CEC Activity'].apply(lambda x: '{0:0>4}'.format(x))
    cec_nwa_df['Gen_rx_Short_Text'] = cec_nwa_df['CEC Network'] + ' ' + cec_nwa_df['CEC Activity'] + ' ' + cec_nwa_df['Task ID']
    # print(cec_nwa_df)
    # print(cec_nwa_df.info())
    # for Gen_rx_Short_Text in has_short_text_df['Gen_rx_Short_Text']:
    #     print(len(Gen_rx_Short_Text))

    check_task_id_df = pd.merge(has_short_text_df, cec_nwa_df, on=['Gen_rx_Short_Text'], how='left', indicator='Exist')
    check_task_id_df['Exist'] = np.where(check_task_id_df.Exist == 'both', "Valid Task ID", "Invalid Task ID")
    invalid_task_id_df = check_task_id_df[check_task_id_df['Exist'] == "Invalid Task ID"]
    invalid_task_id_df.drop(['Task ID', 'CEC Network', 'CEC Activity',
                             'Status', 'Comments', 'Company'],
                            inplace=True, axis=1)
    print(invalid_task_id_df)


def invalid_task_id():
    "Task ID not matching General receiver "

    has_short_text_df = labe01_df[~labe01_df.Short_Text.isnull()]
    has_short_text_df['Gen_rx_Short_Text'] = has_short_text_df['General_receiver'] + ' ' + has_short_text_df['Short_Text']
    # print(has_short_text_df['Gen_rx_Short_Text'])

    cec_nwa = pd.ExcelFile('CEC NWA.XLSX')
    cec_nwa_df = pd.read_excel(cec_nwa, sheet_name='Sheet1')
    cec_nwa_df = cec_nwa_df[cec_nwa_df['Status'] == 'Active']
    cec_nwa_df = cec_nwa_df[cec_nwa_df['Task ID'].str.contains('PA')]
    cec_nwa_df['CEC Network'] = cec_nwa_df['CEC Network'].apply(str)
    cec_nwa_df['CEC Activity'] = cec_nwa_df['CEC Activity'].apply(lambda x: '{0:0>4}'.format(x))
    cec_nwa_df['Gen_rx_Short_Text'] = cec_nwa_df['CEC Network'] + ' ' + cec_nwa_df['CEC Activity'] + ' ' + cec_nwa_df['Task ID']
    # print(cec_nwa_df)

    invalid_task_id_df = pd.DataFrame()
    for short_text in has_short_text_df['Gen_rx_Short_Text']:
        if short_text not in cec_nwa_df['Gen_rx_Short_Text']:
            invalid_task_id_df = invalid_task_id_df.append(has_short_text_df.at[short_text])
    print(invalid_task_id_df)


def no_task_ID():
    "Check if LABE01 has a General receiver number starting with 75"

    no_short_txt_df = labe01_df[labe01_df.Short_Text.isnull()]
    if not no_short_txt_df.empty:
        print("\n LABE01 without Task ID")
        print("-" * 132)
        print(no_short_txt_df)
        print("-" * 132)


def labe00_for_project():
    "Check if LABE00 has a General receiver number **not** starting with 75"

    labe00_df = pd_df[pd_df.Activity_Type == "LABE00"]
    labe00_df_filt = labe00_df['General_receiver'].str.startswith('75')
    labe00_error_df = labe00_df[~labe00_df_filt].sort_values('Date')
    if not labe00_error_df.empty:
        print("\n LABE00 for Project NWA")
        print("-" * 132)
        print(labe00_error_df)
        print("-" * 132)


def labe01_for_overhead():
    "Check if LABE01 has a General receiver number starting with 75"

    labe01_df_filt = labe01_df['General_receiver'].str.startswith('75')
    labe01_error_df = labe01_df[labe01_df_filt].sort_values('Date')
    if not labe01_error_df.empty:
        print("\n LABE01 for Overhead NWA")
        print("-" * 132)
        print(labe01_error_df)
        print("-" * 132)


def holidayNWA_on_work_day():
    "User entered holiday NWA on a working day rather than vacation NWA"

    workday_df = pd_df.drop(holiday_list, errors='ignore')
    workday_df_filt = workday_df.General_receiver == "7500005531 0001"
    holiday_NWA_on_workday = workday_df[workday_df_filt]
    if not holiday_NWA_on_workday.empty:
        print("\n Holiday NWA on a Working Day")
        print("-" * 132)
        print(holiday_NWA_on_workday)
        print("-" * 132)


no_entry_found()
other_NWA_on_holiday()
unfilled_weekly_quota()
# invalid_workcenter()
# invalid_task_id()
no_task_ID()
labe00_for_project()
labe01_for_overhead()
holidayNWA_on_work_day()
