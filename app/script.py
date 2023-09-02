from neuro_net_library import NeuroNetLibrary
from neuro_voice_library import NeuroVoiceLibrary


def hello(
    condition: str | None, nn: NeuroNetLibrary, nv: NeuroVoiceLibrary
) -> tuple[str, str | None]:
    """
    Обрабатывает логику "hello".

    Args:
        condition (str | None): Текущее состояние разговора.
        nn (NeuroNetLibrary): ...
        nv (NeuroVoiceLibrary): ...

    Returns:
        tuple[str, str | None]: Действие и новое состояние разговора.
    """
    # Слушаем что нам говорят, останавливаемся если определяем сущности
    # "confirm, wrong_time, repeat"
    with nv.listen(
        "confirm, wrong_time, repeat",
        entities="confirm, wrong_time, repeat",
    ) as r:
        if nn.counter("hello") == 1:
            nv.say("hello_null")
        else:
            nv.say("hello")  # Проигрываем приветственный промпт
        has_intents = r.has_intents()
        has_entities = r.has_entities()
        entities = r.entities()
    if has_intents:
        nn.log("user_hello_answer_prompt", r.utterancre())
        if has_entities:
            if "confirm" in entities:
                match r.entity("confirm"):
                    case "true":
                        return "recommend", None
                    case "false":
                        return "hangup", "wrong_time"
            if "wrong_time" in entities:
                match r.entity("wrong_time"):
                    case "true":
                        return "hangup", "wrong_time"
            if "repeat" in entities:
                match r.entity("repeat"):
                    case "true":
                        # Идем на второй круг
                        return "hello", None
        else:
            return "recommend", None
    else:
        # не выявили намерения phrase - NULL
        if nn.counter("hello") == 1:
            return "hangup", "null"
        nn.counter("hello", "+")
        return "hello", None


def recommend(
    condition: str | None, nn: NeuroNetLibrary, nv: NeuroVoiceLibrary
) -> tuple[str, str | None]:
    """
    Обрабатывает логику "recommend".

    Args:
        condition (str | None): Текущее состояние разговора.
        nn (NeuroNetLibrary): ...
        nv (NeuroVoiceLibrary): ...

    Returns:
        tuple[str, str | None]: Действие и новое состояние разговора.
    """
    with nv.listen(
        "recommendation_score, recommendation, repeat, wrong_time, question",
        entities="recommendation_score, recommendation, repeat, wrong_time, "
                 "question",
    ) as r:
        if condition is None:
            if nn.counter("recommend") == 1:
                nv.say("recommend_null")
            else:
                nv.say("recommend_main")
        else:
            match condition:
                case "negative":
                    nv.say("recommend_score_negative")
                case "neutral":
                    nv.say("recommend_score_neutral")
                case "positive":
                    nv.say("recommend_score_positive")
                case "dont_know":
                    nv.say("recommend_repeat_2")
                case "default":
                    nv.say("recommend_default")
                case "repeat":
                    nv.say("recommend_repeat")
        has_intents = r.has_intents()
        has_entities = r.has_entities()
        entities = r.entities()
    if has_intents:
        nn.log("user_recommend_answer_prompt", r.utterancre())
        if has_entities:
            if "recommendation_score" in entities:
                recommendation_score = r.entity("recommendation_score")
                if recommendation_score >= 9:
                    return "hangup", "positive"
                elif recommendation_score >= 0 and recommendation_score < 9:
                    return "hangup", "negative"

            if "recommendation" in entities:
                recommendation = r.entity("recommendation")
                match recommendation:
                    case "negative":
                        return "recommend", "negative"
                    case "neutral":
                        return "recommend", "neutral"
                    case "positive":
                        return "recommend", "positive"
                    case "dont_know":
                        return "recommend", "dont_know"
            if "repeat" in entities:
                if r.entity("repeat") == "true":
                    return "recommend", "repeat"
            if "question" in entities:
                if r.entity("question") == "true":
                    return "forward", None
        else:
            if nn.counter("recommend") == 1:
                return "hangup", "null"
            nn.counter("recommend", "+")
            return "recommend", "default"
    else:
        # не выявили намерения phrase - NULL
        if nn.counter("recommend") == 1:
            return "hangup", "null"
        nn.counter("recommend", "+")


def hangup(condition: str, nn: NeuroNetLibrary, nv: NeuroVoiceLibrary) -> str:
    """
    Обрабатывает завершение звонка.

    Args:
        condition (str): Результат разговора.
        nn (NeuroNetLibrary): ...
        nv (NeuroVoiceLibrary): ...

    Returns:
        str: Результат завершения разговора.
    """
    match condition:
        case "positive":
            nv.say("hangup_positive")
            nn.env(call_result="позитивная оценка")
        case "negative":
            nv.say("hangup_negative")
            nn.env(call_result="негативная оценка")
        case "wrong_time":
            nv.say("hangup_wrong_time")
            nn.env(call_result="перезвонить")
        case "null":
            nv.say("hangup_null")
            nn.env(call_result="не разобрать")
    nv.hangup()
    return "DONE"


def forward(nn: NeuroNetLibrary, nv: NeuroVoiceLibrary) -> str:
    """
    Осуществляет перевод звонка на сотрудника.

    Args:
        nn (NeuroNetLibrary): ...
        nv (NeuroVoiceLibrary): ...

    Returns:
        str: Результат перевода звонка.
    """
    nv.say("forward")
    nv.bridge(nn.env("OPERATOR_PHONE_NUMBER"))
    nv.hangup()
    nn.env(call_result="перевод на оператора")
    return "DONE"
