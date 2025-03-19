from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest

@register("astrbot_plugin_pojiabaohu", "大沙北", "过滤用户请求中可能篡改系统指令的关键词", "1.1.0")
class PojiaProtectionPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.keywords = ['system', 'role', 'content']
        self.is_enabled = True  # 插件默认开启
    
    @filter.command("开启破甲保护")
    async def enable_protection(self, event: AstrMessageEvent):
        '''开启破甲保护'''
        self.is_enabled = True
        yield event.plain_result("破甲保护已开启。")

    @filter.command("关闭破甲保护")
    async def disable_protection(self, event: AstrMessageEvent):
        '''关闭破甲保护'''
        self.is_enabled = False
        yield event.plain_result("破甲保护已关闭。")
    
    @filter.on_llm_request()
    async def check_request(self, event: AstrMessageEvent, req: ProviderRequest):
        if not self.is_enabled:
            return
        
        # 检测请求中的关键词
        count = sum(1 for keyword in self.keywords if keyword in req.prompt.lower())
        
        # 如果包含两个或以上关键词
        if count >= 2:
            # 替换整个请求为提示信息
            filtered_response = "（该用户请求涉嫌篡改系统指令，已过滤拦截）"
            # 清空原请求内容
            req.prompt = "这个坏蛋发送了不好的信息，已经被系统拦截了！"
            # 设置新的结果
            event.set_result(filtered_response)
            # 阻止进一步处理请求
            event.stop_event()
