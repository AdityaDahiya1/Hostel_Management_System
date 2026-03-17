
"""main.py
Tkinter GUI application for the Hostel Management System.
Run this file to start the application.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import models
from utils import export_students_csv
import datetime

APP_TITLE = 'Hostel Management System'

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('900x600')
        try:
            models.init_db()
        except Exception as e:
            print('DB init error:', e)
        self.create_widgets()

    def create_widgets(self):
        # top menu
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Export students as CSV', command=self.export_students)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        roommenu = tk.Menu(menubar, tearoff=0)
        roommenu.add_command(label='Add Room', command=self.open_add_room)
        menubar.add_cascade(label='Rooms', menu=roommenu)

        self.config(menu=menubar)

        # Left frame - controls
        left = ttk.Frame(self, width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(left, text='Search Student').pack(pady=(0,5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(left, textvariable=self.search_var)
        search_entry.pack(fill=tk.X)
        search_entry.bind('<Return>', lambda e: self.refresh_students())

        ttk.Button(left, text='New Student', command=self.open_new_student).pack(fill=tk.X, pady=5)
        ttk.Button(left, text='Refresh', command=self.refresh_students).pack(fill=tk.X)
        ttk.Separator(left).pack(fill=tk.X, pady=10)

        ttk.Label(left, text='Quick Actions').pack(pady=(10,5))
        ttk.Button(left, text='Allocate Room', command=self.allocate_room_to_selected).pack(fill=tk.X, pady=2)
        ttk.Button(left, text='Release Room', command=self.release_room_for_selected).pack(fill=tk.X, pady=2)
        ttk.Button(left, text='Record Fee', command=self.record_fee_for_selected).pack(fill=tk.X, pady=2)

        # Right frame - list
        right = ttk.Frame(self)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        cols = ('id', 'name', 'roll_no', 'phone', 'email', 'course', 'year', 'room')
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, anchor=tk.W, minwidth=50)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', lambda e: self.open_edit_selected())

        # bottom
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(bottom, text='Delete Selected', command=self.delete_selected).pack(side=tk.RIGHT, padx=10, pady=5)

        self.refresh_students()

    def refresh_students(self):
        term = self.search_var.get().strip()
        if term:
            rows = models.search_students(term)
        else:
            rows = models.list_students()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            room = f"{r['room_block']}-{r['room_no']}" if r['room_block'] and r['room_no'] else ''
            self.tree.insert('', 'end', values=(r['id'], r['name'], r['roll_no'], r['phone'], r['email'], r['course'], r['year'], room))

    def get_selected_student_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Select', 'Please select a student from the list.')
            return None
        item = self.tree.item(sel[0])
        return item['values'][0]

    def open_new_student(self):
        NewStudentDialog(self, title='New Student')
        self.refresh_students()

    def open_edit_selected(self):
        sid = self.get_selected_student_id()
        if sid:
            EditStudentDialog(self, sid)
            self.refresh_students()

    def delete_selected(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        if messagebox.askyesno('Confirm', 'Delete student?'):
            models.delete_student(sid)
            self.refresh_students()

    def open_add_room(self):
        block = simpledialog.askstring('Block', 'Block name (e.g. A)')
        if not block:
            return
        room_no = simpledialog.askstring('Room no', 'Room number')
        if not room_no:
            return
        try:
            capacity = int(simpledialog.askstring('Capacity', 'Capacity', initialvalue='1'))
        except Exception:
            capacity = 1
        models.add_room(block, room_no, capacity)
        messagebox.showinfo('Done', 'Room added')

    def allocate_room_to_selected(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        rooms = models.list_rooms()
        if not rooms:
            messagebox.showinfo('No rooms', 'No rooms available. Add a room first.')
            return
        choices = [f"{r['id']}: {r['block']}-{r['room_number']} (cap {r['capacity']}, occ {r['occupants']})" for r in rooms]
        choice = simpledialog.askinteger('Room ID', 'Enter room id from list:\n' + '\n'.join(choices))
        if not choice:
            return
        try:
            models.allocate_student_to_room(sid, choice)
            messagebox.showinfo('Done', 'Student allocated')
            self.refresh_students()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def release_room_for_selected(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        models.release_student_from_room(sid)
        messagebox.showinfo('Done', 'Released room (if any)')
        self.refresh_students()

    def record_fee_for_selected(self):
        sid = self.get_selected_student_id()
        if not sid:
            return
        try:
            amt = float(simpledialog.askstring('Amount', 'Fee amount'))
        except Exception:
            messagebox.showerror('Error', 'Invalid amount')
            return
        due = simpledialog.askstring('Due date', 'Due date (YYYY-MM-DD) — optional')
        paid = simpledialog.askstring('Paid on', 'Paid on (YYYY-MM-DD) — optional')
        remarks = simpledialog.askstring('Remarks', 'Remarks — optional')
        models.record_fee(sid, amt, due, paid, remarks)
        messagebox.showinfo('Done', 'Fee recorded')

    def export_students(self):
        rows = models.list_students()
        if not rows:
            messagebox.showinfo('No data', 'No students to export')
            return
        p = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')], initialfile='students.csv')
        if not p:
            return
        path = export_students_csv(rows, p)
        messagebox.showinfo('Exported', f'Exported to {path}')


class NewStudentDialog(tk.Toplevel):
    def __init__(self, parent, title='New Student'):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.build()
        self.wait_window()

    def build(self):
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10)
        self.vars = {k: tk.StringVar() for k in ('name', 'roll_no', 'phone', 'email', 'course', 'year')}
        for idx, (label, key) in enumerate((('Name', 'name'), ('Roll No', 'roll_no'), ('Phone', 'phone'), ('Email', 'email'), ('Course', 'course'), ('Year', 'year'))):
            ttk.Label(frm, text=label).grid(row=idx, column=0, sticky=tk.W, pady=2)
            ttk.Entry(frm, textvariable=self.vars[key]).grid(row=idx, column=1, pady=2)
        ttk.Button(frm, text='Save', command=self.save).grid(row=10, column=0, columnspan=2, pady=10)

    def save(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        if not data['name'] or not data['roll_no']:
            messagebox.showerror('Error', 'Name and Roll No are required')
            return
        try:
            year = int(data['year']) if data['year'] else None
        except ValueError:
            year = None
        models.add_student(data['name'], data['roll_no'], data['phone'] or None, data['email'] or None, data['course'] or None, year)
        messagebox.showinfo('Saved', 'Student added')
        self.destroy()


class EditStudentDialog(tk.Toplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.student_id = student_id
        self.title('Edit Student')
        self.transient(parent)
        self.grab_set()
        self.build()
        self.wait_window()

    def build(self):
        s = models.get_student(self.student_id)
        frm = ttk.Frame(self)
        frm.pack(padx=10, pady=10)
        self.vars = {k: tk.StringVar(value=s[k] if s[k] is not None else '') for k in ('name', 'roll_no', 'phone', 'email', 'course', 'year')}
        for idx, (label, key) in enumerate((('Name', 'name'), ('Roll No', 'roll_no'), ('Phone', 'phone'), ('Email', 'email'), ('Course', 'course'), ('Year', 'year'))):
            ttk.Label(frm, text=label).grid(row=idx, column=0, sticky=tk.W, pady=2)
            ttk.Entry(frm, textvariable=self.vars[key]).grid(row=idx, column=1, pady=2)
        ttk.Button(frm, text='Save', command=self.save).grid(row=10, column=0, columnspan=2, pady=10)

    def save(self):
        data = {k: v.get().strip() for k, v in self.vars.items()}
        try:
            year = int(data['year']) if data['year'] else None
        except ValueError:
            year = None
        models.update_student(self.student_id, name=data['name'], roll_no=data['roll_no'], phone=data['phone'] or None, email=data['email'] or None, course=data['course'] or None, year=year)
        messagebox.showinfo('Saved', 'Student updated')
        self.destroy()


if __name__ == '__main__':
    app = App()
    app.mainloop()
