#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Verify Checker Framework
echo "### Verifying Checker Framework warnings ###"
python3 $SCRIPT_DIR/verify_tool_warnings.py $SCRIPT_DIR/../scripts/parsers/results/cfnullness.warnings $SCRIPT_DIR/../data/tool-warnings/cfnullness.warnings

# Verify Eradicate
echo "### Verifying Eradicate warnings ###"
python3 $SCRIPT_DIR/verify_tool_warnings.py $SCRIPT_DIR/../scripts/parsers/results/eradicate.warnings $SCRIPT_DIR/../data/tool-warnings/eradicate.warnings

# Verify Infer
echo "### Verifying Infer warnings ###"
python3 $SCRIPT_DIR/verify_tool_warnings.py $SCRIPT_DIR/../scripts/parsers/results/infer.warnings $SCRIPT_DIR/../data/tool-warnings/infer.warnings

# Verify NullAway
echo "### Verifying NullAway warnings ###"
python3 $SCRIPT_DIR/verify_tool_warnings.py $SCRIPT_DIR/../scripts/parsers/results/nullaway.warnings $SCRIPT_DIR/../data/tool-warnings/nullaway.warnings

# Verify SpotBugs High Threshold
echo "### Verifying SpotBugs High Threshold warnings ###"
python3 $SCRIPT_DIR/verify_tool_warnings.py $SCRIPT_DIR/../scripts/parsers/results/sbht.warnings $SCRIPT_DIR/../data/tool-warnings/sbht.warnings

# Verify SpotBugs Low Threshold
echo "### Verifying SpotBugs Low Threshold warnings ###"
python3 $SCRIPT_DIR/verify_tool_warnings.py $SCRIPT_DIR/../scripts/parsers/results/sblt.warnings $SCRIPT_DIR/../data/tool-warnings/sblt.warnings

