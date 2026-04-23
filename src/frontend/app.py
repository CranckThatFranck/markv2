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
        self.host_var = tk.StringVar(value=self.preferences.backend_url)
        self.provider_choice = tk.StringVar(value="")
        self.model_choice = tk.StringVar(value="")

        self.providers_payload: dict[str, Any] = {}
        self.models_payload: dict[str, Any] = {}
        self.credentials_status: dict[str, Any] = {}
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
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        top = ttk.Frame(self.root, padding=12)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Backend WS").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.host_var).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ttk.Button(top, text="Reconnect", command=self.reconnect).grid(row=0, column=2, padx=(0, 8))
        ttk.Label(top, textvariable=self.connection_state).grid(row=0, column=3, sticky="e")

        status = ttk.LabelFrame(self.root, text="Operational State", padding=12)
        status.grid(row=1, column=0, sticky="ew", padx=12)
        for index in range(5):
            status.columnconfigure(index, weight=1)

        ttk.Label(status, text="Backend").grid(row=0, column=0, sticky="w")
        ttk.Label(status, textvariable=self.backend_status).grid(row=1, column=0, sticky="w")
        ttk.Label(status, text="Provider").grid(row=0, column=1, sticky="w")
        ttk.Label(status, textvariable=self.backend_provider).grid(row=1, column=1, sticky="w")
        ttk.Label(status, text="Model").grid(row=0, column=2, sticky="w")
        ttk.Label(status, textvariable=self.backend_model).grid(row=1, column=2, sticky="w")
        ttk.Label(status, text="Mode").grid(row=0, column=3, sticky="w")
        ttk.Label(status, textvariable=self.backend_mode).grid(row=1, column=3, sticky="w")
        ttk.Label(status, text="Active Task").grid(row=0, column=4, sticky="w")
        ttk.Label(status, textvariable=self.active_task_id).grid(row=1, column=4, sticky="w")

        body = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        body.grid(row=2, column=0, sticky="nsew", padx=12, pady=(12, 0))

        left = ttk.Frame(body, padding=8)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(5, weight=1)
        body.add(left, weight=3)

        right = ttk.Frame(body, padding=8)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(3, weight=1)
        body.add(right, weight=2)

        controls = ttk.LabelFrame(left, text="Actions", padding=12)
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

        prompt_frame = ttk.LabelFrame(left, text="Execute Task", padding=12)
        prompt_frame.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        prompt_frame.columnconfigure(0, weight=1)

        self.prompt_text = ScrolledText(prompt_frame, height=6, wrap=tk.WORD)
        self.prompt_text.grid(row=0, column=0, sticky="ew")

        buttons = ttk.Frame(prompt_frame)
        buttons.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        buttons.columnconfigure(0, weight=1)
        ttk.Button(buttons, text="Execute Task", command=self.execute_task).grid(row=0, column=0, sticky="w")
        ttk.Button(buttons, text="Interrupt", command=self.interrupt_task).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Button(buttons, text="Refresh Status", command=self.refresh_state).grid(row=0, column=2, sticky="w", padx=(8, 0))

        self.stream_log = ScrolledText(left, height=22, wrap=tk.WORD, state=tk.DISABLED)
        self.stream_log.grid(row=5, column=0, sticky="nsew", pady=(12, 0))

        history_frame = ttk.LabelFrame(right, text="History Rehydrated", padding=8)
        history_frame.grid(row=0, column=0, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        self.history_text = ScrolledText(history_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.history_text.grid(row=0, column=0, sticky="nsew")

        creds_frame = ttk.LabelFrame(right, text="Credentials Status", padding=8)
        creds_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        creds_frame.columnconfigure(0, weight=1)
        creds_frame.rowconfigure(0, weight=1)
        self.credentials_text = ScrolledText(creds_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.credentials_text.grid(row=0, column=0, sticky="nsew")

        session_frame = ttk.LabelFrame(right, text="Session", padding=8)
        session_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        session_frame.columnconfigure(0, weight=1)
        self.session_label = ttk.Label(session_frame, text="-", justify=tk.LEFT)
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
        self.client.update_url(url)

    def refresh_state(self) -> None:
        for action in ("get_status", "get_models", "get_providers", "get_credentials_status", "get_history"):
            self.client.send_action(action)

    def execute_task(self) -> None:
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            self._append_log("Prompt vazio; nada para executar.")
            return
        self.client.send_action("execute_task", {"prompt": prompt})

    def interrupt_task(self) -> None:
        self.client.send_action("interrupt", {})

    def _on_provider_selected(self, _event: object) -> None:
        provider = self.provider_choice.get().strip()
        if provider and provider != self.backend_provider.get():
            self.client.send_action("change_provider", {"provider": provider})

    def _on_model_selected(self, _event: object) -> None:
        model_id = self.model_choice.get().strip()
        if model_id and model_id != self.backend_model.get():
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
                self._append_log(str(payload))

        self.root.after(100, self._drain_ui_queue)

    def _handle_connection_state(self, state: str) -> None:
        self.connection_state.set(state)
        self.events_label.config(text=f"Connection: {state}")

    def _handle_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type", "unknown")
        if event_type == "sync_state":
            self._apply_sync_state(event)
            self._append_log("sync_state recebido.")
            return

        if event_type == "action_response":
            self._handle_action_response(event)
            return

        if event_type == "system":
            self._append_log(f"SYSTEM: {event.get('message', '')}")
            return

        if event_type == "status":
            self._append_log(f"STATUS {event.get('phase')} {event.get('action')} task={event.get('task_id')}")
            return

        if event_type == "message":
            self._append_log(f"MESSAGE: {event.get('content', '')}")
            return

        if event_type == "user":
            self._append_log(f"USER: {event.get('content', '')}")
            return

        if event_type == "code":
            self._append_log(f"CODE: {event.get('content', '')}")
            return

        if event_type == "console":
            self._append_log(f"CONSOLE[{event.get('stream', 'stdout')}]: {event.get('content', '')}")
            return

        if event_type == "provider_event":
            self._append_log(f"PROVIDER_EVENT: {json.dumps(event, ensure_ascii=False)}")
            return

        self._append_log(f"EVENT {event_type}: {json.dumps(event, ensure_ascii=False)}")

    def _handle_action_response(self, event: dict[str, Any]) -> None:
        action = event.get("action", "unknown")
        success = bool(event.get("success"))
        if success:
            self._append_log(f"ACTION_RESPONSE ok: {action}")
        else:
            self._append_log(
                f"ACTION_RESPONSE error: {action} {event.get('error_code', '')} {event.get('message', '')}".strip()
            )

        data = event.get("data", {})
        if action == "get_history" and isinstance(data.get("items"), list):
            self.current_history = list(data["items"])
            self._render_history()
        if action == "get_credentials_status" and isinstance(data.get("credentials_status"), dict):
            self.credentials_status = dict(data["credentials_status"])
            self._render_credentials()

    def _apply_sync_state(self, payload: dict[str, Any]) -> None:
        state = payload.get("state", {})
        self.providers_payload = dict(payload.get("providers", {}))
        self.models_payload = dict(payload.get("models", {}))
        self.credentials_status = dict(payload.get("credentials_status", {}))
        self.current_history = list(payload.get("history", []))
        self.session_payload = dict(payload.get("session", {}))

        self.backend_status.set(str(state.get("status", "unknown")))
        self.backend_provider.set(str(state.get("provider", "-")))
        self.backend_model.set(str(state.get("model", "-")))
        self.backend_mode.set(str(state.get("mode", "-")))
        self.active_task_id.set(str(state.get("active_task_id") or "-"))

        available_providers = list(self.providers_payload.get("available", []))
        self.provider_combo["values"] = available_providers
        self.provider_choice.set(str(self.providers_payload.get("active", self.backend_provider.get())))

        all_models = list(self.models_payload.get("all", []))
        self.model_combo["values"] = all_models
        self.model_choice.set(self.backend_model.get())

        self._render_history()
        self._render_credentials()
        self._render_session()

    def _render_history(self) -> None:
        lines: list[str] = []
        for item in self.current_history:
            created_at = str(item.get("created_at", ""))
            task_id = str(item.get("task_id", "-"))
            event_type = str(item.get("event_type", "-"))
            content = str(item.get("content", ""))
            lines.append(f"{created_at} [{task_id}] {event_type}: {content}")
        self._set_text(self.history_text, "\n".join(lines))

    def _render_credentials(self) -> None:
        self._set_text(self.credentials_text, json.dumps(self.credentials_status, ensure_ascii=False, indent=2))

    def _render_session(self) -> None:
        active_session = self.session_payload.get("active_session")
        metadata = self.session_payload.get("metadata", {})
        if active_session:
            text = (
                f"Active session\n"
                f"task_id: {active_session.get('task_id')}\n"
                f"status: {active_session.get('status')}\n"
                f"prompt: {active_session.get('prompt')}\n"
                f"rules_file: {active_session.get('rules_file')}"
            )
        else:
            text = f"Idle session\nmetadata: {json.dumps(metadata, ensure_ascii=False)}"
        self.session_label.config(text=text)

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
