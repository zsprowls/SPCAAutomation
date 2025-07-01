This tool will give me the totals to copy/paste into the "Monthly Tracking Numbers" files on Teams.

For Adoptions Numbers File:
-Go to Reports Website
    -Click Outcome Dropdown
    -Click Animal:Outcome
        -'Change Outcome Date From' and 'Outcome Date To' to the first and last day of the month you want to pull

For Fosters Number File:
-Go to Reports Website
    -Click on Care Dropdown
    -Click on Foster:Animal Extended
        -Change 'Based On:' to 'Foster Start and Status Date'
        -Change 'Based On From:' and 'Based on To' to first and last day of the month you want to pull

After pulling these files into this folder and insuring that they have the correct names:
Adoptions Numbers: AnimalOutcome.csv
Fosters Numbers: FosterAnimalExtended.xls

Run THE_SCRIPT.py

Ensure that the only things that aren't counted in Outcomes are the DOA's and the Requested Euthanasias and that all of the Fosters were counted.  
If anything was not counted that should have been, fix THE_SCRIPT.py because it is broken now.

NOTE - REPORT FOR JUNE - DID NOT COUNT DOA'S IN SKIPPED, BUT CONFIRMED THAT THEY WERE NOT IN ANY OF THE COUNTS, SO THEY WERE IN FACT SKIPPED.
NOTE - REPORT FOR JUNE - SKIPPED 5 FOSTERS THAT HAD REASON AS 'HOLD EVENT' INSTEAD OF 'POSSIBLE ADOPTION' LIKE I ASSUMED THEY WOULD