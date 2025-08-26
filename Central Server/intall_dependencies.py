import os
import subprocess
import sys

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing: {e.cmd}")
        sys.exit(1)

def main():
    print("Starting dependency installation...")

    # Update package lists
    print("Updating package lists...")
    run_command("sudo apt update")

    # Upgrade packages
    print("Upgrading installed packages...")
    run_command("sudo apt upgrade -y")

    # Install Python and pip
    print("Installing Python and pip...")
    run_command("sudo apt install -y python3 python3-pip")

    # Install MySQL server (if needed)
    print("Installing MySQL server...")
    run_command("sudo apt install -y mysql-server")

    # Install Python libraries
    print("Installing Python libraries...")
    required_libraries = [
        "Flask",
        "mysql-connector-python",
        "pandas",
        "xlsxwriter"
    ]
    for lib in required_libraries:
        run_command(f"pip3 install {lib}")

    # Configure MySQL (optional step, ensure MySQL is running)
    print("Ensuring MySQL is running...")
    run_command("sudo systemctl start mysql")
    run_command("sudo systemctl enable mysql")

    # Allow user to setup MySQL credentials manually
    print("\nMySQL server installed. If not configured, use:")
    print("sudo mysql_secure_installation")
    print("Set up your 'Admin' user credentials as required in 'app.py'.\n")

    # Check Flask installation
    print("Verifying Flask installation...")
    try:
        import flask
        print(f"Flask version {flask.__version__} is installed.")
    except ImportError:
        print("Error: Flask is not installed properly. Please check.")

    print("\nAll dependencies are installed. You can now run your app.")

if __name__ == "__main__":
    main()
