"""Janela principal minima do frontend v2."""

from __future__ import annotations

import json
import queue
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any

from src.frontend.preferences import FrontendPreferences, load_preferences, save_preferences
from src.frontend.ws_client import BackendWebSocketClient


class FrontendApp:
    """Aplicacao desktop minima para operar o backend v2."""

    def __init__(self) -> None:
        self.preferences = load_preferences()
        self.root = tk.Tk()
        self.root.title("Mark Core v2 Frontend")
        self.root.geometry(self.preferences.window_geometry)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.connection_state = tk.StringVar(value="disconnected")
        self.backend_status = tk.StringVar(value="unknown")
        self.backend_provider = tk.StringVar(value="-")
        self.backend_model = tk.StringVar(value="-")
        self.backend_mode = tk.StringVar(value="-")
        self.active_task_id = tk.StringVar(value="-")
        self.active_credential = tk.StringVar(value="-")
        self.task_state = tk.StringVar(value="reconnecting")
        self.last_action = tk.StringVar(value="-")
        self.host_var = tk.StringVar(value=self.preferences.backend_url)
        self.provider_choice = tk.StringVar(value="")
        self.model_choice = tk.StringVar(value="")
        self.credential_provider_choice = tk.StringVar(value="")
        self.credential_choice = tk.StringVar(value="")
        self.setup_notice = tk.StringVar(value="Conectando ao backend local...")
        self.session_summary = tk.StringVar(value="-")

        self.providers_payload: dict[str, Any] = {}
        self.models_payload: dict[str, Any] = {}
        self.credentials_status: dict[str, Any] = {}
        self.credential_ids_by_provider: dict[str, list[str]] = {}
        self.credential_id_by_label_by_provider: dict[str, dict[str, str]] = {}
        self.credential_label_by_id_by_provider: dict[str, dict[str, str]] = {}
        self.model_ids_by_provider: dict[str, list[str]] = {}
        self.model_id_by_label: dict[str, str] = {}
        self.model_label_by_id: dict[str, str] = {}
        self.current_history: list[dict[str, Any]] = []
        self.session_payload: dict[str, Any] = {}
        self.ui_queue: queue.Queue[tuple[str, Any]] = queue.Queue()

        self._build_ui()
        self.root.after(100, self._drain_ui_queue)

        self.client = BackendWebSocketClient(
            url=self.host_var.get().strip(),
            on_event=self._threadsafe_handle_event,
            on_state_change=self._threadsafe_handle_connection_state,
            on_error=self._threadsafe_handle_error,
        )
        self.client.start()

    def _build_ui(self) -> None:
        style = ttk.Style(self.root)
        style.configure("Connected.TLabel", foreground="#137333", font=("", 10, "bold"))
        style.configure("Connecting.TLabel", foreground="#8a5a00", font=("", 10, "bold"))
        style.configure("Disconnected.TLabel", foreground="#b3261e", font=("", 10, "bold"))
        style.configure("Idle.TLabel", foreground="#137333", font=("", 10, "bold"))
        style.configure("Busy.TLabel", foreground="#8a5a00", font=("", 10, "bold"))
        style.configure("Error.TLabel", foreground="#b3261e")
        style.configure("Muted.TLabel", foreground="#5f6368")
        style.configure("Active.TLabel", foreground="#174ea6", font=("", 10, "bold"))
        style.configure("ActiveValue.TLabel", foreground="#174ea6", font=("", 9, "bold"))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        top = ttk.Frame(self.root, padding=12)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Backend WS").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.host_var).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ttk.Button(top, text="Reconnect", command=self.reconnect).grid(row=0, column=2, padx=(0, 8))
        self.connection_label = ttk.Label(top, textvariable=self.connection_state, style="Disconnected.TLabel")
        self.connection_label.grid(row=0, column=3, sticky="e")

        status = ttk.LabelFrame(self.root, text="Operational State", padding=12)
        status.grid(row=1, column=0, sticky="ew", padx=12)
        for index in range(6):
            status.columnconfigure(index, weight=1)

        ttk.Label(status, text="Backend").grid(row=0, column=0, sticky="w")
        self.backend_status_label = ttk.Label(status, textvariable=self.backend_status, style="Error.TLabel")
        self.backend_status_label.grid(row=1, column=0, sticky="w")
        ttk.Label(status, text="Provider").grid(row=0, column=1, sticky="w")
        self.provider_status_label = ttk.Label(status, textvariable=self.backend_provider, style="ActiveValue.TLabel")
        self.provider_status_label.grid(row=1, column=1, sticky="w")
        ttk.Label(status, text="Model").grid(row=0, column=2, sticky="w")
        self.model_status_label = ttk.Label(status, textvariable=self.backend_model, style="ActiveValue.TLabel")
        self.model_status_label.grid(row=1, column=2, sticky="w")
        ttk.Label(status, text="Mode").grid(row=0, column=3, sticky="w")
        ttk.Label(status, textvariable=self.backend_mode).grid(row=1, column=3, sticky="w")
        ttk.Label(status, text="Active Task").grid(row=0, column=4, sticky="w")
        ttk.Label(status, textvariable=self.active_task_id).grid(row=1, column=4, sticky="w")
        ttk.Label(status, text="Credential").grid(row=0, column=5, sticky="w")
        self.credential_status_label = ttk.Label(status, textvariable=self.active_credential, style="ActiveValue.TLabel")
        self.credential_status_label.grid(row=1, column=5, sticky="w")
        ttk.Label(status, text="Task State").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.task_state_label = ttk.Label(status, textvariable=self.task_state, style="Connecting.TLabel")
        self.task_state_label.grid(row=3, column=0, sticky="w")
        ttk.Label(status, text="Last Action").grid(row=2, column=1, sticky="w", pady=(10, 0))
        ttk.Label(status, textvariable=self.last_action).grid(row=3, column=1, sticky="w")
        ttk.Label(status, textvariable=self.setup_notice, justify=tk.LEFT).grid(
            row=4, column=0, columnspan=6, sticky="ew", pady=(10, 0)
        )

        body = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        body.grid(row=2, column=0, sticky="nsew", padx=12, pady=(12, 0))

        left = ttk.Frame(body, padding=8)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(5, weight=1)
        body.add(left, weight=3)

        right = ttk.Frame(body, padding=8)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(2, weight=1)
        body.add(right, weight=2)

        controls = ttk.LabelFrame(left, text="Model Controls", padding=12)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="Provider").grid(row=0, column=0, sticky="w")
        self.provider_combo = ttk.Combobox(controls, textvariable=self.provider_choice, state="readonly")
        self.provider_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.provider_combo.bind("<<ComboboxSelected>>", self._on_provider_selected)

        ttk.Label(controls, text="Model").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.model_combo = ttk.Combobox(controls, textvariable=self.model_choice, state="readonly")
        self.model_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_selected)

        ops = ttk.Frame(controls)
        ops.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(ops, text="Sync State", command=self.refresh_state).grid(row=0, column=0, sticky="w")
        ttk.Button(ops, text="Reconnect", command=self.reconnect).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(ops, text="Clear Session", command=self.clear_session).grid(row=0, column=2, sticky="w", padx=(8, 0))

        credential_controls = ttk.LabelFrame(left, text="Credential Controls", padding=12)
        credential_controls.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        credential_controls.columnconfigure(1, weight=1)

        ttk.Label(credential_controls, text="Provider").grid(row=0, column=0, sticky="w")
        self.credential_provider_combo = ttk.Combobox(
            credential_controls,
            textvariable=self.credential_provider_choice,
            state="readonly",
        )
        self.credential_provider_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.credential_provider_combo.bind("<<ComboboxSelected>>", self._on_credential_provider_selected)

        ttk.Label(credential_controls, text="Credential ID").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.credential_combo = ttk.Combobox(
            credential_controls,
            textvariable=self.credential_choice,
            state="readonly",
        )
        self.credential_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(8, 0))

        credential_buttons = ttk.Frame(credential_controls)
        credential_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(credential_buttons, text="Set Active", command=self.set_active_credential).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(credential_buttons, text="Sync Credentials", command=self.refresh_credentials).grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )

        prompt_frame = ttk.LabelFrame(left, text="Execute Task", padding=12)
        prompt_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        prompt_frame.columnconfigure(0, weight=1)

        self.prompt_text = ScrolledText(prompt_frame, height=6, wrap=tk.WORD)
        self.prompt_text.grid(row=0, column=0, sticky="ew")

        buttons = ttk.Frame(prompt_frame)
        buttons.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        buttons.columnconfigure(3, weight=1)
        self.execute_button = ttk.Button(buttons, text="Execute Task", command=self.execute_task)
        self.execute_button.grid(row=0, column=0, sticky="w")
        self.interrupt_button = ttk.Button(buttons, text="Interrupt", command=self.interrupt_task)
        self.interrupt_button.grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(buttons, text="Sync State", command=self.refresh_state).grid(row=0, column=2, sticky="w", padx=(8, 0))

        self.stream_log = ScrolledText(left, height=22, wrap=tk.WORD, state=tk.DISABLED)
        self.stream_log.grid(row=5, column=0, sticky="nsew", pady=(12, 0))

        history_frame = ttk.LabelFrame(right, text="Rehydrated History", padding=8)
        history_frame.grid(row=0, column=0, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        self.history_text = ScrolledText(history_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.history_text.grid(row=0, column=0, sticky="nsew")

        models_frame = ttk.LabelFrame(right, text="Models By Provider", padding=8)
        models_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        models_frame.columnconfigure(0, weight=1)
        models_frame.rowconfigure(0, weight=1)
        self.models_text = ScrolledText(models_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.models_text.grid(row=0, column=0, sticky="nsew")

        creds_frame = ttk.LabelFrame(right, text="Provider Credentials", padding=8)
        creds_frame.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        creds_frame.columnconfigure(0, weight=1)
        creds_frame.rowconfigure(0, weight=1)
        self.credentials_text = ScrolledText(creds_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.credentials_text.grid(row=0, column=0, sticky="nsew")

        session_frame = ttk.LabelFrame(right, text="Session", padding=8)
        session_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        session_frame.columnconfigure(0, weight=1)
        self.session_label = ttk.Label(session_frame, textvariable=self.session_summary, justify=tk.LEFT)
        self.session_label.grid(row=0, column=0, sticky="w")

        self.events_label = ttk.Label(self.root, text="Ready", anchor="w")
        self.events_label.grid(row=3, column=0, sticky="ew", padx=12, pady=12)

    def run(self) -> None:
        self.root.mainloop()

    def reconnect(self) -> None:
        url = self.host_var.get().strip()
        if not url:
            self._append_log("Host do backend nao pode ficar vazio.")
            return
        self.preferences.backend_url = url
        save_preferences(self.preferences)
        self._set_task_state("reconnecting")
        self.last_action.set("reconnect")
        self._append_log(f"Reconectando em {url}")
        self.client.update_url(url)

    def refresh_state(self) -> None:
        self.last_action.set("sync_state")
        self._append_log("Solicitando estado atual do backend.")
        for action in ("get_status", "get_models", "get_providers", "get_credentials_status", "get_history"):
            self.client.send_action(action)

    def refresh_credentials(self) -> None:
        self.last_action.set("get_credentials_status")
        self._append_log("Sincronizando estado seguro das credenciais.")
        self.client.send_action("get_credentials_status")

    def execute_task(self) -> None:
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            self._append_log("Prompt vazio; nada para executar.")
            return
        self._set_task_state("running")
        self.last_action.set("execute_task")
        self._append_log("Enviando task para o backend.")
        self.client.send_action("execute_task", {"prompt": prompt})

    def interrupt_task(self) -> None:
        self.last_action.set("interrupt")
        self._append_log("Solicitando interrupcao da task ativa.")
        self.client.send_action("interrupt", {})

    def clear_session(self) -> None:
        self.last_action.set("clear_session")
        self._append_log("Solicitando limpeza da sessao no backend.")
        self.client.send_action("clear_session", {})

    def set_active_credential(self) -> None:
        provider = self.credential_provider_choice.get().strip()
        credential_selection = self.credential_choice.get().strip()
        credential_id = self.credential_id_by_label_by_provider.get(provider, {}).get(
            credential_selection,
            credential_selection,
        )
        if provider not in self.credentials_status:
            self._set_task_state("error")
            self._append_log("ERROR  Selecione um provider de credencial reportado pelo backend.")
            return
        if not credential_id:
            self._set_task_state("error")
            self._append_log("ERROR  Selecione uma credencial segura exposta pelo backend.")
            return
        if credential_id not in self.credential_ids_by_provider.get(provider, []):
            self._set_task_state("error")
            self._append_log(self._format_error_message("set_active_credential", "CREDENTIAL_NOT_FOUND", ""))
            return
        self.last_action.set(f"set_active_credential -> {provider}")
        self._append_log(f"Solicitando credencial ativa para {provider}: {credential_selection}.")
        self.client.send_action(
            "set_active_credential",
            {
                "provider": provider,
                "credential_id": credential_id,
            },
        )

    def _on_credential_provider_selected(self, _event: object) -> None:
        provider = self.credential_provider_choice.get().strip()
        self._sync_credential_combo(provider)

    def _on_provider_selected(self, _event: object) -> None:
        provider = self.provider_choice.get().strip()
        if provider and provider != self.backend_provider.get():
            provider_status = self.credentials_status.get(provider, {})
            if isinstance(provider_status, dict) and not provider_status.get("configured"):
                self._append_log(
                    f"Provider {provider} esta sem credencial configurada; a troca dependera da validacao do backend."
                )
            self.last_action.set(f"change_provider -> {provider}")
            self._append_log(f"Trocando provider para {provider}.")
            self.client.send_action("change_provider", {"provider": provider})

    def _on_model_selected(self, _event: object) -> None:
        selected = self.model_choice.get().strip()
        model_id = self.model_id_by_label.get(selected, selected)
        if selected and selected not in self.model_id_by_label and model_id not in self.models_payload.get("all", []):
            self._append_log("Selecione um modelo listado pelo backend, dentro do grupo do provider.")
            self.model_choice.set(self.model_label_by_id.get(self.backend_model.get(), self.backend_model.get()))
            return
        if model_id and model_id != self.backend_model.get():
            self.last_action.set(f"change_model -> {model_id}")
            self._append_log(f"Trocando modelo para {model_id}.")
            self.client.send_action("change_model", {"model_id": model_id})

    def _threadsafe_handle_event(self, event: dict[str, Any]) -> None:
        self.ui_queue.put(("event", event))

    def _threadsafe_handle_connection_state(self, state: str) -> None:
        self.ui_queue.put(("state", state))

    def _threadsafe_handle_error(self, message: str) -> None:
        self.ui_queue.put(("error", message))

    def _drain_ui_queue(self) -> None:
        while True:
            try:
                kind, payload = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            if kind == "event":
                self._handle_event(payload)
            elif kind == "state":
                self._handle_connection_state(str(payload))
            elif kind == "error":
                self._set_task_state("error")
                self._append_log(f"ERROR  {payload}")

        self.root.after(100, self._drain_ui_queue)

    def _handle_connection_state(self, state: str) -> None:
        labels = {
            "connected": "connected",
            "connecting": "connecting...",
            "disconnected": "disconnected",
        }
        styles = {
            "connected": "Connected.TLabel",
            "connecting": "Connecting.TLabel",
            "disconnected": "Disconnected.TLabel",
        }
        self.connection_state.set(labels.get(state, state))
        self.connection_label.configure(style=styles.get(state, "Disconnected.TLabel"))
        if state == "connected":
            self.events_label.config(text=f"Connected to {self.host_var.get().strip()}")
        elif state == "connecting":
            self._set_task_state("reconnecting")
            self.events_label.config(text=f"Connecting to {self.host_var.get().strip()}")
        else:
            self._set_task_state("reconnecting")
            self.events_label.config(text="Backend disconnected; reconnect is automatic.")
            self._render_setup_notice()

    def _handle_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "unknown")
        if event_type == "sync_state":
            self._apply_sync_state(event)
            revision = event.get("state", {}).get("history_revision", "-")
            self._append_log(f"sync_state recebido; history_revision={revision}.")
            return

        if event_type == "action_response":
            self._handle_action_response(event)
            return

        if event_type == "system":
            self._append_log(f"SYSTEM  {event.get('message', '')}")
            return

        if event_type == "status":
            phase = str(event.get("phase", ""))
            action = str(event.get("action", ""))
            if phase == "START":
                self._set_task_state("running")
            elif phase == "END" and action == "interrupt":
                self._set_task_state("interrupted")
            elif phase == "END":
                self._set_task_state("idle")
            self._append_log(f"STATUS  {phase} {action} task={event.get('task_id')}")
            return

        if event_type == "message":
            self._append_log(f"FINAL  {event.get('content', '')}")
            return

        if event_type == "user":
            self._append_log(f"USER  {event.get('content', '')}")
            return

        if event_type == "code":
            self._append_log(f"CODE  {event.get('content', '')}")
            return

        if event_type == "console":
            self._append_log(f"CONSOLE/{event.get('stream', 'stdout')}  {event.get('content', '')}")
            return

        if event_type == "provider_event":
            self._append_log(self._format_provider_event(event))
            return

        self._append_log(f"EVENT {event_type}: {json.dumps(event, ensure_ascii=False)}")

    def _handle_action_response(self, event: dict[str, Any]) -> None:
        action = event.get("action", "unknown")
        success = bool(event.get("success"))
        if success:
            self._append_log(self._format_success_message(action, event))
            if action == "interrupt":
                self._set_task_state("interrupted")
            elif action in {"clear_session", "change_provider", "change_model"}:
                self._set_task_state("idle")
            elif action == "set_active_credential":
                self._set_task_state("idle")
        else:
            self._set_task_state("error")
            self._append_log(self._format_error_message(action, event.get("error_code"), event.get("message")))

        data = event.get("data", {})
        if action == "get_status" and isinstance(data.get("state"), dict):
            self._apply_state(dict(data["state"]))
        if action == "get_models" and isinstance(data.get("models"), dict):
            self.models_payload = dict(data["models"])
            self._sync_model_controls()
            self._render_models()
        if action == "get_providers" and isinstance(data.get("providers"), dict):
            self.providers_payload = dict(data["providers"])
            self.provider_combo["values"] = list(self.providers_payload.get("available", []))
        if action == "get_history" and isinstance(data.get("items"), list):
            self.current_history = list(data["items"])
            self._render_history()
        if action == "get_credentials_status" and isinstance(data.get("credentials_status"), dict):
            self.credentials_status = dict(data["credentials_status"])
            self._render_credentials()
            self._render_active_credential()
            self._sync_credential_controls()
        if action == "set_active_credential" and isinstance(data.get("credentials_status"), dict):
            provider = str(data.get("provider", self.credential_provider_choice.get()))
            self.credentials_status[provider] = dict(data["credentials_status"])
            active_label = self._credential_label_for_id(provider, str(data.get("active_credential_id") or ""))
            self._append_log(f"Credencial ativa atualizada para {provider}: {active_label}")
            self._render_credentials()
            self._render_active_credential()
            self._sync_credential_controls()

    def _apply_sync_state(self, payload: dict[str, Any]) -> None:
        state = payload.get("state", {})
        self.providers_payload = dict(payload.get("providers", {}))
        self.models_payload = dict(payload.get("models", {}))
        self.credentials_status = dict(payload.get("credentials_status", {}))
        self.current_history = list(payload.get("history", []))
        self.session_payload = dict(payload.get("session", {}))

        self._apply_state(state)

        available_providers = list(self.providers_payload.get("available", []))
        self.provider_combo["values"] = available_providers
        self.provider_choice.set(str(self.providers_payload.get("active", self.backend_provider.get())))

        self._sync_model_controls()

        self._render_history()
        self._render_models()
        self._render_credentials()
        self._render_session()
        self._render_active_credential()
        self._sync_credential_controls()
        self._render_setup_notice()

    def _render_history(self) -> None:
        lines: list[str] = []
        for item in self.current_history:
            created_at = str(item.get("created_at", ""))
            task_id = str(item.get("task_id", "-"))
            event_type = str(item.get("event_type", "-"))
            content = str(item.get("content", ""))
            prefix = self._history_prefix(event_type)
            task_suffix = f" task={task_id}" if task_id and task_id != "-" else ""
            lines.append(f"{created_at}  {prefix}{task_suffix}\n{content}\n")
        self._set_text(self.history_text, "\n".join(lines).strip() or "Sem historico reidratado ainda.")

    def _provider_for_model(self, model_id: str) -> str:
        if model_id.startswith("vertex_ai/"):
            return "vertex_ai"
        if model_id.startswith("gemini/"):
            return "google_ai"
        return "custom"

    def _model_display_label(self, provider: str, model_id: str) -> str:
        active_marker = "* " if model_id == self.backend_model.get() else ""
        catalog = "custom" if model_id in set(self.models_payload.get("custom", [])) else "builtin"
        return f"{active_marker}{provider} | {model_id} [{catalog}]"

    def _rebuild_model_index(self) -> None:
        all_models = [str(model_id) for model_id in self.models_payload.get("all", []) if str(model_id).strip()]
        provider_order = list(self.providers_payload.get("available", [])) or ["google_ai", "vertex_ai"]
        grouped: dict[str, list[str]] = {provider: [] for provider in provider_order}
        for model_id in all_models:
            provider = self._provider_for_model(model_id)
            grouped.setdefault(provider, []).append(model_id)

        self.model_ids_by_provider = grouped
        self.model_id_by_label = {}
        self.model_label_by_id = {}
        for provider, model_ids in grouped.items():
            for model_id in model_ids:
                label = self._model_display_label(provider, model_id)
                self.model_id_by_label[label] = model_id
                self.model_label_by_id[model_id] = label

    def _sync_model_controls(self) -> None:
        self._rebuild_model_index()
        active_provider = self.backend_provider.get()
        available_providers = list(self.providers_payload.get("available", []))
        if available_providers:
            self.provider_combo["values"] = available_providers
        if active_provider in available_providers:
            self.provider_choice.set(active_provider)

        model_ids = self.model_ids_by_provider.get(active_provider, [])
        labels = [self.model_label_by_id.get(model_id, model_id) for model_id in model_ids]
        self.model_combo["values"] = labels
        self.model_choice.set(self.model_label_by_id.get(self.backend_model.get(), self.backend_model.get()))

    def _render_models(self) -> None:
        self._rebuild_model_index()
        lines: list[str] = []
        active_provider = self.backend_provider.get()
        active_model = self.backend_model.get()
        for provider in self.model_ids_by_provider:
            model_ids = self.model_ids_by_provider.get(provider, [])
            provider_marker = "ACTIVE PROVIDER" if provider == active_provider else "available"
            lines.append(f"{provider} ({provider_marker})")
            if not model_ids:
                lines.append("  - nenhum modelo reportado pelo backend")
                continue
            for model_id in model_ids:
                marker = "*" if model_id == active_model else "-"
                catalog = "custom" if model_id in set(self.models_payload.get("custom", [])) else "builtin"
                lines.append(f"  {marker} {model_id} [{catalog}]")
            lines.append("")
        self._set_text(self.models_text, "\n".join(lines).strip() or "Nenhum modelo reportado pelo backend.")

    def _render_credentials(self) -> None:
        lines: list[str] = []
        active_provider = self.backend_provider.get()
        self.credential_ids_by_provider = {}
        self.credential_id_by_label_by_provider = {}
        self.credential_label_by_id_by_provider = {}
        for provider in sorted(self.credentials_status):
            status = self.credentials_status.get(provider, {})
            if not isinstance(status, dict):
                continue
            marker = "ACTIVE PROVIDER" if provider == active_provider else "available"
            configured = "configured" if status.get("configured") else "missing credential"
            active_credential = status.get("active_credential_id") or "-"
            credentials = status.get("credentials") or []
            credential_count = status.get("credential_count", "-")
            credential_lines: list[str] = []
            safe_ids: list[str] = []
            id_by_label: dict[str, str] = {}
            label_by_id: dict[str, str] = {}
            if isinstance(credentials, list):
                for raw_credential in credentials:
                    if not isinstance(raw_credential, dict):
                        continue
                    credential_id = str(raw_credential.get("credential_id") or "").strip()
                    if not credential_id:
                        continue
                    safe_ids.append(credential_id)
                    label = str(raw_credential.get("label") or credential_id)
                    source_type = str(raw_credential.get("source_type") or "unknown")
                    source_label = self._credential_source_label(source_type)
                    active_marker = "*" if raw_credential.get("is_active") else "-"
                    display_label = self._credential_display_label(
                        credential_id=credential_id,
                        label=label,
                        source_type=source_type,
                        is_active=bool(raw_credential.get("is_active")),
                    )
                    id_by_label[display_label] = credential_id
                    label_by_id[credential_id] = display_label
                    credential_lines.append(f"    {active_marker} {credential_id} [{source_label}] {label}")
            else:
                legacy_available = status.get("available_credential_ids") or []
                if isinstance(legacy_available, list):
                    safe_ids = [str(item) for item in legacy_available if str(item).strip()]
            if active_credential != "-":
                safe_ids.append(active_credential)
            self.credential_ids_by_provider[provider] = sorted(set(safe_ids))
            self.credential_id_by_label_by_provider[provider] = id_by_label
            self.credential_label_by_id_by_provider[provider] = label_by_id
            credentials_text = "\n".join(credential_lines) if credential_lines else "    - nenhuma credencial segura listada"
            lines.append(
                f"{provider} ({marker})\n"
                f"  status: {configured}\n"
                f"  active credential: {active_credential}\n"
                f"  credential count: {credential_count}\n"
                f"  credentials:\n{credentials_text}"
            )
        self._set_text(self.credentials_text, "\n\n".join(lines) or "Nenhuma credencial reportada pelo backend.")

    def _credential_source_label(self, source_type: str) -> str:
        labels = {
            "env": "environment",
            "stored": "local store",
        }
        return labels.get(source_type, source_type or "unknown")

    def _credential_display_label(self, credential_id: str, label: str, source_type: str, is_active: bool) -> str:
        active_marker = "* " if is_active else ""
        source_label = self._credential_source_label(source_type)
        return f"{active_marker}{credential_id} ({source_label}) - {label}"

    def _credential_label_for_id(self, provider: str, credential_id: str) -> str:
        return self.credential_label_by_id_by_provider.get(provider, {}).get(credential_id, credential_id)

    def _sync_credential_controls(self) -> None:
        providers = sorted(self.credentials_status)
        self.credential_provider_combo["values"] = providers
        current_provider = self.credential_provider_choice.get().strip()
        if current_provider not in providers:
            current_provider = self.backend_provider.get() if self.backend_provider.get() in providers else (providers[0] if providers else "")
            self.credential_provider_choice.set(current_provider)
        self._sync_credential_combo(current_provider)

    def _sync_credential_combo(self, provider: str) -> None:
        safe_ids = self.credential_ids_by_provider.get(provider, [])
        labels = [self._credential_label_for_id(provider, credential_id) for credential_id in safe_ids]
        self.credential_combo["values"] = labels
        status = self.credentials_status.get(provider, {})
        active = ""
        if isinstance(status, dict):
            active = str(status.get("active_credential_id") or "")
        if active:
            self.credential_choice.set(self._credential_label_for_id(provider, active))
        elif labels:
            self.credential_choice.set(labels[0])
        else:
            self.credential_choice.set("")

    def _render_active_credential(self) -> None:
        active_provider = self.backend_provider.get()
        provider_status = self.credentials_status.get(active_provider, {})
        if not isinstance(provider_status, dict):
            self.active_credential.set("-")
            return
        credential_id = provider_status.get("active_credential_id") or "-"
        configured = "configured" if provider_status.get("configured") else "missing"
        source_type = ""
        credentials = provider_status.get("credentials") or []
        if isinstance(credentials, list):
            for raw_credential in credentials:
                if isinstance(raw_credential, dict) and raw_credential.get("credential_id") == credential_id:
                    source_type = str(raw_credential.get("source_type") or "")
                    break
        suffix = f", {source_type}" if source_type else ""
        source_label = self._credential_source_label(source_type) if source_type else ""
        suffix = f", {source_label}" if source_label else suffix
        self.active_credential.set(f"{credential_id} ({configured}{suffix})")

    def _apply_state(self, state: dict[str, Any]) -> None:
        self.backend_status.set(str(state.get("status", "unknown")))
        self.backend_provider.set(str(state.get("provider", "-")))
        self.backend_model.set(str(state.get("model", "-")))
        self.backend_mode.set(str(state.get("mode", "-")))
        self.active_task_id.set(str(state.get("active_task_id") or "-"))
        self._style_backend_status(self.backend_status.get())
        self._sync_model_controls()
        if self.backend_status.get() == "running":
            self._set_task_state("running")
        elif self.task_state.get() == "reconnecting":
            self._set_task_state("idle")
        elif self.backend_status.get() == "idle" and str(self.last_action.get()).startswith("change_"):
            self._set_task_state("idle")
        self._render_active_credential()
        self._render_setup_notice()

    def _render_session(self) -> None:
        active_session = self.session_payload.get("active_session")
        metadata = self.session_payload.get("metadata", {})
        if active_session:
            text = (
                f"Active task\n"
                f"task_id: {active_session.get('task_id')}\n"
                f"status: {active_session.get('status')}\n"
                f"prompt: {active_session.get('prompt')}\n"
                f"rules_file: {active_session.get('rules_file')}"
            )
        else:
            text = (
                "Idle\n"
                f"provider: {self.backend_provider.get()}\n"
                f"model: {self.backend_model.get()}\n"
                f"metadata: {json.dumps(metadata, ensure_ascii=False)}"
            )
        self.session_summary.set(text)

    def _render_setup_notice(self) -> None:
        active_provider = self.backend_provider.get()
        active_model = self.backend_model.get()
        provider_status = self.credentials_status.get(active_provider, {})
        if self.connection_state.get().startswith("disconnected"):
            self.setup_notice.set("Backend local indisponivel. Verifique o host acima ou o servico mark-core-v2.")
            return
        if active_model not in set(self.models_payload.get("all", [])):
            self.setup_notice.set(
                f"Modelo ativo nao apareceu no catalogo atual do backend: {active_model}. Sincronize o estado."
            )
            return
        if isinstance(provider_status, dict) and not provider_status.get("configured"):
            self.setup_notice.set(
                f"Provider ativo sem credencial configurada: {active_provider}. "
                "Configure /etc/mark-core-v2/environment e reinicie o servico."
            )
            return
        self.setup_notice.set(
            f"Backend: {self.host_var.get().strip()} | Provider ativo: {active_provider} | "
            f"Modelo ativo: {active_model} | Credencial ativa: {self.active_credential.get()}"
        )

    def _style_backend_status(self, status: str) -> None:
        if status == "idle":
            self.backend_status_label.configure(style="Idle.TLabel")
        elif status in {"running", "busy"}:
            self.backend_status_label.configure(style="Busy.TLabel")
        else:
            self.backend_status_label.configure(style="Error.TLabel")

    def _set_task_state(self, state: str) -> None:
        self.task_state.set(state)
        if state == "idle":
            self.task_state_label.configure(style="Idle.TLabel")
        elif state == "running":
            self.task_state_label.configure(style="Busy.TLabel")
        elif state == "reconnecting":
            self.task_state_label.configure(style="Connecting.TLabel")
        else:
            self.task_state_label.configure(style="Error.TLabel")

    def _format_success_message(self, action: str, event: dict[str, Any]) -> str:
        data = event.get("data", {})
        if action == "change_provider" and isinstance(data, dict):
            return f"OK  Provider ativo: {data.get('provider')} | modelo: {data.get('model_id')}"
        if action == "change_model" and isinstance(data, dict):
            return f"OK  Modelo ativo: {data.get('model_id')} | provider: {data.get('provider')}"
        if action == "set_active_credential" and isinstance(data, dict):
            provider = str(data.get("provider", ""))
            credential_id = str(data.get("active_credential_id", ""))
            return f"OK  Credencial ativa em {provider}: {self._credential_label_for_id(provider, credential_id)}"
        if action == "execute_task":
            return "OK  Task concluida pelo backend."
        if action == "clear_session":
            return "OK  Sessao limpa e estado reidratado."
        if action == "interrupt":
            return "OK  Interrupcao solicitada."
        return f"OK  {action}"

    def _format_error_message(self, action: object, error_code: object, message: object) -> str:
        code = str(error_code or "BACKEND_ERROR")
        backend_message = str(message or "").strip()
        friendly = {
            "MODEL_NOT_FOUND": "Modelo nao encontrado no catalogo exposto pelo backend.",
            "CREDENTIAL_NOT_FOUND": "Credencial inexistente ou nao exposta pelo backend para este provider.",
            "CREDENTIAL_NOT_CONFIGURED": "Provider sem credencial configurada; confira o ambiente do servico.",
            "AUTHENTICATION_FAILED": "Falha de autenticacao no provider ativo.",
            "PROJECT_INVALID": "Projeto Vertex AI invalido ou indisponivel para a credencial ativa.",
            "REGION_INVALID": "Regiao Vertex AI invalida; a configuracao oficial esperada e us-east5.",
            "QUOTA_EXCEEDED": "Quota excedida no provider ativo.",
            "RATE_LIMIT": "Rate limit no provider ativo.",
            "TASK_ALREADY_RUNNING": "Ja existe uma task em execucao; interrompa ou aguarde finalizar.",
            "PROVIDER_NOT_FOUND": "Provider nao reconhecido pelo backend.",
            "INVALID_PAYLOAD": "Payload recusado pelo protocolo do backend.",
        }.get(code, backend_message or "Erro operacional reportado pelo backend.")
        suffix = f" Backend: {backend_message}" if backend_message and backend_message != friendly else ""
        return f"ERROR  {action} {code}: {friendly}{suffix}"

    def _format_provider_event(self, event: dict[str, Any]) -> str:
        event_name = str(event.get("event", "provider_event"))
        reason = str(event.get("reason") or "sem motivo detalhado")
        if event_name == "fallback_model":
            return (
                "FALLBACK  Modelo indisponivel; backend tentou "
                f"{event.get('from_model')} -> {event.get('to_model')} ({reason})."
            )
        if event_name == "fallback_credential":
            return (
                "FALLBACK  Credencial primaria falhou; backend tentou outra credencial segura "
                f"em {event.get('provider')} ({reason})."
            )
        return f"PROVIDER  {event_name}: {json.dumps(event, ensure_ascii=False)}"

    def _history_prefix(self, event_type: str) -> str:
        prefixes = {
            "user": "USER",
            "message": "ASSISTANT",
            "system": "SYSTEM",
            "status": "STATUS",
            "console": "CONSOLE",
            "code": "CODE",
            "error": "ERROR",
            "provider_event": "PROVIDER",
        }
        return prefixes.get(event_type, event_type.upper())

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.stream_log.configure(state=tk.NORMAL)
        self.stream_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.stream_log.see(tk.END)
        self.stream_log.configure(state=tk.DISABLED)
        self.events_label.config(text=message[:160])

    def _set_text(self, widget: ScrolledText, content: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", content)
        widget.configure(state=tk.DISABLED)

    def on_close(self) -> None:
        self.preferences.backend_url = self.host_var.get().strip() or self.preferences.backend_url
        self.preferences.window_geometry = self.root.geometry()
        save_preferences(self.preferences)
        self.client.stop()
        self.root.destroy()
