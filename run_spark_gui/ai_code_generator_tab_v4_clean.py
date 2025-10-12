"""
AI Code Generator Tab - V4.1 Smart Edition
Intelligent PySpark code generation with analysis and recommendations
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
# AI CODE ANALYZER
# ============================================================================

class SmartCodeAnalyzer:
    """Intelligent code analysis and recommendations"""
    
    @staticmethod
    def analyze_requirements(template_type, params):
        """Analyze requirements and provide recommendations"""
        analysis = {
            'warnings': [],
            'suggestions': [],
            'optimizations': [],
            'estimated_time': 'Unknown',
            'complexity': 'Unknown',
            'data_size': 'Unknown'
        }
        
        # Analyze based on template type
        if template_type == 'word_count':
            analysis['complexity'] = 'Low'
            analysis['estimated_time'] = '< 1 minute for small files (< 100MB)'
            
            if 'input_file' in params and params['input_file']:
                if not params['input_file'].endswith('.txt'):
                    analysis['warnings'].append(
                        '⚠️ Input file không phải .txt, có thể cần xử lý encoding'
                    )
            
            analysis['suggestions'].extend([
                '💡 Nên filter empty lines và special characters',
                '💡 Consider using casefold() để case-insensitive counting',
                '💡 Có thể cache RDD nếu file lớn để reuse'
            ])
            
            analysis['optimizations'].extend([
                '🚀 Sử dụng coalesce() để reduce số partitions khi save',
                '🚀 Thêm filter để loại bỏ stopwords (the, a, an, etc.)'
            ])
        
        elif template_type == 'filter_data':
            analysis['complexity'] = 'Medium'
            analysis['estimated_time'] = '1-5 minutes depending on data size'
            
            if 'column' in params and 'threshold' in params:
                try:
                    threshold = float(params['threshold'])
                    if threshold > 1000000:
                        analysis['warnings'].append(
                            '⚠️ Threshold rất cao, có thể filter quá nhiều data'
                        )
                except ValueError:
                    analysis['warnings'].append(
                        '❌ Threshold không phải là số hợp lệ'
                    )
            
            analysis['suggestions'].extend([
                '💡 Nên check schema trước để đảm bảo column tồn tại',
                '💡 Có thể add multiple conditions với AND/OR',
                '💡 Consider adding null value handling'
            ])
            
            analysis['optimizations'].extend([
                '🚀 Sử dụng broadcast join nếu có lookup table nhỏ',
                '🚀 Partition data theo column được filter để tăng tốc',
                '🚀 Cache DataFrame nếu sẽ filter nhiều lần'
            ])
        
        elif template_type == 'join_tables':
            analysis['complexity'] = 'High'
            analysis['estimated_time'] = '5-30 minutes for large datasets'
            
            if 'join_type' in params:
                join_type = params['join_type']
                if join_type in ['left', 'right', 'outer']:
                    analysis['warnings'].append(
                        f'⚠️ {join_type.upper()} JOIN có thể tạo nhiều null values'
                    )
            
            analysis['suggestions'].extend([
                '💡 Kiểm tra duplicate keys trước khi join',
                '💡 Verify data types của join key columns',
                '💡 Monitor memory usage cho large joins'
            ])
            
            analysis['optimizations'].extend([
                '🚀 Sử dụng broadcast join nếu 1 table < 10MB',
                '🚀 Repartition by join key trước khi join',
                '🚀 Consider salting cho skewed keys',
                '🚀 Use bucketing nếu join thường xuyên'
            ])
        
        elif template_type == 'aggregate':
            analysis['complexity'] = 'Medium-High'
            analysis['estimated_time'] = '2-10 minutes depending on groups'
            
            analysis['suggestions'].extend([
                '💡 Check cardinality của group column',
                '💡 Validate aggregate column có đúng numeric type',
                '💡 Consider adding HAVING clause để filter groups'
            ])
            
            analysis['optimizations'].extend([
                '🚀 Pre-filter data trước khi aggregate',
                '🚀 Sử dụng approx_count_distinct() nếu không cần chính xác',
                '🚀 Partition by group column để tăng parallelism',
                '🚀 Cache result nếu sẽ aggregate nhiều lần'
            ])
        
        return analysis
    
    @staticmethod
    def validate_parameters(template_type, params):
        """Validate input parameters"""
        errors = []
        
        # Common validations
        if not params.get('job_name'):
            errors.append('❌ Job name không được để trống')
        elif not re.match(r'^[a-zA-Z0-9_]+$', params['job_name']):
            errors.append('❌ Job name chỉ được chứa chữ, số và underscore')
        
        if not params.get('input_file'):
            errors.append('❌ Input file không được để trống')
        elif not params['input_file'].startswith(('hdfs://', '/', 's3://')):
            errors.append('⚠️ Input file nên bắt đầu với hdfs:// hoặc /')
        
        if not params.get('output_file'):
            errors.append('❌ Output path không được để trống')
        elif not params['output_file'].startswith(('hdfs://', '/', 's3://')):
            errors.append('⚠️ Output path nên bắt đầu với hdfs:// hoặc /')
        
        # Template-specific validations
        if template_type == 'filter_data':
            if not params.get('column'):
                errors.append('❌ Column name không được để trống')
            
            if not params.get('threshold'):
                errors.append('❌ Threshold không được để trống')
            else:
                try:
                    float(params['threshold'])
                except ValueError:
                    errors.append('❌ Threshold phải là số')
        
        elif template_type == 'join_tables':
            if not params.get('input_file2'):
                errors.append('❌ Second input file không được để trống')
            
            if not params.get('join_key'):
                errors.append('❌ Join key không được để trống')
        
        elif template_type == 'aggregate':
            if not params.get('group_column'):
                errors.append('❌ Group by column không được để trống')
            
            if not params.get('agg_column'):
                errors.append('❌ Aggregate column không được để trống')
        
        return errors
    
    @staticmethod
    def generate_explanation(template_type, params):
        """Generate code explanation"""
        explanations = {
            'word_count': f"""
📝 WORD COUNT ANALYSIS

🎯 Mục đích: Đếm số lần xuất hiện của mỗi từ trong file text

📊 Quy trình xử lý:
1. Đọc file text từ: {params.get('input_file', 'N/A')}
2. Split mỗi dòng thành các từ riêng biệt
3. Map mỗi từ thành tuple (word, 1)
4. Reduce by key để cộng dồn số lần xuất hiện
5. Sort theo frequency (descending)
6. Save kết quả vào: {params.get('output_file', 'N/A')}

⚡ Performance:
- RDD-based operation (lazy evaluation)
- Parallel processing trên cluster
- Memory efficient với mapReduce pattern

🔧 Có thể mở rộng:
- Filter stopwords (a, the, is, etc.)
- Normalize text (lowercase, remove punctuation)
- N-gram analysis (bigrams, trigrams)
""",
            'filter_data': f"""
🔍 DATA FILTERING ANALYSIS

🎯 Mục đích: Lọc rows từ CSV theo điều kiện

📊 Quy trình xử lý:
1. Đọc CSV file từ: {params.get('input_file', 'N/A')}
2. Infer schema tự động (hoặc define explicit)
3. Filter rows where {params.get('column', 'N/A')} > {params.get('threshold', 'N/A')}
4. Show preview (20 rows)
5. Write filtered data to: {params.get('output_file', 'N/A')}

⚡ Performance:
- DataFrame API (optimized với Catalyst optimizer)
- Predicate pushdown optimization
- Column pruning tự động

🔧 Có thể mở rộng:
- Multiple conditions (AND/OR/NOT)
- Range filters (BETWEEN)
- Pattern matching (LIKE, REGEXP)
- Null handling
""",
            'join_tables': f"""
🔗 TABLE JOIN ANALYSIS

🎯 Mục đích: Kết hợp 2 tables theo join key

📊 Quy trình xử lý:
1. Đọc table 1 từ: {params.get('input_file', 'N/A')}
2. Đọc table 2 từ: {params.get('input_file2', 'N/A')}
3. Join type: {params.get('join_type', 'inner').upper()}
4. Join key: {params.get('join_key', 'N/A')}
5. Show preview joined data
6. Save result to: {params.get('output_file', 'N/A')}

⚡ Performance:
- Join type affects performance significantly
- Broadcast join for small tables (< 10MB)
- Sort-merge join for large-large joins
- Hash join cho equal joins

🔧 Có thể mở rộng:
- Multiple join keys
- Complex join conditions
- Join with aggregation
- Self joins
""",
            'aggregate': f"""
📊 DATA AGGREGATION ANALYSIS

🎯 Mục đích: Group by và tính toán metrics

📊 Quy trình xử lý:
1. Đọc CSV từ: {params.get('input_file', 'N/A')}
2. Group by column: {params.get('group_column', 'N/A')}
3. Aggregate column: {params.get('agg_column', 'N/A')}
4. Tính: SUM, AVG, COUNT
5. Sort by total (descending)
6. Save results to: {params.get('output_file', 'N/A')}

⚡ Performance:
- Hash aggregation cho low cardinality
- Sort-based aggregation cho high cardinality
- Partial aggregation on each partition
- Final aggregation on reduced data

🔧 Có thể mở rộng:
- Multiple grouping columns
- Custom aggregation functions (UDF)
- Window functions
- CUBE/ROLLUP operations
"""
        }
        
        return explanations.get(template_type, 'No explanation available')


# ============================================================================
# SMART CODE TEMPLATES
# ============================================================================

class SmartTemplates:
    """Enhanced templates with error handling and optimizations"""
    
    TEMPLATES = {
        'word_count': {
            'name': 'Word Count',
            'desc': 'Count words in text file with optimization',
            'icon': '📝',
            'difficulty': 'Beginner',
            'code': '''        # 2. Đọc file text với error handling
        input_path = "{input_file}"
        try:
            text_rdd = sc.textFile(input_path)
            print(f"✓ Loaded text file: {{input_path}}")
            
            # 3. Word Count với preprocessing
            # Lowercase, remove punctuation, filter empty
            words = text_rdd.flatMap(lambda line: line.lower().split()) \\
                           .filter(lambda word: len(word) > 0) \\
                           .map(lambda word: re.sub(r'[^a-zA-Z0-9]', '', word)) \\
                           .filter(lambda word: len(word) > 0)
            
            word_pairs = words.map(lambda word: (word, 1))
            word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
            
            # 4. Sắp xếp và optimize output
            sorted_counts = word_counts.sortBy(lambda x: x[1], ascending=False)
            
            # Coalesce để reduce số output files
            sorted_counts = sorted_counts.coalesce(1)
            
            output_path = "{output_file}"
            sorted_counts.saveAsTextFile(output_path)
            
            # Statistics
            total_words = word_counts.map(lambda x: x[1]).reduce(lambda a, b: a + b)
            unique_words = word_counts.count()
            
            print(f"✓ Word count complete!")
            print(f"  Total words: {{total_words:,}}")
            print(f"  Unique words: {{unique_words:,}}")
            print(f"  Results saved to: {{output_path}}")
            
        except Exception as e:
            print(f"✗ Error in word count: {{str(e)}}")
            raise'''
        },
        'filter_data': {
            'name': 'Filter Data',
            'desc': 'Filter CSV data with validation',
            'icon': '🔍',
            'difficulty': 'Intermediate',
            'code': '''        # 2. Đọc CSV file với error handling
        input_path = "{input_file}"
        try:
            df = spark.read.csv(input_path, header=True, inferSchema=True)
            print(f"✓ Loaded CSV: {{input_path}}")
            print(f"  Rows: {{df.count():,}}, Columns: {{len(df.columns)}}")
            
            # Validate column exists
            if "{column}" not in df.columns:
                raise ValueError(f"Column '{{column}}' not found. Available: {{df.columns}}")
            
            # Show schema
            print("\\nSchema:")
            df.printSchema()
            
            # 3. Filter data với null handling
            from pyspark.sql import functions as F
            
            # Remove nulls trước khi filter
            filtered_df = df.filter(F.col("{column}").isNotNull())
            filtered_df = filtered_df.filter(F.col("{column}") > {threshold})
            
            filtered_count = filtered_df.count()
            original_count = df.count()
            
            print(f"\\n✓ Filtered data:")
            print(f"  Original rows: {{original_count:,}}")
            print(f"  Filtered rows: {{filtered_count:,}}")
            print(f"  Removed: {{original_count - filtered_count:,}} ({{((original_count - filtered_count) / original_count * 100):.1f}}%)")
            
            # 4. Show preview và save
            print("\\nPreview (top 20 rows):")
            filtered_df.show(20)
            
            output_path = "{output_file}"
            filtered_df.write.csv(output_path, header=True, mode='overwrite')
            
            print(f"\\n✓ Results saved to: {{output_path}}")
            
        except Exception as e:
            print(f"✗ Error in filtering: {{str(e)}}")
            raise'''
        },
        'join_tables': {
            'name': 'Join Tables',
            'desc': 'Join two CSV tables with optimization',
            'icon': '🔗',
            'difficulty': 'Advanced',
            'code': '''        # 2. Đọc 2 CSV files với validation
        try:
            df1 = spark.read.csv("{input_file1}", header=True, inferSchema=True)
            print(f"✓ Loaded table 1: {{df1.count():,}} rows, {{len(df1.columns)}} columns")
            
            df2 = spark.read.csv("{input_file2}", header=True, inferSchema=True)
            print(f"✓ Loaded table 2: {{df2.count():,}} rows, {{len(df2.columns)}} columns")
            
            # Validate join key exists
            if "{join_key}" not in df1.columns:
                raise ValueError(f"Join key '{{join_key}}' not in table 1")
            if "{join_key}" not in df2.columns:
                raise ValueError(f"Join key '{{join_key}}' not in table 2")
            
            # Check for duplicates in join key
            df1_distinct = df1.select("{join_key}").distinct().count()
            df2_distinct = df2.select("{join_key}").distinct().count()
            
            print(f"\\nJoin key analysis:")
            print(f"  Table 1 distinct keys: {{df1_distinct:,}}")
            print(f"  Table 2 distinct keys: {{df2_distinct:,}}")
            
            # 3. Optimize join strategy
            from pyspark.sql import functions as F
            
            # Broadcast smaller table if < 10MB
            df1_size = df1.count()
            df2_size = df2.count()
            
            if df2_size < 100000:  # Broadcast if small
                from pyspark.sql.functions import broadcast
                print("  Using broadcast join (small table optimization)")
                joined_df = df1.join(broadcast(df2), on="{join_key}", how="{join_type}")
            else:
                print("  Using sort-merge join")
                joined_df = df1.join(df2, on="{join_key}", how="{join_type}")
            
            # 4. Analyze results
            joined_count = joined_df.count()
            
            print(f"\\n✓ Join complete:")
            print(f"  Join type: {{join_type.upper()}}")
            print(f"  Result rows: {{joined_count:,}}")
            
            # Show preview
            print("\\nPreview (top 20 rows):")
            joined_df.show(20)
            
            output_path = "{output_file}"
            joined_df.write.csv(output_path, header=True, mode='overwrite')
            
            print(f"\\n✓ Results saved to: {{output_path}}")
            
        except Exception as e:
            print(f"✗ Error in join: {{str(e)}}")
            raise'''
        },
        'aggregate': {
            'name': 'Aggregate Data',
            'desc': 'Group by and aggregate with statistics',
            'icon': '📊',
            'difficulty': 'Intermediate',
            'code': '''        # 2. Đọc CSV với validation
        input_path = "{input_file}"
        try:
            df = spark.read.csv(input_path, header=True, inferSchema=True)
            print(f"✓ Loaded CSV: {{df.count():,}} rows")
            
            # Validate columns exist
            if "{group_column}" not in df.columns:
                raise ValueError(f"Group column '{{group_column}}' not found")
            if "{agg_column}" not in df.columns:
                raise ValueError(f"Aggregate column '{{agg_column}}' not found")
            
            # 3. Pre-analysis
            from pyspark.sql import functions as F
            
            # Check cardinality
            cardinality = df.select("{group_column}").distinct().count()
            print(f"  Group cardinality: {{cardinality:,}} distinct values")
            
            # Check nulls
            null_count = df.filter(F.col("{agg_column}").isNull()).count()
            if null_count > 0:
                print(f"  Warning: {{null_count:,}} null values in aggregate column")
            
            # 4. Aggregate với comprehensive metrics
            agg_df = df.groupBy("{group_column}").agg(
                F.sum("{agg_column}").alias("total"),
                F.avg("{agg_column}").alias("average"),
                F.min("{agg_column}").alias("min"),
                F.max("{agg_column}").alias("max"),
                F.stddev("{agg_column}").alias("stddev"),
                F.count("*").alias("count")
            )
            
            # Round numeric columns
            agg_df = agg_df.withColumn("average", F.round("average", 2))
            agg_df = agg_df.withColumn("stddev", F.round("stddev", 2))
            
            # 5. Sort và analyze
            sorted_df = agg_df.orderBy(F.desc("total"))
            
            print(f"\\n✓ Aggregation complete:")
            print(f"  Groups: {{agg_df.count():,}}")
            
            print("\\nTop 20 groups by total:")
            sorted_df.show(20)
            
            # Statistics
            print("\\nOverall statistics:")
            sorted_df.select(
                F.sum("total").alias("grand_total"),
                F.avg("average").alias("overall_avg"),
                F.max("max").alias("max_value"),
                F.min("min").alias("min_value")
            ).show()
            
            output_path = "{output_file}"
            sorted_df.write.csv(output_path, header=True, mode='overwrite')
            
            print(f"\\n✓ Results saved to: {{output_path}}")
            
        except Exception as e:
            print(f"✗ Error in aggregation: {{str(e)}}")
            raise'''
        }
    }


# ============================================================================
# SMART AI CODE GENERATOR TAB
# ============================================================================

class AICodeGeneratorTabV4Clean:
    """Smart AI Code Generator with analysis and recommendations"""
    
    def __init__(self, parent_frame, config, status_callback, log_callback):
        self.frame = parent_frame
        self.config = config
        self.update_status = status_callback
        self.append_log = log_callback
        self.generated_code = ""
        self.current_analysis = None
        
        self.analyzer = SmartCodeAnalyzer()
        self.templates = SmartTemplates()
        
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
            left_col, text="🤖 Smart AI Generator",
            bg='#F6F8FA', fg='#24292F',
            font=('Segoe UI', 16, 'bold'), anchor='w'
        )
        header.pack(fill=tk.X, pady=(0, 4))
        
        subtitle = tk.Label(
            left_col, text="Intelligent PySpark code generation",
            bg='#F6F8FA', fg='#6E7781',
            font=('Segoe UI', 9), anchor='w'
        )
        subtitle.pack(fill=tk.X, pady=(0, 20))
        
        self.create_left_panel(left_col)
        
        # ===== RIGHT COLUMN =====
        self.create_right_panel(right_col)
    
    def create_left_panel(self, parent):
        """Create left control panel"""
        
        # === Template Selection Card ===
        template_card = SectionCard(parent, title="📋 Select Template")
        template_card.pack(fill=tk.X, pady=(0, 12))
        
        template_content = template_card.get_content()
        
        self.template_var = tk.StringVar(value='word_count')
        
        for key, template in self.templates.TEMPLATES.items():
            # Radio button frame
            radio_frame = tk.Frame(template_content, bg='#FFFFFF')
            radio_frame.pack(fill=tk.X, pady=4)
            
            radio = tk.Radiobutton(
                radio_frame,
                text=f"{template['icon']} {template['name']}",
                variable=self.template_var,
                value=key,
                bg='#FFFFFF', fg='#24292F',
                font=('Segoe UI', 9, 'bold'),
                activebackground='#FFFFFF',
                selectcolor='#FFFFFF',
                command=self.on_template_select
            )
            radio.pack(side=tk.LEFT, anchor='w')
            
            # Difficulty badge
            difficulty_colors = {
                'Beginner': ('#DDF4E6', '#1A7F37'),
                'Intermediate': ('#DDF4FF', '#0969DA'),
                'Advanced': ('#FFE4E6', '#CF222E')
            }
            
            difficulty = template.get('difficulty', 'Intermediate')
            bg_color, fg_color = difficulty_colors.get(difficulty, ('#F6F8FA', '#6E7781'))
            
            diff_label = tk.Label(
                radio_frame,
                text=difficulty,
                bg=bg_color, fg=fg_color,
                font=('Segoe UI', 7),
                padx=6, pady=2
            )
            diff_label.pack(side=tk.LEFT, padx=(8, 0))
            
            # Description
            desc = tk.Label(
                template_content,
                text=f"   {template['desc']}",
                bg='#FFFFFF', fg='#6E7781',
                font=('Segoe UI', 8), anchor='w'
            )
            desc.pack(anchor='w', padx=(20, 0))
        
        # === Parameters Card ===
        params_card = SectionCard(parent, title="⚙️ Parameters")
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
        
        self.input_file_var = tk.StringVar(value='hdfs://namenode:9000/data/input.csv')
        tk.Entry(
            params_content,
            textvariable=self.input_file_var,
            font=('Segoe UI', 9),
            relief=tk.SOLID, borderwidth=1
        ).pack(fill=tk.X, pady=(0, 12))
        
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
        actions_card = SectionCard(parent, title="🚀 Actions")
        actions_card.pack(fill=tk.X, pady=(0, 12))
        
        actions_content = actions_card.get_content()
        
        CleanButton(actions_content, "🔍 Analyze Requirements", 
                   self.analyze_requirements, 'primary').pack(fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "⚙ Generate Code", 
                   self.generate_code, 'success').pack(fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "💾 Save to File", 
                   self.save_code, 'secondary').pack(fill=tk.X, pady=(0, 8))
        CleanButton(actions_content, "📋 Copy Code", 
                   self.copy_code, 'secondary').pack(fill=tk.X)
    
    def create_right_panel(self, parent):
        """Create right display panel"""
        
        # Analysis Results Card
        analysis_card = SectionCard(parent, title="📊 Analysis & Recommendations")
        analysis_card.pack(fill=tk.X, pady=(0, 12))
        
        analysis_content = analysis_card.get_content()
        
        self.analysis_text = tk.Text(
            analysis_content,
            height=12,
            wrap=tk.WORD,
            bg='#F6F8FA', fg='#24292F',
            font=('Segoe UI', 9),
            relief=tk.FLAT, borderwidth=0,
            padx=12, pady=12
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # Color tags for analysis
        self.analysis_text.tag_config('header', foreground='#0969DA', font=('Segoe UI', 10, 'bold'))
        self.analysis_text.tag_config('warning', foreground='#9A6700')
        self.analysis_text.tag_config('error', foreground='#CF222E')
        self.analysis_text.tag_config('success', foreground='#1A7F37')
        self.analysis_text.tag_config('info', foreground='#6E7781')
        
        self.show_welcome_analysis()
        
        # Generated Code Card
        code_card = SectionCard(parent, title="📄 Generated Code")
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
        
        self.show_welcome_code()
    
    def show_welcome_analysis(self):
        """Show welcome message in analysis panel"""
        welcome = """🤖 Smart AI Code Generator - Ready!

📋 Steps to generate intelligent code:

1️⃣ Select a template from the options
2️⃣ Configure parameters (job name, paths, etc.)
3️⃣ Click "Analyze Requirements" to get:
   • Validation errors/warnings
   • Performance recommendations
   • Optimization suggestions
   • Complexity analysis
4️⃣ Review analysis results
5️⃣ Click "Generate Code" to create optimized PySpark script
6️⃣ Review explanation and generated code
7️⃣ Save or copy the code

💡 All generated code includes:
• Error handling
• Input validation
• Performance optimizations
• Detailed logging
• Statistics output
"""
        self.analysis_text.insert('1.0', welcome)
    
    def show_welcome_code(self):
        """Show welcome message in code panel"""
        welcome = """# 🤖 Smart AI Code Generator for PySpark

# Enhanced features in V4.1:
# ✓ Intelligent analysis before generation
# ✓ Validation warnings and errors
# ✓ Performance recommendations
# ✓ Optimization suggestions
# ✓ Error handling in generated code
# ✓ Detailed statistics and logging
# ✓ Code explanation

# Available Templates:
# 📝 Word Count (Beginner) - Count words with preprocessing
# 🔍 Filter Data (Intermediate) - Filter with null handling
# 🔗 Join Tables (Advanced) - Optimized joins with broadcast
# 📊 Aggregate (Intermediate) - Comprehensive aggregation

# Click "Analyze Requirements" to begin!
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
        
        # Clear analysis
        self.current_analysis = None
    
    def get_current_params(self):
        """Get current parameter values"""
        template_key = self.template_var.get()
        
        params = {
            'job_name': self.job_name_var.get(),
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
        
        return params
    
    def analyze_requirements(self):
        """Analyze requirements and show recommendations"""
        template_key = self.template_var.get()
        template = self.templates.TEMPLATES[template_key]
        params = self.get_current_params()
        
        # Clear analysis text
        self.analysis_text.delete('1.0', tk.END)
        
        # Show header
        self.analysis_text.insert(tk.END, f"🔍 ANALYZING: {template['name']}\n\n", 'header')
        
        # 1. Validate parameters
        self.analysis_text.insert(tk.END, "1️⃣ PARAMETER VALIDATION\n", 'header')
        
        errors = self.analyzer.validate_parameters(template_key, params)
        
        if errors:
            self.analysis_text.insert(tk.END, "\n⚠️ Issues found:\n", 'warning')
            for error in errors:
                self.analysis_text.insert(tk.END, f"  {error}\n", 
                                        'error' if error.startswith('❌') else 'warning')
        else:
            self.analysis_text.insert(tk.END, "\n✓ All parameters valid!\n", 'success')
        
        # 2. Analyze requirements
        self.analysis_text.insert(tk.END, "\n\n2️⃣ REQUIREMENTS ANALYSIS\n", 'header')
        
        analysis = self.analyzer.analyze_requirements(template_key, params)
        self.current_analysis = analysis
        
        self.analysis_text.insert(tk.END, f"\n📊 Complexity: {analysis['complexity']}\n", 'info')
        self.analysis_text.insert(tk.END, f"⏱️ Estimated Time: {analysis['estimated_time']}\n\n", 'info')
        
        # 3. Warnings
        if analysis['warnings']:
            self.analysis_text.insert(tk.END, "⚠️ WARNINGS:\n", 'warning')
            for warning in analysis['warnings']:
                self.analysis_text.insert(tk.END, f"  {warning}\n", 'warning')
        
        # 4. Suggestions
        if analysis['suggestions']:
            self.analysis_text.insert(tk.END, "\n\n3️⃣ SUGGESTIONS\n", 'header')
            for suggestion in analysis['suggestions']:
                self.analysis_text.insert(tk.END, f"  {suggestion}\n", 'info')
        
        # 5. Optimizations
        if analysis['optimizations']:
            self.analysis_text.insert(tk.END, "\n\n4️⃣ OPTIMIZATIONS\n", 'header')
            for opt in analysis['optimizations']:
                self.analysis_text.insert(tk.END, f"  {opt}\n", 'success')
        
        # 6. Next steps
        self.analysis_text.insert(tk.END, "\n\n✅ NEXT STEPS\n", 'header')
        
        if errors:
            self.analysis_text.insert(tk.END, "\n⚠️ Please fix validation errors before generating code.\n", 'warning')
        else:
            self.analysis_text.insert(tk.END, "\n✓ Ready to generate code!\n", 'success')
            self.analysis_text.insert(tk.END, "  Click 'Generate Code' to create optimized PySpark script.\n", 'info')
        
        if self.append_log:
            self.append_log(f"✓ Analysis complete for {template['name']}\n")
    
    def generate_code(self):
        """Generate PySpark code with validation"""
        template_key = self.template_var.get()
        template = self.templates.TEMPLATES[template_key]
        params = self.get_current_params()
        
        # Validate first
        errors = self.analyzer.validate_parameters(template_key, params)
        
        if errors:
            error_msg = "Validation errors found:\n\n" + "\n".join(errors)
            error_msg += "\n\nClick 'Analyze Requirements' to see details."
            messagebox.showerror("Validation Error", error_msg)
            return
        
        # Generate code
        params['filename'] = f"{params['job_name']}.py"
        params['app_name'] = params['job_name']
        params['description'] = template['desc']
        
        processing_code = template['code'].format(**params)
        
        base_template = f"""# {params['filename']}
# Generated by Smart AI Code Generator V4.1
# Template: {template['name']} ({template['difficulty']})
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

from pyspark.sql import SparkSession
import re

def main():
    \"\"\"
    {params['description']}
    
    Parameters:
    - Input: {params['input_file']}
    - Output: {params['output_file']}
    \"\"\"
    
    print("=" * 60)
    print(f"🚀 Starting {params['app_name']}")
    print("=" * 60)
    
    # 1. Khởi tạo SparkSession
    spark = SparkSession.builder \\
        .appName("{params['app_name']}") \\
        .getOrCreate()

    # Lấy SparkContext từ SparkSession
    sc = spark.sparkContext
    
    print(f"✓ Spark version: {{spark.version}}")
    print(f"✓ Master: {{sc.master}}")

    try:
{processing_code}
        
        print("\\n" + "=" * 60)
        print("✓ Job completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\\n" + "=" * 60)
        print(f"✗ Job failed with error:")
        print(f"  {{type(e).__name__}}: {{str(e)}}")
        print("=" * 60)
        raise

    finally:
        # Dừng SparkSession để giải phóng tài nguyên
        spark.stop()
        print("\\n✓ Spark session stopped")

if __name__ == "__main__":
    main()
"""
        
        self.generated_code = base_template
        
        # Display code
        self.code_text.delete('1.0', tk.END)
        self.code_text.insert('1.0', self.generated_code)
        
        # Show explanation in analysis panel
        self.analysis_text.delete('1.0', tk.END)
        
        explanation = self.analyzer.generate_explanation(template_key, params)
        self.analysis_text.insert(tk.END, explanation)
        
        if self.append_log:
            self.append_log(f"✓ Generated {template['name']} code ({len(self.generated_code)} chars)\n")
        
        messagebox.showinfo("Success", 
                          f"✓ Generated optimized {template['name']} code!\n\n"
                          f"Lines: {len(self.generated_code.splitlines())}\n"
                          f"Features: Error handling, validation, statistics\n\n"
                          f"Review the code and explanation, then save or copy.")
    
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
