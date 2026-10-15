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

    },
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