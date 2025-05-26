# Import necessary Python standard libraries
import json  # For processing JSON format data
import os  # For operating with file system, handling files and directory paths
import platform  # For getting current operating system information
import shutil  # For checking if executables exist in PATH
import subprocess  # For creating and managing subprocesses
import sys  # For accessing Python interpreter related variables and functions


def check_prerequisites():
    """
    Check if necessary prerequisites are installed
    
    Returns:
        tuple: (python_ok, uv_installed, uvx_installed, ppt_server_installed)
    """
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version.major >= 3 and python_version.minor >= 6

    # Check if uv/uvx is installed
    uv_installed = shutil.which("uv") is not None
    uvx_installed = shutil.which("uvx") is not None

    # Check if office-powerpoint-mcp-server is already installed via pip
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "office-powerpoint-mcp-server"],
            capture_output=True,
            text=True,
            check=False
        )
        ppt_server_installed = result.returncode == 0
    except Exception:
        ppt_server_installed = False

    return (python_ok, uv_installed, uvx_installed, ppt_server_installed)

def setup_venv():
    """
    Function to set up Python virtual environment
    
    Features:
    - Checks if Python version meets requirements (3.6+)
    - Creates Python virtual environment (if it doesn't exist)
    - Installs required dependencies in the newly created virtual environment
    
    No parameters required
    
    Returns: Path to Python interpreter in the virtual environment
    """
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print("Error: Python 3.6 or higher is required.")
        sys.exit(1)

    # Get absolute path of the directory containing the current script
    base_path = os.path.abspath(os.path.dirname(__file__))
    # Set virtual environment directory path
    venv_path = os.path.join(base_path, '.venv')

    # Determine pip and python executable paths based on operating system
    is_windows = platform.system() == "Windows"
    if is_windows:
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        pip_path = os.path.join(venv_path, 'bin', 'pip')
        python_path = os.path.join(venv_path, 'bin', 'python')

    # Check if virtual environment already exists and is valid
    venv_exists = os.path.exists(venv_path)
    pip_exists = os.path.exists(pip_path)

    if not venv_exists or not pip_exists:
        print("Creating new virtual environment...")
        # Remove existing venv if it's invalid
        if venv_exists and not pip_exists:
            print("Existing virtual environment is incomplete, recreating it...")
            try:
                shutil.rmtree(venv_path)
            except Exception as e:
                print(f"Warning: Could not remove existing virtual environment: {e}")
                print("Please delete the .venv directory manually and try again.")
                sys.exit(1)

        # Create virtual environment
        try:
            subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
            print("Virtual environment created successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print("Valid virtual environment already exists.")

    # Double-check that pip exists after creating venv
    if not os.path.exists(pip_path):
        print(f"Error: pip executable not found at {pip_path}")
        print("Try creating the virtual environment manually with: python -m venv .venv")
        sys.exit(1)

    # Install or update dependencies
    print("\nInstalling requirements...")
    try:
        # Install mcp package
        subprocess.run([pip_path, 'install', 'mcp[cli]'], check=True)
        # Install python-pptx package
        subprocess.run([pip_path, 'install', 'python-pptx'], check=True)

        # Also install dependencies from requirements.txt if it exists
        requirements_path = os.path.join(base_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            subprocess.run([pip_path, 'install', '-r', requirements_path], check=True)


        print("Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Could not execute {pip_path}")
        print("Try activating the virtual environment manually and installing requirements:")
        if is_windows:
            print(".venv\\Scripts\\activate")
        else:
            print("source .venv/bin/activate")
        print("pip install mcp[cli] python-pptx")
        sys.exit(1)

    return python_path

def generate_mcp_config_local(python_path):
    """
    Generate MCP configuration for locally installed office-powerpoint-mcp-server
    
    Parameters:
    - python_path: Path to Python interpreter in the virtual environment
    
    Returns: Path to the generated config file
    """
    # Get absolute path of the directory containing the current script
    base_path = os.path.abspath(os.path.dirname(__file__))

    # Path to PowerPoint Server script
    server_script_path = os.path.join(base_path, 'ppt_mcp_server.py')

    # Create MCP configuration dictionary
    config = {
        "mcpServers": {
            "ppt": {
                "command": python_path,
                "args": [server_script_path],
                "env": {
                    "PYTHONPATH": base_path
                }
            }
        }
    }

    # Save configuration to JSON file
    config_path = os.path.join(base_path, 'mcp-config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)  # indent=2 gives the JSON file good formatting

    return config_path

def generate_mcp_config_uvx():
    """
    Generate MCP configuration for PyPI-installed office-powerpoint-mcp-server using UVX
    
    Returns: Path to the generated config file
    """
    # Get absolute path of the directory containing the current script
    base_path = os.path.abspath(os.path.dirname(__file__))

    # Create MCP configuration dictionary
    config = {
        "mcpServers": {
            "ppt": {
                "command": "uvx",
                "args": ["--from", "office-powerpoint-mcp-server", "ppt_mcp_server"],
                "env": {}
            }
        }
    }

    # Save configuration to JSON file
    config_path = os.path.join(base_path, 'mcp-config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)  # indent=2 gives the JSON file good formatting

    return config_path

def generate_mcp_config_module():
    """
    Generate MCP configuration for PyPI-installed office-powerpoint-mcp-server using Python module
    
    Returns: Path to the generated config file
    """
    # Get absolute path of the directory containing the current script
    base_path = os.path.abspath(os.path.dirname(__file__))

    # Create MCP configuration dictionary
    config = {
        "mcpServers": {
            "ppt": {
                "command": sys.executable,
                "args": ["-m", "office_powerpoint_mcp_server"],
                "env": {}
            }
        }
    }

    # Save configuration to JSON file
    config_path = os.path.join(base_path, 'mcp-config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)  # indent=2 gives the JSON file good formatting

    return config_path

def install_from_pypi():
    """
    Install office-powerpoint-mcp-server from PyPI
    
    Returns: True if successful, False otherwise
    """
    print("\nInstalling office-powerpoint-mcp-server from PyPI...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "office-powerpoint-mcp-server"], check=True)
        print("office-powerpoint-mcp-server successfully installed from PyPI!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install office-powerpoint-mcp-server from PyPI.")
        return False

def print_config_instructions(config_path):
    """
    Print instructions for using the generated config
    
    Parameters:
    - config_path: Path to the generated config file
    """
    print(f"\nMCP configuration has been written to: {config_path}")

    with open(config_path) as f:
        config = json.load(f)

    print("\nMCP configuration for Claude Desktop:")
    print(json.dumps(config, indent=2))

    # Provide instructions for adding configuration to Claude Desktop configuration file
    if platform.system() == "Windows":
        claude_config_path = os.path.expandvars("%APPDATA%\\Claude\\claude_desktop_config.json")
    else:  # macOS
        claude_config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")

    print(f"\nTo use with Claude Desktop, merge this configuration into: {claude_config_path}")

def create_package_structure():
    """
    Create necessary package structure
    """
    # Get absolute path of the directory containing the current script
    base_path = os.path.abspath(os.path.dirname(__file__))

    # Create __init__.py file
    init_path = os.path.join(base_path, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('# PowerPoint MCP Server')
        print(f"Created __init__.py at: {init_path}")

    # Create requirements.txt file
    requirements_path = os.path.join(base_path, 'requirements.txt')
    if not os.path.exists(requirements_path):
        with open(requirements_path, 'w') as f:
            f.write('mcp[cli]\npython-pptx\n')
        print(f"Created requirements.txt at: {requirements_path}")

# Main execution entry point
if __name__ == '__main__':
    # Check prerequisites
    python_ok, uv_installed, uvx_installed, ppt_server_installed = check_prerequisites()

    if not python_ok:
        print("Error: Python 3.6 or higher is required.")
        sys.exit(1)

    print("PowerPoint MCP Server Setup")
    print("===========================\n")

    # Create necessary files
    create_package_structure()

    # If office-powerpoint-mcp-server is already installed, offer config options
    if ppt_server_installed:
        print("office-powerpoint-mcp-server is already installed via pip.")

        if uvx_installed:
            print("\nOptions:")
            print("1. Generate MCP config for UVX (recommended)")
            print("2. Generate MCP config for Python module")
            print("3. Set up local development environment")

            choice = input("\nEnter your choice (1-3): ")

            if choice == "1":
                config_path = generate_mcp_config_uvx()
                print_config_instructions(config_path)
            elif choice == "2":
                config_path = generate_mcp_config_module()
                print_config_instructions(config_path)
            elif choice == "3":
                python_path = setup_venv()
                config_path = generate_mcp_config_local(python_path)
                print_config_instructions(config_path)
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)
        else:
            print("\nOptions:")
            print("1. Generate MCP config for Python module")
            print("2. Set up local development environment")

            choice = input("\nEnter your choice (1-2): ")

            if choice == "1":
                config_path = generate_mcp_config_module()
                print_config_instructions(config_path)
            elif choice == "2":
                python_path = setup_venv()
                config_path = generate_mcp_config_local(python_path)
                print_config_instructions(config_path)
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

    # If office-powerpoint-mcp-server is not installed, offer installation options
    else:
        print("office-powerpoint-mcp-server is not installed.")

        print("\nOptions:")
        print("1. Install from PyPI (recommended)")
        print("2. Set up local development environment")

        choice = input("\nEnter your choice (1-2): ")

        if choice == "1":
            if install_from_pypi():
                if uvx_installed:
                    print("\nNow generating MCP config for UVX...")
                    config_path = generate_mcp_config_uvx()
                else:
                    print("\nUVX not found. Generating MCP config for Python module...")
                    config_path = generate_mcp_config_module()
                print_config_instructions(config_path)
        elif choice == "2":
            python_path = setup_venv()
            config_path = generate_mcp_config_local(python_path)
            print_config_instructions(config_path)
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)

    print("\nSetup complete! You can now use the PowerPoint MCP server with compatible clients like Claude Desktop.")
