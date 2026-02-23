#!/usr/bin/env bash
# ==========================================================================
# show_all_files_content.sh - Version corrigée
# Affiche récursivement le contenu de TOUS les fichiers d'un dossier
# Usage: ./show_all_files_content.sh [dossier] [extensions...]
# Exemples:
#   ./show_all_files_content.sh .                  # tous les fichiers
#   ./show_all_files_content.sh . py txt md        # seulement .py .txt .md
# ==========================================================================

set -euo pipefail

DIR="${1:-.}"
shift || true  # retire le premier argument (dossier)

# Extensions (si aucune → tous les fichiers)
EXTENSIONS=("$@")
if [ ${#EXTENSIONS[@]} -eq 0 ]; then
  EXTENSIONS=("")  # cas spécial : tous les fichiers
fi

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================================${NC}"
echo -e "  📂 Affichage récursif du contenu de : ${YELLOW}$DIR${NC}"
echo -e "${CYAN}============================================================${NC}"

print_file() {
  local file="$1"
  local rel_path="${file#$DIR/}"

  echo -e "\n${GREEN}┌── Fichier : ${CYAN}$rel_path${NC}"
  echo -e "${GREEN}│ Taille    : $(du -h "$file" | cut -f1)${NC}"
  echo -e "${GREEN}└────────────────────────────────────────────────────────────${NC}"

  # Contenu avec numéros de ligne et coloration basique
  if command -v bat &> /dev/null; then
    bat --style=plain --paging=never "$file" | sed "s/^/${BLUE}| ${NC}/"
  else
    cat -n "$file" | sed "s/^/${BLUE}| ${NC}/"
  fi

  echo -e "${GREEN}────────────────────────────────────────────────────────────${NC}\n"
}

found=0

for ext in "${EXTENSIONS[@]}"; do
  # Si pas d'extension → tous les fichiers
  if [ -z "$ext" ]; then
    pattern="*"
  else
    pattern="*.${ext}"
  fi

  while IFS= read -r -d '' file; do
    # Ignorer dossiers cachés / venv / caches
    if [[ "$file" =~ /\.(git|venv|node_modules|__pycache__|\.pytest_cache|\.mypy_cache|dist|build)/ ]]; then
      continue
    fi

    ((found++))
    print_file "$file"
  done < <(find "$DIR" -type f -name "$pattern" -print0 2>/dev/null)
done

if [ "$found" -eq 0 ]; then
  echo -e "${YELLOW}Aucun fichier trouvé.${NC}"
else
  echo -e "${GREEN}Total fichiers affichés : $found${NC}"
fi
