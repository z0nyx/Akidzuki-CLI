echo "Installing akidzuki SSH CLI Manager..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Installing package..."
pip3 install -e .

if [ $? -ne 0 ]; then
    echo ""
    echo "Installation failed. Trying with --user flag..."
    pip3 install -e . --user
    if [ $? -ne 0 ]; then
        echo ""
        echo "Installation failed!"
        exit 1
    fi
fi

echo ""
echo "Checking if akidzuki command is available..."

if ! command -v akidzuki &> /dev/null; then
    echo ""
    echo "'akidzuki' command not found in PATH."
    echo ""
    
    USER_BIN=$(python3 -c "import site, os; print(os.path.join(os.path.dirname(site.getusersitepackages()), 'bin'))" 2>/dev/null)
    
    if [ -f "$USER_BIN/akidzuki" ]; then
        echo "Found akidzuki in: $USER_BIN"
        echo ""
        
        if [[ ":$PATH:" == *":$USER_BIN:"* ]]; then
            echo "This directory is already in PATH."
        else
            echo "Adding to PATH..."
            
            if [ -n "$ZSH_VERSION" ]; then
                SHELL_RC="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                SHELL_RC="$HOME/.bashrc"
            else
                SHELL_RC="$HOME/.profile"
            fi
            
            if [ -f "$SHELL_RC" ]; then
                if ! grep -q "export PATH.*$USER_BIN" "$SHELL_RC"; then
                    echo "" >> "$SHELL_RC"
                    echo "# Added by akidzuki installer" >> "$SHELL_RC"
                    echo "export PATH=\"\$PATH:$USER_BIN\"" >> "$SHELL_RC"
                    echo "SUCCESS: Added to $SHELL_RC"
                    echo ""
                    echo "Please run: source $SHELL_RC"
                    echo "Or restart your terminal."
                else
                    echo "Already added to $SHELL_RC"
                    echo "Please run: source $SHELL_RC"
                fi
            else
                echo "WARNING: Could not find shell rc file."
                echo "Please add this directory to your PATH manually:"
                echo "  export PATH=\"\$PATH:$USER_BIN\""
            fi
        fi
    else
        SYSTEM_BIN=$(python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>/dev/null | sed 's/Scripts/bin/')
        
        if [ -f "$SYSTEM_BIN/akidzuki" ] || [ -f "$(dirname "$SYSTEM_BIN")/bin/akidzuki" ]; then
            echo "Found akidzuki in system directory."
            echo "This directory should already be in PATH."
            echo "If 'akidzuki' still doesn't work, restart your terminal."
        else
            echo ""
            echo "ERROR: akidzuki not found in bin directories."
            echo "Please check the installation."
        fi
    fi
else
    echo ""
    echo "SUCCESS: 'akidzuki' command is available!"
    echo ""
    echo "You can now run 'akidzuki' from anywhere in the terminal."
fi

echo ""
