# apps/performance/translations.py

from flask import session


TRANSLATIONS = {
    "hu": {
        # Általános
        "app_name": "Performance App",
        "coach": "Edző",
        "logout": "Kijelentkezés",
        "login": "Bejelentkezés",
        "language": "Nyelv",
        "hungarian": "Magyar",
        "english": "Angol",

        # Navigáció és főoldal
        "dashboard": "Vezérlőpult",
        "players": "Játékosok",
        "teams": "Csapatok",
        "assessments": "Értékelések",
        "profiles": "Profilok",
        "admin": "Adminisztráció",

        # Műveletek
        "save": "Mentés",
        "cancel": "Mégse",
        "edit": "Szerkesztés",
        "delete": "Törlés",
        "add": "Hozzáadás",
        "search": "Keresés",
        "filter": "Szűrés",
        "back": "Vissza",
        "close": "Bezárás",
        "details": "Részletek",
        "export": "Exportálás",
        "import": "Importálás",

        # Játékosok
        "player": "Játékos",
        "player_name": "Játékos neve",
        "first_name": "Keresztnév",
        "last_name": "Vezetéknév",
        "date_of_birth": "Születési dátum",
        "team": "Csapat",
        "no_players": "Nincs megjeleníthető játékos.",

        # Értékelés
        "start_assessment": "Értékelés indítása",
        "new_assessment": "+ Új értékelés",
        "assessment_period": "Értékelési időszak",
        "select_player": "Játékos kiválasztása",
        "select_coach": "Edző kiválasztása",
        "select_team": "Csapat kiválasztása",
        "performance": "Teljesítmény",
        "potential": "Potenciál",
        "assessment_results": "Értékelés eredményei",
        "assessment_saved": "Az értékelés mentése sikeres.",
        "assessment_not_saved": "Az értékelés mentése nem sikerült.",

        # Elemzés és konszenzus
        "analysis": "Elemzés",
        "coach_consensus": "Edzői konszenzus",
        "average": "Átlag",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "range": "Tartomány",
        "major_coach_differences": "Jelentős edzői eltérések",
        "attribute": "Attribútum",
        "all_attributes": "Összes attribútum",
        "no_data": "Nincs elérhető adat.",

        # Általános visszajelzések
        "confirm_delete": "Biztosan törölni szeretnéd?",
        "required_field": "Ez a mező kötelező.",
        "operation_successful": "A művelet sikeres.",
        "operation_failed": "A művelet nem sikerült.",

        # Dashboard
        "about_system": "A rendszerről",
        "about_system_description": "Bővebb tudnivalók a rendszer használatáról",
        "about_system_button": "A rendszerről →",
        "players_description": "Összes játékos keresése, szűrése és adatlapjainak megtekintése.",
        "players_list": "Játékosok listája →",
        "teams_description": "Csapatok és játékoscsoportok kezelése.",
        "teams_manage": "Csapatok kezelése →",
        "assessments_description": "Új értékelés indítása és a korábbi értékelések kezelése.",
        "assessment_start": "Értékelés indítása →",
        "assessments_manage": "Értékelések kezelése →",

        # Játékoslista
        "players_search_filter": "Keresés és szűrés",
        "player_search_placeholder": "Név vagy játékoskód",
        "birth_year_placeholder": "Születési év",
        "all_teams": "Minden csapat",
        "clear_filters": "Szűrők törlése",
        "player_list": "Játékoslista",
        "player_count": "{count} játékos",
        "name": "Név",
        "player_code": "Játékoskód",
        "primary_team": "Elsődleges csapat",
        "team_memberships": "Csapatkapcsolatok",
        "action": "Művelet",
        "no_primary_team": "Nincs elsődleges csapat",
        "no_team_membership": "Nincs csapatkapcsolat",
        "player_profile": "Adatlap →",
        "no_players_match": "A keresési feltételeknek megfelelő játékos nem található.",
        "back_to_dashboard": "← Vissza a vezérlőpultra",

        # Játékos adatlap – fő nézet
        "current_profile": "Aktuális adatlap",
        "trend_view": "Fejlődési trend",
        "select_period": "Mérési időszak",
        "performance_potential": "Teljesítmény × potenciál",
        "player_position_model": "Játékos pozíciója a 9 kategóriás modellben",
        "potential_axis": "Potenciál →",
        "current_category": "Jelenlegi kategória",
        "performance_axis": "Teljesítmény →",
        "performance_profile": "Teljesítményprofil",
        "player_age_average": "Játékos és korosztályátlag · 26 teljesítményattribútum",
        "age_group_average": "Korosztályátlag",
        "main_performance_areas": "Fő teljesítményterületek",
        "team_average_comparison": "Összehasonlítás a csapat átlagával",

        # Edzői konszenzus és eltérések
        "coach_assessment_differences": "Edzői értékelések közötti eltérések",
        "coach_differences_description": "A legalább 2 pontos különbségek jelennek meg a jelenlegi mérési időszakban.",
        "performance_difference": "Performance eltérés",
        "potential_difference": "Potential eltérés",
        "max_points": "Max. {value} pont",
        "no_major_coach_differences": "Nincs legalább 2 pontos eltérés a rendelkezésre álló edzői értékelések között, vagy még nincs összehasonlítható adat.",
        "all_attributes_coach_consensus": "Összes attribútum és edzői konszenzus",
        "attributes_coach_consensus": "Attribútumok és edzői konszenzus",
        "consensus_average_description": "Az átlag a rendelkezésre álló értékelésekből készül; a hiányzó Potential értékek nem számítanak bele.",
        "unknown_coach": "Ismeretlen edző",
        "consensus_average": "Konszenzusátlag",
        "difference_min_max": "Eltérés (min–max)",
        "performance_short": "Perf.",
        "potential_short": "Pot.",
        "no_coach_assessments_display": "Még nincs megjeleníthető edzői értékelés.",
        "close_dialog": "Bezárás",

        # Teljesítményprofil és visszajelzések
        "player_profile_title": "Játékosprofil",
        "mapping_profile_interpretation": "Mapping és játékosprofil-értelmezés",
        "profile_type": "Profil típusa",
        "mapping": "Mapping",
        "mapping_interpretation": "Mapping értelmezése",
        "primary_profile": "Elsődleges profil",
        "secondary_profile": "Másodlagos profil",
        "strengths": "Erősségek",
        "development_areas": "Fejlesztési területek",
        "player_value": "Játékos:",
        "age_group": "Korosztály:",
        "no_positive_difference": "Nincs pozitív eltérés a korosztályátlaghoz képest.",
        "no_negative_difference": "Nincs negatív eltérés a korosztályátlaghoz képest.",

        # Player chart
        "overall": "Összesített",
        "profile": "Profile",
        "tactical_attributes": "Taktikai jellemzők",
        "technical_attributes": "Technikai jellemzők",
        "behavioral_attributes": "Viselkedéses jellemzők",
        "comparison": "Összehasonlítás",
        "coach_assessments": "Edzői értékelések",
        "assessment_count": "értékelés",
        "tactical": "Taktikai",
        "technical": "Technikai",
        "behaviour": "Viselkedés",
        "back_to_team": "← Vissza a csapathoz",
        "download_pdf": "↓ PDF letöltése",

        "tactical_attacking": "Taktika – támadás",
        "tactical_defending": "Taktika – védekezés",
        "technical_attacking": "Technika – támadás",
        "technical_defending": "Technika – védekezés",
        "behaviour_mental": "Viselkedés / mentális",
        "team_score": "csapat",

        # Posztspecifikus illeszkedés
        "position_fit_title": "Posztspecifikus illeszkedés",
        "position_fit_description": "Előzetes eredmény a jelenlegi Performance-attribútumok alapján.",
        "position_fit_physical_excluded": "A fizikai mérések még nincsenek beszámítva.",
        "position_fit_select_role": "Vizsgált posztszerepkör",
        "position_fit_view_profile": "Profil megtekintése",
        "position_fit_score": "Játékprofil-illeszkedés / 10",
        "position_fit_coverage": "Adatlefedettség",
        "position_fit_evaluated_role": "Értékelt szerepkör",
        "position_fit_strengths": "Erősségek a szerepkörhöz",
        "position_fit_development": "Fejlesztési lehetőségek",
        "position_fit_no_attribute_data": "Nincs elegendő attribútumadat.",
        "position_fit_no_period": "A posztilleszkedés kiszámításához először rögzíteni kell legalább egy értékelési időszakot.",
        "position_fit_comparison": "Posztprofilok összehasonlítása",
        "position_fit_rank": "Hely",
        "position_fit_role": "Posztszerepkör",
        "position_fit_score_short": "Játékprofil-illeszkedés",
        "position_fit_weight": "súly: {weight}",

        # Csapatoldal – pozícióilleszkedési táblázat
        "team_position_fit_title": "Játékos-illeszkedés posztonként",
        "team_position_fit_description": (
            "A játékosok posztonként, illeszkedési pontszám szerint "
            "csökkenő sorrendben szerepelnek."
        ),
        "team_position_fit_limit": (
            "Egy játékos legfeljebb ennyi poszton jelenjen meg"
        ),
        "team_position_fit_no_data": (
            "Nincs elegendő értékelési adat az illeszkedési pontszám kiszámításához."
        ),
        "team_position_fit_score": "Illeszkedés",
        "team_position_fit_one": "1 poszt",
        "team_position_fit_two": "2 poszt",
        "team_position_fit_three": "3 poszt",

# Csapatoldal – áttekintés
"team_overview_subtitle": "Csapatáttekintő – teljesítmény, potenciál és posztilleszkedés",

# Performance × Potential mátrix
"team_matrix_title": "Performance × Potential mátrix",
"team_matrix_description": (
    "A kategóriák a kiválasztott mérési időszak eredményeit mutatják. "
    "Kattints egy kategóriára a játékoslista szűréséhez."
),
"team_matrix_player_unit": "játékos",
"team_matrix_clear_filter": "Kategóriaszűrés törlése",
"team_matrix_players": "Játékosok",
"team_matrix_players_in_view": "{count} játékos a kiválasztott nézetben",
"team_matrix_no_assessment": "Nincs értékelés",
"team_matrix_empty": "Nincs játékos ebben a nézetben.",

# Excel-import
"team_import_title": "Játékosok importálása Excelből",
"team_import_first_row": "Az Excel fájl első sora tartalmazza az oszlopneveket.",
"team_import_required_columns": "Elvárt oszlopok:",
"team_import_optional_columns": "Opcionális:",
"team_import_upload": "Excel feltöltése",

# Játékos hozzáadása
"team_add_player_title": "Játékos hozzáadása",
"team_add_player_select": "— Válassz játékost —",
"team_add_player_button": "Játékos hozzáadása",
"team_add_player_empty": (
    "Minden aktív játékos már szerepel ebben a csapatban, "
    "vagy még nincs játékos az adatbázisban."
),

# Csapattagok
"team_roster_title": "Játékosok ({count})",
"team_remove_player": "Eltávolítás",
"team_roster_empty": "Ehhez a csapathoz még nincs hozzárendelt játékos.",
"team_back_to_teams": "← Vissza a csapatokhoz",

"assessment_start_title": "Új értékelés",
"assessment_start_description": "Válaszd ki az értékeléshez szükséges adatokat.",
"assessment_coach_label": "Értékelő edző",
"assessment_select_coach": "-- Válassz edzőt --",
"assessment_select_team": "-- Válassz csapatot --",
"assessment_select_period": "-- Válassz időszakot --",
"assessment_select_team_first": "-- Előbb válassz csapatot --",
"assessment_select_player": "-- Válassz játékost --",
"assessment_start_button": "Értékelés indítása →",

# Játékosértékelés
"player_assessment_title": "Játékosértékelés",
"assessment_evaluator": "Értékelő",
"assessment_period_explanation": "Mindkét értékelés ugyanarra az időszakra vonatkozik. A Potential az edzéseken, a Performance a mérkőzéseken mutatott teljesítményt jelenti.",
"step_tactical": "Taktikai",
"step_technical": "Technikai",
"step_behaviour": "Viselkedés / mentalitás",
"category_tactical": "Taktikai teljesítmény",
"category_technical": "Technikai teljesítmény",
"category_behaviour": "Viselkedés / mentalitás",
"assessment_rate_both": "Mindkét dimenziót értékeld 1–10 között.",
"phase_attacking": "TÁMADÁS",
"phase_defending": "VÉDEKEZÉS",
"phase_mentality": "MENTALITÁS",
"potential_training": "Potential – edzésen mutatott teljesítmény",
"performance_match": "Performance – mérkőzésen mutatott teljesítmény",
"coach_note_title": "Edzői megjegyzés",
"coach_note_placeholder": "Opcionális megjegyzés, fejlesztési fókusz...",
"button_back": "← Vissza",
"button_next": "Következő →",
"button_save_assessment": "Értékelés mentése",
"button_close": "Bezárás",
"perfect_ten_title": "Biztos?",
"perfect_ten_message": "Tényleg 10 pontot adsz erre a tulajdonságra?",
"perfect_ten_back": "Vissza a pontszámhoz",
"perfect_ten_confirm": "Igen, 10-es",
"perfect_ten_superpower": "Valóban 10 pontot érdemel {player} szuperereje?",
"validation_answer_all": "Kérlek, válaszolj minden kérdésre ezen az oldalon.",
    },

    "en": {
        # General
        "app_name": "Performance App",
        "coach": "Coach",
        "logout": "Log out",
        "login": "Log in",
        "language": "Language",
        "hungarian": "Hungarian",
        "english": "English",

        # Navigation and dashboard
        "dashboard": "Dashboard",
        "players": "Players",
        "teams": "Teams",
        "assessments": "Assessments",
        "profiles": "Profiles",
        "admin": "Administration",

        # Actions
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "add": "Add",
        "search": "Search",
        "filter": "Filter",
        "back": "Back",
        "close": "Close",
        "details": "Details",
        "export": "Export",
        "import": "Import",

        # Players
        "player": "Player",
        "player_name": "Player name",
        "first_name": "First name",
        "last_name": "Last name",
        "date_of_birth": "Date of birth",
        "team": "Team",
        "no_players": "No players to display.",

        # Assessment
        "start_assessment": "Start assessment",
        "new_assessment": "+ New assessment",
        "assessment_period": "Assessment period",
        "select_player": "Select player",
        "select_coach": "Select coach",
        "select_team": "Select team",
        "performance": "Performance",
        "potential": "Potential",
        "assessment_results": "Assessment results",
        "assessment_saved": "Assessment saved successfully.",
        "assessment_not_saved": "Failed to save the assessment.",

        # Analysis and consensus
        "analysis": "Analysis",
        "coach_consensus": "Coach consensus",
        "average": "Average",
        "minimum": "Minimum",
        "maximum": "Maximum",
        "range": "Range",
        "major_coach_differences": "Significant differences between coaches",
        "attribute": "Attribute",
        "all_attributes": "All attributes",
        "no_data": "No data available.",

        # General feedback
        "confirm_delete": "Are you sure you want to delete this?",
        "required_field": "This field is required.",
        "operation_successful": "Operation completed successfully.",
        "operation_failed": "The operation failed.",

         # Dashboard
        "about_system": "About the system",
        "about_system_description": "Learn more about how to use the system",
        "about_system_button": "About the system →",
        "players_description": "Search and filter all players and view their profiles.",
        "players_list": "Player list →",
        "teams_description": "Manage teams and player groups.",
        "teams_manage": "Manage teams →",
        "assessments_description": "Start a new assessment and manage previous assessments.",
        "assessment_start": "Start assessment →",
        "assessments_manage": "Manage assessments →",

        # Player list
        "players_search_filter": "Search and filter",
        "player_search_placeholder": "Name or player code",
        "birth_year_placeholder": "Birth year",
        "all_teams": "All teams",
        "clear_filters": "Clear filters",
        "player_list": "Player list",
        "player_count": "{count} players",
        "name": "Name",
        "player_code": "Player code",
        "primary_team": "Primary team",
        "team_memberships": "Team memberships",
        "action": "Action",
        "no_primary_team": "No primary team",
        "no_team_membership": "No team membership",
        "player_profile": "Profile →",
        "no_players_match": "No players match the selected search criteria.",
        "back_to_dashboard": "← Back to dashboard",

        # Player profile – main view
        "current_profile": "Current profile",
        "trend_view": "Development trend",
        "select_period": "Assessment period",
        "performance_potential": "Performance × Potential",
        "player_position_model": "Player position in the 9-category model",
        "potential_axis": "Potential →",
        "current_category": "Current category",
        "performance_axis": "Performance →",
        "performance_profile": "Performance profile",
        "player_age_average": "Player and age-group average · 26 performance attributes",
        "age_group_average": "Age-group average",
        "main_performance_areas": "Main performance areas",
        "team_average_comparison": "Comparison with the team average",

        # Coach consensus and differences
        "coach_assessment_differences": "Differences between coach assessments",
        "coach_differences_description": "Differences of at least 2 points are shown for the current assessment period.",
        "performance_difference": "Performance difference",
        "potential_difference": "Potential difference",
        "max_points": "Max. {value} points",
        "no_major_coach_differences": "There are no differences of at least 2 points between the available coach assessments, or there is not enough comparable data.",
        "all_attributes_coach_consensus": "All attributes and coach consensus",
        "attributes_coach_consensus": "Attributes and coach consensus",
        "consensus_average_description": "The average is calculated from the available assessments; missing Potential values are excluded.",
        "unknown_coach": "Unknown coach",
        "consensus_average": "Consensus average",
        "difference_min_max": "Difference (min–max)",
        "performance_short": "Perf.",
        "potential_short": "Pot.",
        "no_coach_assessments_display": "No coach assessments are available to display yet.",
        "close_dialog": "Close",

        # Performance profile and insights
        "player_profile_title": "Player Profile",
        "mapping_profile_interpretation": "Mapping and Player Profile Interpretation",
        "profile_type": "Profile type",
        "mapping": "Mapping",
        "mapping_interpretation": "Mapping Interpretation",
        "primary_profile": "Primary profile",
        "secondary_profile": "Secondary profile",
        "strengths": "Strengths",
        "development_areas": "Areas for development",
        "player_value": "Player:",
        "age_group": "Age group:",
        "no_positive_difference": "There are no positive differences compared with the age-group average.",
        "no_negative_difference": "There are no negative differences compared with the age-group average.",

        # Player chart
        "overall": "Overall",
        "profile": "profile",
        "tactical_attributes": "Tactical attributes",
        "technical_attributes": "Technical attributes",
        "behavioral_attributes": "Behavioural attributes",
        "comparison": "Comparison",
        "coach_assessments": "Coach assessments",
        "assessment_count": "assessment(s)",
        "tactical": "Tactical",
        "technical": "Technical",
        "behaviour": "Behaviour",
        "back_to_team": "← Back to team",
        "download_pdf": "↓ Download PDF",

        "tactical_attacking": "Tactical – attacking",
        "tactical_defending": "Tactical – defending",
        "technical_attacking": "Technical – attacking",
        "technical_defending": "Technical – defending",
        "behaviour_mental": "Behaviour / mental",
        "team_score": "Team",

        # Position-specific fit
        "position_fit_title": "Position-Specific Fit",
        "position_fit_description": "Preliminary result based on the current Performance attributes.",
        "position_fit_physical_excluded": "Physical measurements are not yet included.",
        "position_fit_select_role": "Position role to assess",
        "position_fit_view_profile": "View profile",
        "position_fit_score": "Playing profile fit / 10",
        "position_fit_coverage": "Data coverage",
        "position_fit_evaluated_role": "Assessed role",
        "position_fit_strengths": "Strengths for this role",
        "position_fit_development": "Development opportunities",
        "position_fit_no_attribute_data": "Insufficient attribute data.",
        "position_fit_no_period": "At least one assessment period must be recorded before position fit can be calculated.",
        "position_fit_comparison": "Position Profile Comparison",
        "position_fit_rank": "Rank",
        "position_fit_role": "Position role",
        "position_fit_score_short": "Playing profile fit",
        "position_fit_weight": "weight: {weight}",

        # Team page – position fit table
        "team_position_fit_title": "Player fit by position",
        "team_position_fit_description": (
            "Players are ranked by fit score in each position."
        ),
        "team_position_fit_limit": "Maximum positions per player",
        "team_position_fit_no_data": (
            "Not enough assessment data to calculate a fit score."
        ),
        "team_position_fit_score": "Fit",
        "team_position_fit_one": "1 position",
        "team_position_fit_two": "2 positions",
        "team_position_fit_three": "3 positions",

# Team page – overview
"team_overview_subtitle": "Team overview – performance, potential and position fit",

# Performance × Potential matrix
"team_matrix_title": "Performance × Potential Matrix",
"team_matrix_description": (
    "The categories show results for the selected assessment period. "
    "Click a category to filter the player list."
),
"team_matrix_player_unit": "players",
"team_matrix_clear_filter": "Clear category filter",
"team_matrix_players": "Players",
"team_matrix_players_in_view": "{count} players in the selected view",
"team_matrix_no_assessment": "No assessment",
"team_matrix_empty": "No players in this view.",

# Excel import
"team_import_title": "Import players from Excel",
"team_import_first_row": "The first row of the Excel file must contain the column headers.",
"team_import_required_columns": "Required columns:",
"team_import_optional_columns": "Optional:",
"team_import_upload": "Upload Excel file",

# Add player
"team_add_player_title": "Add player",
"team_add_player_select": "— Select a player —",
"team_add_player_button": "Add player",
"team_add_player_empty": (
    "All active players are already assigned to this team, "
    "or there are no players in the database yet."
),

# Team roster
"team_roster_title": "Players ({count})",
"team_remove_player": "Remove",
"team_roster_empty": "No players have been assigned to this team yet.",
"team_back_to_teams": "← Back to teams",

"assessment_start_title": "New Assessment",
"assessment_start_description": "Select the details required for the assessment.",
"assessment_coach_label": "Assessing Coach",
"assessment_select_coach": "-- Select a coach --",
"assessment_select_team": "-- Select a team --",
"assessment_select_period": "-- Select an assessment period --",
"assessment_select_team_first": "-- Select a team first --",
"assessment_select_player": "-- Select a player --",
"assessment_start_button": "Start Assessment →",

# Player assessment
"player_assessment_title": "Player Assessment",
"assessment_evaluator": "Assessed by",
"assessment_period_explanation": "Both assessments refer to the same evaluation period. Potential refers to performance in training, while Performance refers to performance in matches.",
"step_tactical": "Tactical",
"step_technical": "Technical",
"step_behaviour": "Behaviour / Mentality",
"category_tactical": "Tactical Performance",
"category_technical": "Technical Performance",
"category_behaviour": "Behaviour / Mentality",
"assessment_rate_both": "Rate both dimensions on a scale of 1–10.",
"phase_attacking": "ATTACKING",
"phase_defending": "DEFENDING",
"phase_mentality": "MENTALITY",
"potential_training": "Potential – Performance in Training",
"performance_match": "Performance – Performance in Matches",
"coach_note_title": "Coach's Notes",
"coach_note_placeholder": "Optional comment, development focus...",
"button_back": "← Back",
"button_next": "Next →",
"button_save_assessment": "Save Assessment",
"button_close": "Close",
"perfect_ten_title": "Are you sure?",
"perfect_ten_message": "Are you sure you want to give this attribute a score of 10?",
"perfect_ten_back": "Back to Score",
"perfect_ten_confirm": "Yes, give it a 10",
"perfect_ten_superpower": "Does {player}'s superpower really deserve a score of 10?",
"validation_answer_all": "Please answer all questions on this page.",
    },
}

QUESTION_TRANSLATIONS = {
    "en": {

        # TACTICAL
        "finding_space": {
            "name": "Positioning / Finding Space",
            "statement": (
                "Recognises and occupies available space to become "
                "an option, create opportunities or support the play."
            ),
        },
        "vision": {
            "name": "Game Vision",
            "statement": (
                "Recognises the positions of teammates and opponents "
                "and identifies opportunities to develop the play."
            ),
        },
        "decision_making": {
            "name": "Decision Making",
            "statement": (
                "Makes effective decisions both before receiving "
                "the ball and while in possession."
            ),
        },
        "support_play": {
            "name": "Supporting Play",
            "statement": (
                "Recognises when and where to move in order "
                "to support the player in possession."
            ),
        },
        "reading_play": {
            "name": "Reading the Game",
            "statement": (
                "Anticipates what will happen in the next phase of play "
                "based on the movement of the ball, teammates and opponents."
            ),
        },
        "reaction_to_losing_ball": {
            "name": "Reaction After Losing Possession",
            "statement": (
                "Reacts appropriately after losing possession by "
                "immediately applying pressure or recovering into position."
            ),
        },

        # TECHNICAL
        "ball_control": {
            "name": "First Touch / Ball Control",
            "statement": (
                "Uses a quality first touch and controls the ball "
                "in a way that prepares the next action."
            ),
        },
        "receiving_under_pressure": {
            "name": "Receiving Under Pressure",
            "statement": (
                "Can receive and control the ball effectively under "
                "pressure, using appropriate body positioning and first touch."
            ),
        },
        "twisting_turning": {
            "name": "Turning and Ball Retention",
            "statement": (
                "Can protect the ball, manipulate opponents and "
                "maintain possession under pressure."
            ),
        },
        "one_v_one_dominance": {
            "name": "1v1 Dominance",
            "statement": (
                "Uses changes of speed, movement and rhythm to beat "
                "an opponent and create an advantage in 1v1 situations."
            ),
        },
        "dribbling": {
            "name": "Dribbling",
            "statement": (
                "Maintains close control of the ball at different "
                "speeds and when changing direction."
            ),
        },
        "passing_range": {
            "name": "Passing Range",
            "statement": (
                "Can pass effectively over short, medium and long distances. "
                "(A high score requires proficiency at all three ranges.)"
            ),
        },
        "passing_quality": {
            "name": "Passing Quality",
            "statement": (
                "Selects and executes passes with appropriate accuracy, "
                "weight, timing and direction."
            ),
        },
        "attacking_heading": {
            "name": "Attacking Heading",
            "statement": (
                "Attacks the ball towards goal with appropriate timing, "
                "accuracy and power."
            ),
        },
        "crossing": {
            "name": "Crossing",
            "statement": (
                "Can deliver accurate and dangerous crosses "
                "from wide positions."
            ),
        },
        "finishing": {
            "name": "Finishing",
            "statement": (
                "Finishes accurately and effectively from different "
                "situations, distances and angles."
            ),
        },
        "hard_to_beat": {
            "name": "1v1 Defending",
            "statement": (
                "Uses patience, aggression and discipline to prevent "
                "opponents from progressing in 1v1 situations."
            ),
        },
        "defensive_heading": {
            "name": "Defensive Heading",
            "statement": (
                "Executes defensive headers with appropriate accuracy, "
                "power and direction to clear danger, in accordance "
                "with the demands of the position."
            ),
        },
        "tackling": {
            "name": "Tackling",
            "statement": (
                "Recognises the right moment to make a tackle "
                "and wins possession safely and effectively."
            ),
        },
        "interceptions": {
            "name": "Interceptions",
            "statement": (
                "Anticipates passes and movements in order "
                "to intercept the ball and regain possession."
            ),
        },

        # BEHAVIOUR / MENTALITY
        "competitive_edge": {
            "name": "Competitive Spirit",
            "statement": (
                "Enjoys competing, winning duels and having a positive "
                "impact on the game, regardless of the score."
            ),
        },
        "bravery_on_ball": {
            "name": "Bravery on the Ball",
            "statement": (
                "Asks for, receives and takes responsibility for the ball "
                "under pressure, showing confidence in their decisions."
            ),
        },
        "bravery_without_ball": {
            "name": "Bravery Without the Ball",
            "statement": (
                "Is willing to defend, press and tackle without the ball, "
                "putting the team's interests ahead of individual concerns."
            ),
        },
        "control": {
            "name": "Emotional Control",
            "statement": (
                "Maintains composure, manages emotions and makes clear "
                "decisions even under pressure."
            ),
        },
        "concentration": {
            "name": "Concentration",
            "statement": (
                "Remains focused, alert and active throughout the match, "
                "even when not directly involved in play."
            ),
        },
        "communication": {
            "name": "Communication",
            "statement": (
                "Supports teammates through clear, purposeful and timely "
                "verbal and non-verbal communication."
            ),
        },
    }
}

def t(key, **kwargs):
    """Return a translation for the current session language."""

    language = session.get("language", "hu")

    if language not in TRANSLATIONS:
        language = "hu"

    # Fall back to Hungarian, then to the key itself.
    value = TRANSLATIONS[language].get(
        key,
        TRANSLATIONS["hu"].get(key, key),
    )

    # Allow optional placeholders, e.g. t("welcome", name="Alex").
    if kwargs:
        try:
            value = value.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return value

def tq(question, field):
    """
    Translate a question field based on the current session language.

    Hungarian uses the original question bank.
    Other languages use QUESTION_TRANSLATIONS.
    """

    language = session.get("language", "hu")

    if language == "hu":
        return question.get(field, "")

    translation = QUESTION_TRANSLATIONS.get(
        language, {}
    ).get(
        question.get("code"), {}
    )

    return translation.get(
        field,
        question.get(field, "")
    )