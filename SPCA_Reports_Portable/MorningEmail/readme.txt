Run and Place the Following Reports in __Load Files Go Here__ Folder
Some of these files are also run for other apps, so may be here already for the timeframe applicable

GO TO THE REPORTS WEBSITE - PLACE FOLLOWING REPORTS IN '__Load Files Go Here__' FOLDER (some for multiple apps and may be there already)

    UNDER THE OUTCOME TAB

    'AnimalOutcome.csv'
        Run Animal: Outcome for Previous Day (or days after weekend)
        For All Outcome Types
        Group By Outcome Type
        Set Detail/Summary to Detail

    UNDER THE INTAKE TAB

    'AnimalIntake.csv'
        Run Animal: Intake for Previous Day (or days after weekend)
        For All Species 
        Group By Intake Type
        Set Detail/Summary to Detail

    UNDER THE ANIMAL TAB

    'AnimalInventory.csv' 
        Run Animal: Animal Inventory for All Stages, All Locations, and All Species
        Group by Location - Alphabetically
        Sort by SubLocation - Alphabetically
        Set Detail/Summary to Detail

    'StageReview.csv' 
        Run Stage: Review for All Stages set to Animal With Above Stage and All Locations
        Group by Location
        Set Detail/Summary to Detail

    UNDER THE CARE TAB

    'FosterCurrent.csv'
        Run Foster: Current For All Species, Foster Start Reasons, and PreAltered
        Group by Foster Parent
        Set Detail/Summary to Detail

Run MorningEmail/morning_report.py
Put in dates you need intakes and outcomes for in mm/dd/yyyy format
Seperate multiple days by commas ex: 06/06/2025, 06/07/2025

Use that report to copy/paste into email template (for now, it'll make the whole email eventually - you just wait)


