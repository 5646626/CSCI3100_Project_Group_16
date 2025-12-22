import shlex
from cli.parser import create_parser
from cli.formatter import OutputFormatter
from services.auth_services import AuthService
from services.board_services import BoardService
from services.task_service import TaskService
from services.search_service import SearchService
from bson import ObjectId
from setup_schema import ensure_schema

# Session storage (for demo - in production use session management)
current_user = None

def execute_command(command_line: str):
    """Execute a single command line."""
    global current_user
    
    # Parse the command line
    try:
        args = shlex.split(command_line)
    except ValueError as e:
        print(f"✗ Error: Invalid command syntax - {e}")
        return
    
    if not args or args[0] in ["quit", "exit", "q"]:
        return False
    
    if args[0] == "help":
        parser = create_parser()
        parser.print_help()
        return True
    
    parser = create_parser()
    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return True
    
    formatter = OutputFormatter()
    
    if not parsed_args.command:
        parser.print_help()
        return True

    try:
        # Auth commands (no user required)
        if parsed_args.command == "signup":
            auth_service = AuthService()
            user_id, resolved_role = auth_service.signup(
                parsed_args.username,
                parsed_args.password,
                parsed_args.email,
                parsed_args.role,
                parsed_args.licence_key,
            )
            formatter.print_success(f"User '{parsed_args.username}' created as '{resolved_role}'")
        
        elif parsed_args.command == "login":
            auth_service = AuthService()
            current_user = auth_service.login(parsed_args.username, parsed_args.password)
            formatter.print_success(f"Logged in as '{current_user.username}' ({current_user.role})")
        
        # All other commands require login
        elif current_user is None:
            formatter.print_error("You must login first. Use: login --username <user> --password <pass>")
        
        # Board commands
        elif parsed_args.command == "create-board":
            board_service = BoardService()
            board_service.create_board(parsed_args.name, current_user._id, current_user.role)
            formatter.print_success(f"Board '{parsed_args.name}' created")
        
        elif parsed_args.command == "list-boards":
            board_service = BoardService()
            boards = board_service.list_boards(current_user._id)
            if boards:
                for board in boards:
                    print(f"  - {board.name} (columns: {', '.join(board.columns)})")
            else:
                print("No boards found")
        
        elif parsed_args.command == "view-board":
            board_service = BoardService()
            board = board_service.get_board_by_name(parsed_args.name, current_user._id)
            task_service = TaskService()
            # Group tasks by column
            tasks_by_column = {}
            for col in board.columns:
                tasks_by_column[col] = task_service.list_tasks_in_column(board._id, col)
            formatter.print_board_view(board.name, board.columns, tasks_by_column)
        
        elif parsed_args.command == "delete-board":
            board_service = BoardService()
            board_service.delete_board(parsed_args.name, current_user._id, current_user.role)
            formatter.print_success(f"Board '{parsed_args.name}' deleted")
        
        # Task commands
        elif parsed_args.command == "add-task":
            board_service = BoardService()
            board = board_service.get_board_by_name(parsed_args.board, current_user._id)
            task_service = TaskService()
            task_id = task_service.create_task(
                title=parsed_args.title,
                board_id=board._id,
                column=parsed_args.column,
                user_role=current_user.role,
                description=parsed_args.desc,
                due_date=parsed_args.due,
                priority=parsed_args.priority,
            )
            formatter.print_success(f"Task '{parsed_args.title}' created on board '{board.name}' (id: {str(task_id)[:8]})")
        
        elif parsed_args.command == "edit-task":
            board_service = BoardService()
            board = board_service.get_board_by_name(parsed_args.board, current_user._id)
            task_service = TaskService()
            # Find task by title in the board
            tasks = task_service.task_repo.find_by_board(board._id)
            task = next((t for t in tasks if t.title == parsed_args.title), None)
            if not task:
                formatter.print_error(f"Task '{parsed_args.title}' not found in board '{parsed_args.board}'")
                return True
            
            updates = {
                key: value
                for key, value in {
                    "title": parsed_args.new_title,
                    "description": parsed_args.desc,
                    "priority": parsed_args.priority,
                }.items()
                if value is not None
            }
            if not updates:
                formatter.print_error("No updates provided")
                return True

            task_service.edit_task(task._id, updates, current_user.role)
            formatter.print_success(f"Task '{parsed_args.title}' updated")
        
        elif parsed_args.command == "move-task":
            board_service = BoardService()
            board = board_service.get_board_by_name(parsed_args.board, current_user._id)
            task_service = TaskService()
            # Find task by title in the board
            tasks = task_service.task_repo.find_by_board(board._id)
            task = next((t for t in tasks if t.title == parsed_args.title), None)
            if not task:
                formatter.print_error(f"Task '{parsed_args.title}' not found in board '{parsed_args.board}'")
                return True
            
            task_service.move_task(task._id, parsed_args.to, current_user.role)
            formatter.print_success(f"Task '{parsed_args.title}' moved to {parsed_args.to}")
        
        elif parsed_args.command == "delete-task":
            board_service = BoardService()
            board = board_service.get_board_by_name(parsed_args.board, current_user._id)
            task_service = TaskService()
            # Find task by title in the board
            tasks = task_service.task_repo.find_by_board(board._id)
            task = next((t for t in tasks if t.title == parsed_args.title), None)
            if not task:
                formatter.print_error(f"Task '{parsed_args.title}' not found in board '{parsed_args.board}'")
                return True
            
            task_service.delete_task(task._id, current_user.role)
            formatter.print_success(f"Task '{parsed_args.title}' deleted")
        
        # Search command
        elif parsed_args.command == "search":
            board_service = BoardService()
            board = board_service.get_board_by_name(parsed_args.board, current_user._id)
            search_service = SearchService()
            results = search_service.search_tasks(board._id, parsed_args.keyword)
            if results:
                formatter.print_task_list(results)
            else:
                print("No matching tasks found")
        
        else:
            formatter.print_error(f"Command '{parsed_args.command}' not implemented yet")
    
    except PermissionError as e:
        formatter.print_error(str(e))
    except ValueError as e:
        formatter.print_error(str(e))
    except Exception as e:
        formatter.print_error(str(e))
    
    return True

def main():
    """Interactive REPL for Kanban CLI."""
    # Ensure DB collections and validators are in place before running
    try:
        ensure_schema()
    except Exception as e:
        print(f"Warning: Schema setup failed: {e}")
    
    print("=" * 60)
    print("CLI-Kanban: Interactive Task Management")
    print("=" * 60)
    print("Commands: signup, login, create-board, list-boards, add-task, edit-task, move-task, delete-task, search")
    print("Type 'help' for full documentation, 'quit' to exit")
    print("=" * 60)

    while True:
        try:
            command_line = input("\nkanban> ").strip()
            
            if not command_line:
                continue
            
            if not execute_command(command_line):
                print("✓ Goodbye!")
                break
        except KeyboardInterrupt:
            print("\n✓ Goodbye!")
            break
        except Exception as e:
            print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()