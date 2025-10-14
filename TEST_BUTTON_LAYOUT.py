#!/usr/bin/env python3
"""
Simple button test - If this works, main GUI should work too
"""
import tkinter as tk
from tkinter import messagebox

def test_copy():
    messagebox.showinfo("Test", "✅ Copy button works!")

def test_save():
    messagebox.showinfo("Test", "✅ Save button works!")

def test_run():
    messagebox.showinfo("Test", "✅ Run button works!")

def test_clear():
    text.delete('1.0', tk.END)
    text.insert('1.0', "Output cleared!")

root = tk.Tk()
root.title("Button Layout Test - AI Engine V8.3")
root.geometry("700x500")

main_frame = tk.Frame(root, bg='#F6F8FA')
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Header
header = tk.Label(
    main_frame,
    text="🔍 Button Visibility Test",
    bg='#24292F',
    fg='white',
    font=('Segoe UI', 14, 'bold'),
    pady=15
)
header.pack(fill=tk.X)

# Output area
output_frame = tk.Frame(main_frame, bg='white')
output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

tk.Label(
    output_frame,
    text="📄 Generated Code:",
    bg='white',
    fg='#24292F',
    font=('Segoe UI', 11, 'bold')
).pack(anchor='w', padx=10, pady=5)

import tkinter.scrolledtext as scrolledtext
text = scrolledtext.ScrolledText(
    output_frame,
    wrap=tk.WORD,
    font=('Consolas', 10),
    bg='#0D1117',
    fg='#C9D1D9',
    height=15
)
text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

text.insert('1.0', """from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Test").getOrCreate()
print("Hello from PySpark!")
spark.stop()

---

Scroll down to see buttons below ↓↓↓
""")

# BUTTONS - Same layout as main GUI
btn_frame = tk.Frame(output_frame, bg='white')
btn_frame.pack(fill=tk.X, padx=10, pady=10)

tk.Button(
    btn_frame,
    text="📋 Copy Code",
    command=test_copy,
    bg='#6E7781',
    fg='white',
    font=('Segoe UI', 9, 'bold'),
    relief=tk.FLAT,
    cursor='hand2',
    padx=15,
    pady=8
).pack(side=tk.LEFT, padx=(0, 5))

tk.Button(
    btn_frame,
    text="💾 Save to File",
    command=test_save,
    bg='#6E7781',
    fg='white',
    font=('Segoe UI', 9, 'bold'),
    relief=tk.FLAT,
    cursor='hand2',
    padx=15,
    pady=8
).pack(side=tk.LEFT, padx=5)

tk.Button(
    btn_frame,
    text="▶️ Run Code",
    command=test_run,
    bg='#0969DA',
    fg='white',
    font=('Segoe UI', 9, 'bold'),
    relief=tk.FLAT,
    cursor='hand2',
    padx=15,
    pady=8
).pack(side=tk.LEFT, padx=5)

tk.Button(
    btn_frame,
    text="🗑️ Clear",
    command=test_clear,
    bg='#CF222E',
    fg='white',
    font=('Segoe UI', 9, 'bold'),
    relief=tk.FLAT,
    cursor='hand2',
    padx=15,
    pady=8
).pack(side=tk.RIGHT)

# Footer
footer = tk.Label(
    main_frame,
    text="✅ If you see 4 buttons above, layout is OK!\nMain GUI should show buttons too.",
    bg='#DDF4FF',
    fg='#0969DA',
    font=('Segoe UI', 9),
    pady=10
)
footer.pack(fill=tk.X)

root.mainloop()
