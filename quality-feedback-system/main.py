#!/usr/bin/env python3
"""
主程序入口
"""
import sys
import argparse
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(description='空调质量反馈分析系统')
    parser.add_argument('command', choices=['web', 'import', 'train', 'report', 'init'], 
                       help='运行命令')
    parser.add_argument('--file', '-f', help='导入的 Excel 文件路径')
    parser.add_argument('--week-start', help='周报开始日期 (YYYY-MM-DD)')
    parser.add_argument('--week-end', help='周报结束日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if args.command == 'web':
        # 启动 Web 界面
        import subprocess
        subprocess.run(['streamlit', 'run', 'src/app.py'])
    
    elif args.command == 'init':
        # 初始化数据库
        from database import Database
        db = Database()
        print("✅ 数据库初始化完成")
    
    elif args.command == 'import':
        # 导入数据
        if not args.file:
            print("❌ 请指定文件路径: --file xxx.xlsx")
            return
        
        from database import Database
        from importer import DataImporter
        
        db = Database()
        importer = DataImporter()
        count = importer.import_excel(args.file, db)
        print(f"✅ 成功导入 {count} 条记录")
    
    elif args.command == 'train':
        # 训练模型
        from database import Database
        from importer import DataImporter
        from classifier import FeedbackClassifier
        
        db = Database()
        importer = DataImporter()
        
        # 获取训练数据
        training_data = importer.get_training_data(db)
        
        if len(training_data) < 10:
            print(f"❌ 训练数据不足 (当前 {len(training_data)} 条，需要至少 10 条)")
            return
        
        print(f"📊 加载了 {len(training_data)} 条训练数据")
        
        # 准备数据
        texts = [item['merged_text'] for item in training_data]
        labels = [item['category'] for item in training_data]
        
        # 训练
        classifier = FeedbackClassifier()
        accuracy = classifier.train(texts, labels)
        print(f"✅ 模型训练完成，准确率: {accuracy:.4f}")
    
    elif args.command == 'report':
        # 生成简报
        from datetime import datetime, timedelta
        from database import Database
        from classifier import FeedbackClassifier
        from report import ReportGenerator
        
        db = Database()
        generator = ReportGenerator()
        
        # 默认本周
        if args.week_end:
            week_end = datetime.strptime(args.week_end, '%Y-%m-%d')
        else:
            week_end = datetime.now()
        
        if args.week_start:
            week_start = datetime.strptime(args.week_start, '%Y-%m-%d')
        else:
            week_start = week_end - timedelta(days=7)
        
        # 获取数据
        feedbacks = db.get_feedback_by_week(
            week_start.strftime('%Y-%m-%d'),
            week_end.strftime('%Y-%m-%d')
        )
        
        if not feedbacks:
            print("❌ 该时间段内无数据")
            return
        
        # 生成报告
        report = generator.generate_report(week_start, week_end, feedbacks)
        print(report['text'])

if __name__ == '__main__':
    main()
