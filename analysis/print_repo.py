import os
import argparse
import json

def get_all_files(base_path, target_dir, include_subdirs=True, excluded_dirs=None, excluded_files=None, excluded_extensions=None):
    if excluded_dirs is None:
        excluded_dirs = []
    if excluded_files is None:
        excluded_files = []
    if excluded_extensions is None:
        excluded_extensions = []
    
    all_files = []
    for root, dirs, files in os.walk(os.path.join(base_path, target_dir)):
        if not include_subdirs:
            dirs[:] = []  # Clear the dirs list to prevent traversing subdirectories
        else:
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file not in excluded_files and not any(file.endswith(ext) for ext in excluded_extensions):
                all_files.append(os.path.relpath(os.path.join(root, file), base_path))
    
    return all_files

def generate_repo_content(base_path, all_files, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        for file_path in all_files:
            full_path = os.path.join(base_path, file_path)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as input_file:
                        content = input_file.read()
                    file.write(f"File: {file_path}\n")
                    file.write(f"Content:\n{content}\n")
                    file.write("-" * 50 + "\n")
                except Exception as e:
                    file.write(f"File: {file_path}\n")
                    file.write(f"Error reading file: {str(e)}\n")
                    file.write("-" * 50 + "\n")
    print(f"File '{output_file}' generated successfully.")

def process_config(config, script_dir):
    base_path = config.get('base_path', '..')
    if not os.path.isabs(base_path):
        base_path = os.path.abspath(os.path.join(script_dir, base_path))
    
    output_dir = config.get('output_dir', 'repo_context')
    full_output_dir = os.path.join(script_dir, output_dir)
    os.makedirs(full_output_dir, exist_ok=True)
    
    for output in config['outputs']:
        all_files = []
        for target_dir in output.get('target_dirs', []):
            all_files.extend(get_all_files(
                base_path, 
                target_dir, 
                include_subdirs=not output.get('exclude_subdirs', False),
                excluded_dirs=output.get('excluded_dirs', []),
                excluded_files=output.get('excluded_files', []),
                excluded_extensions=output.get('excluded_extensions', [])
            ))
        
        output_file = os.path.join(full_output_dir, output['output_file'])
        generate_repo_content(base_path, all_files, output_file)

def main():
    parser = argparse.ArgumentParser(description="Generate repository content file(s).")
    parser.add_argument("--config", default="repo_context_config.json", help="Path to JSON configuration file")
    parser.add_argument("--base_path", help="Base path of the repository")
    parser.add_argument("--output", help="Output file name")
    parser.add_argument("--target_dirs", nargs='+', help="Target directories to process")
    parser.add_argument("--exclude_subdirs", action="store_true", help="Exclude subdirectories of target directories")
    parser.add_argument("--excluded_dirs", nargs='+', help="Directories to exclude")
    parser.add_argument("--excluded_files", nargs='+', help="Files to exclude")
    parser.add_argument("--excluded_extensions", nargs='+', help="File extensions to exclude")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    if args.config:
        config_path = os.path.join(script_dir, args.config) if not os.path.isabs(args.config) else args.config
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        process_config(config, script_dir)
    else:
        config = {
            'base_path': args.base_path or os.path.dirname(script_dir),
            'output_dir': 'repo_context',
            'outputs': [{
                'output_file': args.output or "repo_content.txt",
                'target_dirs': args.target_dirs or ["scripts", "config", "docs"],
                'exclude_subdirs': args.exclude_subdirs,
                'excluded_dirs': args.excluded_dirs or [],
                'excluded_files': args.excluded_files or [],
                'excluded_extensions': args.excluded_extensions or []
            }]
        }
        process_config(config, script_dir)

if __name__ == "__main__":
    main()