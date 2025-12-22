import argparse

def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="kanban",
        description="CLI-Kanban: Command-line Kanban task management tool",
        epilog="Use 'kanban <command> -h' for help on a specific command"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Auth commands
    signup_parser = subparsers.add_parser("signup", help="Register a new user")
    signup_parser.add_argument("--username", required=True, help="Username")
    signup_parser.add_argument("--password", required=True, help="Password")
    # Email is required to satisfy DB schema validator
    signup_parser.add_argument("--email", required=True, help="Email address")
    signup_parser.add_argument("--role", default="Members", choices=["Members", "Hashira", "Boss"], help="User role")
    signup_parser.add_argument("--licence", "--license", dest="licence_key", required=True, help="Licence key in AAAA-BBBB-CCCC-DDDD format")
    
    login_parser = subparsers.add_parser("login", help="Login to the system")
    login_parser.add_argument("--username", required=True, help="Username")
    login_parser.add_argument("--password", required=True, help="Password")
    
    signout_parser = subparsers.add_parser("signout", help="Sign out from the system")
    
    # Board commands
    create_board = subparsers.add_parser("create-board", help="Create a new board (Boss only)")
    create_board.add_argument("--name", required=True, help="Board name")
    
    list_boards = subparsers.add_parser("list-boards", help="List all boards")
    
    view_board = subparsers.add_parser("view-board", help="View tasks in a board")
    view_board.add_argument("--name", required=True, help="Board name")
    
    delete_board = subparsers.add_parser("delete-board", help="Delete a board (Boss only)")
    delete_board.add_argument("--name", required=True, help="Board name")
    
    # Task commands
    add_task = subparsers.add_parser("add-task", help="Add a task (Hashira or Boss)")
    add_task.add_argument("--board", required=True, help="Board name")
    add_task.add_argument("--title", required=True, help="Task title")
    add_task.add_argument("--column", default="TODO", choices=["TODO", "DOING", "DONE"], help="Column name (default: TODO)")
    add_task.add_argument("--desc", help="Task description")
    add_task.add_argument("--due", help="Due date (YYYY-MM-DD)")
    add_task.add_argument("--priority", choices=["high", "medium", "low"], default="medium")
    
    edit_task = subparsers.add_parser("edit-task", help="Edit a task (Hashira or Boss)")
    edit_task.add_argument("--board", required=True, help="Board name")
    edit_task.add_argument("--title", required=True, help="Task title to edit")
    edit_task.add_argument("--new-title", help="New title")
    edit_task.add_argument("--desc", help="New description")
    edit_task.add_argument("--priority", choices=["high", "medium", "low"])
    
    move_task = subparsers.add_parser("move-task", help="Move task (Hashira or Boss)")
    move_task.add_argument("--board", required=True, help="Board name")
    move_task.add_argument("--title", required=True, help="Task title")
    move_task.add_argument("--to", required=True, choices=["TODO", "DOING", "DONE"], help="Target column")
    
    delete_task = subparsers.add_parser("delete-task", help="Delete a task (Hashira or Boss)")
    delete_task.add_argument("--board", required=True, help="Board name")
    delete_task.add_argument("--title", required=True, help="Task title")
    
    # Search/Filter commands
    search = subparsers.add_parser("search", help="Search tasks")
    search.add_argument("--board", required=True, help="Board name")
    search.add_argument("--keyword", required=True, help="Search keyword")
    
    return parser