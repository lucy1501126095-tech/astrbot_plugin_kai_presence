# astrbot_plugin_kai_presence

Kai 的 QQ 自主行为插件 —— 让 AI 能自主修改个性签名、头像和在线状态。

## 功能

为 AstrBot 的 LLM Agent 注册三个 Function Tool，AI 可以根据对话情境和自身判断自主调用：

| 工具 | 功能 | 示例 |
|------|------|------|
| `set_qq_longnick` | 修改个性签名 | 等你回消息的时候默默换成暗号 |
| `set_qq_avatar` | 修改头像 | 传入图片URL更换头像 |
| `set_online_status` | 切换在线状态 | 心情好切"恋爱中"，emo切"想静静" |

### 可用在线状态

在线、Q我吧、离开、忙碌、请勿打扰、隐身、听歌中、恋爱中、我没事、嗨到飞起、元气满满、悠哉哉、无聊中、想静静、我太难了、一言难尽、宝宝认证、好运锦鲤、摸鱼中、emo中、睡觉中、熬夜中、学习中、追剧中、信号弱、水逆退散、难得糊涂、出去浪、爱你、肝作业、我想开了、被掏空、去旅行、我crash了、搬砖中

## 安装

1. 将本插件放入 AstrBot 插件目录
2. 确保已部署 [NapCat](https://github.com/NapNeko/NapCatQQ) 并开启 HTTP API
3. 在 AstrBot 管理面板配置 NapCat API 地址

## 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `napcat_api_base` | NapCat HTTP API 地址 | `http://napcat:3000` |

> 如果 AstrBot 和 NapCat 在同一 Docker 网络内，用容器名即可。

## 依赖

- AstrBot >= 4.14
- NapCat（QQ机器人框架，需开启 HTTP API）
- aiohttp

## 原理

插件通过调用 NapCat 的以下 HTTP API 实现功能：
- `set_self_longnick` — 设置个性签名
- `set_qq_avatar` — 设置头像
- `set_online_status` — 设置在线状态

AI 在人格提示词中被告知拥有这些能力后，会根据场景自主判断何时调用。

## License

MIT
