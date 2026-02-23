#!/usr/bin/env bash

# ═══════════════════════════════════════════════════════════
# NEXUS - Classificateur intelligent de documents IFRI
# Classe automatiquement : Cours / Exercices / Corrigés / Autres
# ═══════════════════════════════════════════════════════════

set -euo pipefail

# Couleurs pour l’affichage
RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[1;33m' BLUE='\033[0;34m'
CYAN='\033[0;36m' MAGENTA='\033[0;35m' NC='\033[0m'

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

SOURCE_DIR="${1:-$(pwd)}"               # Dossier source (1er argument ou courant)
OUTPUT_BASE="DOCS_CLASSES"              # Nom du dossier racine de sortie
DRY_RUN="${2:-no}"                      # "yes" pour simuler sans copier

# Dossiers de destination
COURS_DIR="$OUTPUT_BASE/COURS"
EXOS_DIR="$OUTPUT_BASE/EXERCICES"
CORRIGES_DIR="$OUTPUT_BASE/CORRIGES"
AUTRES_DIR="$OUTPUT_BASE/AUTRES"

# Compteurs
COURS_COUNT=0 EXOS_COUNT=0 CORRIGES_COUNT=0 AUTRES_COUNT=0

# Log
LOG_FILE="classification_$(date +%Y%m%d_%H%M%S).txt"

# Extensions à considérer
DOC_EXTENSIONS=("pdf" "docx" "doc" "txt" "md" "pptx" "ppt" "odt")

# ═══════════════════════════════════════════════════════════
# PATTERNS (mots-clés pour classifier)
# ═══════════════════════════════════════════════════════════

COURS_PATTERNS=("cours" "chapitre" "leçon" "note" "cm" "support" "slide" "powerpoint" "polycopié" "résumé" "théorie" "introduction" "présentation" "fiche" "synthese" "partie" "section")
EXOS_PATTERNS=("exo" "exercice" "td" "tp" "travaux" "série" "problème" "question" "qcm" "devoir" "test" "annale" "sujet" "partiel" "examen" "entrainement")
CORRIGES_PATTERNS=("corrigé" "correction" "solution" "réponse" "corrige" "sol" "answer" "key" "bareme" "reponses")

# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════

print_header() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════"
    echo "  📚 NEXUS - CLASSIFICATEUR INTELLIGENT"
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_config() {
    echo -e "${BLUE}📂 Source:${NC} $SOURCE_DIR"
    echo -e "${BLUE}📁 Destination:${NC} $OUTPUT_BASE"
    echo -e "${BLUE}🏷️ Catégories:${NC}"
    echo "   - $COURS_DIR"
    echo "   - $EXOS_DIR"
    echo "   - $CORRIGES_DIR"
    echo "   - $AUTRES_DIR"
    echo ""
    if [ "$DRY_RUN" = "yes" ]; then
        echo -e "${YELLOW}⚠️ MODE SIMULATION (dry-run)${NC}"
    fi
}

create_directories() {
    mkdir -p "$COURS_DIR" "$EXOS_DIR" "$CORRIGES_DIR" "$AUTRES_DIR"
    echo -e "${GREEN}✅ Dossiers créés${NC}\n"
}

normalize_string() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 'y/àáâãäåèéêëìíîïòóôõöùúûüýÿ/aaaaaaeeeeiiiioooooouuuuyy/'
}

detect_category() {
    local filename="$1"
    local normalized=$(normalize_string "$filename")

    # Priorité 1 : Corrigés (souvent "exercice_corrigé")
    for p in "${CORRIGES_PATTERNS[@]}"; do
        [[ "$normalized" == *"$p"* ]] && echo "CORRIGES" && return
    done

    # Priorité 2 : Exercices
    for p in "${EXOS_PATTERNS[@]}"; do
        [[ "$normalized" == *"$p"* ]] && echo "EXERCICES" && return
    done

    # Priorité 3 : Cours
    for p in "${COURS_PATTERNS[@]}"; do
        [[ "$normalized" == *"$p"* ]] && echo "COURS" && return
    done

    echo "AUTRES"
}

process_files() {
    echo -e "${YELLOW}🔍 Scan et classification...${NC}\n"

    # Compte total
    local total=$(find "$SOURCE_DIR" -type f \( -iname "*.pdf" -o -iname "*.docx" -o -iname "*.txt" -o -iname "*.md" \) | wc -l)
    echo -e "${GREEN}📄 $total documents trouvés${NC}\n"

    local count=0
    find "$SOURCE_DIR" -type f \( -iname "*.pdf" -o -iname "*.docx" -o -iname "*.txt" -o -iname "*.md" \) -print0 | while IFS= read -r -d '' file; do
        ((count++))
        if (( count % 5 == 0 )); then
            echo -ne "\r⏳ Progression: $count / $total"
        fi

        category=$(detect_category "$file")
        filename=$(basename "$file")

        case "$category" in
            COURS)     ((COURS_COUNT++)); dest="$COURS_DIR" ;;
            EXERCICES) ((EXOS_COUNT++));  dest="$EXOS_DIR" ;;
            CORRIGES)  ((CORRIGES_COUNT++)); dest="$CORRIGES_DIR" ;;
            *)         ((AUTRES_COUNT++)); dest="$AUTRES_DIR" ;;
        esac

        # Copie avec chemin relatif
        rel_path="${file#$SOURCE_DIR/}"
        dest_path="$dest/${rel_path%/*}"
        mkdir -p "$dest_path"

        local color=""
        case "$category" in COURS) color="$BLUE" ;; EXERCICES) color="$YELLOW" ;; CORRIGES) color="$GREEN" ;; *) color="$MAGENTA" ;; esac

        echo -e "${color}[$category]${NC} $filename"
        cp -v "$file" "$dest/${rel_path}" 2>/dev/null || echo "   → Erreur copie $filename"
    done
    echo ""
}

display_summary() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ CLASSIFICATION TERMINÉE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}📊 STATISTIQUES:${NC}"
    echo -e "   📘 Cours: ${BLUE}$COURS_COUNT${NC}"
    echo -e "   📝 Exercices: ${YELLOW}$EXOS_COUNT${NC}"
    echo -e "   ✅ Corrigés: ${GREEN}$CORRIGES_COUNT${NC}"
    echo -e "   📄 Autres: ${MAGENTA}$AUTRES_COUNT${NC}"
    echo ""
    echo -e "${BLUE}📁 Dossiers créés dans:${NC} $OUTPUT_BASE"
    echo ""
    echo -e "${YELLOW}💡 RECOMMANDATIONS:${NC}"
    echo "   1. Vérifie surtout AUTRES/ pour les fichiers mal classés"
    echo "   2. Relance ton RAG avec DOCS_CLASSES comme docs_path"
    echo ""
}

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

print_header
print_config
create_directories
process_files
display_summary

echo -e "${GREEN}🎉 Terminé !${NC}"
