"""
SCSS Compiler for Flask Project
-------------------------------
This script compiles SCSS files to CSS for your Flask application.
It can be run as a standalone script or integrated with your Flask app.

Usage:
    python compile_sass.py         # Compile once
    python compile_sass.py --watch # Watch for changes and recompile
"""

import os
import time
import argparse
import sass
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
SCSS_DIR = os.path.join('website', 'static', 'scss')
CSS_OUTPUT_DIR = os.path.join('website', 'static', 'css')
MAIN_SCSS = os.path.join(SCSS_DIR, 'main.scss')
MAIN_CSS = os.path.join(CSS_OUTPUT_DIR, 'main.css')

def ensure_dir_exists(directory):
    """Ensure the directory exists, create if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def compile_sass():
    """Compile SCSS to CSS."""
    try:
        ensure_dir_exists(CSS_OUTPUT_DIR)
        
        # Compile with source maps in development
        css = sass.compile(
            filename=MAIN_SCSS,
            output_style='compressed',  # Options: nested, expanded, compact, compressed
            source_map_filename=f"{MAIN_CSS}.map",
            source_map_contents=True,
            source_map_root=SCSS_DIR
        )
        
        # Write the compiled CSS
        with open(MAIN_CSS, 'w') as f:
            f.write(css)
        
        logger.info(f"SCSS compiled successfully to {MAIN_CSS}")
        return True
    except Exception as e:
        logger.error(f"Error compiling SCSS: {e}")
        return False

class ScssChangeHandler(FileSystemEventHandler):
    """Handler for SCSS file changes."""
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.scss'):
            logger.info(f"SCSS file changed: {event.src_path}")
            compile_sass()

def watch_scss():
    """Watch for changes in SCSS files and recompile."""
    event_handler = ScssChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, SCSS_DIR, recursive=True)
    observer.start()
    
    try:
        logger.info(f"Watching for changes in {SCSS_DIR}...")
        logger.info("Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

def main():
    """Main function to compile SCSS or watch for changes."""
    parser = argparse.ArgumentParser(description='Compile SCSS to CSS')
    parser.add_argument('--watch', action='store_true', help='Watch for changes and recompile')
    args = parser.parse_args()
    
    # Initial compilation
    compile_sass()
    
    # Watch for changes if requested
    if args.watch:
        watch_scss()

if __name__ == '__main__':
    main()
