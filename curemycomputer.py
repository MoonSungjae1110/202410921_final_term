import tkinter as tk
from tkinter import messagebox
import psutil
import subprocess
import os
import shutil
import csv
import io

#pip install psutil

# ─────────────────────────────
# 시스템 상태 점검
# ─────────────────────────────
def check_system_status():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    memory_percent = memory.percent
    disk_percent = disk.percent

    try:
        battery = psutil.sensors_battery()
        if battery:
            battery_status = f"{battery.percent}% ({'충전 중' if battery.power_plugged else '배터리 사용 중'})"
        else:
            battery_status = "없음"
    except:
        battery_status = "지원되지 않음"

    try:
        result = subprocess.check_output('wmic startup get caption', shell=True, text=True)
        startup_programs = result.strip().split('\n')[1:]
        startup_programs = [s.strip() for s in startup_programs if s.strip()]
        startup_count = len(startup_programs)
    except:
        startup_count = "확인 실패"

    # 경고 메시지 초기화
    disk_warning = ""
    startup_warning = ""

    # 디스크 사용률 경고
    if isinstance(disk_percent, (int, float)) and disk_percent >= 70:
        disk_warning = " ⚠️ 디스크 정리가 필요합니다."

    # 시작 프로그램 경고
    if isinstance(startup_count, int) and startup_count >= 10:
        startup_warning = " ⚠️ 시작 프로그램을 10개 이하로 줄이는 것이 좋습니다."

    result_message = (
        f"🖥 CPU 사용률: {cpu_percent}%\n"
        f"💾 메모리 사용률: {memory_percent}%\n"
        f"🗄 디스크 사용률: {disk_percent}%{disk_warning}\n"
        f"🔋 배터리 상태: {battery_status}\n"
        f"🚀 시작프로그램 개수: {startup_count}개{startup_warning}"
    )

    messagebox.showinfo("컴퓨터 상태 점검 결과", result_message)


# ─────────────────────────────
# 디스크 정리
# ─────────────────────────────

def get_drive_usage(drive):
    total, used, free = shutil.disk_usage(drive)
    return used / (1024 * 1024 * 1024), total / (1024 * 1024 * 1024)

def find_large_files(directory, size_threshold_mb):
    large_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path) / (1024 * 1024)
                if file_size >= size_threshold_mb:
                    large_files.append((file_path, file_size))
            except:
                continue
    large_files.sort(key=lambda x: x[1], reverse=True)
    return large_files

def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        messagebox.showerror("오류", f"파일 삭제 중 오류 발생:\n{e}")

def open_disk_cleanup_window():
    cleanup_window = tk.Toplevel(root)
    cleanup_window.title("디스크 정리")
    cleanup_window.geometry("550x450")

    tk.Label(cleanup_window, text="찾을 파일의 최소 크기 (MB):").pack(pady=5)
    size_entry = tk.Entry(cleanup_window)
    size_entry.pack()

    result_listbox = tk.Listbox(cleanup_window, width=75, height=15)
    result_listbox.pack(pady=10)

    def search_files():
        size_text = size_entry.get()
        if not size_text.isdigit():
            messagebox.showerror("오류", "숫자만 입력하세요.")
            return
        size_threshold = float(size_text)
        result_listbox.delete(0, tk.END)
        large_files = find_large_files("C:\\", size_threshold)
        if not large_files:
            messagebox.showinfo("결과", "해당 크기 이상의 파일이 없습니다.")
            return
        for file_path, size in large_files:
            result_listbox.insert(tk.END, f"{file_path} - {size:.2f}MB")

    def delete_selected_file():
        selected = result_listbox.curselection()
        if not selected:
            messagebox.showwarning("선택 안 됨", "삭제할 파일을 선택하세요.")
            return
        file_info = result_listbox.get(selected[0])
        file_path = file_info.split(" - ")[0]
        confirm = messagebox.askyesno("삭제 확인", f"{file_path} 을(를) 삭제하시겠습니까?")
        if confirm:
            delete_file(file_path)
            result_listbox.delete(selected[0])
            messagebox.showinfo("삭제 완료", "파일이 삭제되었습니다.")

    tk.Button(cleanup_window, text="파일 검색", command=search_files).pack(pady=5)
    tk.Button(cleanup_window, text="선택한 파일 삭제", command=delete_selected_file).pack(pady=5)

# ─────────────────────────────
# 시작 프로그램 관리
# ─────────────────────────────

def open_startup_manager():
    startup_window = tk.Toplevel(root)
    startup_window.title("시작 프로그램 관리")
    startup_window.geometry("650x400")

    tk.Label(startup_window, text="시작 프로그램 목록 (더블 클릭하면 삭제)").pack(pady=5)

    listbox = tk.Listbox(startup_window, width=90, height=20)
    listbox.pack(pady=10)

    try:
        result = subprocess.check_output('wmic startup get Caption, Command', shell=True, text=True)
        lines = result.strip().split('\n')[1:]
        for line in lines:
            line = line.strip()
            if line:
                listbox.insert(tk.END, line)
    except Exception as e:
        messagebox.showerror("오류", f"시작 프로그램 정보를 가져오지 못했습니다:\n{e}")
        return

    def delete_selected_program(event=None):
        selected = listbox.curselection()
        if not selected:
            return
        selected_item = listbox.get(selected[0])
        program_name = selected_item.split()[0]
        confirm = messagebox.askyesno("삭제 확인", f"'{program_name}'을(를) 시작 프로그램에서 삭제하시겠습니까?")
        if confirm:
            try:
                subprocess.call(f'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{program_name}" /f', shell=True)
                subprocess.call(f'reg delete "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{program_name}" /f', shell=True)
                listbox.delete(selected[0])
                messagebox.showinfo("삭제 완료", f"{program_name} 삭제 완료")
            except Exception as e:
                messagebox.showerror("삭제 실패", f"삭제 중 오류 발생:\n{e}")

    listbox.bind("<Double-Button-1>", delete_selected_program)

# ─────────────────────────────
# 보안 프로그램 삭제 (서비스 + 레지스트리 기반 확장)
# ─────────────────────────────

import winreg

def open_security_program_manager():
    sec_window = tk.Toplevel(root)
    sec_window.title("보안 프로그램 삭제")
    sec_window.geometry("650x450")

    tk.Label(sec_window, text="아래는 탐지된 보안 프로그램 목록입니다.\n더블 클릭 시 삭제 또는 중지됩니다.").pack(pady=5)

    listbox = tk.Listbox(sec_window, width=90, height=20)
    listbox.pack(pady=10)

    SECURITY_KEYWORDS = ["nProtect", "AhnLab", "TouchEn", "Xecure", "SoftCamp", "INISAFE", "KSign", "SafeKey", "Delfino", "보안"]
    detected_items = []

    # 서비스 기반 탐지
    try:
        result = subprocess.check_output("sc query state= all", shell=True, text=True, encoding="utf-8", errors="ignore")
        for line in result.splitlines():
            if "SERVICE_NAME" in line:
                name = line.split(":", 1)[1].strip()
                if any(keyword.lower() in name.lower() for keyword in SECURITY_KEYWORDS):
                    detected_items.append(("service", name))
                    listbox.insert(tk.END, f"[서비스] {name}")
    except Exception as e:
        print("서비스 검색 오류:", e)

    # 레지스트리 기반 탐지
    try:
        uninstall_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_path) as key:
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        if any(keyword.lower() in display_name.lower() for keyword in SECURITY_KEYWORDS):
                            detected_items.append(("registry", display_name))
                            listbox.insert(tk.END, f"[프로그램] {display_name}")
                except (FileNotFoundError, OSError, PermissionError):
                    continue
    except Exception as e:
        print("레지스트리 탐색 오류:", e)

    def handle_double_click(event=None):
        selected = listbox.curselection()
        if not selected:
            return
        idx = selected[0]
        item_type, name = detected_items[idx]

        if item_type == "service":
            confirm = messagebox.askyesno("서비스 중지/삭제", f"서비스 '{name}'을 중지 및 삭제하시겠습니까?")
            if confirm:
                try:
                    subprocess.call(f"sc stop {name}", shell=True)
                    subprocess.call(f"sc delete {name}", shell=True)
                    listbox.delete(idx)
                    messagebox.showinfo("완료", f"{name} 서비스가 삭제되었습니다.")
                except Exception as e:
                    messagebox.showerror("오류", f"오류 발생:\n{e}")
        elif item_type == "registry":
            confirm = messagebox.askyesno("삭제 확인", f"프로그램 '{name}'을 삭제하시겠습니까? (WMIC 사용)")
            if confirm:
                try:
                    subprocess.call(f'wmic product where "name=\"{name}\"" call uninstall', shell=True)
                    listbox.delete(idx)
                    messagebox.showinfo("완료", f"{name} 삭제 요청 완료.")
                except Exception as e:
                    messagebox.showerror("오류", f"삭제 실패:\n{e}")

    listbox.bind("<Double-Button-1>", handle_double_click)

# ─────────────────────────────
# 작업 스케줄러 관리
# ─────────────────────────────

def open_task_scheduler_manager():
    ts_window = tk.Toplevel(root)
    ts_window.title("작업 스케줄러 관리")
    ts_window.geometry("600x400")

    tk.Label(ts_window, text="등록된 작업 목록 (더블 클릭 시 삭제)").pack(pady=5)

    listbox = tk.Listbox(ts_window, width=85, height=20)
    listbox.pack(pady=10)

    try:
        result = subprocess.check_output('schtasks /query /fo csv /nh', shell=True, text=True, encoding='utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(result))
        for row in reader:
            if len(row) >= 1:
                task_name = row[0].strip('"')
                listbox.insert(tk.END, task_name)
    except Exception as e:
        messagebox.showerror("오류", f"작업 스케줄러 목록을 불러올 수 없습니다:\n{e}")
        return

    def delete_selected_task(event=None):
        selected = listbox.curselection()
        if not selected:
            return
        task_name = listbox.get(selected[0])
        confirm = messagebox.askyesno("삭제 확인", f"'{task_name}' 작업을 삭제하시겠습니까?")
        if confirm:
            try:
                subprocess.call(f'schtasks /delete /tn "{task_name}" /f', shell=True)
                listbox.delete(selected[0])
                messagebox.showinfo("삭제 완료", f"{task_name} 삭제 완료")
            except Exception as e:
                messagebox.showerror("삭제 실패", f"삭제 중 오류 발생:\n{e}")

    listbox.bind("<Double-Button-1>", delete_selected_task)

# ─────────────────────────────
# 불필요한 프로세스 종료
# ─────────────────────────────

def open_process_killer():
    pk_window = tk.Toplevel(root)
    pk_window.title("불필요한 프로세스 종료")
    pk_window.geometry("600x450")

    tk.Label(pk_window, text="필수 프로세스를 제외한 목록입니다.\n더블 클릭 시 종료됩니다.", fg="red").pack(pady=5)

    listbox = tk.Listbox(pk_window, width=85, height=20)
    listbox.pack(pady=10)

    essential_processes = [
        "System", "System Idle Process", "wininit.exe", "winlogon.exe", "explorer.exe",
        "svchost.exe", "csrss.exe", "services.exe", "MsMpEng.exe", "SecurityHealthService.exe",
        "conhost.exe", "SearchIndexer.exe", "RuntimeBroker.exe", "StartMenuExperienceHost.exe"
    ]

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']
            if name and name not in essential_processes:
                listbox.insert(tk.END, f"{name} (PID: {proc.pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    def kill_selected_process(event=None):
        selected = listbox.curselection()
        if not selected:
            return
        selected_item = listbox.get(selected[0])
        pid = int(selected_item.split("PID: ")[1].rstrip(")"))
        confirm = messagebox.askyesno("종료 확인", f"{selected_item}\n이 프로세스를 종료하시겠습니까?")
        if confirm:
            try:
                proc = psutil.Process(pid)
                proc.kill()
                listbox.delete(selected[0])
                messagebox.showinfo("종료됨", f"{selected_item} 종료 완료")
            except Exception as e:
                messagebox.showerror("오류", f"프로세스 종료 실패:\n{e}")

    listbox.bind("<Double-Button-1>", kill_selected_process)
    
# ─────────────────────────────
# 자동 종료 예약
# ─────────────────────────────

def open_shutdown_scheduler():
    sd_window = tk.Toplevel(root)
    sd_window.title("자동 종료 예약")
    sd_window.geometry("300x180")

    tk.Label(sd_window, text="몇 분 후 종료할까요?").pack(pady=10)
    time_entry = tk.Entry(sd_window)
    time_entry.pack(pady=5)

    def schedule_shutdown():
        try:
            minutes = int(time_entry.get())
            seconds = minutes * 60
            subprocess.call(f"shutdown -s -t {seconds}", shell=True)
            messagebox.showinfo("예약 완료", f"{minutes}분 후 종료가 예약되었습니다.")
        except:
            messagebox.showerror("오류", "숫자를 정확히 입력해주세요.")

    def cancel_shutdown():
        subprocess.call("shutdown -a", shell=True)
        messagebox.showinfo("취소 완료", "예약된 종료가 취소되었습니다.")

    tk.Button(sd_window, text="종료 예약", command=schedule_shutdown).pack(pady=5)
    tk.Button(sd_window, text="종료 취소", command=cancel_shutdown).pack(pady=5)

# ─────────────────────────────
# 서비스 관리
# ─────────────────────────────

def open_service_manager():
    svc_window = tk.Toplevel(root)
    svc_window.title("서비스 관리")
    svc_window.geometry("600x450")

    tk.Label(svc_window, text="중지 또는 삭제할 서비스를 선택하세요").pack(pady=5)

    listbox = tk.Listbox(svc_window, width=85, height=20)
    listbox.pack(pady=10)

    ESSENTIAL_SERVICES = [
        "WinDefend", "wuauserv", "EventLog", "LanmanWorkstation",
        "Dhcp", "Dnscache", "W32Time", "Themes", "AudioSrv", "Spooler"
    ]

    try:
        result = subprocess.check_output("sc query state= all", shell=True, text=True, encoding="utf-8", errors="ignore")
        lines = result.splitlines()
        for line in lines:
            if line.strip().startswith("SERVICE_NAME:"):
                svc_name = line.strip().split(":", 1)[1].strip()
                if svc_name not in ESSENTIAL_SERVICES:
                    listbox.insert(tk.END, svc_name)
    except Exception as e:
        messagebox.showerror("오류", f"서비스 목록을 불러오지 못했습니다:\n{e}")
        return

    def stop_service():
        selected = listbox.curselection()
        if not selected:
            return
        svc_name = listbox.get(selected[0])
        confirm = messagebox.askyesno("서비스 중지", f"{svc_name} 서비스를 중지하시겠습니까?")
        if confirm:
            try:
                subprocess.call(f"sc stop {svc_name}", shell=True)
                messagebox.showinfo("중지됨", f"{svc_name} 서비스가 중지되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"중지 실패:\n{e}")

    def delete_service():
        selected = listbox.curselection()
        if not selected:
            return
        svc_name = listbox.get(selected[0])
        confirm = messagebox.askyesno("서비스 삭제", f"{svc_name} 서비스를 삭제하시겠습니까?")
        if confirm:
            try:
                subprocess.call(f"sc delete {svc_name}", shell=True)
                listbox.delete(selected[0])
                messagebox.showinfo("삭제됨", f"{svc_name} 서비스가 삭제되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"삭제 실패:\n{e}")

    tk.Button(svc_window, text="선택한 서비스 중지", command=stop_service).pack(pady=5)
    tk.Button(svc_window, text="선택한 서비스 삭제", command=delete_service).pack(pady=5)

# ─────────────────────────────
# 개선 기능 메뉴
# ─────────────────────────────

def open_improvement_menu():
    improve_window = tk.Toplevel(root)
    improve_window.title("컴퓨터 성능 개선")
    improve_window.geometry("300x420")

    tk.Label(improve_window, text="실행할 기능을 선택하세요", font=("Arial", 12)).pack(pady=15)

    tk.Button(improve_window, text="디스크 정리", width=25, command=open_disk_cleanup_window).pack(pady=5)
    tk.Button(improve_window, text="시작 프로그램 관리", width=25, command=open_startup_manager).pack(pady=5)
    tk.Button(improve_window, text="보안 프로그램 삭제", width=25, command=open_security_program_manager).pack(pady=5)
    tk.Button(improve_window, text="작업 스케줄러 관리", width=25, command=open_task_scheduler_manager).pack(pady=5)
    tk.Button(improve_window, text="불필요한 프로세스 종료", width=25, command=open_process_killer).pack(pady=5)
    tk.Button(improve_window, text="자동 종료 예약", width=25, command=open_shutdown_scheduler).pack(pady=5)  # ✅ 추가됨
    tk.Button(improve_window, text="서비스 관리", width=25, command=open_service_manager).pack(pady=5)        # ✅ 추가됨


# ─────────────────────────────
# 메인 GUI
# ─────────────────────────────

root = tk.Tk()
root.title("컴퓨터 성능 개선 도우미")
root.geometry("300x230")
root.resizable(False, False)

label = tk.Label(root, text="무엇을 하시겠습니까?", font=("Arial", 14))
label.pack(pady=20)

check_btn = tk.Button(root, text="컴퓨터 상태 점검", width=25, command=check_system_status)
check_btn.pack(pady=10)

improve_btn = tk.Button(root, text="컴퓨터 상태 개선", width=25, command=open_improvement_menu)
improve_btn.pack(pady=10)

root.mainloop()
