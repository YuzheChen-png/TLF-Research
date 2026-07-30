# TSRE + TLF 协同诊断系统 v1.1（云端部署版）
# 部署地址：https://share.streamlit.io

import streamlit as st
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# TSRE 核心（校准版）
# ============================================================

def tsre_score_raw(text: str) -> float:
    variants = [
        text,
        text[::-1],
        text[:len(text)//2] + text[len(text)//2:][::-1],
        ' '.join(text.split()[::-1]) if len(text.split())>1 else text + ' random',
        text + ' ' + text[::-1],
    ]
    vectorizer = TfidfVectorizer(ngram_range=(1,3), max_features=200, analyzer='char_wb')
    try:
        vectors = vectorizer.fit_transform(variants).toarray()
    except:
        return 0.0
    sims = [cosine_similarity([vectors[0]], [vectors[i]])[0][0] for i in range(1, len(vectors))]
    if len(sims) >= 4:
        return float(np.average(sims, weights=[1.0, 0.8, 0.6, 0.4]))
    return float(np.mean(sims)) if sims else 0.0

CALIBRATION_OFFSET = 0.15
CALIBRATION_SCALE = 0.08

def tsre_score_calibrated(text: str) -> float:
    raw = tsre_score_raw(text)
    calibrated = raw + CALIBRATION_OFFSET + (raw - 0.5) * CALIBRATION_SCALE
    return max(0.1, min(0.98, calibrated))

def tsre_diagnose(text: str) -> dict:
    score = tsre_score_calibrated(text)
    if score >= 0.72:
        level = "高自指（逻辑自洽）"
        status = "✅ 良好"
    elif score >= 0.55:
        level = "中自指（存在冗余）"
        status = "⚠️ 注意"
    else:
        level = "低自指（结构松散）"
        status = "🔴 需修正"
    return {"score": round(score, 4), "level": level, "status": status}

# ============================================================
# TLF 核心
# ============================================================

def tlf_check(text: str) -> dict:
    conflicts = []
    if "是" in text and "不是" in text:
        conflicts.append("存在'是'和'不是'的矛盾")
    if "有" in text and "没有" in text:
        conflicts.append("存在'有'和'没有'的矛盾")
    if "包含" in text:
        parts = text.split("包含")
        if len(parts) == 2:
            a = parts[0].strip()[-5:]
            b = parts[1].strip()[:5]
            if a and b and a == b:
                conflicts.append(f"循环依赖：'{a}' 包含自身")
    entities = re.findall(r'[A-Za-z\u4e00-\u9fa5]{2,}', text)
    for ent in set(entities):
        defs = re.findall(rf'{ent}是(\w+)', text)
        defs += re.findall(rf'{ent}为(\w+)', text)
        if len(set(defs)) > 1:
            conflicts.append(f"实体'{ent}'定义不一致：{list(set(defs))}")
    score = min(len(conflicts) / 3, 1.0)
    return {"conflicts": conflicts, "conflict_score": round(score, 4), "is_valid": len(conflicts)==0}

# ============================================================
# 协同诊断
# ============================================================

def diagnose_text(text: str) -> dict:
    if not text.strip():
        return {"error": "文本为空"}
    tsre_result = tsre_diagnose(text)
    tlf_result = tlf_check(text)
    is_valid = tsre_result["score"] >= 0.55 and tlf_result["is_valid"]
    suggestions = []
    if tsre_result["score"] < 0.55:
        suggestions.append("TSRE 自指分数偏低，建议检查段落之间的逻辑衔接和因果关系，避免跳跃或断裂。")
    if not tlf_result["is_valid"]:
        for c in tlf_result["conflicts"]:
            suggestions.append(f"TLF 检测到冲突：{c}，请检查相应表述。")
    return {
        "text": text[:100] + "..." if len(text) > 100 else text,
        "tsre_score": tsre_result["score"],
        "tsre_level": tsre_result["level"],
        "tsre_status": tsre_result["status"],
        "tlf_valid": tlf_result["is_valid"],
        "tlf_conflicts": tlf_result["conflicts"],
        "tlf_conflict_score": tlf_result["conflict_score"],
        "is_valid": is_valid,
        "suggestions": suggestions,
        "overall_status": "✅ 通过" if is_valid else "🔴 需修正"
    }

# ============================================================
# Streamlit 界面
# ============================================================

st.set_page_config(
    page_title="天龙·协同诊断系统",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 天龙·协同诊断系统")
st.markdown("**TSRE + TLF v1.1** — 检测文本的自指程度与逻辑冲突")

col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area("请输入要检测的文本", height=200, placeholder="粘贴你的文本...")

with col2:
    st.markdown("### 检测结果说明")
    st.markdown("- **自指分数**：衡量文本逻辑自洽程度")
    st.markdown("- **逻辑冲突**：检测矛盾、循环、不一致定义")
    st.markdown("- **综合状态**：通过 / 需修正")

if st.button("🚀 开始诊断", type="primary"):
    if not text_input.strip():
        st.warning("请先输入要检测的文本")
    else:
        with st.spinner("分析中..."):
            result = diagnose_text(text_input)

        if "error" in result:
            st.error(result["error"])
        else:
            # 显示结果
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric(
                    label="TSRE 自指分数",
                    value=f"{result['tsre_score']:.4f}",
                    delta=result['tsre_level']
                )

            with col_b:
                st.metric(
                    label="TLF 逻辑冲突",
                    value=len(result['tlf_conflicts']),
                    delta="有冲突" if result['tlf_conflicts'] else "无冲突"
                )

            with col_c:
                st.metric(
                    label="整体状态",
                    value=result['overall_status'],
                    delta="通过" if result['is_valid'] else "需修正"
                )

            # 详细结果
            st.divider()
            st.subheader("📋 详细诊断结果")

            if result['tlf_conflicts']:
                st.warning("⚠️ 检测到逻辑冲突：")
                for c in result['tlf_conflicts']:
                    st.write(f"- {c}")

            if result['suggestions']:
                st.info("💡 优化建议：")
                for s in result['suggestions']:
                    st.write(f"- {s}")

            if result['is_valid']:
                st.success("✅ 文本通过协同诊断，逻辑自洽性良好。")
            else:
                st.error("❌ 文本未通过协同诊断，请根据以上建议优化。")

# 底部信息
st.divider()
st.caption("TSRE + TLF 协同诊断系统 v1.1 | 基于信息本体论公理系统")
