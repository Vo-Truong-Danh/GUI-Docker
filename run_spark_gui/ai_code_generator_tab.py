"""
AI Code Generator Tab for Spark Runner GUI
Generates PySpark code based on natural language descriptions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
from pathlib import Path
from datetime import datetime
import re


class AICodeGeneratorTab:
    """AI Code Generator for PySpark"""
    
    # Code templates
    TEMPLATE_BASE = """# {filename}
from pyspark.sql import SparkSession
import re

def main():
    \"\"\"
    {description}
    \"\"\"
    # 1. Khởi tạo SparkSession
    spark = SparkSession.builder \\
        .appName("{app_name}") \\
        .getOrCreate()

    # Lấy SparkContext từ SparkSession
    sc = spark.sparkContext

    try:
{processing_code}
        
    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình xử lý Spark: {{e}}")

    finally:
        # Dừng SparkSession để giải phóng tài nguyên
        spark.stop()

if __name__ == "__main__":
    main()
"""

    def __init__(self, parent_frame, config, status_callback, log_callback):
        """
        Initialize AI Code Generator tab
        
        Args:
            parent_frame: Parent ttk.Frame
            config: Configuration dict
            status_callback: Function to update status bar
            log_callback: Function to append to log
        """
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        self.generated_code = ""
        
        self.create_ui()
    
    def create_ui(self):
        """Create AI Code Generator tab UI"""
        main_container = ttk.Frame(self.frame, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Info section
        info_text = (
            "🤖 AI Code Generator - Tạo code PySpark tự động từ mô tả bằng văn bản\n"
            "Mô tả yêu cầu của bạn, AI sẽ sinh code PySpark hoàn chỉnh"
        )
        info_lbl = ttk.Label(main_container, text=info_text, foreground='#555',
                            font=('Segoe UI', 9))
        info_lbl.pack(fill=tk.X, pady=(0, 10))
        
        # === Input Section ===
        input_frame = ttk.LabelFrame(main_container, text='📝 Mô Tả Yêu Cầu', padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Instructions
        instruction_text = (
            "💡 Ví dụ: 'Đọc file harrypotter.txt từ HDFS, đếm tổng số từ và in ra kết quả'\n"
            "💡 Hoặc: 'Phân tích file CSV, lọc dữ liệu theo điều kiện và lưu kết quả'"
        )
        instruction_lbl = ttk.Label(input_frame, text=instruction_text, 
                                    foreground='#666', font=('Segoe UI', 8, 'italic'))
        instruction_lbl.pack(fill=tk.X, pady=(0, 5))
        
        # Input fields
        fields_frame = ttk.Frame(input_frame)
        fields_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: File path
        row1 = ttk.Frame(fields_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(row1, text='📁 HDFS Path:', font=('Segoe UI', 9), width=15).pack(side=tk.LEFT)
        self.hdfs_path_var = tk.StringVar(value='/input/harrypotter.txt')
        hdfs_entry = ttk.Entry(row1, textvariable=self.hdfs_path_var, width=50,
                              font=('Courier New', 9))
        hdfs_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Row 2: App name
        row2 = ttk.Frame(fields_frame)
        row2.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(row2, text='🏷️ App Name:', font=('Segoe UI', 9), width=15).pack(side=tk.LEFT)
        self.app_name_var = tk.StringVar(value='HDFSDataProcessing')
        app_entry = ttk.Entry(row2, textvariable=self.app_name_var, width=50,
                             font=('Courier New', 9))
        app_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Description text area
        ttk.Label(input_frame, text='📄 Mô Tả Chi Tiết:', font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(5, 5))
        self.description_text = scrolledtext.ScrolledText(input_frame, height=8, wrap=tk.WORD,
                                                          bg='#ffffff', font=('Segoe UI', 9))
        self.description_text.pack(fill=tk.BOTH, expand=True)
        
        # Default description
        default_desc = """Đọc file văn bản từ HDFS, thực hiện các bước sau:
1. Tách từng dòng thành các từ
2. Chuyển tất cả về chữ thường
3. Loại bỏ ký tự đặc biệt
4. Đếm tổng số từ trong văn bản
5. In kết quả ra console"""
        self.description_text.insert('1.0', default_desc)
        
        # Templates buttons
        template_frame = ttk.Frame(input_frame)
        template_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(template_frame, text='📋 Templates:', font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        templates = [
            ('Word Count', self.template_word_count),
            ('CSV Analysis', self.template_csv_analysis),
            ('Data Filter', self.template_data_filter),
            ('Top N', self.template_top_n),
        ]
        
        for name, cmd in templates:
            btn = ttk.Button(template_frame, text=name, command=cmd, width=12)
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Generate button
        generate_btn_frame = ttk.Frame(input_frame)
        generate_btn_frame.pack(pady=(10, 0))
        
        self.generate_btn = ttk.Button(generate_btn_frame, text='✨ Generate Code', 
                                      command=self.generate_code, width=20,
                                      style='Success.TButton')
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(generate_btn_frame, text='🗑️ Clear', 
                              command=self.clear_input, width=12)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # === Output Section ===
        output_frame = ttk.LabelFrame(main_container, text='💻 Generated Code', padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Code display
        self.code_text = scrolledtext.ScrolledText(output_frame, height=20, wrap=tk.NONE,
                                                   bg='#1e1e1e', fg='#d4d4d4',
                                                   font=('Courier New', 9),
                                                   insertbackground='white')
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Syntax highlighting tags
        self.code_text.tag_config('keyword', foreground='#569cd6')
        self.code_text.tag_config('string', foreground='#ce9178')
        self.code_text.tag_config('comment', foreground='#6a9955')
        self.code_text.tag_config('function', foreground='#dcdcaa')
        
        # Action buttons
        action_frame = ttk.Frame(output_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.save_btn = ttk.Button(action_frame, text='💾 Save to File', 
                                   command=self.save_code, width=15, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_btn = ttk.Button(action_frame, text='📋 Copy Code', 
                                   command=self.copy_code, width=15, state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.run_btn = ttk.Button(action_frame, text='▶️ Run in Spark Tab', 
                                  command=self.run_in_spark, width=18, state=tk.DISABLED)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Stats label
        self.stats_label = ttk.Label(action_frame, text='Ready to generate', 
                                     font=('Segoe UI', 9), foreground='#666')
        self.stats_label.pack(side=tk.RIGHT)
        
        # Welcome message
        self.log_ai('🤖 AI Code Generator Ready', 'info')
        self.log_ai('💡 Nhập mô tả và nhấn "Generate Code"', 'info')
    
    def log_ai(self, message, level='info'):
        """Log message to main log"""
        if self.append_log:
            if level == 'info':
                self.append_log(f'🤖 AI: {message}', 'info')
            elif level == 'success':
                self.append_log(f'🤖 AI: {message}', 'success')
            elif level == 'error':
                self.append_log(f'🤖 AI: {message}', 'error')
    
    def template_word_count(self):
        """Load word count template"""
        self.hdfs_path_var.set('/input/harrypotter.txt')
        self.app_name_var.set('HDFSTotalWordCount')
        desc = """Đọc file văn bản từ HDFS và đếm tổng số từ:
1. Đọc file từ HDFS
2. Tách mỗi dòng thành các từ
3. Chuyển về chữ thường
4. Loại bỏ ký tự đặc biệt bằng regex
5. Đếm tổng số từ
6. In kết quả ra console"""
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', desc)
        self.log_ai('Loaded Word Count template', 'success')
    
    def template_csv_analysis(self):
        """Load CSV analysis template"""
        self.hdfs_path_var.set('/input/data.csv')
        self.app_name_var.set('HDFSCSVAnalysis')
        desc = """Phân tích file CSV từ HDFS:
1. Đọc file CSV với header
2. Hiển thị schema
3. Đếm số dòng
4. Hiển thị 10 dòng đầu
5. Tính toán statistics cơ bản"""
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', desc)
        self.log_ai('Loaded CSV Analysis template', 'success')
    
    def template_data_filter(self):
        """Load data filter template"""
        self.hdfs_path_var.set('/input/data.csv')
        self.app_name_var.set('HDFSDataFilter')
        desc = """Lọc dữ liệu từ HDFS:
1. Đọc file CSV
2. Lọc các dòng thỏa điều kiện
3. Sắp xếp theo cột
4. Lưu kết quả vào HDFS output"""
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', desc)
        self.log_ai('Loaded Data Filter template', 'success')
    
    def template_top_n(self):
        """Load top N template"""
        self.hdfs_path_var.set('/input/data.txt')
        self.app_name_var.set('HDFSTopNWords')
        desc = """Tìm top N từ xuất hiện nhiều nhất:
1. Đọc file văn bản
2. Tách và làm sạch từ
3. Đếm số lần xuất hiện
4. Sắp xếp giảm dần
5. Lấy top 10 từ
6. In kết quả"""
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', desc)
        self.log_ai('Loaded Top N template', 'success')
    
    def clear_input(self):
        """Clear all inputs"""
        self.description_text.delete('1.0', tk.END)
        self.hdfs_path_var.set('/input/data.txt')
        self.app_name_var.set('HDFSDataProcessing')
        self.log_ai('Input cleared', 'info')
    
    def generate_code(self):
        """Generate PySpark code based on description"""
        description = self.description_text.get('1.0', tk.END).strip()
        hdfs_path = self.hdfs_path_var.get().strip()
        app_name = self.app_name_var.get().strip()
        
        if not description:
            messagebox.showwarning('Missing Input', 'Vui lòng nhập mô tả yêu cầu')
            return
        
        if not hdfs_path:
            messagebox.showwarning('Missing Input', 'Vui lòng nhập HDFS path')
            return
        
        self.log_ai('Generating code...', 'info')
        self.generate_btn['state'] = tk.DISABLED
        
        try:
            # Generate code based on description keywords
            processing_code = self._generate_processing_code(description, hdfs_path)
            
            # Create filename from app name
            filename = f"{app_name.lower().replace(' ', '_')}.py"
            
            # Fill template
            code = self.TEMPLATE_BASE.format(
                filename=filename,
                description=description.replace('\n', '\n    '),
                app_name=app_name,
                processing_code=processing_code
            )
            
            # Display code
            self.code_text.delete('1.0', tk.END)
            self.code_text.insert('1.0', code)
            self._apply_syntax_highlighting()
            
            self.generated_code = code
            
            # Enable buttons
            self.save_btn['state'] = tk.NORMAL
            self.copy_btn['state'] = tk.NORMAL
            self.run_btn['state'] = tk.NORMAL
            
            # Update stats
            lines = len(code.split('\n'))
            self.stats_label['text'] = f'✅ Generated: {lines} lines'
            
            self.log_ai(f'Code generated successfully ({lines} lines)', 'success')
            self.update_status('✅ AI code generated')
            
        except Exception as e:
            self.log_ai(f'Error generating code: {e}', 'error')
            messagebox.showerror('Generation Error', f'Lỗi khi sinh code:\n{e}')
        finally:
            self.generate_btn['state'] = tk.NORMAL
    
    def _generate_processing_code(self, description, hdfs_path):
        """Generate processing code based on description keywords"""
        desc_lower = description.lower()
        
        # Detect task type
        is_word_count = any(kw in desc_lower for kw in ['đếm từ', 'word count', 'count word', 'số từ'])
        is_csv = hdfs_path.endswith('.csv') or 'csv' in desc_lower
        is_top_n = 'top' in desc_lower and any(kw in desc_lower for kw in ['từ', 'word', 'item'])
        is_filter = any(kw in desc_lower for kw in ['lọc', 'filter', 'điều kiện'])
        
        # Generate appropriate code
        if is_csv:
            return self._generate_csv_code(hdfs_path, desc_lower, is_filter)
        elif is_top_n:
            return self._generate_top_n_code(hdfs_path)
        elif is_word_count:
            return self._generate_word_count_code(hdfs_path)
        else:
            return self._generate_basic_read_code(hdfs_path)
    
    def _generate_word_count_code(self, hdfs_path):
        """Generate word count code"""
        return f"""        # 2. Chỉ định đường dẫn HDFS
        hdfs_input_path = "hdfs://namenode:8020{hdfs_path}"

        # 3. Đọc dữ liệu từ HDFS bằng Spark vào RDD
        lines_rdd = sc.textFile(hdfs_input_path)

        # 4. Xử lý và đếm tổng số từ
        def clean_word(word):
            # Loại bỏ các ký tự không phải chữ cái hoặc số
            return re.sub(r'[^a-z0-9]', '', word)

        # - flatMap: Tách mỗi dòng thành các từ và chuyển về chữ thường
        # - map: Làm sạch từng từ
        # - filter: Loại bỏ các chuỗi rỗng sau khi làm sạch
        # - count: Đếm tổng số phần tử (từ) trong RDD
        total_word_count = lines_rdd.flatMap(lambda line: line.lower().split()) \\
                                    .map(clean_word) \\
                                    .filter(lambda word: len(word) > 0) \\
                                    .count()
        
        # 5. In kết quả tổng số từ ra command line
        print("\\n=============================================")
        print(f"  Tổng số từ trong văn bản là: {{total_word_count}}")
        print("=============================================\\n")"""
    
    def _generate_csv_code(self, hdfs_path, desc_lower, is_filter):
        """Generate CSV processing code"""
        code = f"""        # 2. Chỉ định đường dẫn HDFS
        hdfs_input_path = "hdfs://namenode:8020{hdfs_path}"

        # 3. Đọc file CSV từ HDFS
        df = spark.read.csv(hdfs_input_path, header=True, inferSchema=True)

        # 4. Hiển thị thông tin
        print("\\n=== Schema của DataFrame ===")
        df.printSchema()
        
        print(f"\\nTổng số dòng: {{df.count()}}")
        
        print("\\n=== 10 dòng đầu tiên ===")
        df.show(10)"""
        
        if is_filter:
            code += """
        
        # 5. Lọc dữ liệu (ví dụ: lọc các dòng có giá trị > 100)
        # Thay đổi điều kiện lọc theo yêu cầu
        filtered_df = df.filter(df['column_name'] > 100)
        
        print(f"\\nSố dòng sau khi lọc: {{filtered_df.count()}}")
        filtered_df.show(10)
        
        # 6. Lưu kết quả
        output_path = "hdfs://namenode:8020/output/filtered_result"
        filtered_df.write.mode('overwrite').csv(output_path, header=True)
        print(f"\\nĐã lưu kết quả vào: {{output_path}}")"""
        
        return code
    
    def _generate_top_n_code(self, hdfs_path):
        """Generate top N code"""
        return f"""        # 2. Chỉ định đường dẫn HDFS
        hdfs_input_path = "hdfs://namenode:8020{hdfs_path}"

        # 3. Đọc dữ liệu từ HDFS
        lines_rdd = sc.textFile(hdfs_input_path)

        # 4. Xử lý và đếm từ
        def clean_word(word):
            return re.sub(r'[^a-z0-9]', '', word)

        # - flatMap: Tách thành từ
        # - map: Làm sạch và tạo tuple (word, 1)
        # - filter: Loại từ rỗng
        # - reduceByKey: Cộng dồn số lần xuất hiện
        # - sortBy: Sắp xếp giảm dần theo count
        # - take: Lấy top 10
        word_counts = lines_rdd.flatMap(lambda line: line.lower().split()) \\
                              .map(clean_word) \\
                              .filter(lambda word: len(word) > 0) \\
                              .map(lambda word: (word, 1)) \\
                              .reduceByKey(lambda a, b: a + b) \\
                              .sortBy(lambda x: x[1], ascending=False) \\
                              .take(10)
        
        # 5. In kết quả top 10
        print("\\n=== Top 10 từ xuất hiện nhiều nhất ===")
        for i, (word, count) in enumerate(word_counts, 1):
            print(f"{{i:2d}}. {{word:20s}} - {{count:,}} lần")
        print("=" * 45)"""
    
    def _generate_basic_read_code(self, hdfs_path):
        """Generate basic read code"""
        return f"""        # 2. Chỉ định đường dẫn HDFS
        hdfs_input_path = "hdfs://namenode:8020{hdfs_path}"

        # 3. Đọc dữ liệu từ HDFS
        lines_rdd = sc.textFile(hdfs_input_path)

        # 4. Đếm số dòng
        line_count = lines_rdd.count()
        
        # 5. Hiển thị 10 dòng đầu
        first_lines = lines_rdd.take(10)
        
        print("\\n=============================================")
        print(f"  Tổng số dòng: {{line_count}}")
        print("=============================================")
        print("\\n=== 10 dòng đầu tiên ===")
        for i, line in enumerate(first_lines, 1):
            print(f"{{i}}. {{line[:100]}}")  # Hiển thị tối đa 100 ký tự
        print("=" * 45)"""
    
    def _apply_syntax_highlighting(self):
        """Apply basic syntax highlighting"""
        content = self.code_text.get('1.0', tk.END)
        
        # Keywords
        keywords = ['from', 'import', 'def', 'class', 'if', 'else', 'elif', 'for', 'while', 
                   'return', 'try', 'except', 'finally', 'with', 'as', 'lambda', 'yield']
        
        for keyword in keywords:
            start = '1.0'
            while True:
                pos = self.code_text.search(r'\b' + keyword + r'\b', start, tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.code_text.tag_add('keyword', pos, end)
                start = end
    
    def save_code(self):
        """Save generated code to file"""
        if not self.generated_code:
            return
        
        app_name = self.app_name_var.get().strip()
        default_filename = f"{app_name.lower().replace(' ', '_')}.py"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.py',
            filetypes=[('Python files', '*.py'), ('All files', '*.*')],
            initialfile=default_filename
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.generated_code)
                self.log_ai(f'Code saved to: {filepath}', 'success')
                self.update_status(f'✅ Saved: {Path(filepath).name}')
                messagebox.showinfo('Success', f'Code đã được lưu vào:\n{filepath}')
            except Exception as e:
                self.log_ai(f'Failed to save: {e}', 'error')
                messagebox.showerror('Save Error', f'Lỗi khi lưu file:\n{e}')
    
    def copy_code(self):
        """Copy code to clipboard"""
        if not self.generated_code:
            return
        
        try:
            self.code_text.clipboard_clear()
            self.code_text.clipboard_append(self.generated_code)
            self.log_ai('Code copied to clipboard', 'success')
            self.update_status('✅ Code copied')
            self.stats_label['text'] = '📋 Copied to clipboard'
        except Exception as e:
            self.log_ai(f'Failed to copy: {e}', 'error')
    
    def run_in_spark(self):
        """Save and switch to Spark tab to run"""
        if not self.generated_code:
            return
        
        # Auto-save to temp directory
        temp_dir = Path.cwd() / 'generated_code'
        temp_dir.mkdir(exist_ok=True)
        
        app_name = self.app_name_var.get().strip()
        filename = f"{app_name.lower().replace(' ', '_')}.py"
        filepath = temp_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.generated_code)
            
            self.log_ai(f'Code saved to: {filepath}', 'success')
            self.log_ai('💡 Switch to Spark Runner tab to run the code', 'info')
            self.update_status(f'✅ Ready to run: {filename}')
            
            messagebox.showinfo('Ready to Run', 
                              f'Code đã được lưu vào:\n{filepath}\n\n'
                              f'Chuyển sang tab "Spark Runner" để chạy!')
        except Exception as e:
            self.log_ai(f'Failed to save: {e}', 'error')
            messagebox.showerror('Save Error', f'Lỗi khi lưu file:\n{e}')
