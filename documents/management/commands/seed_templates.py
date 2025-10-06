# documents/management/commands/seed_templates.py
from django.core.management.base import BaseCommand
from documents.models import DocumentTemplate

class Command(BaseCommand):
    help = 'Seed initial document templates'
    
    def handle(self, *args, **options):
        templates = [
            {
                'name': '学术论文模板',
                'template_type': 'academic',
                'description': '标准的学术论文模板，包含摘要、引言、文献综述、研究方法、研究结果、讨论、结论和参考文献等章节。'
            },
            {
                'name': '商业报告模板', 
                'template_type': 'business',
                'description': '专业的商业报告模板，包含执行摘要、市场分析、数据展示、建议策略等部分。'
            },
            {
                'name': '研究报告模板',
                'template_type': 'academic', 
                'description': '适用于科研项目的研究报告模板，强调研究方法和数据分析。'
            }
        ]
        
        for template_data in templates:
            template, created = DocumentTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )