#!/bin/bash
# Generate local files from templates by substituting environment variables
# Templates use ${VARIABLE_NAME} syntax which gets replaced with actual values from .env

set -e -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════╗"
echo "║   Senville Local File Generator        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found"
    echo ""
    echo "Setup instructions:"
    echo "  1. cp .env.example .env"
    echo "  2. Edit .env with your device credentials"
    echo "  3. Run this script again"
    exit 1
fi

# Load environment variables
echo "📋 Loading configuration from .env..."
set -a  # automatically export all variables
source .env
# Keep variables exported for envsubst
# set +a  # Don't turn off export - we need them for envsubst

# Validate required variables
REQUIRED_VARS=(
    "SENVILLE_IP"
    "SENVILLE_TOKEN"
    "SENVILLE_KEY"
)

MISSING=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING+=("$var")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ ERROR: Missing required variables in .env:"
    printf '   - %s\n' "${MISSING[@]}"
    exit 1
fi

echo "✅ Configuration loaded"
echo ""

# Function to substitute environment variables in a file
# Uses envsubst if available, otherwise falls back to perl
substitute_vars() {
    local input="$1"
    local output="$2"

    # Check if envsubst is available
    if command -v envsubst &> /dev/null; then
        envsubst < "$input" > "$output"
    elif command -v perl &> /dev/null; then
        # Perl-based substitution
        perl -pe 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/ge' "$input" > "$output"
    else
        # Pure bash fallback - use eval with heredoc
        eval "cat << 'TEMPLATE_EOF' > \"$output\"
$(<"$input")
TEMPLATE_EOF
"
    fi
}

# List of template files to process
# Format: "template_file:output_file"
TEMPLATES=(
    "PROJECT_NOTES.md:PROJECT_NOTES.local.md"
    "QUICK_REFERENCE.md:QUICK_REFERENCE.local.md"
    "AUTOMATION.md:AUTOMATION.local.md"
    "WEB_INTERFACE.md:WEB_INTERFACE.local.md"
)

echo "🔄 Generating local files..."
echo ""

GENERATED=0
SKIPPED=0

for template_spec in "${TEMPLATES[@]}"; do
    IFS=':' read -r template output <<< "$template_spec"

    if [ -f "$template" ]; then
        if substitute_vars "$template" "$output"; then
            echo "  ✅ $template → $output"
            GENERATED=$((GENERATED + 1))
        else
            echo "  ❌ $template (substitution failed)"
            SKIPPED=$((SKIPPED + 1))
        fi
    else
        echo "  ⏭️  $template (not found, skipping)"
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo ""
echo "╔════════════════════════════════════════╗"
echo "║         Generation Complete!           ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "   Generated: $GENERATED files"
if [ $SKIPPED -gt 0 ]; then
    echo "   Skipped:   $SKIPPED files"
fi
echo ""
echo "📖 Your personalized documentation:"
for template_spec in "${TEMPLATES[@]}"; do
    IFS=':' read -r template output <<< "$template_spec"
    if [ -f "$output" ]; then
        echo "   - $output"
    fi
done
echo ""
echo "💡 Tip: These .local files contain your real IP addresses"
echo "   and are automatically ignored by git (safe to edit)"
echo ""
