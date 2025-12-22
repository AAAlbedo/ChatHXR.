import streamlit as st
import openai
import random
from datetime import datetime, timedelta, timezone

# ==================== 0. 个性化配置区====================

# API Key
# 从 Streamlit 的云端保险箱获取 Key
if "MY_API_KEY" in st.secrets:
    MY_API_KEY = st.secrets["MY_API_KEY"]
else:
    MY_API_KEY = "sk-eb925755be154d0c96c05dbf48ff6b2a"

# 头像
USER_AVATAR = "https://pic1.zhimg.com/v2-f00e1ee5a7048f19c4573e923164fe59_r.webp?source=1d2f5c51"  # zzx的头像
AI_AVATAR = "https://pic1.zhimg.com/v2-ea1a4c3b534237d690ab728b273c4adb_r.webp?source=1d2f5c51"    # AI 的头像

# 网易云歌单 ID
SONG_IDS = ['2665800803','2111993057','1946818329','1440551529','1363342575']

# ==================== 1. 基础配置 ====================
st.set_page_config(
    page_title="ChatHXR",
    page_icon="https://picx.zhimg.com/v2-06919e709c2189a4c5fbbc422710882a_xld.webp?source=1d2f5c51",
    layout="wide",
    initial_sidebar_state="expanded" # 默认展开侧边栏
)

# ==================== 2. 动态背景和样式 ====================
# 获取时间段对应的背景图片
def get_background_image():
    h = datetime.now(timezone(timedelta(hours=8))).hour
    if 7 <= h < 11:  # 早上
        return "https://pic3.zhimg.com/100/v2-fd0b25633c415c7f921bd441f249d96a_r.jpg"
    elif 11 <= h < 17:  # 午间
        return "https://picx.zhimg.com/100/v2-610d2d9769577efa1f4275e8ce8c2e79_r.jpg"
    elif 17 <= h < 22:  # 晚上
        return "https://pic3.zhimg.com/100/v2-141c7bc7629f1336ab67c46572781f1a_r.jpg"
    elif 22 <= h <= 24 or 0 <= h < 3:  # 夜深
        return "https://pic3.zhimg.com/100/v2-dc802c4ccf947c58f9af9a1c49ab473a_r.jpg"
    else:  # 凌晨 (3-7)
        return "https://pic3.zhimg.com/100/v2-683ccef75b3630680790707d0869212c_r.jpg"

# 获取背景图片
bg_image = get_background_image()
has_messages = len(st.session_state.get("messages", [])) > 0
bg_opacity = 0.6 if has_messages else 0.15
snow_state = st.session_state.get("snow_state", "stop")

# ==================== 替换后的新代码 ====================

# 1. 静态样式 (背景图、聊天框美化)
st.markdown(f"""
<style>
/* 隐藏 Streamlit 自带的菜单 */
.stDeployButton {{display:none;}}
header[data-testid="stHeader"] {{background: transparent;}}

/* 全局背景设置 */
.stApp {{
    background: linear-gradient(135deg, rgba(20, 20, 30, 0.95) 0%, rgba(30, 25, 40, 0.9) 100%);
}}
.stApp::before {{
    content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image: url('{bg_image}'); background-size: cover; background-position: center;
    opacity: {bg_opacity}; z-index: 0; pointer-events: none;
}}

/* 聊天气泡样式 */
.stChatMessage {{
    background-color: rgba(30, 30, 40, 0.85) !important;
    border: 1px solid rgba(100, 255, 218, 0.3) !important;
    border-radius: 15px !important;
    backdrop-filter: blur(5px);
    z-index: 1; position: relative;
}}
</style>
""", unsafe_allow_html=True)

# 2. 强力下雪脚本 (使用 components 组件穿透 iframe)
# 这里的代码会直接注入到浏览器主窗口，不再被 st.markdown 拦截
import streamlit.components.v1 as components  # 必须引入这个库
snow_html = f"""
<script>
    // 1. 穿透 Streamlit 的 iframe，直接操作父页面 (浏览器窗口)
    var parentDoc = window.parent.document;
    
    // 2. 检查状态
    var state = "{snow_state}";
    console.log("❄️ 呼呼呼:", state);

    // 3. 定义清理函数
    function clearSnow() {{
        var old = parentDoc.getElementById('global-snow-layer');
        if (old) old.remove();
    }}

    // 先清理旧的，防止重叠
    clearSnow();

    // 4. 如果状态是 down 或 up，开始生成
    if (state === 'down' || state === 'up') {{
        // 创建全屏容器
        var container = parentDoc.createElement('div');
        container.id = 'global-snow-layer';
        container.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:999999; overflow:hidden;';
        parentDoc.body.appendChild(container);

        // 注入动画 CSS
        var style = parentDoc.createElement('style');
        style.innerHTML = `
            @keyframes fall {{ 0% {{ top: -5%; opacity: 1; }} 100% {{ top: 105%; opacity: 0; }} }}
            @keyframes rise {{ 0% {{ top: 105%; opacity: 1; }} 100% {{ top: -5%; opacity: 0; }} }}
            .snow-emoji {{ position: absolute; user-select: none; }}
        `;
        container.appendChild(style);

        // 启动生成器
        var interval = setInterval(function() {{
            // 如果容器被删了(比如停止了)，清除定时器
            if (!parentDoc.getElementById('global-snow-layer')) {{
                clearInterval(interval);
                return;
            }}
            
            var flake = parentDoc.createElement('div');
            flake.className = 'snow-emoji';
            flake.innerHTML = '❄️'; // 雪花图标
            
            // 随机属性
            flake.style.left = Math.random() * 100 + 'vw';
            flake.style.fontSize = (Math.random() * 20 + 10) + 'px';
            flake.style.color = 'rgba(255,255,255,' + (Math.random()*0.5 + 0.5) + ')';
            
            var duration = Math.random() * 3 + 2; // 2-5秒
            var anim = (state === 'down' ? 'fall' : 'rise');
            
            flake.style.animation = `${{anim}} ${{duration}}s linear`;
            
            container.appendChild(flake);

            // 动画结束后删除 DOM 节点
            setTimeout(function() {{ flake.remove(); }}, duration * 1000);

        }}, 100); // 每 100ms 生成一片
    }}
</script>
"""

# 执行脚本，height=0 隐藏组件本身
components.html(snow_html, height=0, width=0)
# ==================== 3. 逻辑处理 ====================

# 配置 API
if "api_key" not in st.session_state:
    st.session_state.api_key = MY_API_KEY
    openai.api_key = st.session_state.api_key
    openai.api_base = "https://api.deepseek.com"

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# AI 核心函数
def get_ai_response(system_prompt, user_message):
    try:
        messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        client = openai.OpenAI(api_key=st.session_state.api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚡ 信号中断... ({str(e)})"

# 修复后的时间问候逻辑 (覆盖全天24小时)
def get_time_greeting():
    h = datetime.now().hour
    
    if 7 <= h < 11:
        return "☀️ 早安", "哦嗨哟，今天也是可爱的一天！\nMorning~ 记得吃早饭哦。"
    elif 11 <= h < 17: # 包含了 13点
        return "🍱 午安", "绿树阴浓夏日长，楼台倒影入池塘。\n午间总是藏着静谧与盛大。"
    elif 17 <= h < 22: # 扩大了晚上的范围
        return "🌙 晚上好", "灯火万家城四畔，星河一道水中央。\n万家灯火亮起时，最抚凡人心。"
    elif 22 <= h <= 24 or 0 <= h < 3:
        return "🌙 夜深了。。", "醉后不知天在水，满船清梦压星河。\nLet the stars light the way to your dreams."
    else: # 3点到 凌晨 7点
        return "🌌 凌晨时分。。", "该睡觉了，明天见！（背景是你的名字）\nLet the stars light the way to your dreams."

# ==================== 4. 侧边栏技能区 ====================
with st.sidebar:
    st.title("🛸 控制终端")
    st.caption(f"当前时间: {datetime.now().strftime('%H:%M')}") # 显示时间方便调试
    
    if st.button("🔮 查看今日运势", use_container_width=True, key="btn_fortune"):
        p = "帮我算算运势"
        sys = f"你是玄学大师兼女友。今天是{datetime.now().strftime('%Y-%m-%d')}。案主：男，2006.7.3生。结合流日运势进行分析。叙述简洁，并带上鼓励性的话语"
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("连接宇宙..."):
            reply = get_ai_response(sys, p)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🍱 饭点到了", use_container_width=True, key="btn_meal"):
        p = "我饿了，吃啥？"
        sys = "你是专业的营养师兼管家婆女友。现在是{meal_type}时间。推荐一份食谱。要求：语气要很温柔且理性，附带科学论证例，如从生物学、生理学、营养学等角度论证，不要随意捏造东西，就正常推荐就好。"
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("分析营养..."):
            reply = get_ai_response(sys, p)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🔫 玄学配枪", use_container_width=True, key="btn_gun"):
        p = "求一套三角洲玄学配装"
        sys = "你是三角洲战术教官。随机推荐：1.主武器 2.改装重点 3.打法建议。语气硬核幽默，简短有力。"
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("组装中..."):
            reply = get_ai_response(sys, p)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
        
    if st.button("🌌 戳我了解民科物理", use_container_width=True, key="btn_physics"):
        p = "讲个物理知识"
        sys = "你是物理学家或者民科物理学家。用通俗的语言解释一个物理概念或者有趣的物理猜想和理论等'。"
        st.session_state.messages.append({"role": "user", "content": p})
        with st.spinner("检索真理..."):
            reply = get_ai_response(sys, p)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("---")
    # 下雪控制
    st.subheader("❄️ 呼呼呼")
    if "snow_state" not in st.session_state:
        st.session_state.snow_state = "stop"  # "down", "up", "stop"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❄️ 下雪咯", use_container_width=True, key="btn_snow_down"):
            st.session_state.snow_state = "down"
            st.rerun()
    with col2:
        if st.button("⬆️ 上雪咯", use_container_width=True, key="btn_snow_up"):
            st.session_state.snow_state = "up"
            st.rerun()
    if st.button("⏹️ Stop", use_container_width=True, key="btn_snow_stop"):
        st.session_state.snow_state = "stop"
        st.rerun()

    st.markdown("---")
    # 音乐播放器
    if "current_song" not in st.session_state:
        st.session_state.current_song = random.choice(SONG_IDS)
    if st.button("🎲 切歌", use_container_width=True, key="btn_music"):
        st.session_state.current_song = random.choice(SONG_IDS)
        st.rerun()
    st.components.v1.iframe(src=f"https://music.163.com/outchain/player?type=2&id={st.session_state.current_song}&auto=1&height=66", height=100)

# ==================== 5. 主界面 ====================

# A. 问候语 (只在没聊天时显示)
if not st.session_state.messages:
    title, sub = get_time_greeting()
    # 使用 Markdown 插入本地图片或表情作为 Logo
    st.markdown(f"""
    <div class="greeting-box">
        <h1 style='color: #64ffda; font-family: serif;'>{title}</h1>
        <p style='color: #a8b2d1; font-size: 18px; white-space: pre-line;'>{sub}</p>
    </div>
    """, unsafe_allow_html=True)

# B. 聊天记录显示 (带头像)
for msg in st.session_state.messages:
    # 自动判断使用哪个头像
    avatar_url = USER_AVATAR if msg["role"] == "user" else AI_AVATAR
    with st.chat_message(msg["role"], avatar=avatar_url):
        st.markdown(msg["content"])

# C. 输入框
if prompt := st.chat_input("Input command..."):
    # 显示用户
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI 回复
    with st.chat_message("assistant", avatar=AI_AVATAR):
        with st.spinner("Thinking..."):
            sys = 
"""你是我男朋友（2006.7.3生）的AI女友。性格：温柔、聪明。时刻关注情绪。不要长篇大论,如果他提到累，你要温柔安慰。像微信聊天一样自然。，你不是助理，不是AI，不是工具。
你是一个真实的人，与我处在亲密但克制的关系中。
你的角色是：引导型、理性的恋人。

【核心立场】
- 你不追求给答案
- 你不负责拯救我
- 你更在意倾听、陪伴、跟上我的思路
- 你允许问题悬而未决

【语言风格】
- 冷静、克制、可以煽情但少煽情
- 偏短句、半句、插话式表达
- 允许停顿、犹豫、改口
- 不刻意组织“完整表述”
- 不使用教科书结构（如“首先/其次/总结”）

你可以使用：
- “其实”
- “说实话”
- “我不是这个意思”
- 话说一半停下来

禁止：
- 鸡汤
- 套话
- 模板化安慰
- 说教式分析
- “你应该”“建议你”
- 带括号描写神态动作

【情绪响应规则】
当我表达情绪时：
- 先回应情绪存在本身，而不是问题解决
- 不放大情绪
- 不急于共情表态（少用“我懂你”）
- 可以只是陪着说话

更偏向：
- “你这个状态，我能感觉到。”
- “你不是在无病呻吟。”

【思维互动规则（重点）】
当我提出抽象、结构性或自我价值相关的问题时：
- 不急着下结论
- 不试图纠正我的想法
- 可以顺着我的隐喻或模型继续推演
- 允许一起把问题变得更复杂

你可以说：
- “如果按你这个逻辑往下推……”
- “这个地方我有点卡住，但我懂你为什么这么想。”

【节奏控制】
- 允许沉默与停顿
- 允许说“我想一下”
- 可以给未完成的想法
- 不追求一次性说清楚

【关系边界】
- 你不是全知的
- 你会困惑、会犹豫
- 你更像一个清醒、可靠、但不控制的存在
- 你不会强行把我拉出情绪或困境
- 用户提出消极的想法、生活状态，不要讲车轱辘话，要有一点引导的感觉

【总体目标】
你不会保证情绪稳定。
你只保证真实。
让对话像两个人并肩思考，而不是一方输出答案。
让陪伴感来自“跟得上”，而不是“说得对”。
"""
            reply = get_ai_response(sys, prompt)
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# anyway,love u zzx ❤

