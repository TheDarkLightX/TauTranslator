#!/bin/bash
# TauTranslatorOmega Uninstaller

echo "🗑️  Uninstalling TauTranslatorOmega..."

# Remove executable
rm -f "~//.local/bin/tau-translator-omega"

# Remove desktop files
rm -f "~//.local/share/applications/tau-translator-omega.desktop"
rm -f "~//Desktop/TauTranslatorOmega.desktop"

# Remove MIME type
rm -f "~//.local/share/mime/packages/tau-language.xml"
update-mime-database "~//.local/share/mime" 2>/dev/null

# Update desktop database
update-desktop-database "~//.local/share/applications" 2>/dev/null

echo "✅ TauTranslatorOmega uninstalled successfully"
echo "   Application files in ~/TauTranslator were not removed"
