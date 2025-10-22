from pathlib import Path

from loadcell_analysis.analysis.runner import run_analysis


def main():
    try:
        cwd = Path.cwd()
        log_files = [
            file for file in cwd.iterdir()
            if file.is_file() and file.name.endswith('log.xlsx') and not file.name.startswith('~')
        ]

        if not log_files:
            raise TypeError("Cannot find any log in this folder!!!")

        if len(log_files) > 1:
            raise TypeError("There's more than one log file in this folder!!! Please just keep only one")

        config_path = cwd / 'config.yaml'

        result = run_analysis(
            config_path=config_path,
            log_path=log_files[0],
            data_root=cwd,
            output_dir=None,
            auto_export=True,
            progress=None
        )

        print("Analysis finished.")
        for entry in result["results"]:
            if entry.output_path:
                print(f"  Exported: {entry.output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
