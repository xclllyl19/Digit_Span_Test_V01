import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime
import pyperclip  # 新增：用于剪贴板操作

# 测试配置
CONFIG = {
    "min_digits": 3,               # 从3位数字开始
    "max_digits": 99,              # 最大数字长度改为99
    "max_consecutive_errors": 2,   # 连续2次错误结束
    "digit_duration": 1.0,         # 数字显示时间改为1秒
    "interval": 1.0,               # 数字间隔时间改为1秒
    "test_timeout": 300,           # 测试总超时时间为5分钟(300秒)
    "ready_duration": 2.0,         # 准备时间(秒)
    "input_timeout": 15,           # 输入超时时间(秒)
    "auto_next_delay": 3           # 自动进入下一轮延迟(秒)
}

class DigitSpanTest:
    def __init__(self):
        self.reset_test()
        
    def reset_test(self):
        """重置测试状态"""
        self.test_id = f"DSP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.current_length = CONFIG["min_digits"]
        self.max_correct_length = CONFIG["min_digits"]
        self.consecutive_errors = 0
        self.results = []
        self.test_start_time = time.time()
        self.stage = "ready"  # ready -> countdown -> testing -> input -> next_round -> finished
        self.current_sequence = []
        self.user_input = ""
        self.current_digit_index = 0
        self.last_digit_time = 0
        self.countdown = 3
        self.input_start_time = 0
        self.next_round_message = ""
        self.last_total_time_check = time.time()
        self.last_input_check_time = time.time()
        self.input_key_counter = 0  # 用于生成唯一的输入框key

    def generate_sequence(self, length):
        """生成随机数字序列"""
        return [random.randint(0, 9) for _ in range(length)]

    def start_test(self):
        """开始新一组测试"""
        self.current_sequence = self.generate_sequence(self.current_length)
        self.user_input = ""
        self.stage = "countdown"
        self.current_digit_index = 0
        self.last_digit_time = 0
        self.countdown = 3
        self.input_key_counter += 1  # 每次新测试递增key

def main():
    st.set_page_config(page_title="数字广度测试", layout="wide")
    
    # 初始化测试
    if "test" not in st.session_state:
        st.session_state.test = DigitSpanTest()
    
    test = st.session_state.test
    
    # 标题和说明
    st.title("数字广度测试 (Digit Span Test)")
    st.markdown("""
    **测试说明**:
    1. 测试开始前会有3秒准备时间
    2. 数字会逐个显示在屏幕中央
    3. 每组数字显示完成后，请在15秒内输入
    4. 输入完成后需按回车提交）
    """)
    
    # 主测试区域
    col1, col2 = st.columns([3, 2])
    
    with col1:
        test_container = st.empty()
        
        if test.stage == "ready":
            with test_container.container():
                st.header("准备开始")
                if st.button("开始测试"):
                    test.test_start_time = time.time()
                    test.last_total_time_check = time.time()
                    test.start_test()
                    st.rerun()
        
        elif test.stage == "countdown":
            with test_container.container():
                st.subheader(f"第 {len(test.results)+1} 组测试准备")
                if test.countdown > 0:
                    st.markdown(f"<div style='font-size: 72px; text-align: center; margin: 50px 0; color: orange;'>"
                               f"{test.countdown}</div>", unsafe_allow_html=True)
                    time.sleep(1)
                    test.countdown -= 1
                    st.rerun()
                else:
                    test.stage = "testing"
                    test.last_digit_time = time.time()
                    st.rerun()
        
        elif test.stage == "testing":
            current_time = time.time()
            
            if test.current_digit_index < len(test.current_sequence):
                if current_time - test.last_digit_time >= CONFIG["interval"]:
                    with test_container.container():
                        st.subheader(f"第 {len(test.results)+1} 组测试: {len(test.current_sequence)} 位数字")
                        
                        st.markdown(f"""
                        <div style="
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            margin: 20px 0;
                        ">
                            <div style='
                                font-size: 72px; 
                                text-align: center; 
                                margin: 0 auto 20px auto;
                                padding: 20px;
                                border: 3px solid #4CAF50;
                                border-radius: 10px;
                                background-color: #f8f8f8;
                                width: 120px;
                            '>{test.current_sequence[test.current_digit_index]}</div>
                            <div style='color: gray; text-align: center; margin-bottom: 10px;'>
                                {test.current_digit_index+1}/{len(test.current_sequence)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.progress((test.current_digit_index + 1) / len(test.current_sequence))
                    
                    test.current_digit_index += 1
                    test.last_digit_time = current_time
                    
                    time.sleep(CONFIG["digit_duration"])
                    st.rerun()
                else:
                    time.sleep(0.1)
                    st.rerun()
            else:
                test.stage = "input"
                test.input_start_time = time.time()
                test.last_input_check_time = time.time()
                st.rerun()
        
        elif test.stage == "input":
            current_time = time.time()
            time_left = max(0, CONFIG["input_timeout"] - (current_time - test.input_start_time))
            
            # 强制刷新剩余时间显示
            if current_time - test.last_input_check_time >= 0.1:
                test.last_input_check_time = current_time
                if time_left <= 0:
                    st.rerun()
            
            with test_container.container():
                st.subheader(f"请输入你看到的 {len(test.current_sequence)} 位数字")
                st.caption(f"剩余时间: {int(time_left)}秒 (超时自动判错)")
                
                # 使用唯一的key确保输入框能正确捕获输入
                user_input = st.text_input("输入数字序列（无需分隔符）", 
                                        key=f"input_{test.input_key_counter}",
                                        max_chars=len(test.current_sequence),
                                        label_visibility="collapsed")
                
                # 当输入长度达到要求或超时时自动提交
                if len(user_input) == len(test.current_sequence) or time_left <= 0:
                    test.user_input = user_input
                    
                    # 处理输入超时
                    if time_left <= 0:
                        test.user_input = ""  # 超时空输入视为错误
                    
                    # 检查答案
                    user_digits = [d for d in test.user_input if d.isdigit()]
                    correct_digits = [str(d) for d in test.current_sequence]
                    is_correct = user_digits == correct_digits
                    
                    if is_correct:
                        test.consecutive_errors = 0
                        test.max_correct_length = max(test.max_correct_length, len(test.current_sequence))
                        next_length = min(test.current_length + 1, CONFIG["max_digits"])
                        test.next_round_message = f"✅ 回答正确！ (数字长度+1 → {next_length}位)"
                    else:
                        test.consecutive_errors += 1
                        next_length = max(test.current_length - 1, CONFIG["min_digits"])
                        test.next_round_message = f"❌ 回答错误！ (数字长度-1 → {next_length}位)"
                    
                    # 记录结果
                    test.results.append({
                        "测试组ID": len(test.results) + 1,
                        "数字长度": len(test.current_sequence),
                        "数字序列": " ".join(map(str, test.current_sequence)),
                        "用户输入": test.user_input,
                        "是否正确": is_correct,
                        "反应时间": current_time - test.test_start_time,
                        "是否超时": time_left <= 0
                    })
                    
                    test.current_length = next_length
                    test.stage = "next_round"
                    test.next_round_start = time.time()
                    st.rerun()
        
        elif test.stage == "next_round":
            current_time = time.time()
            elapsed = current_time - test.next_round_start
            time_left = max(0, CONFIG["auto_next_delay"] - elapsed)
            
            with test_container.container():
                st.subheader("测试结果")
                # 修改后的提示信息显示，移除了额外倒计时
                st.markdown(f"""
                <div style='
                    font-size: 24px; 
                    text-align: center; 
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 10px;
                    background-color: #f0f0f0;
                '>
                    {test.next_round_message}
                    <div style='font-size: 18px; color: #666; margin-top: 10px;'>
                        自动继续中...
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if time_left <= 0:
                    if (test.consecutive_errors >= CONFIG["max_consecutive_errors"] or 
                        current_time - test.test_start_time > CONFIG["test_timeout"]):
                        test.stage = "finished"
                    else:
                        test.start_test()
                    st.rerun()
                else:
                    time.sleep(0.1)
                    st.rerun()
        
        elif test.stage == "finished":
            with test_container.container():
                st.success("测试完成！")
                st.balloons()
                
                # 计算结果
                df = pd.DataFrame(test.results)
                stats = df.groupby("数字长度").agg({
                    "是否正确": ["count", lambda x: sum(x)/len(x)]
                }).reset_index()
                stats.columns = ["数字长度", "测试次数", "正确率"]
                
                # 显示结果
                st.subheader("测试结果")
                st.write(f"**最大正确位数**: {test.max_correct_length}")
                
                st.write("**详细结果**")
                st.dataframe(df.style.applymap(
                    lambda x: "background-color: #e6ffe6" if x == True else (
                        "background-color: #ffe6e6" if x == False else ""
                    ), subset=["是否正确"]))
                
                st.write("**统计摘要**")
                st.dataframe(stats)
                
                # 修复后的复制到剪贴板功能
                if st.button("📋 复制结果到剪贴板"):
                    result_str = f"测试ID: {test.test_id}\n最大正确位数: {test.max_correct_length}\n\n"
                    result_str += df.to_csv(index=False, sep="\t")
                    try:
                        pyperclip.copy(result_str)
                        st.success("结果已复制到剪贴板！")
                    except Exception as e:
                        st.error(f"复制失败: {str(e)}")
                
                if st.button("🔄 重新开始测试"):
                    test.reset_test()
                    st.rerun()
    
    with col2:
        st.subheader("测试信息")
        st.write(f"📝 测试ID: `{test.test_id}`")
        
        if test.stage != "ready":
            current_time = time.time()
            elapsed_time = current_time - test.test_start_time
            time_left = max(0, CONFIG["test_timeout"] - elapsed_time)
            
            # 强制刷新总时间显示
            if current_time - test.last_total_time_check >= 0.1:
                test.last_total_time_check = current_time
                st.rerun()
            
            st.write(f"⏱️ 剩余时间: {int(time_left)}秒 / {CONFIG['test_timeout']}秒")
            st.write(f"🔢 当前数字长度: {test.current_length}位")
            st.write(f"🏆 最大正确位数: {test.max_correct_length}位")
            st.write(f"❌ 连续错误次数: {test.consecutive_errors}/{CONFIG['max_consecutive_errors']}")
            
            if test.results:
                last_result = test.results[-1]
                st.write(f"📊 上一组结果: {'✅ 正确' if last_result['是否正确'] else '❎ 错误'}")

if __name__ == "__main__":
    main()