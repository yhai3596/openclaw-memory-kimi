"""
Streamlit Web 界面
"""
import sys
import yaml
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from database import Database
from importer import DataImporter
from classifier import FeedbackClassifier
from report import ReportGenerator

# 页面配置
st.set_page_config(
    page_title="空调质量反馈分析系统",
    page_icon="🔧",
    layout="wide"
)

# 初始化
@st.cache_resource
def get_db():
    return Database()

@st.cache_resource
def get_classifier():
    clf = FeedbackClassifier()
    clf.load_classifier()
    return clf

def main():
    st.title("🔧 空调质量反馈分析系统")
    
    # 侧边栏导航
    page = st.sidebar.radio(
        "功能菜单",
        ["📊 总览", "📥 数据导入", "🏷️ 分类管理", "📋 质量简报", "⚙️ 系统配置"]
    )
    
    db = get_db()
    classifier = get_classifier()
    
    if page == "📊 总览":
        show_overview(db)
    elif page == "📥 数据导入":
        show_import(db)
    elif page == "🏷️ 分类管理":
        show_classification(db, classifier)
    elif page == "📋 质量简报":
        show_report(db, classifier)
    elif page == "⚙️ 系统配置":
        show_config()

def show_overview(db):
    """总览页面"""
    st.header("📊 系统总览")
    
    # 获取统计数据
    conn = sqlite3.connect(db.db_path)
    
    # 总反馈数
    total = pd.read_sql("SELECT COUNT(*) as count FROM feedback_raw", conn).iloc[0]['count']
    classified = pd.read_sql("SELECT COUNT(*) as count FROM feedback_classified", conn).iloc[0]['count']
    qc_count = pd.read_sql("SELECT COUNT(*) as count FROM qc_review", conn).iloc[0]['count']
    
    conn.close()
    
    # 显示指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总反馈数", int(total))
    with col2:
        st.metric("已分类", int(classified))
    with col3:
        st.metric("待分类", int(total - classified))
    with col4:
        st.metric("QC 检讨", int(qc_count))
    
    st.info("👈 使用左侧菜单进行数据导入、分类管理和查看简报")

def show_import(db):
    """数据导入页面"""
    st.header("📥 数据导入")
    
    uploaded_file = st.file_uploader("上传 Zoho Desk 导出的 Excel 文件", type=['xlsx', 'xls'])
    
    if uploaded_file:
        if st.button("开始导入"):
            with st.spinner("正在导入数据..."):
                try:
                    # 保存临时文件
                    temp_path = f"./data/temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    # 导入数据
                    importer = DataImporter()
                    count = importer.import_excel(temp_path, db)
                    
                    st.success(f"✅ 成功导入 {count} 条记录")
                    
                    # 删除临时文件
                    Path(temp_path).unlink()
                    
                except Exception as e:
                    st.error(f"❌ 导入失败: {e}")

def show_classification(db, classifier):
    """分类管理页面"""
    st.header("🏷️ 分类管理")
    
    # 获取未分类数据
    unclassified = db.get_unclassified_feedback()
    
    if not unclassified:
        st.success("✅ 所有数据已分类")
        return
    
    st.write(f"待分类数据: {len(unclassified)} 条")
    
    if st.button("开始自动分类"):
        with st.spinner("正在分类..."):
            for item in unclassified:
                # 合并文本
                merged = item.get('merged_text', '')
                if not merged:
                    merged = f"{item.get('subject', '')} | {item.get('description', '')}"
                
                # 预测
                label, confidence = classifier.predict(merged)
                
                # 保存结果
                result = {
                    'feedback_id': item['id'],
                    'is_quality_issue': classifier.is_quality_issue(label),
                    'primary_category': classifier.get_display_name(label),
                    'secondary_category': '',
                    'severity': classifier.get_severity(label),
                    'confidence': confidence,
                    'keywords': [],
                    'merged_text': merged,
                    'model_version': 'v1.0'
                }
                
                db.insert_classification(result)
            
            st.success(f"✅ 完成 {len(unclassified)} 条分类")
            st.rerun()
    
    # 显示待复核项
    st.subheader("⚠️ 需人工复核")
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.ticket_id, r.subject, c.confidence, c.primary_category
        FROM feedback_raw r
        JOIN feedback_classified c ON r.id = c.feedback_id
        WHERE c.needs_review = TRUE
    ''')
    
    review_items = cursor.fetchall()
    conn.close()
    
    if review_items:
        for item in review_items:
            with st.expander(f"Ticket {item['ticket_id']} - 置信度: {item['confidence']:.2f}"):
                st.write(f"**主题:** {item['subject']}")
                st.write(f"**预测分类:** {item['primary_category']}")
                # 这里可以添加修改分类的功能
    else:
        st.info("暂无需要复核的项")

def show_report(db, classifier):
    """质量简报页面"""
    st.header("📋 质量简报")
    
    # 选择周
    col1, col2 = st.columns(2)
    with col1:
        week_start = st.date_input("开始日期", datetime.now() - timedelta(days=7))
    with col2:
        week_end = st.date_input("结束日期", datetime.now())
    
    if st.button("生成简报"):
        with st.spinner("正在生成..."):
            # 获取数据
            feedbacks = db.get_feedback_by_week(
                week_start.strftime('%Y-%m-%d'),
                week_end.strftime('%Y-%m-%d')
            )
            
            if not feedbacks:
                st.warning("该时间段内无数据")
                return
            
            # 生成报告
            generator = ReportGenerator()
            report = generator.generate_report(
                week_start, week_end, feedbacks
            )
            
            # 显示报告
            st.markdown(report['text'])
            
            # 保存按钮
            if st.button("保存到 QC 检讨"):
                for detail in report['details']:
                    if detail['needs_qc']:
                        db.insert_qc_review({
                            'category': detail['category'],
                            'model': detail['model'],
                            'feedback_ids': detail['feedback_ids'],
                            'count': detail['count'],
                            'severity_score': detail['score']
                        })
                st.success("✅ 已保存到 QC 检讨列表")

def show_config():
    """系统配置页面"""
    st.header("⚙️ 系统配置")
    
    # 读取配置
    with open('./config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    st.subheader("模型配置")
    st.write(f"当前模型: `{config['model']['name']}`")
    st.write(f"设备: `{config['model']['device']}`")
    
    st.subheader("简报推送")
    st.write(f"推送时间: `{config['schedule']['push_time']}`")
    
    st.subheader("严重度配置")
    st.json(config['severity']['levels'])

if __name__ == '__main__':
    import sqlite3
    main()
