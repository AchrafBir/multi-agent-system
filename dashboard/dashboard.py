import tkinter as tk
from tkinter import ttk, scrolledtext
import queue
import time
from datetime import datetime
from communication.protocol import (
    TOPIC_AGENT_STATUS_UPDATE, TOPIC_SYSTEM_LOG, TOPIC_TASK_COMPLETED, TOPIC_AGENT_REGISTER
)
from config.settings import DASHBOARD_ID

class Dashboard:
    def __init__(self, root, message_bus, task_queue):
        self.root = root
        self.message_bus = message_bus
        self.task_queue = task_queue
        self.agent_id = DASHBOARD_ID
        
        self.root.title("Multi-Agent System Dashboard")
        self.root.geometry("1400x900")
        
        self.setup_styles()

        self.gui_queue = queue.Queue()
        self.worker_metadata = {}
        self.start_time = time.time()
        self.task_completion_times = []
        
        self.monitoring_active = True
        
        self._setup_widgets()
        self.subscribe_to_topics()
        self.process_gui_queue()

    def setup_styles(self):
        style = ttk.Style()
        
        style.configure("Treeview", background="#f8f9fa", foreground="#333333")
        style.configure("Treeview.Heading", background="#e9ecef", foreground="#495057", font=("Arial", 10, "bold"))
        
        style.configure("status.TLabel", font=("Arial", 10, "bold"))

    def _setup_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="Multi-Agent System Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.uptime_label = ttk.Label(header_frame, text="Uptime: 00:00:00", 
                                     font=("Arial", 10))
        self.uptime_label.pack(side=tk.RIGHT)
        
        metrics_frame = ttk.Frame(main_frame)
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        queue_frame = ttk.LabelFrame(metrics_frame, text="Task Queue", padding="10")
        queue_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.task_queue_label = ttk.Label(queue_frame, text="Tasks in Queue: 0", 
                                         font=("Arial", 12, "bold"))
        self.task_queue_label.pack()
        
        completed_frame = ttk.LabelFrame(metrics_frame, text="Completed Tasks", padding="10")
        completed_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.completed_tasks_label = ttk.Label(completed_frame, text="Completed: 0", 
                                              font=("Arial", 12, "bold"))
        self.completed_tasks_label.pack()
        self.completed_count = 0
        
        perf_frame = ttk.LabelFrame(metrics_frame, text="Performance", padding="10")
        perf_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.avg_completion_label = ttk.Label(perf_frame, text="Avg Time: --", 
                                             font=("Arial", 10))
        self.avg_completion_label.pack()
        
        self.throughput_label = ttk.Label(perf_frame, text="Tasks/min: --", 
                                         font=("Arial", 10))
        self.throughput_label.pack()
        
        resources_row = ttk.Frame(main_frame)
        resources_row.pack(fill=tk.X, pady=(0, 10))
        
        agent_resources_frame = ttk.LabelFrame(resources_row, text="Agent Resources Summary", padding="10")
        agent_resources_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.avg_cpu_label = ttk.Label(agent_resources_frame, text="Avg CPU: 0%", font=("Arial", 10))
        self.avg_cpu_label.pack()
        
        self.avg_memory_label = ttk.Label(agent_resources_frame, text="Avg Memory: 0%", font=("Arial", 10))
        self.avg_memory_label.pack()
        
        self.high_resource_agents_label = ttk.Label(agent_resources_frame, text="High Usage Agents: 0", font=("Arial", 10))
        self.high_resource_agents_label.pack()
        
        node_frame = ttk.LabelFrame(resources_row, text="Node Distribution", padding="10")
        node_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.total_nodes_label = ttk.Label(node_frame, text="Total Nodes: 0", font=("Arial", 10))
        self.total_nodes_label.pack()
        
        self.agents_per_node_label = ttk.Label(node_frame, text="Avg Agents/Node: 0", font=("Arial", 10))
        self.agents_per_node_label.pack()
        
        perf_summary_frame = ttk.LabelFrame(resources_row, text="Agent Performance", padding="10")
        perf_summary_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.most_productive_label = ttk.Label(perf_summary_frame, text="Most Productive: --", font=("Arial", 10))
        self.most_productive_label.pack()
        
        self.total_agent_tasks_label = ttk.Label(perf_summary_frame, text="Total Agent Tasks: 0", font=("Arial", 10))
        self.total_agent_tasks_label.pack()
        
        agent_frame = ttk.LabelFrame(main_frame, text="Worker Agents Status", padding="10")
        agent_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tree_frame = ttk.Frame(agent_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.agent_status_tree = ttk.Treeview(tree_frame, 
                                             columns=("ID", "Node", "Status", "Task", "CPU", "Memory", "Tasks Done", "Last Update"), 
                                             show="headings", height=8)
        
        self.agent_status_tree.heading("ID", text="Agent ID")
        self.agent_status_tree.heading("Node", text="Node ID")
        self.agent_status_tree.heading("Status", text="Status")
        self.agent_status_tree.heading("Task", text="Current Task")
        self.agent_status_tree.heading("CPU", text="CPU %")
        self.agent_status_tree.heading("Memory", text="Memory %")
        self.agent_status_tree.heading("Tasks Done", text="Tasks Done")
        self.agent_status_tree.heading("Last Update", text="Last Update")
        
        self.agent_status_tree.column("ID", width=120)
        self.agent_status_tree.column("Node", width=120)
        self.agent_status_tree.column("Status", width=70)
        self.agent_status_tree.column("Task", width=150)
        self.agent_status_tree.column("CPU", width=60)
        self.agent_status_tree.column("Memory", width=70)
        self.agent_status_tree.column("Tasks Done", width=80)
        self.agent_status_tree.column("Last Update", width=100)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.agent_status_tree.yview)
        self.agent_status_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.agent_status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.agent_status_tree.tag_configure("busy", background="#fff3cd")
        self.agent_status_tree.tag_configure("idle", background="#d4edda")
        self.agent_status_tree.tag_configure("error", background="#f8d7da")
        self.agent_status_tree.tag_configure("high_cpu", background="#ffe6e6")
        self.agent_status_tree.tag_configure("high_memory", background="#fff0e6")
        
        log_frame = ttk.LabelFrame(main_frame, text="System Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(0, 5))
        
        clear_log_btn = ttk.Button(log_controls, text="Clear Log", command=self.clear_log)
        clear_log_btn.pack(side=tk.RIGHT)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_cb = ttk.Checkbutton(log_controls, text="Auto-scroll", 
                                        variable=self.auto_scroll_var)
        auto_scroll_cb.pack(side=tk.RIGHT, padx=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', 
                                                 wrap=tk.WORD, height=12,
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_configure("INFO", foreground="#0066cc")
        self.log_text.tag_configure("WARNING", foreground="#ff8800")
        self.log_text.tag_configure("ERROR", foreground="#cc0000")
        self.log_text.tag_configure("timestamp", foreground="#666666")

    def subscribe_to_topics(self):
        self.message_bus.subscribe(TOPIC_AGENT_REGISTER, 
                                  lambda msg: self.gui_queue.put((self.handle_agent_update, msg)))
        self.message_bus.subscribe(TOPIC_AGENT_STATUS_UPDATE, 
                                  lambda msg: self.gui_queue.put((self.handle_agent_update, msg)))
        self.message_bus.subscribe(TOPIC_SYSTEM_LOG, 
                                  lambda msg: self.gui_queue.put((self.update_log, msg)))
        self.message_bus.subscribe(TOPIC_TASK_COMPLETED, 
                                  lambda msg: self.gui_queue.put((self.update_completed_count, msg)))

    def process_gui_queue(self):
        try:
            while not self.gui_queue.empty():
                callback, msg = self.gui_queue.get_nowait()
                callback(msg)
        finally:
            self.update_task_queue_size()
            self.update_uptime()
            self.update_performance_metrics()
            self.update_agent_resource_summary()
            self.root.after(1000, self.process_gui_queue)

    def handle_agent_update(self, message):
        payload = message["payload"]
        agent_id = payload.get("agent_id", message.get("sender_id"))

        if not agent_id.startswith("worker_"):
            return
        
        if "node_id" in payload:
            self.worker_metadata.setdefault(agent_id, {})["node_id"] = payload["node_id"]
        
        current_metadata = self.worker_metadata.get(agent_id, {})
        status = payload.get("status", current_metadata.get("status", "UNKNOWN"))
        task_id = payload.get("task_id", current_metadata.get("task_id", ""))
        node_id = current_metadata.get("node_id", "N/A")
        last_update = datetime.now().strftime("%H:%M:%S")
        
        cpu_usage = payload.get("cpu_usage", current_metadata.get("cpu_usage", 0))
        memory_usage = payload.get("memory_usage", current_metadata.get("memory_usage", 0))
        tasks_completed = payload.get("tasks_completed", current_metadata.get("tasks_completed", 0))

        metadata = self.worker_metadata.setdefault(agent_id, {})
        metadata.update({
            "status": status,
            "task_id": task_id,
            "last_update": last_update,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "tasks_completed": tasks_completed
        })
        
        tags = []
        if status == "BUSY":
            tags.append("busy")
        elif status == "IDLE":
            tags.append("idle")
        elif status in ["ERROR", "FAILED"]:
            tags.append("error")
            
        if cpu_usage > 80:
            tags.append("high_cpu")
        if memory_usage > 85:
            tags.append("high_memory")
        
        cpu_display = f"{cpu_usage:.1f}%" if cpu_usage > 0 else "--"
        memory_display = f"{memory_usage:.1f}%" if memory_usage > 0 else "--"
        tasks_display = str(tasks_completed) if tasks_completed > 0 else "0"
        
        values_tuple = (agent_id, node_id, status, task_id, cpu_display, memory_display, tasks_display, last_update)
        if self.agent_status_tree.exists(agent_id):
            self.agent_status_tree.item(agent_id, values=values_tuple, tags=tags)
        else:
            self.agent_status_tree.insert("", "end", iid=agent_id, values=values_tuple, tags=tags)

    def update_log(self, message):
        log_entry = message["payload"]["log"]
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.log_text.config(state='normal')
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        if "ERROR" in log_entry.upper():
            self.log_text.insert(tk.END, log_entry + "\n", "ERROR")
        elif "WARNING" in log_entry.upper():
            self.log_text.insert(tk.END, log_entry + "\n", "WARNING")
        else:
            self.log_text.insert(tk.END, log_entry + "\n", "INFO")
        
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        
        self.log_text.config(state='disabled')
        
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', '100.0')
            self.log_text.config(state='disabled')

    def update_task_queue_size(self):
        size = self.task_queue.qsize()
        self.task_queue_label.config(text=f"Tasks in Queue: {size}")
        
        if size > 1000:
            self.task_queue_label.config(foreground="#cc0000")
        elif size > 100:
            self.task_queue_label.config(foreground="#ff8800")
        else:
            self.task_queue_label.config(foreground="#0066cc")

    def update_completed_count(self, message):
        self.completed_count += 1
        self.completed_tasks_label.config(text=f"Completed: {self.completed_count}")
        
        current_time = time.time()
        self.task_completion_times.append(current_time)
        
        if len(self.task_completion_times) > 100:
            self.task_completion_times.pop(0)

    def update_uptime(self):
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        self.uptime_label.config(text=f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_performance_metrics(self):
        if len(self.task_completion_times) >= 2:
            time_window = 60
            current_time = time.time()
            recent_completions = [t for t in self.task_completion_times 
                                if current_time - t <= time_window]
            tasks_per_minute = len(recent_completions)
            
            self.throughput_label.config(text=f"Tasks/min: {tasks_per_minute}")
            
            if len(self.task_completion_times) >= 2:
                avg_interval = (self.task_completion_times[-1] - self.task_completion_times[0]) / (len(self.task_completion_times) - 1)
                self.avg_completion_label.config(text=f"Avg Time: {avg_interval:.1f}s")

    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')

    def update_agent_resource_summary(self):
        if not self.worker_metadata:
            return
            
        cpu_values = [w.get("cpu_usage", 0) for w in self.worker_metadata.values() if w.get("cpu_usage", 0) > 0]
        memory_values = [w.get("memory_usage", 0) for w in self.worker_metadata.values() if w.get("memory_usage", 0) > 0]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
        
        self.avg_cpu_label.config(text=f"Avg CPU: {avg_cpu:.1f}%")
        self.avg_memory_label.config(text=f"Avg Memory: {avg_memory:.1f}%")
        
        high_resource_count = sum(1 for w in self.worker_metadata.values() 
                                 if w.get("cpu_usage", 0) > 80 or w.get("memory_usage", 0) > 85)
        self.high_resource_agents_label.config(text=f"High Usage Agents: {high_resource_count}")
        
        nodes = set(w.get("node_id", "N/A") for w in self.worker_metadata.values())
        nodes.discard("N/A")
        total_nodes = len(nodes)
        avg_agents_per_node = len(self.worker_metadata) / total_nodes if total_nodes > 0 else 0
        
        self.total_nodes_label.config(text=f"Total Nodes: {total_nodes}")
        self.agents_per_node_label.config(text=f"Avg Agents/Node: {avg_agents_per_node:.1f}")
        
        most_productive_agent = max(self.worker_metadata.items(), 
                                   key=lambda x: x[1].get("tasks_completed", 0),
                                   default=(None, {}))
        
        if most_productive_agent[0]:
            agent_name = most_productive_agent[0].replace("worker_", "")
            tasks_done = most_productive_agent[1].get("tasks_completed", 0)
            self.most_productive_label.config(text=f"Most Productive: {agent_name} ({tasks_done})")
        else:
            self.most_productive_label.config(text="Most Productive: --")
        
        total_agent_tasks = sum(w.get("tasks_completed", 0) for w in self.worker_metadata.values())
        self.total_agent_tasks_label.config(text=f"Total Agent Tasks: {total_agent_tasks}")

    def monitor_resources(self):
        pass
        
    def update_resource_display(self, resource_data):
        pass
        
    def get_resource_stats(self):
        if not self.worker_metadata:
            return None
            
        cpu_values = [w.get("cpu_usage", 0) for w in self.worker_metadata.values() if w.get("cpu_usage", 0) > 0]
        memory_values = [w.get("memory_usage", 0) for w in self.worker_metadata.values() if w.get("memory_usage", 0) > 0]
        
        return {
            'agents_count': len(self.worker_metadata),
            'avg_cpu': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            'avg_memory': sum(memory_values) / len(memory_values) if memory_values else 0,
            'high_cpu_agents': sum(1 for w in self.worker_metadata.values() if w.get("cpu_usage", 0) > 80),
            'high_memory_agents': sum(1 for w in self.worker_metadata.values() if w.get("memory_usage", 0) > 85),
            'total_agent_tasks': sum(w.get("tasks_completed", 0) for w in self.worker_metadata.values())
        }
        
        busy_workers = sum(1 for w in self.worker_metadata.values() if w.get("status") == "BUSY")
        idle_workers = sum(1 for w in self.worker_metadata.values() if w.get("status") == "IDLE")
        total_workers = len(self.worker_metadata)
        
        return {
            "total_workers": total_workers,
            "busy_workers": busy_workers,
            "idle_workers": idle_workers,
            "queue_size": self.task_queue.qsize(),
            "completed_tasks": self.completed_count,
            "uptime": int(time.time() - self.start_time)
        }