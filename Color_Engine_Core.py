# Coller_Engine_Core.py

from dataclasses import dataclass
import tkinter as tk
import datetime
from tkinter import ttk, scrolledtext, filedialog, messagebox
import re


@dataclass(frozen=True)
class ColorToken:
    char: str
    hex_code: str
    rgb: tuple

class SimpleHexColorEngine:
    def __init__(self):
        self.hex_mapping = {
            'h': '#FF8E53', 'e': '#A8E6CF', 'l': '#DcedC1', 'o': '#FFD3A5',
            'w': '#01F0D8', 'r': '#C44569', 'd': '#01F0D8', ' ': '#F0F0F0',
            'a': '#FF6B6B', 'b': '#4ECDC4', 'c': '#FFE66D', 'f': '#FF9FF3',
            'g': '#4834D4', 'i': '#45B7D1', 'j': '#96CEB4', 'k': '#00D2D3',
            'm': '#FECA57', 'n': '#0ABDE3', 'p': '#F368E0', 'q': '#FF9F43',
            's': '#3742FA', 't': '#FF6B6B', 'u': '#4ECDC4', 'v': '#FFE66D',
            'x': '#A8E6CF', 'y': '#FF9FF3', 'z': '#4834D4'
        }
        self.reverse_mapping = {v: k for k, v in self.hex_mapping.items()}
        self.punct_color = '#2B2B2B'

        self.learner = LearningEngine()  # محرك التعلم

    def text_to_hex(self, text: str):
        parts = re.findall(r"[a-zA-Z0-9']+|[.,!?;: ]", text)
        out = []
        for p in parts:  # ✅ إضافة النقطتين المفقودتين
            if p in '.,!?;:':
                out.append(p)
            elif p == ' ':
                out.append('#F0F0F0')  # ✅ self.space_color → قيمة ثابتة
            else:
                colors = []
                for ch in p:
                    if ch.isalpha():
                        colors.append(self.hex_mapping[ch.lower()])
                    else:
                        colors.append(self.punct_color)
                out.append('(' + "'".join(colors) + ')')
        return ' '.join(out)

    def hex_to_text(self, hex_string: str):
        result = []
        current_word = []
        hex_string = hex_string.replace(' ', '')

        i = 0
        while i < len(hex_string):
            if hex_string[i] == '(':
                current_word = []
                i += 1
            elif hex_string[i] == ')':
                if current_word:
                    word = ''.join([self.reverse_mapping.get(c, '?') for c in current_word])
                    result.append(word)
            elif hex_string[i] == "'":
                i += 1
            elif len(hex_string) - i >= 7 and hex_string[i:i+7].startswith('#'):
                hex_code = hex_string[i:i+7]
                current_word.append(hex_code)
                i += 7
            elif hex_string[i] in '.,!?;:':
                if current_word:
                    word = ''.join([self.reverse_mapping.get(c, '?') for c in current_word])
                    result.append(word)
                result.append(hex_string[i])
            else:
                i += 1

        if current_word:
            word = ''.join([self.reverse_mapping.get(c, '?') for c in current_word])
            result.append(word)

        return ''.join(result)

    def text_to_hex_preserved(self, text: str):
        """تحويل مع الحفاظ على الترتيب والمسافات والنقاط"""
        lines = text.splitlines(keepends=True)  # الحفاظ على \n
        result_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_lines.append(line)  # سطر فارغ
                continue

            # إذا سطر مرقّم أو ينتهي بنقطتين
            if re.match(r'^\\d+\\.', stripped) or stripped.endswith(':'):
                result_lines.append(line)  # يبقى كما هو
            else:
                # تحويل الكلمات فقط
                parts = re.findall(r"[a-zA-Z0-9']+|[.,!?;: \\n\\t]", line)
                converted_parts = []
                for p in parts:
                    if p.strip() in '.,!?;:':
                        converted_parts.append(p)
                    elif p.strip() == '':
                        converted_parts.append(p)
                    else:
                        colors = [self.hex_mapping[ch.lower()] for ch in p if ch.isalpha()]
                        converted_parts.append('(' + "'".join(colors) + ')')
                result_lines.append(''.join(converted_parts))

        return ''.join(result_lines)

    def hex_to_tokens(self, hex_string: str):
        """استخراج قائمة hex codes من السلسلة"""
        tokens = re.findall(r'#\w{6}', hex_string)
        return tokens

    def colors_to_embedding(self, hex_string: str):
        """تحويل ألوان hex إلى embedding رقمي"""
        tokens = self.hex_to_tokens(hex_string)
        # تحويل hex إلى أرقام (للنماذج اللغوية)
        embeddings = []
        for token in tokens:
            # hex → decimal (4 أرقام)
            num = int(token[1:], 16) % 10000
            embeddings.append(num)
        return embeddings

    def embedding_to_semantic(self, embeddings):
        """تحليل دلالي بسيط"""
        if not embeddings:
            return {"خطأ": "لا توجد ألوان"}

        return {
            'عدد الرموز': len(embeddings),
            'المتوسط': sum(embeddings) / len(embeddings),
            'التنوع': len(set(embeddings)),
            'الأقوى': max(embeddings),
            'الأضعف': min(embeddings)
    }

class HexColorGUI:
    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("محرك تحويل الألوان")
        self.root.geometry("1000x700")

        # إطار رئيسي واحد بـ grid
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # عنوان
        ttk.Label(main_frame, text="محرك تحويل الألوان إلى Hex Codes",
                font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)

        # خانة النص الأصلي
        ttk.Label(main_frame, text="النص الأصلي:", font=('Arial', 12)).grid(row=1, column=0, sticky='w', pady=5)
        self.text_input = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=6)
        self.text_input.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=5)

        # الأزرار الملونة
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=15)

        tk.Button(btn_frame, text="نص → ألوان", command=self.to_colors,
                bg='#4CAF50', fg='white', activebackground='#45a049',
                font=('Arial', 11, 'bold'), relief='flat', padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="ألوان → نص", command=self.to_text,
                bg='#2196F3', fg='white', activebackground='#1976D2',
                font=('Arial', 11, 'bold'), relief='flat', padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="مسح", command=self.clear,
                bg='#FF5722', fg='white', activebackground='#E64A19',
                font=('Arial', 11, 'bold'), relief='flat', padx=20).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📁 رفع ملف", command=self.load_file,
                bg='#9C27B0', fg='white', activebackground='#7B1FA2',
                font=('Arial', 11, 'bold'), relief='flat', padx=20).pack(side=tk.LEFT, padx=5)

        # زر رفع الملف
        ttk.Button(btn_frame, text="📁 رفع ملف", command=self.load_file).pack(side=tk.LEFT, padx=5)

        # خانة النتيجة
        ttk.Label(main_frame, text="النتيجة (Hex Colors):", font=('Arial', 12)).grid(row=4, column=0, sticky='w', pady=(20,5))
        self.result_output = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=6)
        self.result_output.grid(row=5, column=0, columnspan=3, sticky='nsew', pady=5)

        # شريط الحالة
        self.status = ttk.Label(main_frame, text="جاهز - اسحب النافذة للتكبير", relief='sunken', anchor='w')
        self.status.grid(row=6, column=0, columnspan=3, sticky='ew', pady=(10,0))

        # تكوين التكبير التلقائي
        main_frame.grid_rowconfigure(2, weight=1)   # خانة النص
        main_frame.grid_rowconfigure(5, weight=1)   # خانة النتيجة
        main_frame.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # إضافة file_label
        self.file_label = ttk.Label(main_frame, text="لا يوجد ملف", foreground='gray')
        self.file_label.grid(row=3, column=2, sticky='w')

        tk.Button(btn_frame, text="تحليل دلالي", command=self.semantic_analysis,
                bg='#9C27B0', fg='white').pack(side=tk.LEFT, padx=5)

        # البحث المشابه
        tk.Button(btn_frame, text="🔍 مشابه", command=self.find_similar_advanced,
                bg='#607D8B', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🔍 بحث متقدّم", command=self.find_similar_advanced,
                bg='#FF9800', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="📊 تقرير ذاكرة", command=self.generate_report,
                bg='#607D8B', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="🔍 فحص الذاكرة",
                command=lambda: self.status.config(text=self.engine.learner.memory_stats()),
                bg='#FF9800', fg='white').pack(side=tk.LEFT, padx=5)

    def load_file(self):
        from tkinter import filedialog, messagebox

        filename = filedialog.askopenfilename(
            title="اختر ملف TXT",
            filetypes=[("Text files", "*.txt")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(1.0, content)

                result = self.engine.text_to_hex(content)
                self.result_output.delete(1.0, tk.END)
                self.result_output.insert(1.0, result)

                # تصحيح الألوان
                self.file_label.config(text=f"تم تحميل: {filename.split('/')[-1]}",
                                    foreground='#4CAF50')
                self.status.config(text=f"تم التحويل ✓", foreground='#2196F3')

            except Exception as e:
                messagebox.showerror("خطأ", str(e))

    def to_colors(self):
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            result = self.engine.text_to_hex(text)
            self.result_output.delete(1.0, tk.END)
            self.result_output.insert(1.0, result)
            self.status.config(text=f"تم التحويل ✓")

    def to_text(self):
        hex_text = self.result_output.get(1.0, tk.END).strip()
        if hex_text:
            result = self.engine.hex_to_text(hex_text)
            self.text_input.delete(1.0, tk.END)
            self.text_input.insert(1.0, result)
            self.status.config(text=f"تم الاستعادة ✓")

    def semantic_analysis(self):
        hex_text = self.result_output.get(1.0, tk.END).strip()
        if hex_text:
            embeddings = self.engine.colors_to_embedding(hex_text)
            analysis = self.engine.embedding_to_semantic(embeddings)

            result = "تحليل دلالي:\n"
            for key, value in analysis.items():
                result += f"{key}: {value}\n"

            self.result_output.delete(1.0, tk.END)
            self.result_output.insert(1.0, result)
            self.status.config(text=f"تم التحليل ({len(embeddings)} رمز) ✓")

    def to_colors_preserved(self):
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            result = self.engine.text_to_hex_preserved(text)
            self.result_output.delete(1.0, tk.END)
            self.result_output.insert(1.0, result)
            self.status.config(text="تم التحويل مع الحفاظ على الترتيب ✓")

    def generate_report(self):
        report = self.engine.learner.generate_report()
        self.status.config(text=report, foreground='#4CAF50')

        # عرض الإحصائيات السريعة
        stats = self.engine.learner.memory_stats()
        self.result_output.insert(tk.END, f"\n\n{stats}")

    # ---------- البحث المتشابه find similar words --------------------
    def find_similar_advanced(self):
        """البحث المتقدّم: كلمات + جمل + عناوين"""
        hex_text = self.result_output.get(1.0, tk.END).strip()
        if not hex_text:
            return

        # استخراج المكوّنات
        words = re.findall(r'\([#0-9A-Fa-f\' ]+\)', hex_text)
        sentences = re.split(r'[.!?]+', hex_text)
        titles = re.findall(r'^[#0-9A-Fa-f\' ]+\)', hex_text, re.MULTILINE)

        results = {
            'كلمات متشابهة': self._find_similar_words(words),
            'جمل متشابهة': self._find_similar_sentences(sentences),
            'عناوين متشابهة': self._find_similar_titles(titles)
        }

        output = "نتائج البحث المتقدّم:\n\n"
        for category, matches in results.items():
            output += f"{category}:\n"
            if matches:
                for match in matches[:3]:  # أفضل 3
                    output += f"  • {match[0]} ({match[1]:.1%})\n"
            else:
                output += "  لا توجد تشابهات\n"
            output += "\n"

        self.result_output.delete(1.0, tk.END)
        self.result_output.insert(1.0, output)
        self.status.config(text=f"تم البحث المتقدّم ({len(words)} كلمة) ✓", foreground='#FF9800')

    def _find_similar_words(self, words, threshold=0.6):
        """البحث عن كلمات متشابهة"""
        similarities = []
        for word in words:
            matches = self.engine.learner.find_similar(word)
            similarities.extend([(f"{word[:30]}...", score) for name, score in matches if score > threshold])
        return similarities[:5]

    def _find_similar_sentences(self, sentences, threshold=0.5):
        """البحث عن جمل متشابهة"""
        similarities = []
        for sent in sentences:
            if len(sent.strip()) > 10:  # جمل طويلة فقط
                matches = self.engine.learner.find_similar(sent.strip())
                similarities.extend([(f"جملة: {sent[:50]}...", score) for name, score in matches if score > threshold])
        return similarities[:5]

    def _find_similar_titles(self, titles, threshold=0.7):
        """البحث عن عناوين متشابهة"""
        similarities = []
        for title in titles:
            matches = self.engine.learner.find_similar(title.strip())
            similarities.extend([(f"عنوان: {title[:40]}...", score) for name, score in matches if score > threshold])
        return similarities[:5]

    # ---------- دوال مساعدة --------------------

    def clear(self):
        self.text_input.delete(1.0, tk.END)
        self.result_output.delete(1.0, tk.END)
        self.status.config(text="تم المسح")

    def run(self):
        self.root.mainloop()

    def check_memory_status(self):
        """فحص حالة الذاكرة"""
        files_count = len(self.engine.learner.knowledge_base)
        if files_count == 0:
            return "🚨 الذاكرة فارغة! لا توجد ملفات محملة"
        else:
            return f"✅ الذاكرة جاهزة: {files_count} ملف"

    def check_knowledge_base(self):
        """تشخيص سريع"""
        print(f"عدد الملفات: {len(self.knowledge_base)}")
        print(f"المحتوى: {list(self.knowledge_base.keys())}")
        return self.knowledge_base

class LearningEngine:
    def __init__(self):
        self.knowledge_base = {}
        self.load_knowledge()
        self.knowledge_base = {}
        self.auto_analyze()  # تشغيل تلقائي عند البدء

    def auto_analyze(self, output_file='تقرير_شامل_تلقائي.txt'):
        """تحليل دالي تلقائي شامل + تقرير موحد"""
        from datetime import datetime

        report = []
        report.append("🎯 تقرير الذاكرة التلقائي الشامل\n")
        report.append("=" * 60 + "\n")
        report.append(f"⏰ التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        files_count = len(self.knowledge_base)
        report.append(f"📁 حالة الذاكرة: {files_count} ملف\n")

        if files_count == 0:
            report.append("\n🚨 الذاكرة فارغة تماماً\n")
            report.append("🔧 الحل التلقائي:\n")
            report.append("   1. تحميل ملفات .txt\n")
            report.append("   2. تشغيل load_knowledge()\n")
            report.append("   3. إعادة تشغيل auto_analyze()\n")
        else:
            # تحليل شامل
            report.append("\n📊 التحليل الدالي التلقائي:\n")
            report.append("-" * 40)

            lengths = [data['length'] for data in self.knowledge_base.values()]
            uniques = [data['unique_colors'] for data in self.knowledge_base.values()]

            report.append(f"📏 الطول الإجمالي: {sum(lengths):,} حرف")
            report.append(f"🎨 إجمالي الألوان: {sum(uniques)}")
            report.append(f"📈 متوسط الألوان/ملف: {sum(uniques)/files_count:.1f}")
            report.append(f"🏆 أطول ملف: {max(lengths)} حرف")
            report.append(f"🌈 أكثر تنوع: {max(uniques)} لون\n")

            # قائمة الملفات
            report.append("📋 الملفات المحملة:\n")
            for i, (name, data) in enumerate(sorted(self.knowledge_base.items(),
                                                key=lambda x: x[1]['length'], reverse=True), 1):
                report.append(f"{i:2d}. {name:<25} | {data['length']:>5}ح | {data['unique_colors']:>2}ل")

        # حفظ تلقائي
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        return f"✅ تم إنشاء التقرير التلقائي: {output_file}"

    def quick_scan(self):
        """فحص سريع واحد للتشخيص"""
        count = len(self.knowledge_base)
        if count == 0:
            return "🚨 الذاكرة فارغة - تحتاج تحميل ملفات"
        return f"✅ جاهز: {count} ملف محمل"

    def generate_report(self, output_file='تحليل_الذاكرة.txt'):
        """إنشاء تقرير شامل للذاكرة"""
        from datetime import datetime

        report = []
        report.append("=== تقرير ذاكرة الألوان ===\n")
        report.append(f"تاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

        total_files = len(self.knowledge_base)
        report.append(f"إجمالي الملفات: {total_files}\n")

        if total_files == 0:
            report.append("\n⚠️  الذاكرة فارغة!\n")
            report.append("💡 خطوات الاستخدام:\n")
            report.append("   1. اضغط 'تحميل ملف'\n")
            report.append("   2. اختر ملف .txt\n")
            report.append("   3. اضغط 'تدريب الذاكرة'\n")
            report.append("   4. جرب 'تقرير ذاكرة'\n\n")
        else:
            all_lengths = [data['length'] for data in self.knowledge_base.values()]
            all_unique = [data['unique_colors'] for data in self.knowledge_base.values()]

            report.append("\n📊 إحصائيات عامة:\n")
            report.append(f"  📏 متوسط الطول: {sum(all_lengths)/total_files:.0f} حرف\n")
            report.append(f"  🎨 متوسط الألوان: {sum(all_unique)/total_files:.1f}\n")
            report.append(f"  📈 أطول ملف: {max(all_lengths)} حرف\n")
            report.append(f"  🌈 أكثر تنوع: {max(all_unique)} لون\n\n")

            report.append("📋 قائمة الملفات:\n")
            report.append("-" * 80)
            for name, data in sorted(self.knowledge_base.items(), key=lambda x: x[1]['length'], reverse=True):
                report.append(f"{name:<30} | {data['length']:>6} حرف | {data['unique_colors']:>3} لون")
                report.append(f"  بصمة: {data['hex_signature'][:60]}...")
                report.append("")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

        status = "جاهزة!" if total_files > 0 else "فارغة"
        return f"تم حفظ التقرير: {output_file} | {status}"

    def top_similar_colors(self, top_n=10):
        """أكثر الألوان شيوعًا"""
        all_colors = []
        for data in self.knowledge_base.values():
            all_colors.extend(re.findall(r'#[0-9A-Fa-f]{6}', data['hex_signature']))

        color_count = {}
        for color in all_colors:
            color_count[color] = color_count.get(color, 0) + 1

        report = "أكثر 10 ألوان شيوعًا:\n"
        for color, count in sorted(color_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"{color}: {count} مرة ({count/len(all_colors)*100:.1f}%)\n"

        return report

    def memory_stats(self):
        """إحصائيات سريعة آمنة"""
        files = len(self.knowledge_base)

        if files == 0:
            return "📊 الذاكرة: فارغة | جاهزة للتحميل 📂"

        total_chars = sum(data['length'] for data in self.knowledge_base.values())
        total_unique = sum(data['unique_colors'] for data in self.knowledge_base.values())
        avg_unique = total_unique / files

        return f"📊 الذاكرة: {files} ملف | {total_chars:,} حرف | {avg_unique:.1f} لون/ملف"

    def learn_from_file(self, filename, hex_result):
        """تتعلم من الملف المرفوع"""
        basename = filename.split('/')[-1].split('\\')[-1]

        self.knowledge_base[basename] = {
            'hex_signature': hex_result,
            'length': len(hex_result),
            'unique_colors': len(set(re.findall(r'#[0-9A-Fa-f]{6}', hex_result))),
            'timestamp': '2026-04-19'
        }
        self.save_knowledge()
        return f"تم التعلم: {basename}"

    def save_knowledge(self):
        import json
        with open('color_knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)

    def load_knowledge(self):
        import json, os
        if os.path.exists('color_knowledge.json'):
            with open('color_knowledge.json', 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)

    def find_similar(self, hex_query, threshold=0.5):
        similarities = []
        for name, data in self.knowledge_base.items():
            query_colors = set(re.findall(r'#[0-9A-Fa-f]{6}', hex_query))
            stored_colors = set(re.findall(r'#[0-9A-Fa-f]{6}', data['hex_signature']))

            if query_colors and stored_colors:
                score = len(query_colors & stored_colors) / len(query_colors | stored_colors)
                if score >= threshold:  # استخدام threshold
                    similarities.append((name, score))

        return sorted(similarities, key=lambda x: x[1], reverse=True)

if __name__ == '__main__':
    engine = SimpleHexColorEngine()
    app = HexColorGUI(engine)
    app.run()
