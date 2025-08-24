import os

def main():
    if os.path.exists("dashboard_module/data.json"):
        os.remove("dashboard_module/data.json")

if __name__ == "__main__":
    main()