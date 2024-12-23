import json
from pathlib import Path
from PyInstaller.__main__ import run as pyinstaller_run
import shutil
import site
from pyloid.builder.spec import create_spec_from_json

__all__ = ['create_spec_from_json', 'cleanup_before_build', 'build_from_spec', 'get_site_packages']

def cleanup_before_build(json_path):
    """Function to clean up unnecessary files before build"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        cleanup_patterns = config.get('before_build', {}).get('cleanup_patterns', [])
        if not cleanup_patterns:
            return Exception("Cannot find cleanup patterns.")
        
        site_packages = get_site_packages()
        if not site_packages:
            raise Exception("Cannot find site-packages directory.")
            
        dist_dir = Path(f'{site_packages}')
        if not dist_dir.exists():
            raise Exception(f"Cannot find directory to clean: {dist_dir}")

        print("\033[1;34mCleaning up unnecessary files...\033[0m")
        exclude_patterns = [p[1:] for p in cleanup_patterns if p.startswith('!')]
        include_patterns = [p for p in cleanup_patterns if not p.startswith('!')]  
        
        for pattern in include_patterns:
            matching_files = list(dist_dir.glob(pattern))
            for file_path in matching_files:
                if any(file_path.match(p) for p in exclude_patterns):
                    print(f"\033[33mSkipping: {file_path}\033[0m")
                    continue
                print(f"\033[33mRemoving: {file_path}\033[0m")
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                print(f"\033[32mRemoved: {file_path}\033[0m")
        
        print("\033[1;32mFile cleanup completed.\033[0m")
        
    except Exception as e:
        raise Exception(f"\033[1;31mError occurred during file cleanup: {e}\033[0m")

def build_from_spec(spec_path):
    try:
        pyinstaller_run([
            '--clean',  # Clean temporary files
            spec_path   # Spec file path
        ])
        print("Build completed.")
    
    except Exception as e:
        raise Exception(f"Error occurred during build: {e}")

def get_site_packages():
    """
    Returns the path to the site-packages directory.
    Raises an exception if the directory is not found.
    """
    for path in site.getsitepackages():
        if 'site-packages' in path:
            return path
    raise Exception("Site-packages directory not found.")

def main():
    spec_path = create_spec_from_json('build_config.json')
    
    cleanup_before_build('build_config.json')
    
    # build_from_spec(spec_path)
    
    
    
if __name__ == "__main__":
    main()