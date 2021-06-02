import time
import datetime


def current_time_mills() -> int:
    return round(time.time() * 1000)


def date(mills: int) -> str:
    return datetime.datetime.fromtimestamp(round(mills / 1000)).strftime("%d.%m.%Y")


def hour(mills: int) -> str:
    return datetime.datetime.fromtimestamp(round(mills / 1000)).strftime("%H:%M:%S")


def get_duration_breakdown(mills: int) -> str:
    if mills == 0:
        return "0"

    days = int(mills / (1000 * 60 * 60 * 24))
    if days > 0: mills -= days * 1000 * 60 * 60 * 24

    hours = int(mills / (1000 * 60 * 60))
    if hours > 0: mills -= hours * 1000 * 60 * 60

    minutes = int(mills / (1000 * 60))
    if minutes > 0: mills -= minutes * 1000 * 60

    seconds = int(mills / 1000)

    result = ""
    if days > 0:
        result += str(days)
        result += " dzien " if days == 1 else " dni "

    if hours > 0:
        result += str(hours)
        i = hours % 10
        result += " godzina " if hours == 1 else (
            " godzin " if (i <= 1 or i >= 5 or (12 <= hours <= 14)) else " godziny ")

    if minutes > 0:
        result += str(minutes)
        i = minutes % 10
        result += " minuta " if minutes == 1 else (
            " minut " if (i <= 1 or i >= 5 or (12 <= minutes <= 14)) else " minuty ")

    if seconds > 0:
        result += str(seconds)
        i = seconds % 10
        result += " sekunda " if seconds == 1 else (
            " sekund " if (i <= 1 or i >= 5 or (12 <= seconds <= 14)) else " sekundy ")

    return result


def get_duration_breakdown_short(mills: int) -> str:
    if mills == 0:
        return "0"

    days = int(mills / (1000 * 60 * 60 * 24))
    if days > 0: mills -= days * 1000 * 60 * 60 * 24

    hours = int(mills / (1000 * 60 * 60))
    if hours > 0: mills -= hours * 1000 * 60 * 60

    minutes = int(mills / (1000 * 60))
    if minutes > 0: mills -= minutes * 1000 * 60

    seconds = int(mills / 1000)

    result = ""
    if days > 0:
        result += str(days) + "d "

    if hours > 0:
        result += str(hours) + "h "

    if minutes > 0:
        result += str(minutes) + "m "

    if seconds > 0:
        result += str(seconds) + "s "

    return result
