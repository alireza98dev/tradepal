from datetime import datetime


seconds_of_a_day = 3600 * 24

forex_sessions = {
    "tokyo": datetime(2023, 2, 1, 22, 0, 0),
    "london": datetime(2023, 2, 1, 8, 0, 0),
    "ny": datetime(2023, 2, 1, 13, 0, 0),
}

forex_session_duration = {
    "tokyo": 10 * seconds_of_a_day,
    "london": 9 * seconds_of_a_day,
    "ny": 9 * seconds_of_a_day,
}
