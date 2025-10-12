"""
AI Code Generator Tab - V4 Clean Professional Edition
Clean, minimal UI inspired by GitHub/VS Code
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from datetime import datetime
import re


# ============================================================================
# V4 CLEAN COMPONENTS (Shared)
# ============================================================================

class CleanButton:
    """Clean button with GitHub-style design"""
    
    STYLES = {
        'primary': {
            'bg': '#0969DA', 'fg': 'white',
            'hover_bg': '#0860CA', 'active_bg': '#0757BA'
        },
        'success': {
            'bg': '#1A7F37', 'fg': 'white',
            'hover_bg': '#1A7F37', 'active_bg': '#18692F'
        },
        'danger': {
            'bg': '#CF222E', 'fg': 'white',
            'hover_bg': '#C11F2A', 'active_bg': '#A40E26'
        },
        'secondary': {
            'bg': '#6E7781', 'fg': 'white',
            'hover_bg': '#57606A', 'active_bg': '#424A53'
        },
        'outline': {
            'bg': '#FFFFFF', 'fg': '#24292F',
            'hover_bg': '#F3F4F6', 'active_bg': '#E5E7EB',
            'border': '#D0D7DE'
        }
    }
    
    def __init__(self, parent, text, command=None, style='primary'):
        self.command = command
        self.style_config = self.STYLES.get(style, self.STYLES['primary'])
        self.default_bg = self.style_config['bg']
        self.hover_bg = self.style_config['hover_bg']
        
        self.label = tk.Label(
            parent, text=text,
            bg=self.default_bg, fg=self.style_config['fg'],
            font=('Segoe UI', 9, 'normal'),
            cursor='hand2', padx=12, pady=7, relief=tk.FLAT
        )
        
        if style == 'outline':
            self.label.config(relief=tk.SOLID, borderwidth=1,
                            highlightthickness=1,
                            highlightbackground=self.style_config['border'])
        
        self.label.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self.label.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.label.config(bg=self.default_bg)
    
    def pack(self, **kwargs):
        return self.label.pack(**kwargs)
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            state = kwargs['state']
            if state == 'disabled':
                self.label.config(cursor='arrow', bg='#E5E7EB', fg='#9CA3AF')
                self.label.unbind('<Button-1>')
            else:
                self.label.config(cursor='hand2', bg=self.default_bg,
                                fg=self.style_config['fg'])
                self.label.bind('<Button-1>', self._on_click)


class SectionCard(tk.Frame):
    """Clean section card with subtle border"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg='#FFFFFF', relief=tk.FLAT,
                        borderwidth=1, highlightthickness=1,
                        highlightbackground='#D0D7DE', **kwargs)
        
        if title:
            title_frame = tk.Frame(self, bg='#F6F8FA', height=32)
            title_frame.pack(fill=tk.X, side=tk.TOP)
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(
                title_frame, text=title,
                bg='#F6F8FA', fg='#24292F',
                font=('Segoe UI', 10, 'bold'),
                anchor='w', padx=16
            )
            title_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.content = tk.Frame(self, bg='#FFFFFF', padx=16, pady=12)
        self.content.pack(fill=tk.BOTH, expand=True)
    
    def get_content(self):
        return self.content


# ============================================================================
# AI CODE GENERATOR TAB
# ============================================================================

class AICodeGeneratorTabV4Clean:
    """AI Code Generator with Clean Professional UI"""
    
    TEMPLATES = {
        'word_count': {
            'name': 'Word Count',
            'desc': 'Count words in text file',
            'icon': '📝',
            'code': '''        # 2. Đọc file text
        input_path = "{input_file}"
        text_rdd = sc.textFile(input_path)
        
        # 3. Word Count
        words = text_rdd.flatMap(lambda line: line.split())
        word_pairs = words.map(lambda word: (word, 1))
        word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
        
        # 4. Sắp xếp và lưu kết quả
        sorted_counts = word_counts.sortBy(lambda x: x[1], ascending=False)
        output_path = "{output_file}"
        sorted_counts.saveAsTextFile(output_path)
        
        print(f"Word count complete! Results saved to {{output_path}}")'''
        },
        'filter_data': {
            'name': 'Filter Data',
            'desc': 'Filter CSV data by condition',
            'icon': '🔍',
            'code': '''        # 2. Đọc CSV file
        input_path = "{input_file}"
        df = spark.read.csv(input_path, header=True, inferSchema=True)
        
        # 3. Filter data
        filtered_df = df.filter(df["{column}"] > {threshold})
        
        # 4. Show và save kết quả
        print("Filtered data:")
        filtered_df.show(20)
        
        output_path = "{output_file}"
        filtered_df.write.csv(output_path, header=True, mode='overwrite')
        
        print(f"Filtered {{filtered_df.count()}} rows saved to {{output_path}}")'''
        },
        'join_tables': {
            'name': 'Join Tables',
            'desc': 'Join two CSV tables',
            'icon': '🔗',
            'code': '''        # 2. Đọc 2 CSV files
        df1 = spark.read.csv("{input_file1}", header=True, inferSchema=True)
        df2 = spark.read.csv("{input_file2}", header=True, inferSchema=True)
        
        # 3. Join tables
        joined_df = df1.join(df2, on="{join_key}", how="{join_type}")
        
        # 4. Show và save kết quả
        print("Joined data:")
        joined_df.show(20)
        
        output_path = "{output_file}"
        joined_df.write.csv(output_path, header=True, mode='overwrite')
        
        print(f"Joined {{joined_df.count()}} rows saved to {{output_path}}")'''
        },
        'aggregate': {
            'name': 'Aggregate Data',
            'desc': 'Group by and aggregate',
            'icon': '📊',
            'code': '''        # 2. Đọc CSV file
        input_path = "{input_file}"
        df = spark.read.csv(input_path, header=True, inferSchema=True)
        
        # 3. Group by và aggregate
        from pyspark.sql import functions as F
        agg_df = df.groupBy("{group_column}").agg(
            F.sum("{agg_column}").alias("total"),
            F.avg("{agg_column}").alias("average"),
            F.count("*").alias("count")
        )
        
        # 4. Sort và save
        sorted_df = agg_df.orderBy(F.desc("total"))
        print("Aggregated data:")
        sorted_df.show(20)
        
        output_path = "{output_file}"
        sorted_df.write.csv(output_path, header=True, mode='overwrite')
        
        print(f"Aggregated results saved to {{output_path}}")'''
        }
    }
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        self.generated_code = ""
        
        self.create_ui()
    
    def create_ui(self):
        """Create V4 Clean Professional UI"""
        # Note: parent_frame is ttk.Frame, can't set bg directly
        
        # Main container with scrollbar
        canvas = tk.Canvas(self.frame, bg='#F6F8FA', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.frame, orient='vertical', command=canvas.yview)
        
        scroll_frame = tk.Frame(canvas, bg='#F6F8FA')
        scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Two column layout - Left 30%, Right 70%
        scroll_frame.grid_columnconfigure(0, weight=30, minsize=400)
        scroll_frame.grid_columnconfigure(1, weight=70)
        scroll_frame.grid_rowconfigure(0, weight=1)
        
        left_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        left_col.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        
        right_col = tk.Frame(scroll_frame, bg='#F6F8FA')
        right_col.grid(row=0, column=1, sticky='nsew', padx=(8, 0))
        
        # ===== LEFT COLUMN =====
        
        # Header
        header = tk.Label(
            left_col, text="🤖 AI Code Generator",
            bg='#F6F8FA', fg='#24292F',
            font=('Segoe UI', 16, 'bold'), anchor='w'
        )
        header.pack(fill=tk.X, pady=(0, 4))
        
        subtitle = tk.Label(
            left_col, text="Generate PySpark code from templates",
            bg='#F6F8FA', fg='#6E7781',
            font=('Segoe UI', 9), anchor='w'
        )
        subtitle.pack(fill=tk.X, pady=(0, 20))
        
        # === Template Selection Card ===
        template_card = SectionCard(left_col, title="📋 Select Template")
        template_card.pack(fill=tk.X, pady=(0, 12))
        
        template_content = template_card.get_content()
        
        self.template_var = tk.StringVar(value='word_count')
        
        for key, template in self.TEMPLATES.items():
            radio = tk.Radiobutton(
                template_content,
                text=f"{template['icon']} {template['name']}",
                variable=self.template_var,
                value=key,
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9),
                activebackground='#FFFFFF',
                selectcolor='#FFFFFF',
                command=self.on_template_select
            )
            radio.pack(anchor='w', pady=4)
            
            desc = tk.Label(
                template_content,
                text=f"   {template['desc']}",
                bg='#FFFFFF', fg='#6E7781',
                font=('Segoe UI', 8), anchor='w'
            )
            desc.pack(anchor='w', padx=(20, 0))
        
        # === Parameters Card ===
        params_card = SectionCard(left_col, title="⚙️ Parameters")
        params_card.pack(fill=tk.X, pady=(0, 12))
        
        params_content = params_card.get_content()
        
        # Job name
        tk.Label(
            params_content, text="Job Name:",
            bg='#FFFFFF', fg='#24292F',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 4))
        
        self.job_name_var = tk.StringVar(value='spark_job')
        tk.Entry(
            params_content,
            textvariable=self.job_name_var,
            font=('Segoe UI', 9),
            relief=tk.SOLID, borderwidth=1
        ).pack(fill=tk.X, pady=(0, 12))
        
        # Input file
        tk.Label(
            params_content, text="Input File:",
            bg='#FFFFFF', fg='#24292F',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 4))
        
        input_frame = tk.Frame(params_content, bg='#FFFFFF')
        input_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.input_file_var = tk.StringVar(value='hdfs://namenode:9000/data/input.csv')
        tk.Entry(
            input_frame,
            textvariable=self.input_file_var,
            font=('Segoe UI', 9),
            relief=tk.SOLID, borderwidth=1
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        
        # Output file
        tk.Label(
            params_content, text="Output Path:",
            bg='#FFFFFF', fg='#24292F',
            font=('Segoe UI', 9, 'bold')
        ).pack(anchor='w', pady=(0, 4))
        
        self.output_file_var = tk.StringVar(value='hdfs://namenode:9000/output')
        tk.Entry(
            params_content,
            textvariable=self.output_file_var,
            font=('Segoe UI', 9),
            relief=tk.SOLID, borderwidth=1
        ).pack(fill=tk.X, pady=(0, 12))
        
        # Template-specific params frame
        self.extra_params_frame = tk.Frame(params_content, bg='#FFFFFF')
        self.extra_params_frame.pack(fill=tk.X)
        
        self.on_template_select()  # Initialize
        
        # === Actions Card ===
        actions_card = SectionCard(left_col, title="🚀 Actions")
        actions_card.pack(fill=tk.X, pady=(0, 12))
        
        actions_content = actions_card.get_content()
        
        CleanButton(actions_content, "⚙ Generate Code", self.generate_code, 'success').pack(
            fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "💾 Save to File", self.save_code, 'primary').pack(
            fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "📋 Copy to Clipboard", self.copy_code, 'secondary').pack(
            fill=tk.X)
        
        # ===== RIGHT COLUMN =====
        
        # Generated Code Card
        code_card = SectionCard(right_col, title="📄 Generated Code")
        code_card.pack(fill=tk.BOTH, expand=True)
        
        code_content = code_card.get_content()
        
        self.code_text = tk.Text(
            code_content,
            wrap=tk.NONE,
            bg='#24292F', fg='#E6EDF3',
            font=('Consolas', 9),
            relief=tk.FLAT, borderwidth=0,
            padx=12, pady=12
        )
        
        # Add scrollbars
        code_scroll_y = tk.Scrollbar(code_content, orient='vertical', 
                                     command=self.code_text.yview)
        code_scroll_x = tk.Scrollbar(code_content, orient='horizontal',
                                     command=self.code_text.xview)
        
        self.code_text.configure(yscrollcommand=code_scroll_y.set,
                                xscrollcommand=code_scroll_x.set)
        
        self.code_text.grid(row=0, column=0, sticky='nsew')
        code_scroll_y.grid(row=0, column=1, sticky='ns')
        code_scroll_x.grid(row=1, column=0, sticky='ew')
        
        code_content.grid_rowconfigure(0, weight=1)
        code_content.grid_columnconfigure(0, weight=1)
        
        # Syntax highlighting tags
        self.code_text.tag_config('keyword', foreground='#FF7B72')
        self.code_text.tag_config('string', foreground='#A5D6FF')
        self.code_text.tag_config('comment', foreground='#8B949E')
        self.code_text.tag_config('function', foreground='#D2A8FF')
        
        # Welcome message
        welcome = """# 🤖 AI Code Generator for PySpark

# 1. Select a template from the left panel
# 2. Configure parameters (job name, input/output paths, etc.)
# 3. Click "Generate Code" to create PySpark script
# 4. Save or copy the generated code

# Available Templates:
# - Word Count: Count words in text files
# - Filter Data: Filter CSV data by conditions
# - Join Tables: Join two CSV tables
# - Aggregate Data: Group by and aggregate

# Select a template to begin!
"""
        self.code_text.insert('1.0', welcome)
    
    def on_template_select(self):
        """Handle template selection"""
        # Clear extra params
        for widget in self.extra_params_frame.winfo_children():
            widget.destroy()
        
        template_key = self.template_var.get()
        
        # Add template-specific parameters
        if template_key == 'filter_data':
            tk.Label(
                self.extra_params_frame, text="Column Name:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.column_var = tk.StringVar(value='value')
            tk.Entry(
                self.extra_params_frame,
                textvariable=self.column_var,
                font=('Segoe UI', 9),
                relief=tk.SOLID, borderwidth=1
            ).pack(fill=tk.X, pady=(0, 8))
            
            tk.Label(
                self.extra_params_frame, text="Threshold:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.threshold_var = tk.StringVar(value='100')
            tk.Entry(
                self.extra_params_frame,
                textvariable=self.threshold_var,
                font=('Segoe UI', 9),
                relief=tk.SOLID, borderwidth=1
            ).pack(fill=tk.X)
        
        elif template_key == 'join_tables':
            tk.Label(
                self.extra_params_frame, text="Second Input File:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.input_file2_var = tk.StringVar(value='hdfs://namenode:9000/data/input2.csv')
            tk.Entry(
                self.extra_params_frame,
                textvariable=self.input_file2_var,
                font=('Segoe UI', 9),
                relief=tk.SOLID, borderwidth=1
            ).pack(fill=tk.X, pady=(0, 8))
            
            tk.Label(
                self.extra_params_frame, text="Join Key:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.join_key_var = tk.StringVar(value='id')
            tk.Entry(
                self.extra_params_frame,
                textvariable=self.join_key_var,
                font=('Segoe UI', 9),
                relief=tk.SOLID, borderwidth=1
            ).pack(fill=tk.X, pady=(0, 8))
            
            tk.Label(
                self.extra_params_frame, text="Join Type:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.join_type_var = tk.StringVar(value='inner')
            ttk.Combobox(
                self.extra_params_frame,
                textvariable=self.join_type_var,
                values=['inner', 'left', 'right', 'outer'],
                state='readonly',
                font=('Segoe UI', 9)
            ).pack(fill=tk.X)
        
        elif template_key == 'aggregate':
            tk.Label(
                self.extra_params_frame, text="Group By Column:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.group_column_var = tk.StringVar(value='category')
            tk.Entry(
                self.extra_params_frame,
                textvariable=self.group_column_var,
                font=('Segoe UI', 9),
                relief=tk.SOLID, borderwidth=1
            ).pack(fill=tk.X, pady=(0, 8))
            
            tk.Label(
                self.extra_params_frame, text="Aggregate Column:",
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold')
            ).pack(anchor='w', pady=(0, 4))
            
            self.agg_column_var = tk.StringVar(value='amount')
            tk.Entry(
                self.extra_params_frame,
                textvariable=self.agg_column_var,
                font=('Segoe UI', 9),
                relief=tk.SOLID, borderwidth=1
            ).pack(fill=tk.X)
    
    def generate_code(self):
        """Generate PySpark code"""
        template_key = self.template_var.get()
        template = self.TEMPLATES[template_key]
        
        # Get parameters
        params = {
            'filename': f"{self.job_name_var.get()}.py",
            'app_name': self.job_name_var.get(),
            'description': template['desc'],
            'input_file': self.input_file_var.get(),
            'output_file': self.output_file_var.get()
        }
        
        # Add template-specific params
        if template_key == 'filter_data':
            params['column'] = self.column_var.get()
            params['threshold'] = self.threshold_var.get()
        elif template_key == 'join_tables':
            params['input_file1'] = self.input_file_var.get()
            params['input_file2'] = self.input_file2_var.get()
            params['join_key'] = self.join_key_var.get()
            params['join_type'] = self.join_type_var.get()
        elif template_key == 'aggregate':
            params['group_column'] = self.group_column_var.get()
            params['agg_column'] = self.agg_column_var.get()
        
        # Generate code
        processing_code = template['code'].format(**params)
        
        base_template = f"""# {params['filename']}
from pyspark.sql import SparkSession

def main():
    \"\"\"
    {params['description']}
    \"\"\"
    # 1. Khởi tạo SparkSession
    spark = SparkSession.builder \\
        .appName("{params['app_name']}") \\
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
        
        self.generated_code = base_template
        
        # Display code
        self.code_text.delete('1.0', tk.END)
        self.code_text.insert('1.0', self.generated_code)
        
        if self.append_log:
            self.append_log(f"✓ Generated {template['name']} code\n")
        
        messagebox.showinfo("Success", f"Generated {template['name']} code successfully!")
    
    def save_code(self):
        """Save generated code to file"""
        if not self.generated_code:
            messagebox.showwarning("No Code", "Please generate code first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension='.py',
            filetypes=[('Python files', '*.py'), ('All files', '*.*')],
            initialfile=f"{self.job_name_var.get()}.py"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.generated_code)
                
                if self.append_log:
                    self.append_log(f"✓ Saved to {filename}\n")
                
                messagebox.showinfo("Success", f"Code saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def copy_code(self):
        """Copy code to clipboard"""
        if not self.generated_code:
            messagebox.showwarning("No Code", "Please generate code first")
            return
        
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.generated_code)
        
        if self.append_log:
            self.append_log("✓ Code copied to clipboard\n")
        
        messagebox.showinfo("Success", "Code copied to clipboard!")
