import requests
import os
import datetime
import re


def getJSON(url):
    try:
        response = requests.get(url)
        return response.json()
    except requests.exceptions.RequestException:
        print("Возникли проблемы при получении данных")
        exit(0)


def getDateTime(line):
    dateTime = re.search(r"\d{2}[.]\d{2}[.]\d{4}[ ]\d{2}[:]\d{2}", line)
    return dateTime[0].replace(".", "-").replace(" ", "T").replace(":", "\uA789")


def getReport(user, completedUserTasks, notCompletedUserTasks):
    try:
        report = f"{user['name']} <{user['email']}> {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n" \
                 f"{user['company']['name']}\n\nЗавершённые задачи:\n"
        for completedTask in completedUserTasks:
            report += completedTask["title"][:50] + "...\n" if len(completedTask["title"]) > 50 else completedTask[
                                                                                                         "title"] + "\n"
        report += "\nОставшиеся задачи:\n"
        for notCompletedTask in notCompletedUserTasks:
            report += notCompletedTask["title"][:50] + "...\n" if len(notCompletedTask["title"]) > 50 else \
            notCompletedTask[
                "title"] + "\n"
        return report
    except (KeyError, ValueError):
        print("Ошибка при формировании отчета")
        exit(0)


jsonTodos = getJSON("https://json.medrating.org/todos")
jsonUsers = getJSON("https://json.medrating.org/users")
pathToTasks = os.path.join(os.getcwd(), "tasks")
numberCloneReport = 0
try:
    os.mkdir(pathToTasks)
    print("Папка успешно создана")
except FileExistsError:
    print("Папка уже существует")
for user in jsonUsers:
    try:
        userPathNameFile = os.path.join(pathToTasks, f"{user['username']}")
        if os.path.exists(userPathNameFile + ".txt"):
            dateTime = getDateTime(open(userPathNameFile + ".txt", "r").readline())
            try:
                os.rename(userPathNameFile + ".txt",
                          userPathNameFile + f"_{dateTime}.txt")
            except FileExistsError:
                os.rename(userPathNameFile + ".txt",
                          userPathNameFile + f"_{dateTime}_{numberCloneReport}.txt")
                numberCloneReport += 1
        completedUserTasks = []
        notCompletedUserTasks = []
        for task in jsonTodos:
            try:
                if task["userId"] == user["id"]:
                    completedUserTasks.append(task) if task["completed"] else notCompletedUserTasks.append(task)
            except KeyError:
                pass
        report = getReport(user, completedUserTasks, notCompletedUserTasks)
        open(userPathNameFile + ".txt", "w").write(report)
    except KeyError:
        pass
