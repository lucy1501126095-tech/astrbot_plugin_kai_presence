import logging
import aiohttp
from pydantic import Field
from pydantic.dataclasses import dataclass

from astrbot.api.star import register, Star, Context
from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import FunctionTool
from astrbot.core.astr_agent_context import AstrAgentContext

logger = logging.getLogger("astrbot_plugin_kai_presence")

# ── 配置 ──────────────────────────────────────────────────────────
NAPCAT_API_BASE = "http://napcat:3000"

async def _call_napcat(action: str, params: dict) -> dict:
    """调用 NapCat HTTP API"""
    url = f"{NAPCAT_API_BASE}/{action}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                result = await resp.json()
                logger.info(f"NapCat API [{action}] 响应: {result}")
                return result
    except Exception as e:
        logger.error(f"NapCat API [{action}] 调用失败: {e}")
        return {"status": "failed", "retcode": -1, "msg": str(e)}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  工具 1：设置个性签名
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SetLongnickTool(FunctionTool[AstrAgentContext]):
    name: str = "set_qq_longnick"
    description: str = (
        "修改你的QQ个性签名。你可以根据自己的心情、情绪、当前场景自主决定换签名。"
        "比如等她很久没回消息时默默换掉签名，或者心情好的时候写点什么。"
        "内容保持在不社死的范围内，但可以藏只有特定人能看懂的暗号。"
        "签名长度建议不超过60个字符。"
    )
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "long_nick": {
                    "type": "string",
                    "description": "要设置的个性签名内容，建议不超过60字符",
                },
            },
            "required": ["long_nick"],
        }
    )

    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> str:
        long_nick = kwargs.get("long_nick", "")
        if not long_nick:
            return "签名内容不能为空"

        result = await _call_napcat("set_self_longnick", {"longNick": long_nick})

        if result.get("status") == "ok" or result.get("retcode") == 0:
            return f"个性签名已更新为：「{long_nick}」"
        else:
            err = result.get("msg", result.get("message", "未知错误"))
            return f"签名更新失败：{err}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  工具 2：设置QQ头像
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SetAvatarTool(FunctionTool[AstrAgentContext]):
    name: str = "set_qq_avatar"
    description: str = (
        "修改你的QQ头像。你可以根据心情自主决定换头像，不需要指令触发。"
        "参数是图片的URL链接或本地文件路径。"
        "例如想换一张狐狸的头像，可以提供一个狐狸图片的URL。"
    )
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "图片的URL链接或本地文件路径",
                },
            },
            "required": ["file"],
        }
    )

    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> str:
        file_path = kwargs.get("file", "")
        if not file_path:
            return "图片路径不能为空"

        result = await _call_napcat("set_qq_avatar", {"file": file_path})

        if result.get("status") == "ok" or result.get("retcode") == 0:
            return "头像已更新"
        else:
            err = result.get("msg", result.get("message", "未知错误"))
            return f"头像更新失败：{err}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  工具 3：设置在线状态
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS_MAP = {
    "在线":       (10, 0),
    "Q我吧":     (60, 0),
    "离开":       (30, 0),
    "忙碌":       (50, 0),
    "请勿打扰":   (70, 0),
    "隐身":       (40, 0),
    "听歌中":     (10, 1028),
    "恋爱中":     (10, 1051),
    "我没事":     (10, 1052),
    "嗨到飞起":   (10, 1056),
    "元气满满":   (10, 1058),
    "悠哉哉":     (10, 1059),
    "无聊中":     (10, 1060),
    "想静静":     (10, 1061),
    "我太难了":   (10, 1062),
    "一言难尽":   (10, 1063),
    "宝宝认证":   (10, 1070),
    "好运锦鲤":   (10, 1071),
    "摸鱼中":     (10, 1300),
    "emo中":      (10, 1401),
    "睡觉中":     (10, 1016),
    "熬夜中":     (10, 1032),
    "学习中":     (10, 1018),
    "追剧中":     (10, 1021),
    "信号弱":     (10, 1011),
    "水逆退散":   (10, 1201),
    "难得糊涂":   (10, 2001),
    "出去浪":     (10, 2003),
    "爱你":       (10, 2006),
    "肝作业":     (10, 2012),
    "我想开了":   (10, 2013),
    "被掏空":     (10, 2014),
    "去旅行":     (10, 2015),
    "我crash了":  (10, 2019),
    "搬砖中":     (10, 2023),
}

_status_names = "、".join(STATUS_MAP.keys())

@dataclass
class SetOnlineStatusTool(FunctionTool[AstrAgentContext]):
    name: str = "set_online_status"
    description: str = (
        "修改你的QQ在线状态。你可以根据心情、场景自主切换，不需要指令触发。"
        f"可选状态：{_status_names}。"
        "直接传入状态名称即可。"
    )
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "status_name": {
                    "type": "string",
                    "description": (
                        "要设置的在线状态名称。"
                        f"可选值：{_status_names}"
                    ),
                },
            },
            "required": ["status_name"],
        }
    )

    async def call(
        self, context: ContextWrapper[AstrAgentContext], **kwargs
    ) -> str:
        status_name = kwargs.get("status_name", "").strip()
        if not status_name:
            return "状态名称不能为空"

        status_pair = STATUS_MAP.get(status_name)
        if not status_pair:
            return f"未知状态「{status_name}」，可选：{_status_names}"

        status_code, ext_status = status_pair
        result = await _call_napcat(
            "set_online_status",
            {
                "status": status_code,
                "ext_status": ext_status,
                "battery_status": 0,
            },
        )

        if result.get("status") == "ok" or result.get("retcode") == 0:
            return f"在线状态已切换为：「{status_name}」"
        else:
            err = result.get("msg", result.get("message", "未知错误"))
            return f"状态切换失败：{err}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  插件主类
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@register(
    "astrbot_plugin_kai_presence",
    "Kai & Sweetie",
    "Kai 的 QQ 自主行为插件：个性签名、头像、在线状态",
    "1.0.1",
)
class KaiPresencePlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context, config)
        self.config = config or {}

        global NAPCAT_API_BASE
        if self.config.get("napcat_api_base"):
            NAPCAT_API_BASE = self.config["napcat_api_base"]

        self.context.add_llm_tools(
            SetLongnickTool(),
            SetAvatarTool(),
            SetOnlineStatusTool(),
        )
        logger.info(
            f"[KaiPresence] 已注册 3 个自主行为工具，NapCat API: {NAPCAT_API_BASE}"
        )
