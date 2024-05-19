import asyncio
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js

# Глобальные переменные для хранения сообщений чата и онлайн пользователей
chat_msgs = []
online_users = set()

# Максимальное количество сообщений в чате
MAX_MESSAGES_COUNT = 250

async def main():
    global chat_msgs

    # Приветственное сообщение
    put_markdown("## 🗡️Приветствуем вас в нашем онлайн-чате😎 <<КИ21-05>>!\n 👀 _____Naimovv_________________________________________________________________________________________________________________  🛡️!")

    # Контейнер для сообщений
    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    # Вход в чат с проверкой уникальности ника
    nickname = await input("⚔️Войти в чат⚔️", required=True, placeholder="Ваше имя😶‍🌫️", validate=lambda n: "🏹Такой ник уже используется!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    # Сообщение о присоединении пользователя к чату
    chat_msgs.append(('🎉', f'`{nickname}` присоединился к чату!'))
    msg_box.append(put_markdown(f'🎉 `{nickname}` присоединился к чату'))

    # Асинхронная задача для обновления сообщений
    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        # Ввод нового сообщения
        data = await input_group("🧐 Новое сообщение", [
            input(placeholder="🔤Текст сообщения ...", name="msg"),
            actions(name="cmd", buttons=["Отправить▶️", {'label': "🚨Выйти из чата", 'type': 'cancel'}])
        ], validate=lambda m: ('msg', "🔤Введите текст сообщения!") if m["cmd"] == "Отправить▶️" and not m['msg'] else None)

        # Проверка на выход из чата
        if data is None:
            break

        # Добавление нового сообщения в чат
        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    # Остановка задачи обновления сообщений
    refresh_task.close()

    # Удаление пользователя из списка онлайн
    online_users.remove(nickname)
    toast("⭕Вы вышли из чата!")
    msg_box.append(put_markdown(f'🚀 Пользователь `{nickname}` покинул чат!'))
    chat_msgs.append(('🚀', f'Пользователь `{nickname}` покинул чат!'))

    # Кнопка для перезагрузки страницы и повторного входа в чат
    put_buttons(['🪂Перезайти'], onclick=lambda btn: run_js('window.location.reload()'))

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)
        
        # Обновление новых сообщений в чате
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # если сообщение не от текущего пользователя
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        # Удаление старых сообщений, чтобы не переполнить чат
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)

# Запуск сервера PyWebIO
if __name__ == "__main__":
    start_server(main, host='0.0.0.0', port=8080, debug=True, cdn=False)
