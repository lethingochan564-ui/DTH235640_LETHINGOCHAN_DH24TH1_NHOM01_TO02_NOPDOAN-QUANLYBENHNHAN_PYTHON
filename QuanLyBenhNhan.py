from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
import mysql.connector

# Cấu hình kết nối Database
db_connect = {
        'host': 'localhost',
        'user': 'root',
        'password': 'han1234', 
        'database': 'QuanLyBenhNhan'
}
def get_connection():
    try:   
        conn = mysql.connector.connect(**db_connect)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi kết nối", f"Không thể kết nối Database: {err}")
        return None

# Hàm chuyển đổi định dạng ngày tháng
def date_ui_to_db(date_str):
    try: return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except: 
        return None

def date_db_to_ui(date_obj):
    try:
        if isinstance(date_obj, str): return datetime.strptime(date_obj, '%Y-%m-%d').strftime('%d/%m/%Y')
        return date_obj.strftime('%d/%m/%Y')
    except: 
        return ""

                                                            # FROM ĐĂNG NHẬP
class LoginSystem:

    # Giao diện chính
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập hệ thống")
        w, h = 600, 400
        sw = root.winfo_screenwidth(); 
        sh = root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw//2)-(w//2)}+{(sh//2)-(h//2)}")
        self.root.resizable(False, False); 
        self.root.config(bg="#F0F8FF")

        # Biến lưu thông tin đăng nhập
        self.username = StringVar(); 
        self.password = StringVar()

        # Tạo khung đăng nhập
        Label(self.root, text="HỆ THỐNG Y TẾ", font=("Times New Roman", 20, "bold"), bg="#F0F8FF").place(x=180, y=30)
        frame = Frame(self.root, bg="#B2EBF2", width=450, height=200); frame.place(x=75, y=90)
        Label(frame, text="Đăng nhập", font=("Times New Roman", 14, "bold"), bg="#B2EBF2").place(x=10, y=10)
        
        # Các thành phần nhập liệu
        Label(frame, text="Tài khoản:", font=("Times New Roman", 13), bg="#B2EBF2").place(x=50, y=60)
        Entry(frame, textvariable=self.username, font=("Times New Roman", 13), width=25).place(x=150, y=60)
        
        Label(frame, text="Mật khẩu:", font=("Times New Roman", 13), bg="#B2EBF2").place(x=50, y=110)
        e_pass = Entry(frame, textvariable=self.password, font=("Times New Roman", 13), width=25, show="*"); 
        e_pass.place(x=150, y=110)
        e_pass.bind('<Return>', lambda e: self.login())

        # Nút đăng nhập và thoát
        Button(self.root, text="Đăng nhập", command=self.login, font=("Times New Roman", 12, "bold"), 
               bg="#FFC0CB", width=12).place(x=180, y=320)
        Button(self.root, text="Thoát", command=root.quit, font=("Times New Roman", 12, "bold"), 
               bg="#A9A9A9", width=12).place(x=350, y=320)
    # Hàm xử lý đăng nhập
    def login(self):
        user = self.username.get()
        pwd = self.password.get()
        
        if user == "admin" and pwd == "123":
            messagebox.showinfo("Thành công", "Đăng nhập với quyền Quản trị viên")
            self.open_main("admin")
            return

        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            sql_nv = "SELECT * FROM NHANVIEN WHERE TAIKHOAN = %s AND MATKHAU = %s"
            cursor.execute(sql_nv, (user, pwd))
            if cursor.fetchone():
                conn.close(); 
                messagebox.showinfo("Thành công", f"Đăng nhập với quyền Nhân viên!")
                self.open_main("nhanvien"); 
                return

            sql_bs = "SELECT * FROM BACSI WHERE TAIKHOAN = %s AND MATKHAU = %s"
            cursor.execute(sql_bs, (user, pwd))
            if cursor.fetchone():
                conn.close(); 
                messagebox.showinfo("Thành công", f"Đăng nhập với quyền Bác sĩ!")
                self.open_main("bacsi"); 
                return
            
            conn.close()
            messagebox.showerror("Lỗi", "Sai thông tin đăng nhập!")
    # Mở giao diện sau khi đăng nhập thành công
    def open_main(self, role):
        self.root.destroy()
        new_root = Tk()
        QuanLyBenhNhan(new_root, role) 
        new_root.mainloop()

                                                    #  FROM QUẢN LÝ BỆNH NHÂN
class QuanLyBenhNhan:

    # Tạo giao diện chính
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"Quản lý bệnh nhân - Quyền: {self.role.upper()}")
        self.root.geometry("1000x600")
        self.center_window(1000, 600)
        self.root.config(bg="#E0F7FA")
        self.create_menu()

        # Giao diện quản lý bệnh nhân
        style = ttk.Style(); style.theme_use("default")
        Label(self.root, text="QUẢN LÝ BỆNH NHÂN", font=("Times New Roman", 24, "bold"), bg="#E0F7FA").pack(pady=10)
        frame_info = LabelFrame(self.root, text="Thông tin", font=("Times New Roman", 14, "bold"), bg="#B2EBF2", bd=2, relief=GROOVE)
        frame_info.place(x=50, y=70, width=900, height=220)

        # Các thành phần nhập liệu
        self.entries = {}
        labels_left = ["Mã bệnh nhân:", 
                       "Họ và tên:", 
                       "Mã BHYT:", 
                       "Giới tính:"]
        labels_right = ["Địa chỉ:", 
                        "Số điện thoại:", 
                        "Ngày sinh:"]

        # Điền các nhãn và ô nhập liệu- bên trái
        for i, text in enumerate(labels_left):
            Label(frame_info, text=text, font=("Times New Roman", 13), bg="#B2EBF2").grid(row=i, column=0, padx=20, pady=10, sticky="w")
            if text == "Giới tính:":
                cbo = ttk.Combobox(frame_info, values=["Nam", "Nữ"], font=("Times New Roman", 13), state="readonly", width=23)
                cbo.grid(row=i, column=1, padx=10, pady=10); 
                cbo.current(0); 
                self.entries["Giới tính"] = cbo
            else:
                entry = Entry(frame_info, font=("Times New Roman", 13), width=25)
                entry.grid(row=i, column=1, padx=10, pady=10); 
                self.entries[text.replace(":", "")] = entry
        # Điền các nhãn và ô nhập liệu- bên phải
        for i, text in enumerate(labels_right):
            Label(frame_info, text=text, font=("Times New Roman", 13), bg="#B2EBF2").grid(row=i, column=2, padx=40, pady=10, sticky="w")
            if text == "Ngày sinh:":
                date_entry = DateEntry(frame_info, width=23, background='darkblue', 
                                       foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy', font=("Times New Roman", 13))
                date_entry.grid(row=i, column=3, padx=10, pady=10); 
                self.entries["Ngày sinh"] = date_entry
            else:
                entry = Entry(frame_info, font=("Times New Roman", 13), width=25)
                entry.grid(row=i, column=3, padx=10, pady=10); 
                self.entries[text.replace(":", "")] = entry

        # Khung nút chức năng
        frame_buttons = Frame(self.root, bg="#E0F7FA")
        frame_buttons.place(x=50, y=300, width=900, height=60)
        
        # Nút chức năng
        for i in range(5):
            frame_buttons.grid_columnconfigure(i, weight=1)

        btn_configs = [
            ("Thêm", "#6495ED", self.them), 
            ("Xóa", "#D3D3D3", self.xoa), 
            ("Sửa", "#B0C4DE", self.sua), 
            ("Lưu", "#FFC0CB", self.luu), 
            ("Làm mới", "#98FB98", self.clear_form)
        ]

        for i, (text, color, cmd) in enumerate(btn_configs):
            Button(frame_buttons, text=text, command=cmd, font=("Times New Roman", 13, "bold"), 
                   bg=color, width=12, bd=2, relief=RAISED).grid(row=0, column=i, padx=5, pady=10)
            
        # Khung bảng dữ liệu
        frame_table = Frame(self.root, bd=2, relief=RIDGE)
        frame_table.place(x=30, y=380, width=940, height=200)
        scroll_y = Scrollbar(frame_table, orient=VERTICAL); 
        scroll_y.pack(side=RIGHT, fill=Y)
        columns = ("Mã bệnh nhân", "Họ và tên", "Giới tính", "Mã BHYT", "Địa chỉ", "Số điện thoại", "Ngày sinh",)
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)
 
            # Định dạng cột
        for col in columns:
            self.tree.heading(col, text=col); 
            self.tree.column(col, width=150 if col in ["Họ và tên", "Địa chỉ"] else 100, anchor="center")
            self.tree.pack(fill=BOTH, expand=True)
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.load_data()

    # Hàm căn giữa cửa sổ
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth(); 
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2); 
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # Hàm tạo menu
    def create_menu(self):
        menubar = Menu(self.root); 
        self.root.config(menu=menubar)
        sys_menu = Menu(menubar, tearoff=0)
        sys_menu.add_command(label="Đăng xuất", command=self.dang_xuat); 
        sys_menu.add_command(label="Thoát", command=self.root.quit)
        menubar.add_cascade(label=f"Hệ thống ({self.role})", menu=sys_menu)
        
        man_menu = Menu(menubar, tearoff=0)
        man_menu.add_command(label="Quản lý Bệnh Nhân", state="disabled")
        
        if self.role == "admin": 
            man_menu.add_command(label="Quản lý Bác Sĩ", command=self.open_quan_ly_bac_si)
        else: 
            man_menu.add_command(label="Quản lý Bác Sĩ (Admin only)", state="disabled")

        if self.role in ["admin", "nhanvien"]: 
            man_menu.add_command(label="Đặt lịch khám", command=self.open_quan_ly_dat_lich)
        else: 
            man_menu.add_command(label="Đặt lịch khám (No Access)", state="disabled")

        if self.role in ["admin", "bacsi"]: 
            man_menu.add_command(label="Khám bệnh", command=self.open_kham_benh)    
        else: 
            man_menu.add_command(label="Khám bệnh (No Access)", state="disabled")

        menubar.add_cascade(label="Quản lý", menu=man_menu)

   # Hàm tải dữ liệu từ database vào bảng
    def load_data(self):
        for row in self.tree.get_children(): 
            self.tree.delete(row)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM BENHNHAN")
            for row in cursor.fetchall():
                self.tree.insert("", END, values=(
                    row[0],                
                    row[1],               
                    row[4],                 
                    row[6],                
                    row[5],                
                    row[2],                 
                    date_db_to_ui(row[3])   
                ))
            conn.close()

    # Hàm thêm bệnh nhân 
    def them(self):
        vals = {
            "MABN": self.entries["Mã bệnh nhân"].get(),
            "HOTEN": self.entries["Họ và tên"].get(),
            "GIOITINH": self.entries["Giới tính"].get(), 
            "MA_BHYT": self.entries["Mã BHYT"].get(),
            "DIACHI": self.entries["Địa chỉ"].get(), 
            "DIENTHOAI": self.entries["Số điện thoại"].get(),
            "NGAYSINH": date_ui_to_db(self.entries["Ngày sinh"].get()), 
        }
        if vals["MABN"] == "": 
            messagebox.showerror("Lỗi", "Vui lòng nhập Mã bệnh nhân"); 
            return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO BENHNHAN (MABN, HOTEN, GIOITINH, MA_BHYT, DIACHI, DIENTHOAI, NGAYSINH) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, tuple(vals.values()))
                conn.commit()
                self.load_data()
                self.clear_form()
                messagebox.showinfo("Thành công", "Đã thêm!")
            except mysql.connector.Error as err: 
                messagebox.showerror("Lỗi Database", f"Chi tiết: {err}")
            finally: 
                conn.close()

    # Hàm xóa bệnh nhân
    def xoa(self):
        sel = self.tree.selection()
        if sel:
            mabn = self.tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Xác nhận", f"Xóa bệnh nhân {mabn}?"):
                conn = get_connection()
                if conn:
                    try: 
                        conn.cursor().execute("DELETE FROM BENHNHAN WHERE MABN = %s", (mabn,)); 
                        conn.commit(); 
                        self.load_data(); 
                        self.clear_form()
                        messagebox.showinfo("Thành công", "Đã xóa!")
                    except Exception as e:
                        messagebox.showerror("Lỗi", str(e))
                    conn.close()

    # Hàm sửa thông tin bệnh nhân
    def sua(self):
        sel = self.tree.selection()
        if not sel: 
            return
        vals = [self.entries["Họ và tên"].get(), 
                self.entries["Giới tính"].get(), 
                self.entries["Mã BHYT"].get(),
                self.entries["Địa chỉ"].get(), 
                self.entries["Số điện thoại"].get(), 
                date_ui_to_db(self.entries["Ngày sinh"].get()),
                self.entries["Mã bệnh nhân"].get()]
        conn = get_connection()
        if conn:
            try:
                conn.cursor().execute("UPDATE BENHNHAN SET HOTEN=%s, GIOITINH=%s, MA_BHYT=%s, DIACHI=%s, DIENTHOAI=%s, NGAYSINH=%s"
                                         "WHERE MABN=%s", vals)
                conn.commit(); 
                self.load_data(); 
                messagebox.showinfo("Thông Báo", "Đã cập nhật!")
            except Exception as e: 
                messagebox.showerror("Lỗi", str(e))
            conn.close()

    # Hàm lưu dữ liệu
    def luu(self):
        self.load_data()
        messagebox.showinfo("Thông báo", "Dữ liệu đã được lưu và cập nhật từ hệ thống!")

    # Hàm làm mới form nhập liệu
    def clear_form(self):
        for k, v in self.entries.items():
            if isinstance(v, ttk.Combobox): 
                v.current(0)
            elif isinstance(v, DateEntry): 
                v.set_date(datetime.now())
            else: 
                v.delete(0, END)

    # Hàm xử lý khi chọn một dòng trong bảng
    def on_tree_select(self, event):
        try:
            sel = self.tree.selection()[0]; 
            val = self.tree.item(sel)['values']
            self.entries["Mã bệnh nhân"].delete(0, END); 
            self.entries["Mã bệnh nhân"].insert(0, val[0])
            self.entries["Họ và tên"].delete(0, END); 
            self.entries["Họ và tên"].insert(0, val[1])
            self.entries["Giới tính"].set(val[2])
            self.entries["Mã BHYT"].delete(0, END); 
            self.entries["Mã BHYT"].insert(0, str(val[3]))
            self.entries["Địa chỉ"].delete(0, END); 
            self.entries["Địa chỉ"].insert(0, val[4])
            self.entries["Số điện thoại"].delete(0, END); 
            self.entries["Số điện thoại"].insert(0, str(val[5]))
            try: 
                self.entries["Ngày sinh"].set_date(datetime.strptime(val[6], '%d/%m/%Y'))
            except: 
                pass 
        except:
            pass

    # Hàm điều hướng menu
    def dang_xuat(self):
        self.root.destroy(); 
        root = Tk(); 
        LoginSystem(root); 
        root.mainloop()
    def thoat_ung_dung(self):
        self.root.quit()
    def open_quan_ly_dat_lich(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyDatLich(new_root, self.role); 
        new_root.mainloop()
    def open_quan_ly_bac_si(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyBacSi(new_root, self.role); 
        new_root.mainloop()
    def open_kham_benh(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyKhamBenh(new_root, self.role); 
        new_root.mainloop()

                                                        # FROM QUẢN LÝ BÁC SĨ
class QuanLyBacSi:

    # Tạo giao diện chính
    def __init__(self, root, role):
        self.root = root; 
        self.role = role
        self.root.title(f"Quản lý Bác sĩ - Quyền: {self.role.upper()}")
        self.root.geometry("1000x600")
        self.center_window(1000, 600)
        self.root.config(bg="#E0F7FA")
        self.create_menu()

        # Giao diện quản lý bác sĩ
        Label(self.root, text="QUẢN LÝ BÁC SĨ", font=("Times New Roman", 24, "bold"), bg="#E0F7FA").pack(pady=10)
        frame_info = LabelFrame(self.root, text="Thông tin", font=("Times New Roman", 14, "bold"), bg="#B2EBF2", bd=2, relief=GROOVE)
        frame_info.place(x=50, y=70, width=900, height=220)

        # Các thành phần nhập liệu
        self.entries = {}
        labels_left = ["Mã bác sĩ:", 
                       "Họ và tên:",
                         "Chức vụ:", 
                         "Chuyên khoa:"]
        labels_right = ["Điện thoại:",
                         "Ngày sinh:", 
                         "Địa chỉ:", 
                         "Giới tính:"]

        # Điền các nhãn và ô nhập liệu- bên trái
        for i, text in enumerate(labels_left):
            Label(frame_info, text=text, font=("Times New Roman", 13), bg="#B2EBF2").grid(row=i, column=0, padx=20, pady=10, sticky="w")
            if text == "Chức vụ:":
                cbo = ttk.Combobox(frame_info, values=["Bác sĩ chính thức", "Bác sĩ thực tập"], 
                                   font=("Times New Roman", 13), state="readonly", width=23)
                cbo.grid(row=i, column=1, padx=10, pady=10); 
                cbo.current(0); 
                self.entries["Chức vụ"] = cbo
            elif text == "Chuyên khoa:":
                cbo = ttk.Combobox(frame_info, values=["Nội", "Ngoại"], font=("Times New Roman", 13), state="readonly", width=23)
                cbo.grid(row=i, column=1, padx=10, pady=10); 
                cbo.current(0); 
                self.entries["Chuyên khoa"] = cbo
            else:
                entry = Entry(frame_info, font=("Times New Roman", 13), width=25); 
                entry.grid(row=i, column=1, padx=10, pady=10); 
                self.entries[text.replace(":", "")] = entry
        
        # Điền các nhãn và ô nhập liệu- bên phải
        for i, text in enumerate(labels_right):
            Label(frame_info, text=text, font=("Times New Roman", 13), 
                  bg="#B2EBF2").grid(row=i, column=2, padx=40, pady=10, sticky="w")
            if text == "Ngày sinh:":
                date_entry = DateEntry(frame_info, width=23, background='darkblue', foreground='white', borderwidth=2, 
                                       date_pattern='dd/mm/yyyy', font=("Times New Roman", 13))
                date_entry.grid(row=i, column=3, padx=10, pady=10); 
                self.entries["Ngày sinh"] = date_entry
            elif text == "Giới tính:":
                cbo = ttk.Combobox(frame_info, values=["Nam", "Nữ"], font=("Times New Roman", 13), state="readonly", width=23)
                cbo.grid(row=i, column=3, padx=10, pady=10); 
                cbo.current(0); 
                self.entries["Giới tính"] = cbo
            else:
                entry = Entry(frame_info, font=("Times New Roman", 13), width=25); 
                entry.grid(row=i, column=3, padx=10, pady=10); 
                self.entries[text.replace(":", "")] = entry
        
        # Khung nút chức năng
        frame_buttons = Frame(self.root, bg="#E0F7FA")
        frame_buttons.place(x=50, y=300, width=900, height=60)
        
        # Nút chức năng
        for i in range(5):
            frame_buttons.grid_columnconfigure(i, weight=1)
        
        btn_configs = [
            ("Thêm", "#6495ED", self.them), 
            ("Xóa", "#D3D3D3", self.xoa), 
            ("Sửa", "#B0C4DE", self.sua), 
            ("Lưu", "#FFC0CB", self.luu), 
            ("Làm mới", "#98FB98", self.clear_form)
        ]
        
        for i, (text, color, cmd) in enumerate(btn_configs):
            Button(frame_buttons, text=text, command=cmd, font=("Times New Roman", 13, "bold"), 
                   bg=color, width=12, bd=2, relief=RAISED).grid(row=0, column=i, padx=5, pady=10)
        # Khung bảng dữ liệu
        frame_table = Frame(self.root, bd=2, relief=RIDGE)
        frame_table.place(x=30, y=380, width=940, height=200)
        scroll_y = Scrollbar(frame_table, orient=VERTICAL); 
        scroll_y.pack(side=RIGHT, fill=Y)
        columns = ("Mã bác sĩ", 
                   "Họ và tên", 
                   "Chức vụ", 
                   "Chuyên khoa", 
                   "Điện thoại", 
                   "Ngày sinh", 
                   "Địa chỉ", 
                   "Giới tính")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)
        for col in columns:
            self.tree.heading(col, text=col); 
            self.tree.column(col, width=150 if col in ["Họ và tên", "Địa chỉ"] else 100, anchor="center")
            self.tree.pack(fill=BOTH, expand=True)
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.load_data()

    # Hàm căn giữa cửa sổ
    def center_window(self, width, height):
        x = (self.root.winfo_screenwidth() // 2) - (width // 2); 
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # Hàm tạo menu
    def create_menu(self):
        menubar = Menu(self.root); 
        self.root.config(menu=menubar)
        sys_menu = Menu(menubar, tearoff=0)
        sys_menu.add_command(label="Đăng xuất", command=self.dang_xuat); 
        sys_menu.add_command(label="Thoát", command=self.root.quit)
        menubar.add_cascade(label=f"Hệ thống ({self.role})", menu=sys_menu)
        man_menu = Menu(menubar, tearoff=0)
        man_menu.add_command(label="Quản lý Bệnh Nhân", command=self.open_quan_ly_benh_nhan)
        man_menu.add_command(label="Quản lý Bác Sĩ", state="disabled")
        
        if self.role in ["admin", "nhanvien"]: 
            man_menu.add_command(label="Đặt lịch khám", command=self.open_quan_ly_dat_lich)
        else:
            man_menu.add_command(label="Đặt lịch khám (No Access)", state="disabled")

        if self.role in ["admin", "bacsi"]: 
            man_menu.add_command(label="Khám bệnh", command=self.open_kham_benh)  
        else: 
            man_menu.add_command(label="Khám bệnh (No Access)", state="disabled")

        menubar.add_cascade(label="Quản lý", menu=man_menu)

    # Hàm tải dữ liệu từ database vào bảng
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM BACSI")
            for row in cursor.fetchall():
                self.tree.insert("", END, 
                                 values=(row[0], row[1], row[2], row[3], row[4], date_db_to_ui(row[5]), row[6], row[7]))
            conn.close()

    # Hàm thêm bác sĩ
    def them(self):
        vals = { "MABS": self.entries["Mã bác sĩ"].get(),
                 "TENBS": self.entries["Họ và tên"].get(),
                "CHUCVU": self.entries["Chức vụ"].get(), 
                "KHOA": self.entries["Chuyên khoa"].get(),
                "DIENTHOAI": self.entries["Điện thoại"].get(), 
                "NGAYSINH": date_ui_to_db(self.entries["Ngày sinh"].get()),
                "DIACHI": self.entries["Địa chỉ"].get(), 
                "GIOITINH": self.entries["Giới tính"].get() }
        if vals["MABS"] == "": messagebox.showerror("Lỗi", "Nhập Mã BS"); return
        conn = get_connection()
        if conn:
            try:
                conn.cursor().execute("INSERT INTO BACSI (MABS, TENBS, CHUCVU, KHOA, DIENTHOAI, NGAYSINH, DIACHI, GIOITINH)" \
                                        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", tuple(vals.values()))
                conn.commit(); 
                self.load_data(); 
                self.clear_form()
                messagebox.showinfo("Thành công", "Đã thêm!")
            except Exception as e: 
                messagebox.showerror("Lỗi", str(e))
            conn.close()

    # Hàm xóa bác sĩ
    def xoa(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Xóa bác sĩ này?"):
            conn = get_connection()
            if conn: conn.cursor().execute("DELETE FROM BACSI WHERE MABS=%s", (self.tree.item(sel[0])['values'][0],)); 
            conn.commit(); 
            conn.close(); 
            self.load_data(); 
            messagebox.showinfo("Thành công", "Đã xóa!")
            self.clear_form()

    # Hàm sửa thông tin bác sĩ
    def sua(self):
        sel = self.tree.selection()
        if sel:
             vals = [self.entries["Họ và tên"].get(), 
                     self.entries["Chức vụ"].get(),
                     self.entries["Chuyên khoa"].get(),
                     self.entries["Điện thoại"].get(), 
                     date_ui_to_db(self.entries["Ngày sinh"].get()), 
                     self.entries["Địa chỉ"].get(),
                     self.entries["Giới tính"].get(),   
                     self.entries["Mã bác sĩ"].get()]
             conn = get_connection()
             if conn:
                 try: 
                    conn.cursor().execute("UPDATE BACSI SET TENBS=%s, CHUCVU=%s, KHOA=%s, DIENTHOAI=%s, NGAYSINH=%s, " \
                                            "DIACHI=%s, GIOITINH=%s WHERE MABS=%s", vals); 
                    conn.commit(); 
                    self.load_data()
                    messagebox.showinfo("Thông báo", "Đã cập nhật! ")
                 except Exception as e: 
                    messagebox.showerror("Lỗi", str(e))
                 conn.close()

    # Hàm lưu dữ liệu
    def luu(self):
        self.load_data()
        messagebox.showinfo("Thông báo", "Dữ liệu đã được lưu và cập nhật từ hệ thống!")

    # Hàm làm mới form nhập liệu
    def clear_form(self):
        for k, v in self.entries.items():
            if isinstance(v, ttk.Combobox): 
                v.current(0)
            elif isinstance(v, DateEntry): 
                v.set_date(datetime.now())
            else: 
                v.delete(0, END)

    # Hàm xử lý khi chọn một dòng trong bảng
    def on_tree_select(self, event):
        try:
            sel = self.tree.selection()[0]; 
            val = self.tree.item(sel)['values']
            self.entries["Mã bác sĩ"].delete(0, END); 
            self.entries["Mã bác sĩ"].insert(0, val[0])
            self.entries["Họ và tên"].delete(0, END);  
            self.entries["Họ và tên"].insert(0, val[1])
            self.entries["Chức vụ"].set(val[2]); 
            self.entries["Chuyên khoa"].set(val[3])
            self.entries["Điện thoại"].delete(0, END); 
            self.entries["Điện thoại"].insert(0, str(val[4]))
            try:
                self.entries["Ngày sinh"].set_date(datetime.strptime(val[5], '%d/%m/%Y'))
            except:
                pass
            self.entries["Địa chỉ"].delete(0, END); 
            self.entries["Địa chỉ"].insert(0, val[6])
            self.entries["Giới tính"].set(val[7])
        except:
            pass

    # Hàm điều hướng menu
    def dang_xuat(self): 
        self.root.destroy(); 
        root = Tk(); 
        LoginSystem(root); 
        root.mainloop()
    def thoat_ung_dung(self):
        self.root.quit()
    def open_quan_ly_dat_lich(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyDatLich(new_root, self.role); 
        new_root.mainloop()
    def open_quan_ly_benh_nhan(self):
         self.root.destroy(); 
         new_root = Tk(); 
         QuanLyBenhNhan(new_root, self.role); 
         new_root.mainloop()
    def open_kham_benh(self):
         self.root.destroy(); 
         new_root = Tk(); 
         QuanLyKhamBenh(new_root, self.role); 
         new_root.mainloop()

                                                        # FROM QUẢN LÝ ĐẶT LỊCH

class QuanLyDatLich:

    # Tạo giao diện chính
    def __init__(self, root, role):
        self.root = root; 
        self.role = role
        self.root.title(f"Đặt lịch khám - Quyền: {self.role.upper()}")
        self.root.geometry("1000x600")
        self.center_window(1000, 600)
        self.root.config(bg="#E0F7FA")
        self.create_menu()

        # Giao diện quản lý đặt lịch khám
        Label(self.root, text="ĐẶT LỊCH KHÁM BỆNH", font=("Times New Roman", 24, "bold"), bg="#E0F7FA").pack(pady=10)
        frame_info = LabelFrame(self.root, text="Thông tin", font=("Times New Roman", 14, "bold"), bg="#B2EBF2", bd=2, relief=GROOVE)
        frame_info.place(x=50, y=70, width=900, height=220)

        # Các thành phần nhập liệu
        self.entries = {}
        labels_left = ["Mã đặt:", 
                       "Ngày đặt:", 
                       "Thời gian:"]
        labels_right = ["Mã bệnh nhân:", 
                        "Mã bác sĩ:", 
                        "Triệu chứng:"]

        # Điền các nhãn và ô nhập liệu- bên trái
        for i, text in enumerate(labels_left):
            Label(frame_info, text=text, font=("Times New Roman", 13), 
                  bg="#B2EBF2").grid(row=i, column=0, padx=20, pady=15, sticky="w")
            if text == "Ngày đặt:":
                date_entry = DateEntry(frame_info, width=28, background='darkblue', foreground='white', 
                                       borderwidth=2, date_pattern='dd/mm/yyyy', font=("Times New Roman", 13))
                date_entry.grid(row=i, column=1, padx=10, pady=15); 
                self.entries["Ngày đặt"] = date_entry
            elif text == "Thời gian:":
                times = [f"{h:02d}:{m}" for h in range(7, 17) for m in ["00", "30"]] + ["17:00"]
                cbo = ttk.Combobox(frame_info, values=times, font=("Times New Roman", 13), state="readonly", width=28)
                cbo.grid(row=i, column=1, padx=10, pady=15); cbo.current(0); 
                self.entries["Thời gian"] = cbo
            else:
                entry = Entry(frame_info, font=("Times New Roman", 13), width=30); 
                entry.grid(row=i, column=1, padx=10, pady=15); 
                self.entries[text.replace(":", "")] = entry
        
        # Điền các nhãn và ô nhập liệu- bên phải
        for i, text in enumerate(labels_right):
            Label(frame_info, text=text, font=("Times New Roman", 13), 
                  bg="#B2EBF2").grid(row=i, column=2, padx=40, pady=15, sticky="w")
            entry = Entry(frame_info, font=("Times New Roman", 13), width=30); 
            entry.grid(row=i, column=3, padx=10, pady=15); 
            self.entries[text.replace(":", "")] = entry
        
        # Khung nút chức năng
        frame_buttons = Frame(self.root, bg="#E0F7FA")
        frame_buttons.place(x=250, y=300, width=500, height=60)
        Button(frame_buttons, text="Đặt lịch", command=self.dat_lich, font=("Times New Roman", 13, "bold"), 
               bg="#FFC0CB", width=15, bd=2, relief=RAISED).place(x=20, y=10)
        Button(frame_buttons, text="Hủy", command=self.huy_lich, font=("Times New Roman", 13, "bold"), 
               bg="#A9A9A9", width=15, bd=2, relief=RAISED).place(x=300, y=10)

        # Khung bảng dữ liệu    
        frame_table = Frame(self.root, bd=2, relief=RIDGE)
        frame_table.place(x=30, y=380, width=940, height=200)
        scroll_y = Scrollbar(frame_table, orient=VERTICAL); 
        scroll_y.pack(side=RIGHT, fill=Y)
        columns = ("Mã đặt", "Ngày đặt", "Thời gian", "Mã bệnh nhân", "Mã bác sĩ", "Triệu chứng")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.tree.yview)
        for col in columns:
            self.tree.heading(col, text=col); 
            self.tree.column(col, width=150 if col == "Triệu chứng" else 120, anchor="center")
            self.tree.pack(fill=BOTH, expand=True)
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.load_data()   

    # Hàm căn giữa cửa sổ
    def center_window(self, width, height):
        x = (self.root.winfo_screenwidth() // 2) - (width // 2);
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # Hàm tạo menu
    def create_menu(self):
        menubar = Menu(self.root); 
        self.root.config(menu=menubar)
        sys_menu = Menu(menubar, tearoff=0)
        sys_menu.add_command(label="Đăng xuất", command=self.dang_xuat); 
        sys_menu.add_command(label="Thoát", command=self.root.quit)
        menubar.add_cascade(label=f"Hệ thống ({self.role})", menu=sys_menu)
        man_menu = Menu(menubar, tearoff=0)
        man_menu.add_command(label="Quản lý Bệnh Nhân", command=self.open_quan_ly_benh_nhan)
        
        if self.role == "admin":
             man_menu.add_command(label="Quản lý Bác Sĩ", command=self.open_quan_ly_bac_si)
        else: 
            man_menu.add_command(label="Quản lý Bác Sĩ (Admin only)", state="disabled")
            man_menu.add_command(label="Đặt lịch khám", state="disabled")
        
        if self.role in ["admin", "bacsi"]:
            man_menu.add_command(label="Khám bệnh", command=self.open_kham_benh)  
        else: 
            man_menu.add_command(label="Khám bệnh (No Access)", state="disabled")
        
        menubar.add_cascade(label="Quản lý", menu=man_menu)

    # Hàm tải dữ liệu từ database vào bảng
    def load_data(self):
        for row in self.tree.get_children(): 
            self.tree.delete(row)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DATLICH")
            for row in cursor.fetchall():
                self.tree.insert("", END, values=(row[0], date_db_to_ui(row[3]), str(row[4]), row[1], row[2], row[5]))
            conn.close()

    # Hàm đặt lịch
    def dat_lich(self):
        ngay_dat = date_ui_to_db(self.entries["Ngày đặt"].get())
        thoi_gian = self.entries["Thời gian"].get()
        ma_bn = self.entries["Mã bệnh nhân"].get()
        ma_bs = self.entries["Mã bác sĩ"].get()
        trieu_chung = self.entries["Triệu chứng"].get()

        # Kiểm tra dữ liệu trống
        if not ma_bn or not ma_bs:
             messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ Mã BN và Mã BS"); 
             return
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO DATLICH (MABN, MABS, NGAYDAT, THOIGIAN, TRIEUCHUNG) VALUES (%s, %s, %s, %s, %s)"
                val = (ma_bn, ma_bs, ngay_dat, thoi_gian, trieu_chung)
                cursor.execute(sql, val)
                conn.commit()
                messagebox.showinfo("Thành công", "Đã đặt lịch thành công!")
                self.load_data()
                self.clear_form()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi Database", f"Chi tiết lỗi: {err}")
            finally:
                conn.close()
                
    # Hàm hủy lịch
    def huy_lich(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Hủy lịch này?"):
            conn = get_connection()
            if conn: conn.cursor().execute("DELETE FROM DATLICH WHERE MADAT=%s",                            
                (self.tree.item(sel[0])['values'][0],)); conn.commit(); 
            conn.close(); 
            self.load_data(); 
            self.clear_form()
   
    # Hàm làm mới form nhập liệu
    def clear_form(self):
        for k, v in self.entries.items():
            if isinstance(v, ttk.Combobox): 
                v.current(0)
            elif isinstance(v, DateEntry): 
                v.set_date(datetime.now())
            else: 
                v.delete(0, END)

    # Hàm xử lý khi chọn một dòng trong bảng
    def on_tree_select(self, event):
        try:
            sel = self.tree.selection()[0]; val = self.tree.item(sel)['values']
            self.entries["Mã đặt"].delete(0, END); 
            self.entries["Mã đặt"].insert(0, val[0])
            try: 
                self.entries["Ngày đặt"].set_date(datetime.strptime(val[1], '%d/%m/%Y'))
            except: 
                pass
            self.entries["Thời gian"].set(val[2])
            self.entries["Mã bệnh nhân"].delete(0, END); 
            self.entries["Mã bệnh nhân"].insert(0, str(val[3]))
            self.entries["Mã bác sĩ"].delete(0, END); 
            self.entries["Mã bác sĩ"].insert(0, str(val[4]))
            self.entries["Triệu chứng"].delete(0, END); 
            self.entries["Triệu chứng"].insert(0, val[5])
        except: 
            pass
   
    # Hàm điều hướng menu
    def dang_xuat(self): 
        self.root.destroy(); 
        root = Tk(); 
        LoginSystem(root); 
        root.mainloop()
    def thoat_ung_dung(self):
        self.root.quit()
    def open_quan_ly_benh_nhan(self):
         self.root.destroy(); 
         new_root = Tk(); 
         QuanLyBenhNhan(new_root, self.role); 
         new_root.mainloop()
    def open_quan_ly_bac_si(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyBacSi(new_root, self.role); 
        new_root.mainloop()
    def open_kham_benh(self):
         self.root.destroy(); 
         new_root = Tk(); 
         QuanLyKhamBenh(new_root, self.role); 
         new_root.mainloop()

                                                        # FROM QUẢN LÝ KHÁM BỆNH

class QuanLyKhamBenh:

    # Tạo giao diện chính
    def __init__(self, root, role):
        self.root = root; 
        self.role = role
        self.root.title(f"Khám Bệnh - Quyền: {self.role.upper()}")
        self.root.geometry("1000x600")
        self.center_window(1000, 600)
        self.root.config(bg="#E0F7FA")
        self.create_menu()
        self.medicine_data = {}

        # Giao diện quản lý khám bệnh
        Label(self.root, text="KHÁM BỆNH", font=("Times New Roman", 24, "bold"), bg="#E0F7FA").pack(pady=10)

        # Khung danh sách đặt lịch
        frame_list = LabelFrame(self.root, text="Đặt lịch (Chờ khám)", font=("Times New Roman", 12, "bold"), bg="#E0F7FA")
        frame_list.place(x=20, y=60, width=530, height=280)

        # Bảng danh sách đặt lịch
        cols = ("Mã đặt", "Mã BN", "Mã BS", "Triệu chứng")
        self.tree_datlich = ttk.Treeview(frame_list, columns=cols, show="headings")
        for col in cols:
            self.tree_datlich.heading(col, text=col); 
            self.tree_datlich.column(col, width=150 if col == "Triệu chứng" else 80)
            self.tree_datlich.pack(fill=BOTH, expand=True)
            self.tree_datlich.bind("<<TreeviewSelect>>", 
            self.on_schedule_select)

        self.load_schedule_data()

        # Khung khám bệnh
        frame_kham = LabelFrame(self.root, text="Khám bệnh", font=("Times New Roman", 12, "bold"), bg="#B2EBF2")
        frame_kham.place(x=20, y=350, width=530, height=250)
        self.entries_kham = {}

        # Các thành phần nhập liệu khám bệnh
        labels_kham = ["Mã bác sĩ", "Mã bệnh nhân", "Triệu Chứng", "Chuẩn đoán"]

        # Các nhãn và ô nhập liệu
        for i, text in enumerate(labels_kham):
            Label(frame_kham, text=text, font=("Times New Roman", 12),
                   bg="#B2EBF2").grid(row=i, column=0, padx=20, pady=15, sticky="w")
            entry = Entry(frame_kham, font=("Times New Roman", 12), width=35); 
            entry.grid(row=i, column=1, padx=10, pady=15); self.entries_kham[text] = entry

        # Khung thuốc
        frame_thuoc = LabelFrame(self.root, text="Thuốc", font=("Times New Roman", 12, "bold"), bg="#B2EBF2")
        frame_thuoc.place(x=570, y=60, width=410, height=280)
        self.entries_thuoc = {}


        # Các nhãn và ô nhập liệu thuốc
        Label(frame_thuoc, text="Mã thuốc", font=("Times New Roman", 12), bg="#B2EBF2").place(x=20, y=30)
        self.ent_ma_thuoc = Entry(frame_thuoc, font=("Times New Roman", 12), width=30); 
        self.ent_ma_thuoc.place(x=100, y=30)

        Label(frame_thuoc, text="Tên thuốc", font=("Times New Roman", 12), bg="#B2EBF2").place(x=20, y=80)
        self.cbo_ten_thuoc = ttk.Combobox(frame_thuoc, font=("Times New Roman", 12), width=28, state="readonly"); 
        self.cbo_ten_thuoc.place(x=100, y=80)
        self.cbo_ten_thuoc.bind("<<ComboboxSelected>>", self.on_select_medicine)

        self.load_medicine_data()

        Label(frame_thuoc, text="Số lượng", font=("Times New Roman", 12), bg="#B2EBF2").place(x=20, y=130)
        self.ent_so_luong = Entry(frame_thuoc, font=("Times New Roman", 12), width=10); 
        self.ent_so_luong.place(x=100, y=130)

        Label(frame_thuoc, text="Đơn giá", font=("Times New Roman", 12), bg="#B2EBF2").place(x=20, y=180)
        self.ent_don_gia = Entry(frame_thuoc, font=("Times New Roman", 12), width=15); 
        self.ent_don_gia.place(x=100, y=180)

        Label(frame_thuoc, text="VND", font=("Times New Roman", 12, "bold"), bg="#B2EBF2").place(x=300, y=180)

        # Khung nút chức năng
        frame_btn_action = Frame(self.root, bg="#E0F7FA")
        frame_btn_action.place(x=570, y=350, width=410, height=60)

        # Chia khung
        frame_btn_action.grid_columnconfigure(0, weight=1)
        frame_btn_action.grid_columnconfigure(1, weight=1)

        # Nút Xuất hóa đơn 
        Button(frame_btn_action, text="Xuất phiếu khám", command=self.xuat_hoa_don, 
               font=("Times New Roman", 12, "bold"), bg="#FFC0CB", 
               width=15, height=2).grid(row=0, column=0, padx=5, pady=5)

        # Nút Hủy 
        Button(frame_btn_action, text="Hủy", command=self.huy_kham, 
               font=("Times New Roman", 12, "bold"), bg="#D3D3D3", 
               width=15, height=2).grid(row=0, column=1, padx=5, pady=5)


    # Hàm căn giữa cửa sổ
    def center_window(self, width, height):
        x = (self.root.winfo_screenwidth() // 2) - (width // 2); 
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")


    # Hàm tạo menu
    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        sys_menu = Menu(menubar, tearoff=0)
        sys_menu.add_command(label="Đăng xuất", command=self.dang_xuat)
        sys_menu.add_command(label="Thoát", command=self.root.quit)
        menubar.add_cascade(label=f"Hệ thống ({self.role})", menu=sys_menu)

        man_menu = Menu(menubar, tearoff=0)
        man_menu.add_command(label="Quản lý Bệnh Nhân", command=self.open_quan_ly_benh_nhan)

        if self.role == "admin":
            man_menu.add_command(label="Quản lý Bác Sĩ", command=self.open_quan_ly_bac_si)
        else:
            man_menu.add_command(label="Quản lý Bác Sĩ (Admin only)", state="disabled")
            
        if self.role in ["admin", "nhanvien"]:
            man_menu.add_command(label="Đặt lịch khám", command=self.open_quan_ly_dat_lich)
        else:
            man_menu.add_command(label="Đặt lịch khám (No Access)", state="disabled")
            
        if self.role in ["admin", "bacsi"]:
             man_menu.add_command(label="Khám bệnh (Đang mở)", state="disabled") 
        else:
             man_menu.add_command(label="Khám bệnh (No Access)", state="disabled")

        menubar.add_cascade(label="Quản lý", menu=man_menu)

    # Hàm tải dữ liệu lịch khám
    def load_schedule_data(self):
        for row in self.tree_datlich.get_children(): 
            self.tree_datlich.delete(row)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MADAT, MABN, MABS, TRIEUCHUNG FROM DATLICH")
            for row in cursor.fetchall(): 
                    self.tree_datlich.insert("", END, values=row)
            conn.close()

    # Hàm tải dữ liệu thuốc
    def load_medicine_data(self):
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MATHUOC, TENTHUOC, DONGIA FROM THUOC")
            for row in cursor.fetchall(): 
                self.medicine_data[row[1]] = {"id": row[0], "price": row[2]}
            self.cbo_ten_thuoc['values'] = list(self.medicine_data.keys())
            conn.close()

    # Hàm xử lý khi chọn một lịch khám
    def on_schedule_select(self, event):
        try:
            sel = self.tree_datlich.selection()[0]; 
            val = self.tree_datlich.item(sel)['values']
            self.entries_kham["Mã bệnh nhân"].delete(0, END); 
            self.entries_kham["Mã bệnh nhân"].insert(0, str(val[1]))
            self.entries_kham["Mã bác sĩ"].delete(0, END); 
            self.entries_kham["Mã bác sĩ"].insert(0, str(val[2]))
            self.entries_kham["Triệu Chứng"].delete(0, END); 
            self.entries_kham["Triệu Chứng"].insert(0, str(val[3]))
        except: 
            pass

    # Hàm xử lý khi chọn một thuốc
    def on_select_medicine(self, event):
        name = self.cbo_ten_thuoc.get()
        if name in self.medicine_data:
            data = self.medicine_data[name]
            self.ent_ma_thuoc.delete(0, END); 
            self.ent_ma_thuoc.insert(0, data["id"])
            self.ent_don_gia.delete(0, END); 
            self.ent_don_gia.insert(0, str(int(data["price"])))


    # Hàm xuất hóa đơn
    def xuat_hoa_don(self):
        try:
            sl_str = self.ent_so_luong.get()
            if not sl_str.strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập số lượng thuốc!")
                return
                
            sl = int(sl_str)
            if sl <= 0: raise ValueError
            
            gia = float(self.ent_don_gia.get())
            tong_tien = sl * gia
            
            # Lấy thông tin chẩn đoán
            trieu_chung = self.entries_kham["Triệu Chứng"].get()
            chuan_doan = self.entries_kham["Chuẩn đoán"].get() 
            ten_thuoc = self.cbo_ten_thuoc.get()
            ma_thuoc = self.ent_ma_thuoc.get()
            ma_bn = self.entries_kham["Mã bệnh nhân"].get()
            ma_bs = self.entries_kham["Mã bác sĩ"].get()
            ngay_gio = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # 2. Lưu vào Database
            conn = get_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    sql = "INSERT INTO HOADON_KHAMBENH (MABN, MABS, NGAYKHAM, MATHUOC, TRIEUCHUNG, CHUANDOAN) VALUES (%s, %s, NOW(), %s, %s, %s)"
                    val = (ma_bn, ma_bs, ma_thuoc, trieu_chung, chuan_doan)
                    
                    cursor.execute(sql, val)
                    conn.commit()
                except Exception as err:
                    messagebox.showerror("Lỗi Database", f"Không lưu được vào DB (kiểm tra lại cột CHUANDOAN): {err}")
                    return 
                finally:
                    conn.close()

            # TẠO GIAO DIỆN HÓA ĐƠN
            bill_window = Toplevel(self.root)
            bill_window.title("Phiếu Khám")
            bill_window.geometry("500x600")
            bill_window.config(bg="white")

            # Tiêu đề
            Label(bill_window, text="PHIẾU KHÁM & ĐƠN THUỐC", font=("Times New Roman", 16, "bold"), bg="white").pack(pady=5)
            Label(bill_window, text=f"Ngày: {ngay_gio}", font=("Times New Roman", 10), bg="white").pack()
            
            # Đường kẻ
            Frame(bill_window, height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=20, pady=10)

            # Nội dung hóa đơn
            content_frame = Frame(bill_window, bg="white")
            content_frame.pack(fill=BOTH, expand=True, padx=30)

            info_text = f"""
            THÔNG TIN BỆNH NHÂN
            
            Mã bệnh nhân : {ma_bn}
            Mã bác sĩ    : {ma_bs}
            
            CHẨN ĐOÁN
            
            Triệu chứng  : {trieu_chung}
            Chẩn đoán    : {chuan_doan}

            ĐƠN THUỐC & THANH TOÁN
            
            Tên thuốc    : {ten_thuoc}
            Số lượng     : {sl}
            Đơn giá      : {gia:,.0f} VNĐ

            """
            
            lbl_info = Label(content_frame, text=info_text, font=("Courier New", 12), bg="white", justify=LEFT, anchor="w")
            lbl_info.pack(fill=X)

            # Tổng tiền 
            total_frame = Frame(bill_window, bg="#F0F8FF", bd=1, relief=SOLID)
            total_frame.pack(fill=X, padx=20, pady=20)
            Label(total_frame, text=f"TỔNG CỘNG: {tong_tien:,.0f} VNĐ", font=("Times New Roman", 18, "bold"),
                   bg="#F0F8FF", fg="red").pack(pady=10)

            # Nút đóng
            Button(bill_window, text="In Phiếu / Đóng", command=bill_window.destroy, 
                   bg="#FFC0CB", font=("Times New Roman", 12)).pack(pady=10)

        except ValueError: 
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên dương!")

    # Hàm hủy khám
    def huy_kham(self):
        if messagebox.askyesno("Hủy", "Bạn có chắc muốn hủy đơn thuốc này?"):
            self.cbo_ten_thuoc.set(''); 
            self.ent_ma_thuoc.delete(0, END); 
            self.ent_so_luong.delete(0, END); 
            self.ent_don_gia.delete(0, END)

    # Hàm điều hướng menu
    def dang_xuat(self): 
        self.root.destroy(); 
        root = Tk(); 
        LoginSystem(root); 
        root.mainloop()
    def thoat_ung_dung(self):
        self.root.quit()
    def open_quan_ly_bac_si(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyBacSi(new_root, self.role); 
        new_root.mainloop()
    def open_quan_ly_dat_lich(self): 
        self.root.destroy(); 
        new_root = Tk(); 
        QuanLyDatLich(new_root, self.role); 
        new_root.mainloop()
    def open_quan_ly_benh_nhan(self):
         self.root.destroy(); 
         new_root = Tk(); 
         QuanLyBenhNhan(new_root, self.role); 
         new_root.mainloop()

# Main Program
if __name__ == "__main__":
    root = Tk()
    app = LoginSystem(root)
    root.mainloop()



