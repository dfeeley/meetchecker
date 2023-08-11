import datetime
import inquirer


def emphasis(text):
    return f'<span class="emphasis">{text}</span>'


def expand_date_macros(text, date=None):
    date = date or datetime.date.today()
    if not text:
        return text
    return date.strftime(text)


def select_from_user(choices, message="Please select one", color="blue"):
    key = "key"
    questions = [
        inquirer.List(key, message, choices=choices),
    ]
    answer = inquirer.prompt(questions)
    if answer:
        return answer.get("key")


def approx_equals(float1, float2, epsilon=0.001):
    return abs(float1 - float2) <= epsilon
