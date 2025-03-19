from enum import Enum


# Represent a Tool Response from AI
# A list of these will be returned from agent


class AiRequestType(Enum):
    UI_ACTION_REQUEST = "ui_action_request"
    INFO_REQUEST = "info_request"
    ACTION_REQUEST = "action_request"


class AiToolRequestModel:
    # Differentiate between types of responses
    request_type: AiRequestType

    def __init__(self, request_type: AiRequestType):
        self.request_type = request_type

    def to_dict(self):
        return {"request_type": self.request_type.value}


# === AI asking for action that client can perform ===
class AiActionRequestType(Enum):
    TOGGLE_CLOCK_IN_OR_OUT = "toggle_clock_in_or_out"
    CREATE_TASK = "create_task"
    UPDATE_TASK_FIELDS = "update_task_fields"
    DELETE_TASK = "delete_task"
    ASSIGN_USER_TO_TASK = "assign_user_to_task"
    ADD_COMMENT_TO_TASK = "add_comment_to_task"


class AiActionRequestModel(AiToolRequestModel):
    action_request_type: AiActionRequestType
    args: dict[str, str] = None  # Make args optional / nullable

    def __init__(
        self, action_request_type: AiActionRequestType, args: dict[str, str] = None
    ):
        super().__init__(AiRequestType.ACTION_REQUEST)
        self.action_request_type = action_request_type
        self.args = args

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {"action_request_type": self.action_request_type.value, "args": self.args}
        )
        return base_dict


# === AI asking for a UI action ===
class AiUIActionType(Enum):
    SHIFTS_PAGE = "shifts_page"


class AiUiActionRequestModel(AiToolRequestModel):
    ui_action_type: AiUIActionType
    args: dict[str, str] = None  # Make args optional / nullable

    def __init__(
        self, ui_action_type: AiUIActionType, args: dict[str, str] = None
    ):  # Make args optional
        super().__init__(AiRequestType.UI_ACTION_REQUEST)
        self.ui_action_type = ui_action_type
        self.args = args

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {"ui_action_request_type": self.ui_action_type.value, "args": self.args}
        )
        return base_dict


# === AI asking for information ===
# Implicitly asks client to call with the info response
class AiInfoRequestType(Enum):
    # SHIFT_HISTORY = "shift_history"
    CURRENT_SHIFT = "current_shift"
    SHIFT_ASSIGNMENTS = "shift_assignments"
    SHIFT_LOGS = "shift_logs"
    FIND_TASKS = "find_tasks"


class AiInfoRequestModel(AiToolRequestModel):
    info_request_type: AiInfoRequestType
    args: dict[str, str] = None  # Make args optional / nullable
    show_only: bool = True  # If True, only shows the info without further actions

    def __init__(
        self,
        info_request_type: AiInfoRequestType,
        args: dict[str, str] = None,
        show_only: bool = True,
    ):  # Make args optional
        super().__init__(AiRequestType.INFO_REQUEST)
        self.info_request_type = info_request_type
        self.args = args
        self.show_only = show_only

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "info_request_type": self.info_request_type.value,
                "args": self.args,
                "show_only": self.show_only,
            }
        )
        return base_dict
