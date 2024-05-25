# CATSReporter

## Purpose

The purpose of this tool is to flag the following anamolies in the CATS entered
by employees

1. No CATS entry found 
2. Other NWA on a holiday
3. Unfilled weekly quota
4. LABE00 for project
5. LABE01 for overhead
6. Holiday NWA on a working 

The above are defined by the CATS team at CEC level. Hence the tool implements the same
functionalities.

While the functions implemented are self-explanatory, here is a brief descriptions for clarity

## No CATS entry found 
+
Flags if there are no CATS entries for the employee for the given time period (week, month to date etc)
+
## Other NWA on a holiday

Flags if the employee has entered a different NWA instead of a holiday NWA. The NWA's are defined in the
ChennaiTCWorkbook.xlsx. Check with business specific CATS focal if you do not have that document.

## Unfilled weekly quota

A weekly (minimum) quota of 40 hours per week is expected to be filled by each employee. If the hours
filled are less than 40 hours per week, then those entries are flagged. If there were no entries at all, 
then, "No CATS entry found" is flagged. If hours were recorded, but found to be less than 40 hours, then 
"Unfilled weekly quota" is raised.

## LABE00 for project

If an employee enters LABE00 for a LABE01 NWA, then LABE00 for project is flagged.

## LABE01 for project

If an employee enters LABE01 for a LABE01 NWA, then LABE01 for project is flagged.

## Holiday NWA on a workday

In an employee enters a Holiday NWA on a working day, then this error is flagged.



