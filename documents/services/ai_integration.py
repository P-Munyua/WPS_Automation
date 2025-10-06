# documents/services/ai_integration.py
import requests
import json
from django.conf import settings

class DeepSeekIntegration:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
    
    def generate_academic_content(self, topic, requirements):
        """Generate academic article content using DeepSeek API"""
        prompt = self._build_academic_prompt(topic, requirements)
        return self._call_api(prompt)
    
    def generate_business_content(self, topic, requirements):
        """Generate business report content using DeepSeek API"""
        prompt = self._build_business_prompt(topic, requirements)
        return self._call_api(prompt)
    
    def _build_academic_prompt(self, topic, requirements):
        """Build prompt for academic article generation"""
        word_count = requirements.get('word_count', 2000)
        language = requirements.get('language', 'zh')
        
        if language == 'zh':
            return f"""
            请撰写一篇关于"{topic}"的学术论文。

            要求：
            - 严格的学术写作风格
            - 字数约{word_count}字
            - 包含以下章节：
              1. 摘要
              2. 引言
              3. 文献综述
              4. 研究方法
              5. 研究结果
              6. 讨论与分析
              7. 结论
              8. 参考文献
            
            - 使用专业的学术语言
            - 在适当位置标注需要插入图表的地方 [图表位置]
            - 在需要数学公式的地方标注 [公式位置]
            - 确保逻辑严谨，论证充分
            - 提供真实的参考文献格式

            请生成完整的论文内容：
            """
        else:
            return f"""
            Please write a comprehensive academic paper on the topic: "{topic}"

            Requirements:
            - Strict academic writing style
            - Approximately {word_count} words
            - Include the following sections:
              1. Abstract
              2. Introduction
              3. Literature Review
              4. Methodology
              5. Findings
              6. Discussion and Analysis
              7. Conclusion
              8. References

            - Use professional academic language
            - Mark places for charts with [CHART LOCATION]
            - Mark places for formulas with [FORMULA LOCATION]
            - Ensure logical rigor and sufficient argumentation
            - Provide proper reference formatting

            Please generate the complete paper content:
            """
    
    def _build_business_prompt(self, topic, requirements):
        """Build prompt for business report generation"""
        word_count = requirements.get('word_count', 2000)
        language = requirements.get('language', 'zh')
        
        if language == 'zh':
            return f"""
            请撰写一份关于"{topic}"的商业报告。

            要求：
            - 专业的商业报告风格
            - 字数约{word_count}字
            - 包含以下章节：
              1. 执行摘要
              2. 背景介绍
              3. 市场分析
              4. 数据分析
              5. 建议与策略
              6. 实施计划
              7. 风险评估
              8. 结论

            - 使用专业的商业语言
            - 在适当位置标注需要插入图表的地方 [图表位置]
            - 提供具体的数据分析和建议
            - 结构清晰，重点突出

            请生成完整的报告内容：
            """
        else:
            return f"""
            Please write a comprehensive business report on the topic: "{topic}"

            Requirements:
            - Professional business writing style
            - Approximately {word_count} words
            - Include the following sections:
              1. Executive Summary
              2. Background
              3. Market Analysis
              4. Data Analysis
              5. Recommendations and Strategies
              6. Implementation Plan
              7. Risk Assessment
              8. Conclusion

            - Use professional business language
            - Mark places for charts with [CHART LOCATION]
            - Provide specific data analysis and recommendations
            - Clear structure with emphasized key points

            Please generate the complete report content:
            """
    
    def _call_api(self, prompt):
        """Make API call to DeepSeek"""
        if not self.api_key:
            return self._get_fallback_content()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API Error: {e}")
            return self._get_fallback_content()
    
    def _get_fallback_content(self):
        """Return fallback content when API fails"""
        return f"""
        学术论文示例内容

        摘要
        本文探讨了相关主题的研究现状和发展趋势。通过综合分析现有文献和研究方法，提出了新的研究视角和分析框架。

        1. 引言
        研究背景和意义在此阐述。当前领域面临的主要问题和挑战需要系统性的分析和解决方案。

        2. 文献综述
        现有研究主要集中在以下几个方面：[图表位置]
        主要理论框架包括...
        研究方法主要采用...

        3. 研究方法
        本研究采用[研究方法]进行分析。数据收集和处理过程如下：[公式位置]
        研究假设和验证方法...

        4. 研究结果
        通过分析发现：[图表位置]
        主要研究结果包括...
        数据表明...

        5. 讨论与分析
        结果分析表明...[公式位置]
        与现有研究的比较...
        理论意义和实践价值...

        6. 结论
        总结研究发现和贡献...
        研究局限性和未来方向...

        参考文献
        1. 作者 (年份). 文章标题. 期刊名称.
        2. 作者 (年份). 书籍名称. 出版社.
        """