"""
分类器模块
支持可配置的 Embedding 模型
"""
import re
import yaml
import torch
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle

class FeedbackClassifier:
    def __init__(self, config_path="./config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.model_name = self.config['model']['name']
        self.device = self.config['model']['device'] if torch.cuda.is_available() else 'cpu'
        self.max_length = self.config['model']['max_length']
        
        # 标签体系
        self.labels = [
            'non_quality_dealer',      # 经销商咨询
            'non_quality_sales',       # 销售咨询
            'non_quality_warranty',    # 保修注册
            'non_quality_tax',         # 税务咨询
            'non_quality_other',       # 其他非质量
            'quality_not_cooling',     # 不制冷
            'quality_not_heating',     # 不制热
            'quality_wont_start',      # 无法启动
            'quality_leaking',         # 漏水
            'quality_noise',           # 噪音
            'quality_installation',    # 安装问题
            'quality_error_code',      # 错误代码
            'quality_cosmetic',        # 外观瑕疵
            'quality_other'            # 其他质量问题
        ]
        
        # 关键词映射（用于规则辅助）
        self.keywords = {
            'non_quality_dealer': ['distributor', 'dealer', 'wholesale', 'locator'],
            'non_quality_sales': ['sales', 'become a dealer', 'interested in', 'purchasing'],
            'non_quality_warranty': ['warranty registration', 'register', 'warranty inquiry'],
            'non_quality_tax': ['tax credit', 'federal', 'irs', 'qualification'],
            'quality_not_cooling': ['not cooling', 'warm air', 'no cool', 'blowing hot', 'not cold'],
            'quality_not_heating': ['not heating', 'cold air', 'no heat', 'blowing cold', 'not hot'],
            'quality_wont_start': ['won\'t start', 'not working', 'dead', 'no power'],
            'quality_leaking': ['leak', 'leaking', 'water', 'drip', 'oil in drain'],
            'quality_noise': ['noise', 'noisy', 'loud', 'vibration', 'rattling'],
            'quality_installation': ['installation', 'installed', 'mounting', 'piping'],
            'quality_error_code': ['error', 'code', 'fault', 'display', 'P2', 'G3'],
            'quality_cosmetic': ['scratch', 'dent', 'cosmetic', 'damage'],
        }
        
        self.embedding_model = None
        self.classifier = None
        self.is_trained = False
    
    def load_embedding_model(self):
        """加载 Embedding 模型"""
        if self.embedding_model is None:
            print(f"正在加载模型: {self.model_name}")
            
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(
                    self.model_name,
                    device=self.device
                )
                print(f"模型加载完成，使用设备: {self.device}")
            except Exception as e:
                print(f"加载模型失败: {e}")
                raise
        
        return self.embedding_model
    
    def get_embeddings(self, texts):
        """获取文本嵌入向量"""
        model = self.load_embedding_model()
        embeddings = model.encode(
            texts,
            batch_size=self.config['model']['batch_size'],
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def extract_keywords(self, text):
        """提取匹配的关键词"""
        text_lower = text.lower()
        matched_keywords = []
        
        for label, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched_keywords.append((label, keyword))
        
        return matched_keywords
    
    def rule_based_classify(self, text):
        """基于规则的快速分类（用于辅助）"""
        matched = self.extract_keywords(text)
        
        if not matched:
            return None, 0.0
        
        # 统计每个标签的匹配次数
        label_counts = {}
        for label, keyword in matched:
            label_counts[label] = label_counts.get(label, 0) + 1
        
        # 返回最匹配的标签
        best_label = max(label_counts, key=label_counts.get)
        confidence = min(label_counts[best_label] * 0.3, 0.9)
        
        return best_label, confidence
    
    def train(self, texts, labels, model_dir="./models"):
        """训练分类器"""
        print(f"开始训练，样本数: {len(texts)}")
        
        # 获取嵌入向量
        embeddings = self.get_embeddings(texts)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings, labels,
            test_size=self.config['model']['training']['test_size'],
            random_state=42,
            stratify=labels
        )
        
        # 训练逻辑回归分类器
        self.classifier = LogisticRegression(
            max_iter=1000,
            multi_class='ovr',
            random_state=42
        )
        self.classifier.fit(X_train, y_train)
        
        # 评估
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"测试集准确率: {accuracy:.4f}")
        print("\n分类报告:")
        print(classification_report(y_test, y_pred))
        
        # 保存模型
        Path(model_dir).mkdir(parents=True, exist_ok=True)
        model_path = Path(model_dir) / "classifier.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(self.classifier, f)
        
        self.is_trained = True
        print(f"模型已保存到: {model_path}")
        
        return accuracy
    
    def load_classifier(self, model_path="./models/classifier.pkl"):
        """加载训练好的分类器"""
        if Path(model_path).exists():
            with open(model_path, 'rb') as f:
                self.classifier = pickle.load(f)
            self.is_trained = True
            print(f"分类器已加载: {model_path}")
            return True
        return False
    
    def predict(self, text):
        """预测单条文本"""
        if not self.is_trained:
            # 未训练时使用规则分类
            return self.rule_based_classify(text)
        
        # 获取嵌入向量
        embedding = self.get_embeddings([text])
        
        # 预测
        proba = self.classifier.predict_proba(embedding)[0]
        pred_idx = np.argmax(proba)
        confidence = proba[pred_idx]
        label = self.classifier.classes_[pred_idx]
        
        # 如果置信度低，尝试规则辅助
        if confidence < self.config['classification']['confidence_threshold']:
            rule_label, rule_conf = self.rule_based_classify(text)
            if rule_label and rule_conf > 0.5:
                return rule_label, max(confidence, rule_conf)
        
        return label, confidence
    
    def predict_batch(self, texts):
        """批量预测"""
        if not self.is_trained:
            results = []
            for text in texts:
                label, conf = self.rule_based_classify(text)
                results.append({
                    'label': label or 'quality_other',
                    'confidence': conf,
                    'needs_review': conf < 0.75
                })
            return results
        
        # 批量获取嵌入
        embeddings = self.get_embeddings(texts)
        
        # 批量预测
        probas = self.classifier.predict_proba(embeddings)
        predictions = []
        
        for i, proba in enumerate(probas):
            pred_idx = np.argmax(proba)
            confidence = proba[pred_idx]
            label = self.classifier.classes_[pred_idx]
            
            predictions.append({
                'label': label,
                'confidence': confidence,
                'needs_review': confidence < self.config['classification']['confidence_threshold']
            })
        
        return predictions
    
    def is_quality_issue(self, label):
        """判断是否为质量问题"""
        return label.startswith('quality_')
    
    def get_severity(self, label):
        """获取严重度"""
        mapping = self.config['severity']['mapping']
        
        severity_map = {
            'quality_not_cooling': mapping.get('not_cooling', 4),
            'quality_not_heating': mapping.get('not_heating', 4),
            'quality_wont_start': mapping.get('wont_start', 4),
            'quality_leaking': mapping.get('leaking', 4),
            'quality_noise': mapping.get('noise', 3),
            'quality_installation': mapping.get('installation', 3),
            'quality_error_code': mapping.get('error_code', 2),
            'quality_cosmetic': mapping.get('cosmetic', 2),
            'quality_other': mapping.get('other', 1),
        }
        
        return severity_map.get(label, 1)
    
    def get_display_name(self, label):
        """获取显示名称"""
        display_names = {
            'non_quality_dealer': '经销商咨询',
            'non_quality_sales': '销售咨询',
            'non_quality_warranty': '保修注册',
            'non_quality_tax': '税务咨询',
            'non_quality_other': '其他非质量',
            'quality_not_cooling': '不制冷',
            'quality_not_heating': '不制热',
            'quality_wont_start': '无法启动',
            'quality_leaking': '漏水',
            'quality_noise': '噪音',
            'quality_installation': '安装问题',
            'quality_error_code': '错误代码',
            'quality_cosmetic': '外观瑕疵',
            'quality_other': '其他质量问题',
        }
        return display_names.get(label, label)
