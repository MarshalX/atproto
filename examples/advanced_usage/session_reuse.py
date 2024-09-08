from typing import Optional

from atproto_client import Client, Session, SessionEvent


def get_session() -> Optional[str]:
    try:
        with open('session.txt', encoding='UTF-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def save_session(session_string: str) -> None:
    with open('session.txt', 'w', encoding='UTF-8') as f:
        f.write(session_string)


def on_session_change(event: SessionEvent, session: Session) -> None:
    print('Session changed:', event, repr(session))
    if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
        print('Saving changed session')
        save_session(session.export())


def init_client() -> Client:
    client = Client()
    client.on_session_change(on_session_change)

    session_string = get_session()
    if session_string:
        print('Reusing session')
        client.login(session_string=session_string)
    else:
        print('Creating new session')
        client.login('username', 'password')

    return client


if __name__ == '__main__':
    client = init_client()
    # do something with the client
    print('Client is ready to use!')
