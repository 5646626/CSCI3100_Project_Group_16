from tabulate import tabulate

class OutputFormatter:
    """Format output for the CLI."""
    
    @staticmethod
    def print_board_view(board_name: str, columns: list, tasks_by_column: dict):
        """Print board as ASCII table with task details."""
        print(f"\n{'='*100}")
        print(f"{'BOARD':^100}")
        print(f"{board_name:^100}")
        print(f"{'='*100}\n")
        
        # Create table rows
        table_data = []
        max_rows = max(
            [len(tasks_by_column.get(col, [])) for col in columns],
            default=0
        )
        
        if max_rows == 0:
            print("No tasks in this board.\n")
            return
        
        for row_idx in range(max_rows):
            row = []
            for col in columns:
                tasks = tasks_by_column.get(col, [])
                if row_idx < len(tasks):
                    task = tasks[row_idx]
                    # Format: Title (Priority)
                    # Due date if exists
                    task_str = f"• {task.title}\n"
                    if task.priority:
                        task_str += f"  [{task.priority.upper()}]"
                    if task.due_date:
                        task_str += f" | Due: {task.due_date}"
                    row.append(task_str)
                else:
                    row.append("")
            table_data.append(row)
        
        print(tabulate(table_data, headers=columns, tablefmt="grid"))
        print()
    
    @staticmethod
    def print_task_list(tasks: list):
        """Print tasks as table."""
        data = []
        for task in tasks:
            data.append([
                str(task._id)[:8],
                task.title,
                task.column,
                task.priority,
                task.due_date or "N/A"
            ])
        
        print(tabulate(
            data,
            headers=["ID", "Title", "Column", "Priority", "Due Date"],
            tablefmt="grid"
        ))
    
    @staticmethod
    def print_success(message: str):
        """Print success message."""
        print(f"✓ {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print error message."""
        print(f"✗ Error: {message}")