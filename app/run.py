import os

from dotenv import load_dotenv
from neuro_net_library import NeuroNetLibrary
from neuro_voice_library import NeuroVoiceLibrary

from .custom_exceptions import RecordsNotFoundError
from .script import forward, hangup, hello, recommend

load_dotenv()

PROMPTS = [
    "hello",
    "hello_null",
    "recommend",
    "recommend_null",
    "recommend_main",
    "recommend_score_negative",
    "recommend_score_neutral",
    "recommend_score_positive",
    "recommend_repeat_2",
    "recommend_repeat",
    "recommend_default",
    "hangup_positive",
    "hangup_negative",
    "hangup_wrong_time",
    "hangup_null",
]
RECOMMENDATION_SCORE_LIST = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
RECOMMENDATION_LIST = (["positive", "negative", "neutral", "dont_know"],)
CONFIRM_LIST = ["true", "false"]
WRONG_TIME_LIST = [
    "true",
]
REPEAT_LIST = [
    "true",
]
QUESTION_LIST = [
    "true",
]


def check_prompts(nn: NeuroNetLibrary) -> None:
    """
    Функция проверяет наличие в базе необходимых промптов.
    Args:
        nn (NeuroNetLibrary): ...
    Returns:
        None
    """
    not_found = nn.has_records(
        *PROMPTS,
        confirm=CONFIRM_LIST,
        wrong_time=WRONG_TIME_LIST,
        repeat=REPEAT_LIST,
        recommendation_score=RECOMMENDATION_SCORE_LIST,
        recommendation=RECOMMENDATION_LIST,
        question=QUESTION_LIST
    )
    if not_found:
        raise RecordsNotFoundError(not_found)
    else:
        nn.log("Все запрошенные записи существуют")


def main() -> None:
    """
    Логика запуска ассистента.
    """
    nn = NeuroNetLibrary()
    nv = NeuroVoiceLibrary()
    nn.env("lang", os.environ.get("VOICE_LANGUAGE"))
    nn.env("OPERATOR_PHONE_NUMBER", os.environ.get("OPERATOR_PHONE_NUMBER"))

    token = nn.storage("middleware_token")
    headers = {"Authorization": "Bearer " + token}
    response = ...
    # тут получили список msisdn откуда-то
    msisdn_list = ...

    try:
        check_prompts(nn)

        for msisdn in msisdn_list:
            # Логируем номер абонента
            nn.log("msisdn", nn.dialog.msisdn)
            # Логируем время начала звонка
            nn.log("call_start_time", nn.dialog.call_start_time)
            nn.call(msisdn=msisdn)
            condition = None
            # Завершить диалог и завершить звонок это разные вещи?
            action, condition = hello(condition=condition, nn=nn, nv=nv)
            while condition != "DONE":
                if action == "hello":
                    action, condition = hello(
                        condition=condition, nn=nn, nv=nv
                    )
                elif action == "recommend":
                    action, condition = recommend(
                        condition=condition, nn=nn, nv=nv
                    )
                elif action == "hangup":
                    hangup(condition=condition, nn=nn, nv=nv)
                elif action == "forward":
                    forward(nn=nn, nv=nv)
            # Завершили звонок сделали dump
            nn.dump()
        # надеюсь это так работает xD, dialog он же для всех звонков один?
        nn.dialog.result = nn.RESULT_DONE
    except RecordsNotFoundError as e:
        nn.log("Ошибка:", e)
        nn.log("Не найдены записи", e.not_found)


if __name__ == "__main__":
    main()
