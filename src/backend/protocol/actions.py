"""Catalogo de acoes do protocolo do Mark Core v2."""

from __future__ import annotations

from enum import StrEnum


class ActionName(StrEnum):
    HEALTHCHECK = "healthcheck"
    GET_STATUS = "get_status"
    GET_CONFIG = "get_config"
    UPDATE_CONFIG = "update_config"
    GET_MODELS = "get_models"
    GET_PROVIDERS = "get_providers"
    GET_CREDENTIALS_STATUS = "get_credentials_status"
    CHANGE_MODEL = "change_model"
    CHANGE_PROVIDER = "change_provider"
    SET_ACTIVE_CREDENTIAL = "set_active_credential"
    ADD_CUSTOM_MODEL = "add_custom_model"
    REMOVE_CUSTOM_MODEL = "remove_custom_model"
    GET_HISTORY = "get_history"
    CLEAR_SESSION = "clear_session"
    EXECUTE_TASK = "execute_task"
    INTERRUPT = "interrupt"
    SHUTDOWN_BACKEND = "shutdown_backend"


def all_actions() -> set[str]:
    """Retorna todas as acoes aceitas pelo backend."""

    return {action.value for action in ActionName}


def is_valid_action(action: str) -> bool:
    """Valida se a acao informada existe no contrato v2."""

    return action in all_actions()
