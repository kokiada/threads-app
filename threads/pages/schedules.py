import reflex as rx
from ..components import sidebar
from ..states.schedule_state import ScheduleState

def schedules_page() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.box(
            rx.vstack(
                rx.heading("スケジュール設定", size="8"),
                
                rx.card(
                    rx.vstack(
                        rx.heading("新規スケジュール作成", size="6"),
                        rx.select.root(
                            rx.select.trigger(placeholder="アカウントを選択"),
                            rx.select.content(
                                rx.foreach(
                                    ScheduleState.accounts,
                                    lambda a: rx.select.item(a["name"], value=a["id"]),
                                ),
                            ),
                            on_change=ScheduleState.set_selected_account_id,
                        ),
                        rx.select(
                            ["FIXED", "RANDOM"],
                            value=ScheduleState.schedule_type,
                            on_change=ScheduleState.set_schedule_type,
                        ),
                        rx.cond(
                            ScheduleState.schedule_type == "FIXED",
                            rx.input(
                                placeholder="時刻（例: 10:00, 15:00, 20:00）",
                                value=ScheduleState.fixed_times,
                                on_change=ScheduleState.set_fixed_times,
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.text("開始時刻:"),
                                    rx.input(
                                        type="time",
                                        value=ScheduleState.random_start,
                                        on_change=ScheduleState.set_random_start,
                                    ),
                                ),
                                rx.hstack(
                                    rx.text("終了時刻:"),
                                    rx.input(
                                        type="time",
                                        value=ScheduleState.random_end,
                                        on_change=ScheduleState.set_random_end,
                                    ),
                                ),
                                rx.hstack(
                                    rx.text("投稿回数:"),
                                    rx.input(
                                        type="number",
                                        value=ScheduleState.random_count,
                                        on_change=ScheduleState.set_random_count,
                                    ),
                                ),
                            ),
                        ),
                        rx.checkbox(
                            "有効化",
                            checked=ScheduleState.is_active,
                            on_change=ScheduleState.set_is_active,
                        ),
                        rx.button("作成", on_click=ScheduleState.create_schedule),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                rx.card(
                    rx.vstack(
                        rx.heading("登録済みスケジュール", size="6"),
                        rx.foreach(
                            ScheduleState.schedules,
                            lambda s: rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(s["account_name"], weight="bold"),
                                        rx.badge(s["schedule_type"]),
                                        rx.cond(
                                            s["is_active"],
                                            rx.badge("有効", color_scheme="green"),
                                            rx.badge("無効", color_scheme="gray"),
                                        ),
                                    ),
                                    rx.cond(
                                        s["schedule_type"] == "FIXED",
                                        rx.hstack(rx.text("時刻:"), rx.text(s["fixed_times"])),
                                        rx.hstack(rx.text(s["random_start_time"]), rx.text("-"), rx.text(s["random_end_time"])),
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            "有効/無効切替",
                                            on_click=lambda sid=s["id"]: ScheduleState.toggle_schedule(sid),
                                            size="2",
                                        ),
                                        rx.button(
                                            "削除",
                                            on_click=lambda sid=s["id"]: ScheduleState.delete_schedule(sid),
                                            color_scheme="red",
                                            size="2",
                                        ),
                                    ),
                                    spacing="2",
                                ),
                            ),
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                
                spacing="6",
                padding="2rem",
                align="start",
            ),
            margin_left="250px",
            on_mount=[
                ScheduleState.load_accounts,
                ScheduleState.load_schedules,
            ],
        ),
    )
