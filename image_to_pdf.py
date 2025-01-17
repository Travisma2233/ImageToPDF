import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
from reportlab.pdfgen import canvas
import os
import webbrowser
import sys

class ImageToPdfConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("图片转PDF工具 / Image to PDF Converter")
        self.root.geometry("800x600")
        
        # 设置程序图标
        try:
            # 获取图标路径（处理打包后的路径）
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(application_path, 'app_icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception:
            pass  # 如果找不到图标文件，就使用默认图标
        
        # 设置主题色
        self.colors = {
            'primary': '#2196F3',  # 蓝色
            'secondary': '#757575',  # 灰色
            'background': '#F5F5F5',  # 浅灰色背景
            'text': '#212121',  # 深灰色文字
            'success': '#4CAF50',  # 绿色
            'warning': '#FFC107'  # 黄色
        }
        
        # 配置根窗口
        self.root.configure(bg=self.colors['background'])
        self.style = ttk.Style()
        self.style.configure('Custom.TFrame', background=self.colors['background'])
        self.style.configure('Custom.TButton', 
                           padding=10, 
                           font=('Arial', 10))
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'),
                           background=self.colors['background'],
                           foreground=self.colors['primary'])
        self.style.configure('Status.TLabel',
                           font=('Arial', 10),
                           background=self.colors['background'],
                           foreground=self.colors['secondary'])
        
        # 存储选择的图片路径
        self.image_files = []
        
        # 语言设置
        self.current_language = 'cn'  # 默认中文
        self.texts = {
            'cn': {
                'title': '图片转PDF工具',
                'select': '选择图片',
                'clear': '清空列表',
                'convert': '转换为PDF',
                'delete': '删除选中',
                'warning': '警告',
                'success': '成功',
                'error': '错误',
                'no_images': '请先选择图片文件！',
                'completed': '转换完成！',
                'created': 'PDF文件已成功创建！',
                'files_selected': '已选择 {} 个文件',
                'list_cleared': '文件列表已清空',
                'processing': '正在处理第 {}/{} 张图片...',
                'convert_failed': '转换失败',
                'switch_lang': '切换为英文',
                'file_list': '文件列表'
            },
            'en': {
                'title': 'Image to PDF Converter',
                'select': 'Select Images',
                'clear': 'Clear List',
                'convert': 'Convert to PDF',
                'delete': 'Delete Selected',
                'warning': 'Warning',
                'success': 'Success',
                'error': 'Error',
                'no_images': 'Please select image files first!',
                'completed': 'Conversion completed!',
                'created': 'PDF file has been created successfully!',
                'files_selected': '{} files selected',
                'list_cleared': 'File list cleared',
                'processing': 'Processing image {}/{}...',
                'convert_failed': 'Conversion failed',
                'switch_lang': 'Switch to Chinese',
                'file_list': 'File List'
            }
        }
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, style='Custom.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, 
                              text=self.texts[self.current_language]['title'],
                              style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 顶部按钮框架
        button_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮样式
        for btn in ['select', 'delete', 'clear', 'switch_lang']:
            btn_style = f'{btn}.TButton'
            self.style.configure(btn_style, 
                               background=self.colors['primary'],
                               font=('Arial', 10))
        
        # 选择文件按钮
        self.select_btn = ttk.Button(button_frame, 
                                   text=self.texts[self.current_language]['select'],
                                   command=self.select_images,
                                   style='select.TButton')
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # 删除选中按钮
        self.delete_btn = ttk.Button(button_frame,
                                   text=self.texts[self.current_language]['delete'],
                                   command=self.delete_selected,
                                   style='delete.TButton')
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空列表按钮
        self.clear_btn = ttk.Button(button_frame,
                                  text=self.texts[self.current_language]['clear'],
                                  command=self.clear_list,
                                  style='clear.TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 语言切换按钮
        self.lang_btn = ttk.Button(button_frame,
                                 text=self.texts[self.current_language]['switch_lang'],
                                 command=self.switch_language,
                                 style='switch_lang.TButton')
        self.lang_btn.pack(side=tk.RIGHT, padx=5)
        
        # 文件列表框架
        list_frame = ttk.LabelFrame(main_frame, 
                                  text=self.texts[self.current_language]['file_list'],
                                  style='Custom.TLabelframe',
                                  padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建列表框来显示选择的文件
        self.file_listbox = tk.Listbox(list_frame,
                                     width=70,
                                     height=15,
                                     font=('Arial', 10),
                                     selectmode=tk.EXTENDED,
                                     bg='white',
                                     fg=self.colors['text'])
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 转换按钮
        self.convert_btn = ttk.Button(main_frame,
                                    text=self.texts[self.current_language]['convert'],
                                    command=self.convert_to_pdf,
                                    style='Custom.TButton')
        self.convert_btn.pack(pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame,
                                    text="",
                                    style='Status.TLabel')
        self.status_label.pack(pady=5)
        
        # 水印标签
        self.watermark = tk.Label(main_frame,
                                text="Created by Travis Ma",
                                fg=self.colors['primary'],
                                bg=self.colors['background'],
                                cursor="hand2",
                                font=('Arial', 9))
        self.watermark.pack(pady=5)
        self.watermark.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Travisma2233"))
        
        # 绑定键盘删除键
        self.file_listbox.bind('<Delete>', lambda e: self.delete_selected())

    def switch_language(self):
        # 切换语言
        self.current_language = 'en' if self.current_language == 'cn' else 'cn'
        
        # 更新所有文本
        self.root.title(self.texts[self.current_language]['title'])
        self.select_btn.configure(text=self.texts[self.current_language]['select'])
        self.delete_btn.configure(text=self.texts[self.current_language]['delete'])
        self.clear_btn.configure(text=self.texts[self.current_language]['clear'])
        self.convert_btn.configure(text=self.texts[self.current_language]['convert'])
        self.lang_btn.configure(text=self.texts[self.current_language]['switch_lang'])
        
    def delete_selected(self):
        # 获取选中的索引
        selected = self.file_listbox.curselection()
        if not selected:
            return
            
        # 从后向前删除（避免索引变化）
        for index in reversed(selected):
            del self.image_files[index]
            self.file_listbox.delete(index)
            
        self.update_status(self.texts[self.current_language]['files_selected'].format(len(self.image_files)))
        
    def select_images(self):
        # 打开文件选择对话框
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        
        # 添加选择的文件到列表
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        
        self.update_status(self.texts[self.current_language]['files_selected'].format(len(self.image_files)))
    
    def clear_list(self):
        self.image_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_status(self.texts[self.current_language]['list_cleared'])
    
    def update_status(self, message):
        self.status_label.configure(text=message)
    
    def convert_to_pdf(self):
        if not self.image_files:
            messagebox.showwarning(
                self.texts[self.current_language]['warning'],
                self.texts[self.current_language]['no_images']
            )
            return
        
        # 选择保存路径
        output_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")],
            title="保存PDF文件"
        )
        
        if not output_pdf:
            return
        
        try:
            # 获取第一张图片来确定PDF的大小
            first_image = Image.open(self.image_files[0])
            pdf_width, pdf_height = first_image.size
            
            # 创建PDF文件
            c = canvas.Canvas(output_pdf, pagesize=(pdf_width, pdf_height))
            
            # 处理每张图片
            total_images = len(self.image_files)
            for i, image_path in enumerate(self.image_files, 1):
                # 更新状态
                self.update_status(
                    self.texts[self.current_language]['processing'].format(i, total_images)
                )
                self.root.update()
                
                # 将图片绘制到PDF页面上
                c.drawImage(image_path, 0, 0, pdf_width, pdf_height)
                c.showPage()
            
            # 保存PDF文件
            c.save()
            
            self.update_status(self.texts[self.current_language]['completed'])
            messagebox.showinfo(
                self.texts[self.current_language]['success'],
                self.texts[self.current_language]['created']
            )
            
        except Exception as e:
            messagebox.showerror(
                self.texts[self.current_language]['error'],
                f"{str(e)}"
            )
            self.update_status(self.texts[self.current_language]['convert_failed'])

def main():
    root = tk.Tk()
    app = ImageToPdfConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main() 